from braces.views import GroupRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django_filters.views import FilterView

from commex.decorators import group_required

from .filters import RequisicaoFilter
from .forms import ConfiguracaoIAForm, CotaUsuarioForm
from .models import CotaUsuario, RequisicaoIA, StatusRequisicao
from .servico import (
    IAError,
    chamar_ia,
    cota_do_usuario,
    inicio_do_mes,
    obter_api_key,
    obter_configuracao,
    salvar_api_key,
    tokens_consumidos_no_mes,
)

GRUPO_COORDENADORES = settings.GRUPO_COORDENADORES


class RequisicaoList(GroupRequiredMixin, FilterView):
    """Auditoria de todas as chamadas feitas à IA."""

    group_required = GRUPO_COORDENADORES
    model = RequisicaoIA
    filterset_class = RequisicaoFilter
    template_name = 'ia/requisicoes.html'
    paginate_by = 20

    def get_queryset(self):
        return RequisicaoIA.objects.select_related('usuario')


@group_required(GRUPO_COORDENADORES)
def configuracao(request):
    config = obter_configuracao()
    form = ConfiguracaoIAForm(request.POST or None, instance=config)
    if request.method == 'POST' and form.is_valid():
        config = form.save(commit=False)
        nova_chave = form.cleaned_data.get('nova_api_key')
        if nova_chave:
            salvar_api_key(config, nova_chave)
        config.save()
        messages.success(request, 'Configuração da IA salva com sucesso.')
        return redirect('ia:configuracao')
    return render(request, 'ia/configuracao.html', {'form': form, 'chave_configurada': bool(obter_api_key(config))})


@group_required(GRUPO_COORDENADORES)
@require_POST
def testar_conexao(request):
    try:
        resposta = chamar_ia(
            request.user,
            [{'role': 'user', 'content': 'Responda apenas com a palavra OK.'}],
            origem='teste',
            max_tokens=20,
            ignorar_cota=True,
        )
        messages.success(
            request,
            f'Conexão OK. Resposta: "{resposta.texto.strip()[:80]}" ({resposta.tokens_total} tokens).',
        )
    except IAError as exc:
        messages.error(request, f'Falha ao testar a conexão: {exc}')
    return redirect('ia:configuracao')


@group_required(GRUPO_COORDENADORES)
def usuarios(request):
    """IA por usuário: cota, permissão e consumo do mês."""
    config = obter_configuracao()
    consumo = {
        linha['usuario']: (linha['e'] or 0) + (linha['s'] or 0)
        for linha in RequisicaoIA.objects.filter(status=StatusRequisicao.SUCESSO, criado_em__gte=inicio_do_mes())
        .values('usuario')
        .annotate(e=Sum('tokens_entrada'), s=Sum('tokens_saida'))
    }
    linhas = []
    for usuario in get_user_model().objects.select_related('cota_ia').order_by('username'):
        cota_propria = getattr(usuario, 'cota_ia', None)
        cota = cota_propria.cota_mensal if cota_propria else config.cota_mensal_padrao
        usado = consumo.get(usuario.pk, 0)
        linhas.append({
            'usuario': usuario,
            'cota': cota,
            'cota_propria': cota_propria is not None,
            'permitido': cota_propria.permitido if cota_propria else True,
            'usado': usado,
            'percentual': min(100, round(usado * 100 / cota)) if cota else 100,
        })
    return render(request, 'ia/usuarios.html', {'linhas': linhas})


@group_required(GRUPO_COORDENADORES)
def usuario_editar(request, pk):
    usuario = get_object_or_404(get_user_model(), pk=pk)
    config = obter_configuracao()
    cota, _ = CotaUsuario.objects.get_or_create(
        usuario=usuario, defaults={'cota_mensal': config.cota_mensal_padrao}
    )
    form = CotaUsuarioForm(request.POST or None, instance=cota)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Cota de IA de {usuario.get_username()} atualizada com sucesso.')
        return redirect('ia:usuarios')
    return render(request, 'ia/usuario_form.html', {'form': form, 'alvo': usuario})


@login_required
def meu_consumo(request):
    config = obter_configuracao()
    cota, permitido = cota_do_usuario(request.user, config)
    usado = tokens_consumidos_no_mes(request.user)
    recentes = RequisicaoIA.objects.filter(usuario=request.user).order_by('-criado_em')[:15]
    return render(request, 'ia/meu_consumo.html', {
        'cota': cota,
        'usado': usado,
        'restante': max(0, cota - usado),
        'percentual': min(100, round(usado * 100 / cota)) if cota else 100,
        'permitido': permitido,
        'requisicoes': recentes,
    })
