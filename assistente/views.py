import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from ia.servico import CotaExcedida, IAError

from .models import Mensagem
from .servico import MAX_CARACTERES_PERGUNTA, perguntar as perguntar_ao_assistente


@login_required
def assistente(request):
    historico = [
        {'papel': m.papel, 'conteudo': m.conteudo}
        for m in Mensagem.objects.filter(usuario=request.user).order_by('-criado_em', '-id')[:50][::-1]
    ]
    return render(request, 'assistente/assistente.html', {
        'historico': historico,
        'max_caracteres': MAX_CARACTERES_PERGUNTA,
    })


@login_required
@require_POST
def perguntar(request):
    """Recebe a pergunta por AJAX (JSON + cabeçalho X-CSRFToken) e devolve a resposta em Markdown."""
    try:
        pergunta = (json.loads(request.body or '{}').get('pergunta') or '').strip()
    except (ValueError, AttributeError):
        return JsonResponse({'erro': 'Requisição inválida.'}, status=400)

    if not pergunta:
        return JsonResponse({'erro': 'Digite uma pergunta.'}, status=400)
    if len(pergunta) > MAX_CARACTERES_PERGUNTA:
        return JsonResponse({'erro': f'A pergunta pode ter no máximo {MAX_CARACTERES_PERGUNTA} caracteres.'}, status=400)

    try:
        resposta = perguntar_ao_assistente(request.user, pergunta)
    except CotaExcedida as exc:
        return JsonResponse({'erro': str(exc)}, status=429)
    except IAError as exc:
        return JsonResponse({'erro': str(exc)}, status=502)
    return JsonResponse({'resposta': resposta})


@login_required
@require_POST
def limpar(request):
    Mensagem.objects.filter(usuario=request.user).delete()
    messages.success(request, 'Histórico da conversa apagado com sucesso.')
    return redirect('assistente')
