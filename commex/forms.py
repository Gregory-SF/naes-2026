from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, HTML, Layout, Row
from django import forms

from .models import (
    Aluno,
    Branch,
    DiaSemana,
    ConfiguracaoGlobal,
    DiaAulaConfiguracao,
    Equipe,
    MembroEquipe,
    PapelScrum,
    Projeto,
    Repositorio,
    Sprint,
    StatusProjeto,
)
from .services.github import GitHubValidationError, normalize_owner_from_url, validate_github_url


class ProjetoForm(forms.ModelForm):
    dias_aula = forms.MultipleChoiceField(
        choices=DiaSemana.choices,
        required=False,
        widget=forms.SelectMultiple,
        label='Dias da semana',
    )

    nova_sprint_nome = forms.CharField(required=False, label='Nome da sprint')
    nova_sprint_data_inicio = forms.DateField(required=False, label='Inicio', widget=forms.DateInput(attrs={'type': 'date'}))
    nova_sprint_data_fim = forms.DateField(required=False, label='Fim', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Projeto
        fields = ['nome', 'status', 'ano', 'dias_aula', 'link_organizacao_github']

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = StatusProjeto.choices
        for name in ['nome', 'ano', 'link_organizacao_github', 'nova_sprint_nome', 'nova_sprint_data_inicio', 'nova_sprint_data_fim']:
            self.fields[name].widget.attrs['class'] = 'form-control form-control-sm'
        self.fields['status'].widget.attrs['class'] = 'form-select form-select-sm'
        self.fields['dias_aula'].widget.attrs.update({'class': 'form-select form-select-sm', 'size': '1'})

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('nome'),
            Row(
                Column('status', css_class='col-md-6'),
                Column('ano', css_class='col-md-6'),
            ),
            Field('link_organizacao_github'),
            Field('dias_aula'),
            HTML('<hr>'),
            Row(
                Column('nova_sprint_nome', css_class='col-md-4'),
                Column('nova_sprint_data_inicio', css_class='col-md-4'),
                Column('nova_sprint_data_fim', css_class='col-md-4'),
            ),
        )

    def clean_dias_aula(self):
        return self.cleaned_data.get('dias_aula', [])

    def clean(self):
        cleaned = super().clean()

        nome = cleaned.get('nova_sprint_nome')
        inicio = cleaned.get('nova_sprint_data_inicio')
        fim = cleaned.get('nova_sprint_data_fim')
        if any([nome, inicio, fim]):
            if not all([nome, inicio, fim]):
                raise forms.ValidationError('Para criar sprint, preencha nome, inicio e fim.')
            if fim < inicio:
                raise forms.ValidationError('A data de fim da sprint deve ser posterior a data de inicio.')

        link_org = cleaned.get('link_organizacao_github')
        if link_org:
            try:
                validate_github_url(link_org, kind='organization')
            except GitHubValidationError as exc:
                raise forms.ValidationError(str(exc)) from exc

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if not commit:
            return instance

        if self.cleaned_data.get('nova_sprint_nome'):
            sprint = Sprint.objects.create(
                nome=self.cleaned_data['nova_sprint_nome'],
                data_inicio=self.cleaned_data['nova_sprint_data_inicio'],
                data_fim=self.cleaned_data['nova_sprint_data_fim'],
                cadastrado_por=instance.cadastrado_por,
            )
            instance.sprints.add(sprint)

        return instance


