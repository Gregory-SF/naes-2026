from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import (
    AnaliseExecucaoForm,
    BranchCreateForm,
    ConfiguracaoGlobalForm,
    EquipeForm,
    ProjetoForm,
    build_projeto_repositorio_formset,
    SprintFiltroForm,
    SprintForm,
    sync_projeto_repositorios,
)
from .models import (
    Aluno,
    Branch,
    ConfiguracaoGlobal,
    DiaAulaConfiguracao,
    Equipe,
    ExecucaoAnalise,
    MembroEquipe,
    PapelScrum,
    Projeto,
    Repositorio,
    Sprint,
    StatusProjeto,
)
from .services.analysis import AnalysisServiceError, fetch_remote_branches, import_commits_for_execution, persist_branch_names
from .services.global_settings import (
    bootstrap_dias_aula_choices,
    clear_token,
    get_plain_github_token,
    get_or_create_global_settings,
    mask_token,
    save_global_settings,
)


class ProjetoFormMixin:
    """Monta e valida o formset de repositórios junto com o ModelForm de Projeto."""

    model = Projeto
    form_class = ProjetoForm
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')

    def get_repositorio_formset(self, data=None):
        return build_projeto_repositorio_formset(
            data=data,
            projeto=getattr(self, 'object', None),
            project_owner=(data or {}).get('link_organizacao_github'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('repositorio_formset', self.get_repositorio_formset())
        context['titulo'] = self.titulo
        context['botao'] = self.botao
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() if 'pk' in kwargs else None
        form = self.get_form()
        repositorio_formset = self.get_repositorio_formset(data=request.POST)
        if form.is_valid() and repositorio_formset.is_valid():
            return self.form_valid(form, repositorio_formset)
        return self.form_invalid(form, repositorio_formset)

    def form_valid(self, form, repositorio_formset):
        with transaction.atomic():
            projeto = form.save()
            sync_projeto_repositorios(projeto, repositorio_formset)
        self.object = projeto
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)

    def form_invalid(self, form, repositorio_formset):
        context = self.get_context_data(form=form, repositorio_formset=repositorio_formset)
        return render(self.request, self.template_name, context)


class ProjetoCreate(LoginRequiredMixin, ProjetoFormMixin, CreateView):
    titulo = 'Cadastro de Projeto'
    botao = 'Criar Projeto'
    success_message = 'Projeto criado com sucesso.'


class ProjetoUpdate(LoginRequiredMixin, ProjetoFormMixin, UpdateView):
    titulo = 'Editar dados do Projeto'
    botao = 'Atualizar Projeto'
    success_message = 'Projeto atualizado com sucesso.'


class ProjetoDelete(LoginRequiredMixin, DeleteView):
    model = Projeto
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {'titulo': 'Excluir Projeto', 'botao': 'Sim, excluir!'}


class ProjetoList(LoginRequiredMixin, ListView):
    model = Projeto
    template_name = 'commex/list/projeto.html'
    context_object_name = 'projetos'
    paginate_by = 20

    def get_queryset(self):
        return Projeto.objects.prefetch_related('repositorios').order_by('-ano', 'nome')


class ProjetoDetail(LoginRequiredMixin, DetailView):
    model = Projeto
    template_name = 'commex/detail/projeto.html'

    def get_queryset(self):
        return Projeto.objects.prefetch_related('repositorios')


class EquipeList(LoginRequiredMixin, ListView):
    model = Equipe
    template_name = 'commex/equipes/list.html'
    paginate_by = 20

    def get_queryset(self):
        return (
            Equipe.objects.select_related('projeto')
            .prefetch_related('membros__aluno')
            .order_by('nome')
        )


class EquipeDetail(LoginRequiredMixin, DetailView):
    model = Equipe
    template_name = 'commex/equipes/detail.html'

    def get_queryset(self):
        return (
            Equipe.objects.select_related('projeto')
            .prefetch_related('membros__aluno')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membros = self.object.membros.select_related('aluno').all()
        context['membros_sm'] = [m for m in membros if m.papel == PapelScrum.SCRUM_MASTER]
        context['membros_po'] = [m for m in membros if m.papel == PapelScrum.PRODUCT_OWNER]
        context['membros_dev'] = [m for m in membros if m.papel == PapelScrum.DESENVOLVEDOR]
        return context


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_member_data(post_data):
    sm_nome = (post_data.get('membros_sm_nome') or '').strip()
    po_nome = (post_data.get('membros_po_nome') or '').strip()
    total_devs = max(1, _safe_int(post_data.get('membros_total_devs'), default=1))

    dev_nomes = []
    for index in range(total_devs):
        dev_nomes.append((post_data.get(f'membros_dev_{index}_nome') or '').strip())

    return {
        'sm_nome': sm_nome,
        'po_nome': po_nome,
        'dev_nomes': dev_nomes,
        'total_devs': total_devs,
    }


def _initial_member_data(equipe=None):
    if equipe is None:
        return {
            'sm_nome': '',
            'po_nome': '',
            'dev_nomes': [''],
            'total_devs': 1,
        }

    membros = equipe.membros.select_related('aluno').all()
    sm_nome = ''
    po_nome = ''
    dev_nomes = []

    for membro in membros:
        if membro.papel == PapelScrum.SCRUM_MASTER:
            sm_nome = membro.aluno.nome
        elif membro.papel == PapelScrum.PRODUCT_OWNER:
            po_nome = membro.aluno.nome
        elif membro.papel == PapelScrum.DESENVOLVEDOR:
            dev_nomes.append(membro.aluno.nome)

    if not dev_nomes:
        dev_nomes = ['']

    return {
        'sm_nome': sm_nome,
        'po_nome': po_nome,
        'dev_nomes': dev_nomes,
        'total_devs': len(dev_nomes),
    }


def _resolve_aluno_por_texto(texto):
    candidatos_nome = list(Aluno.objects.filter(nome__iexact=texto)[:2])
    if len(candidatos_nome) == 1:
        return candidatos_nome[0], None

    if len(candidatos_nome) > 1:
        aluno_por_apelido = Aluno.objects.filter(github_nickname__iexact=texto).first()
        if aluno_por_apelido:
            return aluno_por_apelido, None
        return None, 'Mais de um aluno encontrado com este nome. Informe um apelido GitHub unico.'

    aluno_por_apelido = Aluno.objects.filter(github_nickname__iexact=texto).first()
    if aluno_por_apelido:
        return aluno_por_apelido, None

    return None, 'Aluno nao encontrado por nome ou apelido GitHub.'


def _validar_e_resolver_membros(member_data):
    errors = {
        'sm_nome': '',
        'po_nome': '',
        'dev_nomes': {},
        'geral': [],
    }

    resolved_members = []

    if not member_data['sm_nome']:
        errors['sm_nome'] = 'Informe o nome do Scrum Master.'
    if not member_data['po_nome']:
        errors['po_nome'] = 'Informe o nome do Product Owner.'

    devs_preenchidos = [(i, nome) for i, nome in enumerate(member_data['dev_nomes']) if nome]
    if not devs_preenchidos:
        errors['geral'].append('A equipe deve ter ao menos um Desenvolvedor.')

    seen_alunos = set()

    if member_data['sm_nome']:
        aluno, erro = _resolve_aluno_por_texto(member_data['sm_nome'])
        if erro:
            errors['sm_nome'] = erro
        else:
            resolved_members.append((PapelScrum.SCRUM_MASTER, aluno))
            seen_alunos.add(aluno.pk)

    if member_data['po_nome']:
        aluno, erro = _resolve_aluno_por_texto(member_data['po_nome'])
        if erro:
            errors['po_nome'] = erro
        else:
            if aluno.pk in seen_alunos:
                errors['po_nome'] = 'O mesmo aluno nao pode ocupar mais de um papel na equipe.'
            else:
                resolved_members.append((PapelScrum.PRODUCT_OWNER, aluno))
                seen_alunos.add(aluno.pk)

    for index, dev_nome in devs_preenchidos:
        aluno, erro = _resolve_aluno_por_texto(dev_nome)
        if erro:
            errors['dev_nomes'][index] = erro
            continue
        if aluno.pk in seen_alunos:
            errors['dev_nomes'][index] = 'O mesmo aluno nao pode ocupar mais de um papel na equipe.'
            continue
        resolved_members.append((PapelScrum.DESENVOLVEDOR, aluno))
        seen_alunos.add(aluno.pk)

    has_errors = bool(
        errors['sm_nome']
        or errors['po_nome']
        or errors['dev_nomes']
        or errors['geral']
    )
    if has_errors:
        return None, errors
    return resolved_members, errors


def _persistir_membros_equipe(equipe, resolved_members):
    MembroEquipe.objects.filter(equipe=equipe).delete()
    MembroEquipe.objects.bulk_create(
        [
            MembroEquipe(equipe=equipe, aluno=aluno, papel=papel)
            for papel, aluno in resolved_members
        ]
    )


class EquipeCreate(LoginRequiredMixin, View):
    template_name = 'commex/equipes/form.html'

    def get(self, request):
        form = EquipeForm()
        member_data = _initial_member_data()
        member_errors = {'sm_nome': '', 'po_nome': '', 'dev_nomes': {}, 'geral': []}
        return render(
            request,
            self.template_name,
            {'form': form, 'member_data': member_data, 'member_errors': member_errors, 'titulo': 'Cadastro de Equipe'},
        )

    def post(self, request):
        form = EquipeForm(request.POST)
        member_data = _extract_member_data(request.POST)
        resolved_members, member_errors = _validar_e_resolver_membros(member_data)

        if form.is_valid() and resolved_members is not None:
            with transaction.atomic():
                equipe = form.save()
                _persistir_membros_equipe(equipe, resolved_members)
            messages.success(request, 'Equipe criada com sucesso.')
            return redirect('equipe-detail', pk=equipe.pk)

        return render(
            request,
            self.template_name,
            {'form': form, 'member_data': member_data, 'member_errors': member_errors, 'titulo': 'Cadastro de Equipe'},
        )


class EquipeUpdate(LoginRequiredMixin, View):
    template_name = 'commex/equipes/form.html'

    def get_object(self, pk):
        return get_object_or_404(Equipe, pk=pk)

    def get(self, request, pk):
        equipe = self.get_object(pk)
        form = EquipeForm(instance=equipe)
        member_data = _initial_member_data(equipe)
        member_errors = {'sm_nome': '', 'po_nome': '', 'dev_nomes': {}, 'geral': []}
        return render(
            request,
            self.template_name,
            {'form': form, 'member_data': member_data, 'member_errors': member_errors, 'titulo': 'Editar Equipe', 'object': equipe},
        )

    def post(self, request, pk):
        equipe = self.get_object(pk)
        form = EquipeForm(request.POST, instance=equipe)
        member_data = _extract_member_data(request.POST)
        resolved_members, member_errors = _validar_e_resolver_membros(member_data)

        if form.is_valid() and resolved_members is not None:
            with transaction.atomic():
                form.save()
                _persistir_membros_equipe(equipe, resolved_members)
            messages.success(request, 'Equipe atualizada com sucesso.')
            return redirect('equipe-detail', pk=equipe.pk)
        return render(
            request,
            self.template_name,
            {'form': form, 'member_data': member_data, 'member_errors': member_errors, 'titulo': 'Editar Equipe', 'object': equipe},
        )


class EquipeDelete(LoginRequiredMixin, View):
    template_name = 'commex/equipes/confirm_disable.html'

    def get(self, request, pk):
        equipe = get_object_or_404(Equipe, pk=pk)
        return render(request, self.template_name, {'object': equipe})

    def post(self, request, pk):
        equipe = get_object_or_404(Equipe, pk=pk)
        if equipe.membros.count() == 0:
            equipe.ativo = False
            equipe.save(update_fields=['ativo'])
            messages.success(request, 'Equipe inativada com sucesso.')
            return redirect('equipe-list')
        messages.error(request, 'Nao e possivel inativar equipe com membros ativos. Remova os membros antes.')
        return redirect('equipe-detail', pk=equipe.pk)


@login_required
def membro_delete(request, pk):
    membro = get_object_or_404(MembroEquipe, pk=pk)
    equipe = membro.equipe
    if request.method == 'POST':
        if membro.papel != PapelScrum.DESENVOLVEDOR:
            messages.error(request, 'Scrum Master e Product Owner so podem ser alterados via edicao da equipe.')
        elif equipe.membros.filter(papel=PapelScrum.DESENVOLVEDOR).count() <= 1:
            messages.error(request, 'A equipe deve manter ao menos um Desenvolvedor.')
        else:
            membro.delete()
            messages.success(request, 'Membro removido com sucesso.')
        return redirect('equipe-update', pk=equipe.pk)
    return render(request, 'commex/membros/confirm_delete.html', {'object': membro})


class SprintList(LoginRequiredMixin, ListView):
    model = Sprint
    template_name = 'commex/sprints/list.html'
    paginate_by = 20

    def get_queryset(self):
        qs = Sprint.objects.prefetch_related('projetos').order_by('-data_inicio', 'nome')
        self.filter_form = SprintFiltroForm(self.request.GET or None)
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data.get('nome'):
                qs = qs.filter(nome__icontains=data['nome'])
            if data.get('projeto'):
                qs = qs.filter(projetos=data['projeto'])
            if data.get('inicio_de'):
                qs = qs.filter(data_inicio__gte=data['inicio_de'])
            if data.get('fim_ate'):
                qs = qs.filter(data_fim__lte=data['fim_ate'])
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = getattr(self, 'filter_form', SprintFiltroForm())
        return ctx


class SprintDetail(LoginRequiredMixin, DetailView):
    model = Sprint
    template_name = 'commex/sprints/detail.html'


class SprintCreate(LoginRequiredMixin, View):
    template_name = 'commex/sprints/form.html'

    def get(self, request):
        form = SprintForm()
        return render(request, self.template_name, {'form': form, 'titulo': 'Cadastrar Sprint'})

    def post(self, request):
        form = SprintForm(request.POST)
        if form.is_valid():
            sprint = form.save()
            messages.success(request, 'Sprint criada com sucesso.')
            return redirect('sprint-detail', pk=sprint.pk)
        return render(request, self.template_name, {'form': form, 'titulo': 'Cadastrar Sprint'})


class SprintUpdate(LoginRequiredMixin, View):
    template_name = 'commex/sprints/form.html'

    def get(self, request, pk):
        sprint = get_object_or_404(Sprint, pk=pk)
        form = SprintForm(instance=sprint, initial={'projetos': sprint.projetos.all()})
        return render(request, self.template_name, {'form': form, 'titulo': 'Editar Sprint', 'object': sprint})

    def post(self, request, pk):
        sprint = get_object_or_404(Sprint, pk=pk)
        form = SprintForm(request.POST, instance=sprint)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sprint atualizada com sucesso.')
            return redirect('sprint-detail', pk=sprint.pk)
        return render(request, self.template_name, {'form': form, 'titulo': 'Editar Sprint', 'object': sprint})


@login_required
def configuracoes_globais(request):
    bootstrap_dias_aula_choices()
    config = get_or_create_global_settings()
    if request.method == 'POST':
        form = ConfiguracaoGlobalForm(request.POST, instance=config)
        if form.is_valid():
            token = form.cleaned_data.get('github_token', '')
            dias = form.cleaned_data.get('dias_aula')
            save_global_settings(token, dias)
            messages.success(request, 'Configuracoes salvas com sucesso.')
            return redirect('configuracoes-globais')
    else:
        form = ConfiguracaoGlobalForm(instance=config)

    token_masked = mask_token(form.instance.github_token)
    token_masked = mask_token(get_plain_github_token())
    return render(
        request,
        'commex/form/configuracoes.html',
        {
            'form': form,
            'token_masked': token_masked,
            'token_configurado': bool(config.github_token),
        },
    )


@login_required
def configuracoes_remover_token(request):
    if request.method == 'POST':
        clear_token()
        messages.success(request, 'Token removido com sucesso.')
    return redirect('configuracoes-globais')


@login_required
def analysis_branches(request):
    form = BranchCreateForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Branch cadastrada com sucesso.')
        return redirect('analysis-branches')

    repositorio_id = request.POST.get('repositorio') or request.GET.get('repositorio')
    if request.method == 'POST' and request.POST.get('action') == 'fetch' and repositorio_id:
        repositorio = get_object_or_404(Repositorio, pk=repositorio_id)
        try:
            names = fetch_remote_branches(repositorio.link)
            created = persist_branch_names(repositorio, names)
            messages.success(request, f'{created} branch(es) novas cadastradas com sucesso.')
        except AnalysisServiceError as exc:
            messages.error(request, str(exc))

    branches = Branch.objects.select_related('repositorio', 'repositorio__projeto').order_by('repositorio__nome', 'nome')
    repositorios = Repositorio.objects.select_related('projeto').order_by('nome')
    return render(request, 'commex/analysis/branches.html', {'form': form, 'branches': branches, 'repositorios': repositorios})


@login_required
def analysis_start(request):
    form = AnaliseExecucaoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        sprint = data.get('sprint')
        inicio = sprint.data_inicio if sprint else data.get('data_inicio')
        fim = sprint.data_fim if sprint else data.get('data_fim')

        execucao = ExecucaoAnalise.objects.create(
            projeto=data['projeto'],
            repositorio=data['repositorio'],
            branch=data['branch'],
            sprint=sprint,
            data_inicio=inicio,
            data_fim=fim,
        )
        try:
            import_commits_for_execution(execucao)
            messages.success(request, 'Analise executada com sucesso.')
        except Exception as exc:
            messages.error(request, f'Analise finalizada com erro: {exc}')
        return redirect('analysis-status', pk=execucao.pk)

    return render(request, 'commex/analysis/start.html', {'form': form})


@login_required
def analysis_status(request, pk=None):
    if pk:
        execucao = get_object_or_404(
            ExecucaoAnalise.objects.select_related('projeto', 'repositorio', 'branch').prefetch_related('commits'),
            pk=pk,
        )
        execucoes = ExecucaoAnalise.objects.select_related('projeto', 'repositorio', 'branch').all()[:30]
        return render(request, 'commex/analysis/status.html', {'object': execucao, 'execucoes': execucoes})

    execucoes = ExecucaoAnalise.objects.select_related('projeto', 'repositorio', 'branch').all()[:30]
    return render(request, 'commex/analysis/status.html', {'execucoes': execucoes})


class IndexView(LoginRequiredMixin, ListView):
    model = Projeto
    template_name = 'commex/index.html'
    context_object_name = 'projetos'
    paginate_by = 5

    def get_queryset(self):
        return Projeto.objects.prefetch_related('repositorios').order_by('-ano', 'nome')
