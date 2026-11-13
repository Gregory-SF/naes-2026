import django_filters
from django.contrib.auth import get_user_model

from .models import RequisicaoIA, StatusRequisicao


class RequisicaoFilter(django_filters.FilterSet):
    usuario = django_filters.ModelChoiceFilter(queryset=get_user_model().objects.order_by('username'), label='Usuário', empty_label='Todos')
    status = django_filters.ChoiceFilter(choices=StatusRequisicao.choices, label='Status', empty_label='Todos')
    origem = django_filters.CharFilter(lookup_expr='icontains', label='Origem')

    class Meta:
        model = RequisicaoIA
        fields = ['usuario', 'status', 'origem']