class RepositorioCardForm(forms.Form):
    repositorio_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    delete = forms.BooleanField(required=False, widget=forms.HiddenInput())
    nome = forms.CharField(label='Nome do repositório', max_length=120, required=False)
    link = forms.URLField(label='Link do repositório', max_length=500, required=False)
    branch_principal = forms.CharField(label='Nome da branch', max_length=120, required=False)

    def __init__(self, *args, project_owner=None, initial_is_empty=False, **kwargs):
        self.project_owner = project_owner
        self.initial_is_empty = initial_is_empty
        super().__init__(*args, **kwargs)
        for name in ['nome', 'link', 'branch_principal']:
            self.fields[name].widget.attrs['class'] = 'form-control form-control-sm'
        self.fields['delete'].widget.attrs['class'] = 'd-none'

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('delete'):
            return cleaned

        repositorio_id = cleaned.get('repositorio_id')
        nome = (cleaned.get('nome') or '').strip()
        link = (cleaned.get('link') or '').strip()
        branch_principal = (cleaned.get('branch_principal') or '').strip()

        if not any([repositorio_id, nome, link, branch_principal]) and self.initial_is_empty:
            return cleaned

        if not nome:
            self.add_error('nome', 'Informe o nome do repositório.')
        if not link:
            self.add_error('link', 'Informe o link do repositório.')
        if not branch_principal:
            self.add_error('branch_principal', 'Informe o nome da branch.')

        if self.errors:
            return cleaned

        try:
            validate_github_url(link, kind='repository')
        except GitHubValidationError as exc:
            self.add_error('link', str(exc))
            return cleaned

        if self.project_owner:
            try:
                owner_projeto = normalize_owner_from_url(self.project_owner)
                owner_repositorio = normalize_owner_from_url(link)
            except GitHubValidationError:
                owner_projeto = None
                owner_repositorio = None
            if owner_projeto and owner_repositorio and owner_repositorio != owner_projeto:
                self.add_error('link', 'Repositorio fora da organizacao/conta do projeto.')

        return cleaned


class RepositorioCardCollection:
    def __init__(self, *, data=None, projeto=None, project_owner=None):
        self.data = data
        self.project_owner = project_owner or (projeto.link_organizacao_github if projeto else None)
        self.is_bound = data is not None
        self.forms = []
        self._non_form_errors = []
        self.cleaned_repositories = []

        initial_rows = []
        if projeto is not None and projeto.pk:
            initial_rows = [
                {
                    'repositorio_id': repo.pk,
                    'nome': repo.nome,
                    'link': repo.link,
                    'branch_principal': repo.branch_principal,
                }
                for repo in projeto.repositorios.all().order_by('nome', 'link')
            ]
        elif projeto is None:
            initial_rows = []

        if self.is_bound:
            submitted_total = data.get('repositorios_total', '1')
            try:
                total_forms = max(1, int(submitted_total))
            except (TypeError, ValueError):
                total_forms = 1
        else:
            total_forms = max(1, len(initial_rows) + 1)

        for index in range(total_forms):
            initial = initial_rows[index] if index < len(initial_rows) else None
            form = RepositorioCardForm(
                data=data if self.is_bound else None,
                prefix=f'repositorios-{index}',
                initial=initial,
                project_owner=self.project_owner,
                initial_is_empty=initial is None,
            )
            self.forms.append(form)

        self.total_forms = total_forms

    @property
    def non_form_errors(self):
        return self._non_form_errors

    def is_valid(self):
        self._non_form_errors = []
        self.cleaned_repositories = []
        seen_links = set()
        has_repository = False
        valid = True

        for form in self.forms:
            if not form.is_valid():
                valid = False
                continue

            cleaned = form.cleaned_data
            if cleaned.get('delete'):
                continue

            repositorio_id = cleaned.get('repositorio_id')
            nome = (cleaned.get('nome') or '').strip()
            link = (cleaned.get('link') or '').strip()
            branch_principal = (cleaned.get('branch_principal') or '').strip()

            if not any([repositorio_id, nome, link, branch_principal]):
                continue

            if not nome or not link or not branch_principal:
                valid = False
                continue

            normalized_link = link.lower()
            if normalized_link in seen_links:
                self._non_form_errors.append('Nao e permitido repetir o mesmo link de repositório no mesmo projeto.')
                valid = False
                continue
            seen_links.add(normalized_link)
            has_repository = True

            self.cleaned_repositories.append(
                {
                    'repositorio_id': repositorio_id,
                    'nome': nome,
                    'link': link,
                    'branch_principal': branch_principal,
                }
            )

        if not has_repository:
            self._non_form_errors.append('Adicione ao menos um repositório.')
            valid = False

        return valid


def build_projeto_repositorio_formset(*, data=None, projeto=None, project_owner=None):
    return RepositorioCardCollection(data=data, projeto=projeto, project_owner=project_owner)


