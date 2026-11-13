from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.db.models import ProtectedError
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django_filters.views import FilterView

from django.conf import settings

from .decorators import group_required

GRUPO_COORDENADORES = settings.GRUPO_COORDENADORES
GRUPO_PROFESSORES = settings.GRUPO_PROFESSORES

from .filters import EquipeFilter, ProjetoFilter, SprintFilter
from .forms import (
    AnaliseExecucaoForm,
    BranchCreateForm,
    ConfiguracaoGlobalForm,
    EquipeForm,
    ProjetoForm,
    build_projeto_repositorio_formset,
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


class DonoQuerysetMixin:
    """Restringe o queryset aos registros cadastrados pelo usuário logado (404 para os de outros)."""

    def get_queryset(self):
        return super().get_queryset().filter(cadastrado_por=self.request.user)


class ProjetoFormMixin:
    """Monta e valida o formset de repositórios junto com o ModelForm de Projeto."""

    model = Projeto
    form_class = ProjetoForm
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')

    def get_queryset(self):
        return Projeto.objects.filter(cadastrado_por=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

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
        if not form.instance.pk:
            form.instance.cadastrado_por = self.request.user
        with transaction.atomic():
            projeto = form.save()
            sync_projeto_repositorios(projeto, repositorio_formset)
        self.object = projeto
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)

    def form_invalid(self, form, repositorio_formset):
        context = self.get_context_data(form=form, repositorio_formset=repositorio_formset)
        return render(self.request, self.template_name, context)


class ProjetoCreate(GroupRequiredMixin, ProjetoFormMixin, CreateView):
    group_required = GRUPO_COORDENADORES
    titulo = 'Cadastro de Projeto'
    botao = 'Criar Projeto'
    success_message = 'Projeto criado com sucesso.'


class ProjetoUpdate(GroupRequiredMixin, ProjetoFormMixin, UpdateView):
    group_required = GRUPO_COORDENADORES
    titulo = 'Editar dados do Projeto'
    botao = 'Atualizar Projeto'
    success_message = 'Projeto atualizado com sucesso.'


class ProjetoDelete(GroupRequiredMixin, DonoQuerysetMixin, DeleteView):
    group_required = GRUPO_COORDENADORES
    model = Projeto
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {'titulo': 'Excluir Projeto', 'botao': 'Sim, excluir!'}

    def form_valid(self, form):
        nome = self.object.nome
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, f'Não é possível excluir o projeto "{nome}": existem equipes ou análises vinculadas.')
            return redirect('projeto-list')
        messages.success(self.request, f'Projeto "{nome}" excluído com sucesso.')
        return response


class ProjetoList(GroupRequiredMixin, FilterView):
    group_required = [GRUPO_COORDENADORES, GRUPO_PROFESSORES]
    model = Projeto
    filterset_class = ProjetoFilter
    template_name = 'commex/list/projeto.html'
    context_object_name = 'projetos'
    paginate_by = 20

    def get_queryset(self):
        # annotate evita um COUNT por linha ao renderizar a coluna "Repositórios"
        return (
            Projeto.objects.filter(cadastrado_por=self.request.user)
            .prefetch_related('repositorios')
            .annotate(total_repositorios=Count('repositorios', distinct=True))
            .order_by('-ano', 'nome')
        )


class ProjetoDetail(GroupRequiredMixin, DetailView):
    group_required = [GRUPO_COORDENADORES, GRUPO_PROFESSORES]
    model = Projeto
    template_name = 'commex/detail/projeto.html'

    def get_queryset(self):
        return Projeto.objects.filter(cadastrado_por=self.request.user).prefetch_related('repositorios')


class EquipeList(GroupRequiredMixin, FilterView):
    group_required = [GRUPO_COORDENADORES, GRUPO_PROFESSORES]
    model = Equipe
    filterset_class = EquipeFilter
    template_name = 'commex/equipes/list.html'
    paginate_by = 20

    def get_queryset(self):
        return (
            Equipe.objects.filter(cadastrado_por=self.request.user)
            .select_related('projeto')
            .prefetch_related('membros__aluno')
            .order_by('nome')
        )


