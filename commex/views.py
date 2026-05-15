from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from .forms import ProjetoForm
from .models import *

class ProjetoCreate(CreateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {
        'titulo': 'Cadastro de Projeto',
        'botao': 'Criar Projeto',
    }


class ProjetoUpdate(UpdateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {
        'titulo': 'Editar dados do Projeto',
        'botao': 'Atualizar Projeto',
    }


class ProjetoDelete(DeleteView):
    model = Projeto
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {
        'titulo': 'Excluir Projeto',
        'botao': 'Sim, excluir!',
    }


class ProjetoList(ListView):
    model = Projeto
    template_name = 'commex/list/projeto.html'
    context_object_name = 'projetos'
    extra_context = {
        'plural_name': 'Projetos',
        'url_create': 'projeto-create',
        'fields': ['nome', 'status', 'ano'],
    }
    paginate_by = 20


class ProjetoDetail(DetailView):
    model = Projeto
    template_name = 'commex/detail/projeto.html'


class EquipeCreate(CreateView):
    model = Equipe
    fields = ['nome', 'projeto', 'alunos']
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {
        'titulo': 'Cadastro de Equipe',
        'botao': 'Criar Equipe',
    }

class EquipeUpdate(UpdateView):
    model = Equipe
    fields = ['nome', 'projeto', 'alunos']
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {
        'titulo': 'Editar dados da Equipe',
        'botao': 'Atualizar Equipe',
    }

class EquipeDelete(DeleteView):
    model = Equipe
    template_name = 'commex/form.html'
    success_url = reverse_lazy('projeto-list')
    extra_context = {
        'titulo': 'Excluir Equipe',
        'botao': 'Sim, excluir!',
    }

class EquipeList(ListView):
    model = Equipe
    template_name = 'commex/list/equipe.html'
    paginate_by = 20

class EquipeDetail(DetailView):
    model = Equipe
    template_name = 'commex/detail/equipe.html'

class IndexView(ListView):
    model = Projeto
    template_name = 'commex/index.html'
    context_object_name = 'projetos'
    paginate_by = 5
