import json
from urllib.parse import urlparse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Field, HTML, Layout, Row
from django import forms

from .models import DiaSemana, Projeto, Repositorio, Sprint, TipoRepositorio


class ProjetoForm(forms.ModelForm):
    dias_aula = forms.MultipleChoiceField(
        choices=DiaSemana.choices,
        required=False,
        widget=forms.SelectMultiple,
        label='Dias da semana',
    )

    # ── Criação inline de Sprint ──────────────────────────────────────────
    nova_sprint_nome = forms.CharField(
        required=False,
        label='Nome',
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Sprint 1'}),
    )
    nova_sprint_data_inicio = forms.DateField(
        required=False,
        label='Início',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    nova_sprint_data_fim = forms.DateField(
        required=False,
        label='Fim',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    # Links de repositórios novos – serializado pelo JS antes do submit
    novo_repos_json = forms.CharField(
        required=False,
        widget=forms.TextInput(),
        label='Link do repositório',
    )

    class Meta:
        model = Projeto
        fields = ['nome', 'status', 'ano', 'dias_aula']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ── Widget attrs ──────────────────────────────────────────────────
        multi_attrs = {
            'class': 'form-select form-select-sm',
            'size': '1',
            'data-placeholder': 'Selecione',
        }
        self.fields['dias_aula'].widget.attrs.update(multi_attrs)

        self.fields['nome'].widget.attrs['class'] = 'form-control form-control-sm'
        self.fields['status'].widget.attrs['class'] = 'form-select form-select-sm'
        self.fields['ano'].widget.attrs['class'] = 'form-control form-control-sm'
        self.fields['nova_sprint_nome'].widget.attrs['class'] = 'form-control form-control-sm'
        self.fields['nova_sprint_data_inicio'].widget.attrs['class'] = 'form-control form-control-sm'
        self.fields['nova_sprint_data_fim'].widget.attrs['class'] = 'form-control form-control-sm'
        self.fields['novo_repos_json'].widget.attrs['class'] = 'form-control form-control-sm'

        # ── Crispy layout ─────────────────────────────────────────────────
        self.helper = FormHelper()
        self.helper.form_tag = False   # <form> e {% csrf_token %} ficam no template
        self.helper.layout = Layout(

            Field('nome'),

            Row(
                Column('status', css_class='col-md-6'),
                Column('ano', css_class='col-md-6'),
            ),

            Field('dias_aula'),

            HTML('<hr>'),

            Field('repositorios'),

            Field('nova_sprint_nome'),

            Field('sprints'),
        )
    # ── Validações ────────────────────────────────────────────────────────

    def clean_dias_aula(self):
        return self.cleaned_data.get('dias_aula', [])

    def clean(self):
        cleaned = super().clean()

        nome  = cleaned.get('nova_sprint_nome')
        inicio = cleaned.get('nova_sprint_data_inicio')
        fim    = cleaned.get('nova_sprint_data_fim')

        if any([nome, inicio, fim]):
            if not all([nome, inicio, fim]):
                raise forms.ValidationError(
                    'Para criar uma sprint preencha nome, data de início e data de fim.'
                )
            if inicio and fim and fim < inicio:
                raise forms.ValidationError(
                    'A data de fim deve ser posterior à data de início.'
                )

        return cleaned

    # ── Utilitários ───────────────────────────────────────────────────────

    def _nome_from_link(self, link: str) -> str:
        parsed = urlparse(link)
        path   = (parsed.path or '').strip('/').split('/')
        return path[-1] if path and path[-1] else link

    # ── Save ──────────────────────────────────────────────────────────────

    def save(self, commit=True):
        instance = super().save(commit=commit)

        if commit:
            # Cria sprint inline se preenchida
            nova_sprint_nome = self.cleaned_data.get('nova_sprint_nome')
            if nova_sprint_nome:
                print(f"Criando sprint '{nova_sprint_nome}' para o projeto '{instance.nome}'")
                sprint = Sprint.objects.create(
                    nome        = nova_sprint_nome,
                    data_inicio = self.cleaned_data['nova_sprint_data_inicio'],
                    data_fim    = self.cleaned_data['nova_sprint_data_fim'],
                )
                instance.sprints.add(sprint)

            # Cria repositórios a partir dos links enviados via JSON
            novo_repos_json = self.cleaned_data.get('novo_repos_json', '')
            if novo_repos_json:
                print(novo_repos_json)
                try:
                    links = json.loads(novo_repos_json)
                    print(f"Links recebidos para criação de repositórios: {links}")
                except (json.JSONDecodeError, ValueError):
                    links = []

                for raw_link in links:
                    link = raw_link.strip()
                    if not link:
                        continue
                    repo, _ = Repositorio.objects.get_or_create(
                        link=link,
                        defaults={
                            'nome': self._nome_from_link(link),
                            'tipo': TipoRepositorio.BACKEND,
                        },
                    )
                    instance.repositorios.add(repo)

        return instance