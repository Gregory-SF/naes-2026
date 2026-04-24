from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from .models import Projeto


class ProjetoCreate(CreateView):
    model = Projeto
    fields = ['nome', 'status', 'ano', 'organizacao', 'equipe']
    template_name = 'campeonato/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {
        'titulo': 'Cadastro de Projeto',
        'botao': 'Criar Projeto',
    }


class ProjetoUpdate(UpdateView):
    model = Projeto
    fields = ['nome', 'status', 'ano', 'organizacao', 'equipe']
    template_name = 'campeonato/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {
        'titulo': 'Editar dados do Projeto',
        'botao': 'Atualizar Projeto',
    }


class ProjetoDelete(DeleteView):
    model = Projeto
    template_name = 'campeonato/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {
        'titulo': 'Excluir Projeto',
        'botao': 'Sim, excluir!',
    }


class ProjetoList(ListView):
    model = Projeto
    template_name = 'campeonato/list/projeto.html'
    paginate_by = 20


class ProjetoDetail(DetailView):
    model = Projeto
    template_name = 'campeonato/detail/projeto.html'
