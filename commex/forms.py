import json
from urllib.parse import urlparse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, HTML, Layout, Row
from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

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
    novo_repos_json = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Projeto
        fields = ['nome', 'status', 'ano', 'dias_aula', 'link_organizacao_github']

    def __init__(self, *args, **kwargs):
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
            Field('novo_repos_json'),
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

        links_json = cleaned.get('novo_repos_json')
        normalized_links = []
        if links_json:
            try:
                links = json.loads(links_json)
            except (json.JSONDecodeError, ValueError):
                raise forms.ValidationError('Links de repositorios em formato invalido.')
            if not isinstance(links, list):
                raise forms.ValidationError('Links de repositorios devem ser uma lista.')
            owner_org = normalize_owner_from_url(link_org) if link_org else None
            for link in links:
                link = str(link).strip()
                if not link:
                    continue
                try:
                    validate_github_url(link, kind='repository')
                except GitHubValidationError as exc:
                    raise forms.ValidationError(str(exc)) from exc
                if owner_org and normalize_owner_from_url(link) != owner_org:
                    raise forms.ValidationError('Repositorio fora da organizacao/conta do projeto.')
                normalized_links.append(link)

        self._repo_links = normalized_links
        return cleaned

    def _repo_name(self, link: str) -> str:
        parts = [x for x in urlparse(link).path.split('/') if x]
        return parts[-1] if parts else link

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if not commit:
            return instance

        if self.cleaned_data.get('nova_sprint_nome'):
            sprint = Sprint.objects.create(
                nome=self.cleaned_data['nova_sprint_nome'],
                data_inicio=self.cleaned_data['nova_sprint_data_inicio'],
                data_fim=self.cleaned_data['nova_sprint_data_fim'],
            )
            instance.sprints.add(sprint)

        for link in getattr(self, '_repo_links', []):
            repo, _ = Repositorio.objects.get_or_create(
                projeto=instance,
                link=link,
                defaults={'nome': self._repo_name(link)},
            )
            instance.repositorios.add(repo)

        return instance


class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = ['nome', 'projeto', 'ativo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['projeto'].queryset = Projeto.objects.filter(status=StatusProjeto.ATIVO)


class MembroEquipeForm(forms.ModelForm):
    class Meta:
        model = MembroEquipe
        fields = ['aluno', 'papel']


class MembroEquipeInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        papeis = []
        alunos = []
        valid_forms = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
        if not valid_forms:
            raise forms.ValidationError('A equipe deve conter ao menos um membro.')

        for form in valid_forms:
            aluno = form.cleaned_data.get('aluno')
            papel = form.cleaned_data.get('papel')
            if aluno in alunos:
                raise forms.ValidationError('Um aluno nao pode ser repetido na mesma equipe.')
            alunos.append(aluno)
            papeis.append(papel)

        if papeis.count(PapelScrum.SCRUM_MASTER) > 1:
            raise forms.ValidationError('A equipe pode ter apenas um Scrum Master.')
        if papeis.count(PapelScrum.PRODUCT_OWNER) > 1:
            raise forms.ValidationError('A equipe pode ter apenas um Product Owner.')


MembroEquipeFormSet = inlineformset_factory(
    Equipe,
    MembroEquipe,
    form=MembroEquipeForm,
    formset=MembroEquipeInlineFormSet,
    extra=1,
    can_delete=True,
)


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
