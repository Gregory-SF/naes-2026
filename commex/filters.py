import django_filters
from django import forms

from .models import Equipe, Projeto, Sprint, StatusProjeto


def _projetos_do_usuario(request):
    if request is None:
        return Projeto.objects.none()
    return Projeto.objects.filter(cadastrado_por=request.user)


class ProjetoFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains', label='Nome')
    status = django_filters.ChoiceFilter(choices=StatusProjeto.choices, label='Status', empty_label='Todos')
    ano = django_filters.NumberFilter(label='Ano')

    class Meta:
        model = Projeto
        fields = ['nome', 'status', 'ano']


class EquipeFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains', label='Nome')
    projeto = django_filters.ModelChoiceFilter(
        queryset=_projetos_do_usuario, label='Projeto', empty_label='Todos'
    )
    ativo = django_filters.BooleanFilter(
        label='Situação',
        widget=forms.Select(choices=[('', 'Todas'), ('true', 'Ativas'), ('false', 'Inativas')]),
    )

    class Meta:
        model = Equipe
        fields = ['nome', 'projeto', 'ativo']


class SprintFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains', label='Nome')
    projeto = django_filters.ModelChoiceFilter(
        field_name='projetos', queryset=_projetos_do_usuario, label='Projeto', empty_label='Todos', distinct=True
    )
    inicio_de = django_filters.DateFilter(
        field_name='data_inicio', lookup_expr='gte', label='Início a partir de',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    fim_ate = django_filters.DateFilter(
        field_name='data_fim', lookup_expr='lte', label='Fim até',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Sprint
        fields = ['nome', 'projeto', 'inicio_de', 'fim_ate']
