from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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
    MembroEquipeFormSet,
    ProjetoForm,
    SprintFiltroForm,
    SprintForm,
)
from .models import (
    Branch,
    ConfiguracaoGlobal,
    DiaAulaConfiguracao,
    Equipe,
    ExecucaoAnalise,
    MembroEquipe,
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


class ProjetoCreate(LoginRequiredMixin, CreateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {'titulo': 'Cadastro de Projeto', 'botao': 'Criar Projeto'}


class ProjetoUpdate(LoginRequiredMixin, UpdateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {'titulo': 'Editar dados do Projeto', 'botao': 'Atualizar Projeto'}


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


class ProjetoDetail(LoginRequiredMixin, DetailView):
    model = Projeto
    template_name = 'commex/detail/projeto.html'


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


class EquipeCreate(LoginRequiredMixin, View):
    template_name = 'commex/equipes/form.html'

    def get(self, request):
        form = EquipeForm()
        formset = MembroEquipeFormSet(prefix='membros')
        return render(request, self.template_name, {'form': form, 'formset': formset, 'titulo': 'Cadastro de Equipe'})

    def post(self, request):
        form = EquipeForm(request.POST)
        formset = MembroEquipeFormSet(request.POST, prefix='membros')
        if form.is_valid():
            equipe = form.save(commit=False)
            formset = MembroEquipeFormSet(request.POST, instance=equipe, prefix='membros')
            if formset.is_valid():
                equipe.save()
                formset.instance = equipe
                formset.save()
                messages.success(request, 'Equipe criada com sucesso.')
                return redirect('equipe-detail', pk=equipe.pk)
        return render(request, self.template_name, {'form': form, 'formset': formset, 'titulo': 'Cadastro de Equipe'})


class EquipeUpdate(LoginRequiredMixin, View):
    template_name = 'commex/equipes/form.html'

    def get_object(self, pk):
        return get_object_or_404(Equipe, pk=pk)

    def get(self, request, pk):
        equipe = self.get_object(pk)
        form = EquipeForm(instance=equipe)
        formset = MembroEquipeFormSet(instance=equipe, prefix='membros')
        return render(request, self.template_name, {'form': form, 'formset': formset, 'titulo': 'Editar Equipe', 'object': equipe})

    def post(self, request, pk):
        equipe = self.get_object(pk)
        form = EquipeForm(request.POST, instance=equipe)
        formset = MembroEquipeFormSet(request.POST, instance=equipe, prefix='membros')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Equipe atualizada com sucesso.')
            return redirect('equipe-detail', pk=equipe.pk)
        return render(request, self.template_name, {'form': form, 'formset': formset, 'titulo': 'Editar Equipe', 'object': equipe})


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
        if equipe.membros.count() <= 1:
            messages.error(request, 'A equipe deve manter ao menos um membro.')
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