def sync_projeto_repositorios(projeto, formset):
    existing_repositorios = list(projeto.repositorios.all())
    kept_repositorios = []
    kept_ids = set()
    for item in getattr(formset, 'cleaned_repositories', []):
        repositorio_id = item['repositorio_id']
        if repositorio_id:
            repositorio = Repositorio.objects.filter(pk=repositorio_id).first()
            if repositorio is None:
                repositorio = Repositorio()
        else:
            repositorio = Repositorio()

        repositorio.projeto = projeto
        repositorio.nome = item['nome']
        repositorio.link = item['link']
        repositorio.branch_principal = item['branch_principal']
        repositorio.save()
        kept_repositorios.append(repositorio)
        kept_ids.add(repositorio.pk)

    projeto.repositorios.set(kept_repositorios)

    for repositorio in existing_repositorios:
        if repositorio.pk not in kept_ids and repositorio.projeto_id == projeto.pk:
            repositorio.projeto = None
            repositorio.save(update_fields=['projeto'])


class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = ['nome', 'projeto', 'ativo']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Só é possível vincular a equipe a projetos do próprio usuário
        self.fields['projeto'].queryset = Projeto.objects.filter(status=StatusProjeto.ATIVO, cadastrado_por=user)
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})
        self.fields['projeto'].widget.attrs.update({'class': 'form-select'})
        self.fields['ativo'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['ativo'].label = 'Equipe ativa'

    def clean_nome(self):
        nome = (self.cleaned_data.get('nome') or '').strip()
        projeto = self.cleaned_data.get('projeto')
        if not nome or projeto is None:
            return nome

        queryset = Equipe.objects.filter(projeto=projeto, nome__iexact=nome)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError('Ja existe uma equipe com este nome para o projeto selecionado.')
        return nome


class SprintForm(forms.ModelForm):
    projetos = forms.ModelMultipleChoiceField(
        queryset=Projeto.objects.filter(status=StatusProjeto.ATIVO),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Sprint
        fields = ['nome', 'data_inicio', 'data_fim', 'ativo', 'projetos']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Só é possível vincular a sprint a projetos do próprio usuário
        self.fields['projetos'].queryset = Projeto.objects.filter(status=StatusProjeto.ATIVO, cadastrado_por=user)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('data_inicio') and cleaned.get('data_fim') and cleaned['data_fim'] < cleaned['data_inicio']:
            raise forms.ValidationError('Data de fim deve ser posterior a data de inicio.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            instance.projetos.set(self.cleaned_data.get('projetos', []))
        return instance


class SprintFiltroForm(forms.Form):
    nome = forms.CharField(required=False)
    projeto = forms.ModelChoiceField(required=False, queryset=Projeto.objects.all())
    inicio_de = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    fim_ate = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class ConfiguracaoGlobalForm(forms.ModelForm):
    dias_aula = forms.ModelMultipleChoiceField(
        queryset=DiaAulaConfiguracao.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        label='Dias de aula',
    )

    class Meta:
        model = ConfiguracaoGlobal
        fields = ['github_token', 'dias_aula']
        widgets = {
            'github_token': forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}),
        }


class BranchCreateForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['repositorio', 'nome', 'ativo']


class AnaliseExecucaoForm(forms.Form):
    projeto = forms.ModelChoiceField(queryset=Projeto.objects.filter(status=StatusProjeto.ATIVO))
    repositorio = forms.ModelChoiceField(queryset=Repositorio.objects.none())
    branch = forms.ModelChoiceField(queryset=Branch.objects.none())
    sprint = forms.ModelChoiceField(queryset=Sprint.objects.filter(ativo=True), required=False)
    data_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        projeto_id = self.data.get('projeto') or self.initial.get('projeto')
        if projeto_id:
            self.fields['repositorio'].queryset = Repositorio.objects.filter(projeto_id=projeto_id)
        repo_id = self.data.get('repositorio') or self.initial.get('repositorio')
        if repo_id:
            self.fields['branch'].queryset = Branch.objects.filter(repositorio_id=repo_id, ativo=True)

    def clean(self):
        cleaned = super().clean()
        sprint = cleaned.get('sprint')
        inicio = cleaned.get('data_inicio')
        fim = cleaned.get('data_fim')

        if sprint and (inicio or fim):
            raise forms.ValidationError('Use sprint OU intervalo manual de datas, nao ambos.')
        if not sprint and not (inicio and fim):
            raise forms.ValidationError('Informe uma sprint ou data de inicio e fim.')
        if inicio and fim and fim < inicio:
            raise forms.ValidationError('Data final deve ser posterior a inicial.')

        repo = cleaned.get('repositorio')
        projeto = cleaned.get('projeto')
        if repo and projeto and repo.projeto_id != projeto.id:
            raise forms.ValidationError('Repositorio nao pertence ao projeto selecionado.')

        return cleaned