class EquipeDetail(GroupRequiredMixin, DetailView):
    group_required = [GRUPO_COORDENADORES, GRUPO_PROFESSORES]
    model = Equipe
    template_name = 'commex/equipes/detail.html'

    def get_queryset(self):
        return (
            Equipe.objects.filter(cadastrado_por=self.request.user)
            .select_related('projeto')
            .prefetch_related('membros__aluno')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membros = list(self.object.membros.all())  # já vem do prefetch (membros__aluno)
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


class EquipeCreate(GroupRequiredMixin, View):
    group_required = GRUPO_COORDENADORES
    template_name = 'commex/equipes/form.html'

    def get(self, request):
        form = EquipeForm(user=request.user)
        member_data = _initial_member_data()
        member_errors = {'sm_nome': '', 'po_nome': '', 'dev_nomes': {}, 'geral': []}
        return render(
            request,
            self.template_name,
            {'form': form, 'member_data': member_data, 'member_errors': member_errors, 'titulo': 'Cadastro de Equipe'},
        )

    def post(self, request):
        form = EquipeForm(request.POST, user=request.user)
        member_data = _extract_member_data(request.POST)
        resolved_members, member_errors = _validar_e_resolver_membros(member_data)

        if form.is_valid() and resolved_members is not None:
            with transaction.atomic():
                equipe = form.save(commit=False)
                equipe.cadastrado_por = request.user
                equipe.save()
                _persistir_membros_equipe(equipe, resolved_members)
            messages.success(request, 'Equipe criada com sucesso.')
            return redirect('equipe-detail', pk=equipe.pk)

        return render(
            request,
            self.template_name,
            {'form': form, 'member_data': member_data, 'member_errors': member_errors, 'titulo': 'Cadastro de Equipe'},
        )


class EquipeUpdate(GroupRequiredMixin, View):
    group_required = GRUPO_COORDENADORES
    template_name = 'commex/equipes/form.html'

    def get_object(self, pk):
        return get_object_or_404(Equipe, pk=pk, cadastrado_por=self.request.user)

    def get(self, request, pk):
        equipe = self.get_object(pk)
        form = EquipeForm(instance=equipe, user=request.user)
        member_data = _initial_member_data(equipe)
        member_errors = {'sm_nome': '', 'po_nome': '', 'dev_nomes': {}, 'geral': []}
        return render(
            request,
            self.template_name,
            {'form': form, 'member_data': member_data, 'member_errors': member_errors, 'titulo': 'Editar Equipe', 'object': equipe},
        )

    def post(self, request, pk):
        equipe = self.get_object(pk)
        form = EquipeForm(request.POST, instance=equipe, user=request.user)
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


class EquipeDelete(GroupRequiredMixin, View):
    group_required = GRUPO_COORDENADORES
    template_name = 'commex/equipes/confirm_disable.html'

    def get(self, request, pk):
        equipe = get_object_or_404(Equipe, pk=pk, cadastrado_por=request.user)
        return render(request, self.template_name, {'object': equipe})

    def post(self, request, pk):
        equipe = get_object_or_404(Equipe, pk=pk, cadastrado_por=request.user)
        if equipe.membros.count() == 0:
            equipe.ativo = False
            equipe.save(update_fields=['ativo'])
            messages.success(request, 'Equipe inativada com sucesso.')
            return redirect('equipe-list')
        messages.error(request, 'Nao e possivel inativar equipe com membros ativos. Remova os membros antes.')
        return redirect('equipe-detail', pk=equipe.pk)


@group_required(GRUPO_COORDENADORES)
def membro_delete(request, pk):
    membro = get_object_or_404(MembroEquipe.objects.select_related('equipe'), pk=pk, equipe__cadastrado_por=request.user)
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


class SprintList(GroupRequiredMixin, FilterView):
    group_required = [GRUPO_COORDENADORES, GRUPO_PROFESSORES]
    model = Sprint
    filterset_class = SprintFilter
    template_name = 'commex/sprints/list.html'
    paginate_by = 20

    def get_queryset(self):
        return (
            Sprint.objects.filter(cadastrado_por=self.request.user)
            .prefetch_related('projetos')
            .annotate(total_projetos=Count('projetos', distinct=True))
            .order_by('-data_inicio', 'nome')
        )


class SprintDetail(GroupRequiredMixin, DonoQuerysetMixin, DetailView):
    group_required = [GRUPO_COORDENADORES, GRUPO_PROFESSORES]
    model = Sprint
    template_name = 'commex/sprints/detail.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('projetos')


class SprintCreate(GroupRequiredMixin, View):
    group_required = GRUPO_COORDENADORES
    template_name = 'commex/sprints/form.html'

    def get(self, request):
        form = SprintForm(user=request.user)
        return render(request, self.template_name, {'form': form, 'titulo': 'Cadastrar Sprint'})

    def post(self, request):
        form = SprintForm(request.POST, user=request.user)
        if form.is_valid():
            sprint = form.save(commit=False)
            sprint.cadastrado_por = request.user
            sprint.save()
            sprint.projetos.set(form.cleaned_data.get('projetos', []))
            messages.success(request, 'Sprint criada com sucesso.')
            return redirect('sprint-detail', pk=sprint.pk)
        return render(request, self.template_name, {'form': form, 'titulo': 'Cadastrar Sprint'})


class SprintUpdate(GroupRequiredMixin, View):
    group_required = GRUPO_COORDENADORES
    template_name = 'commex/sprints/form.html'

    def get(self, request, pk):
        sprint = get_object_or_404(Sprint, pk=pk, cadastrado_por=request.user)
        form = SprintForm(instance=sprint, user=request.user, initial={'projetos': sprint.projetos.all()})
        return render(request, self.template_name, {'form': form, 'titulo': 'Editar Sprint', 'object': sprint})

    def post(self, request, pk):
        sprint = get_object_or_404(Sprint, pk=pk, cadastrado_por=request.user)
        form = SprintForm(request.POST, instance=sprint, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sprint atualizada com sucesso.')
            return redirect('sprint-detail', pk=sprint.pk)
        return render(request, self.template_name, {'form': form, 'titulo': 'Editar Sprint', 'object': sprint})


@group_required(GRUPO_COORDENADORES)
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


@group_required(GRUPO_COORDENADORES)
def configuracoes_remover_token(request):
    if request.method == 'POST':
        clear_token()
        messages.success(request, 'Token removido com sucesso.')
    return redirect('configuracoes-globais')


@group_required(GRUPO_COORDENADORES)
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


@group_required(GRUPO_COORDENADORES)
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


@group_required(GRUPO_COORDENADORES, GRUPO_PROFESSORES)
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


class IndexView(GroupRequiredMixin, ListView):
    group_required = [GRUPO_COORDENADORES, GRUPO_PROFESSORES]
    model = Projeto
    template_name = 'commex/index.html'
    context_object_name = 'projetos'
    paginate_by = 5

    def get_queryset(self):
        return (
            Projeto.objects.filter(cadastrado_por=self.request.user)
            .prefetch_related('repositorios')
            .annotate(total_repositorios=Count('repositorios', distinct=True))
            .order_by('-ano', 'nome')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        equipes = Equipe.objects.filter(cadastrado_por=usuario)
        sprints = Sprint.objects.filter(cadastrado_por=usuario)
        projetos = Projeto.objects.filter(cadastrado_por=usuario)
        context['projetos_recentes'] = projetos.order_by('-cadastrado_em')[:5]
        context['equipes_recentes'] = equipes.select_related('projeto').order_by('-id')[:5]
        context['sprints_recentes'] = sprints.order_by('-data_inicio', 'nome')[:5]
        # o total de projetos vem do paginator (que já executou o COUNT da lista)
        context['total_projetos'] = context['paginator'].count if context.get('paginator') else projetos.count()
        context['total_equipes'] = equipes.count()
        context['total_sprints'] = sprints.count()
        return context
