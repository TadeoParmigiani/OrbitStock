from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Event
from django.http import JsonResponse
import json
from django.views.decorators.http import require_http_methods

@login_required(login_url='login')
def eventList(request):
    return render(request, 'calendar.html')


@login_required(login_url='login')
def eventos_arrastrables(request):
    eventos = Event.objects.filter(is_template=True)
    data = []

    for evento in eventos:
        data.append({
            'id': evento.id,
            'title': evento.title,
            'allDay': evento.all_day,
            'color': evento.color,
        })

    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required(login_url='login')
def eventCreate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            evento = Event.objects.create(
                title=data['title'],
                start=data.get('start', None),
                all_day=data.get('all_day', True),
                color=data.get('color', '#3788d8'),
                is_template=data.get('is_template', False),
            )
            return JsonResponse({'status': 'ok', 'id': evento.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)



@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url='login')
def eventDelete(request):
    try:
        data = json.loads(request.body)
        event_id = data.get('id')

        if not event_id:
            return JsonResponse({'status': 'error', 'message': 'ID no proporcionado'}, status=400)

        evento = Event.objects.get(id=event_id)
        evento.delete()
        return JsonResponse({'status': 'ok', 'message': 'Evento eliminado'})
    
    except Event.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Evento no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required(login_url='login')
def eventos_calendario(request):
    eventos = Event.objects.filter(start__isnull=False)
    data = [{
        'id': e.id,
        'title': e.title,
        'start': e.start.isoformat(),
        'allDay': e.all_day,
        'color': e.color,
    } for e in eventos]
    return JsonResponse(data, safe=False)