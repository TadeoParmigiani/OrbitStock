from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Event
import json

# Página del calendario
@login_required(login_url='login')
def eventList(request):
    return render(request, 'calendar.html')

# Obtener eventos ya creados (para cargarlos en el calendario)
@login_required(login_url='login')
def eventos_calendario(request):
    eventos = Event.objects.filter(start__isnull=False)
    data = [{
        'id': e.id,
        'title': e.title,
        'start': e.start.isoformat(),
        'color': e.color,
    } for e in eventos]
    return JsonResponse(data, safe=False)

# Crear nuevo evento
@csrf_exempt
@login_required(login_url='login')
def eventCreate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            evento = Event.objects.create(
                title=data.get('title'),
                start=data.get('start'),
                color=data.get('color', '#007bff'),
                
            )
            return JsonResponse({'status': 'ok', 'id': evento.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

# Eliminar evento
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
    
@csrf_exempt
@login_required(login_url='login')
def eventUpdate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            event_id = data.get('id')
            if not event_id:
                return JsonResponse({'status': 'error', 'message': 'ID no proporcionado'}, status=400)

            evento = Event.objects.get(id=event_id)
            evento.title = data.get('title', evento.title)
            evento.start = data.get('start', evento.start)
            evento.color = data.get('color', evento.color)
            evento.save()

            return JsonResponse({'status': 'ok'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Evento no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)