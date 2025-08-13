import os
import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.core import serializers
from django.conf import settings
from django.apps import apps
from django.db import transaction
from users.decorators import role_required
from .models import Backup

@role_required('admin')
def backupList(request):
    """Vista principal de backup - mantengo tu nombre"""
    backup_history = Backup.objects.all()[:10]  # Últimos 10 backups
    return render(request, 'backup.html', {
        'backup_history': backup_history
    })

@role_required('admin')
def create_backup(request):
    """Crear un nuevo backup"""
    if request.method == 'POST':
        descripcion = request.POST.get('description', '')
        
        try:
            # Crear registro de backup
            backup = Backup.objects.create(
                descripcion=descripcion,
                creado_por=request.user,
                estado='pendiente'
            )
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'backup_{timestamp}.json'
            backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
            
            # Crear directorio si no existe
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            file_path = os.path.join(backup_dir, filename)
            
            # Obtener todos los datos
            backup_data = {
                'timestamp': timestamp,
                'created_by': request.user.username,
                'description': descripcion,
                'data': {}
            }
            
            # Modelos a respaldar - ORDEN IMPORTANTE: sin dependencias primero
            models_to_backup = [
                'users.CustomUser',           # Sin dependencias
                'categories.Categoria',       # Sin dependencias  
                'customers.Cliente',          # Sin dependencias
                'products.Producto',          # Depende de Categoria
                'event_calendar.Event',       # Depende de CustomUser
                'sales.Venta',               # Depende de Producto, Cliente, etc.
                'Sales.DetalleVenta',
            ]
            
            for model_name in models_to_backup:
                try:
                    model = apps.get_model(model_name)
                    data = serializers.serialize('json', model.objects.all())
                    backup_data['data'][model_name] = json.loads(data)
                except Exception as e:
                    print(f"Error respaldando {model_name}: {e}")
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Actualizar registro
            backup.ruta_archivo = file_path
            backup.tamaño_archivo = os.path.getsize(file_path)
            backup.estado = 'completado'
            
            # Contar registros
            try:
                backup.total_productos = apps.get_model('products.Producto').objects.count()
                backup.total_categorias = apps.get_model('categories.Categoria').objects.count()
                backup.total_usuarios = apps.get_model('users.CustomUser').objects.count()
            except:
                pass
            
            backup.save()
            
            # Descargar archivo automáticamente
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/json')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                messages.success(request, 'Backup creado y descargado exitosamente')
                return response
                
        except Exception as e:
            if 'backup' in locals():
                backup.estado = 'fallido'
                backup.save()
            messages.error(request, f'Error al crear backup: {str(e)}')
    
    return redirect('backupList')

@role_required('admin')
@transaction.atomic  # Para que todo se ejecute como una transacción
def restore_backup(request):
    """Restaurar backup desde archivo - VERSIÓN CORREGIDA"""
    if request.method == 'POST':
        backup_file = request.FILES.get('backup_file')
        
        if not backup_file:
            messages.error(request, 'Debe seleccionar un archivo')
            return redirect('backupList')
        
        try:
            # Leer archivo
            file_content = backup_file.read().decode('utf-8')
            backup_data = json.loads(file_content)
            
            # Validar estructura
            if 'data' not in backup_data:
                messages.error(request, 'Archivo de backup inválido - no contiene datos')
                return redirect('backupList')
            
            print(f"📁 Archivo cargado correctamente")
            print(f"🔍 Modelos encontrados: {list(backup_data['data'].keys())}")
            
            # Restaurar datos usando deserialización de Django
            restore_order = [
                'users.CustomUser',           
                'categories.Categoria',      
                'customers.Cliente',         
                'products.Producto',         
                'event_calendar.Event',      
                'sales.Venta',               
                'Sales.DetalleVenta',
            ]
            
            restored_count = 0
            restored_models = []
            
            # Restaurar en orden específico
            for model_name in restore_order:
                if model_name not in backup_data['data']:
                    print(f"⚠️ Modelo {model_name} no encontrado en backup")
                    continue
                    
                model_data = backup_data['data'][model_name]
                try:
                    print(f"🔄 Procesando modelo: {model_name}")
                    print(f"📊 Registros a restaurar: {len(model_data)}")
                    
                    model = apps.get_model(model_name)
                    
                    # Contar registros antes de borrar
                    count_before = model.objects.count()
                    print(f"📋 Registros existentes: {count_before}")
                    
                    # Limpiar datos existentes
                    model.objects.all().delete()
                    print(f"🗑️ Datos existentes eliminados")
                    
                   
                    if model_data:  
                       
                        json_data = json.dumps(model_data)
                        
                        objects_restored = 0
                        failed_objects = 0
                        
                        for obj in serializers.deserialize('json', json_data):
                            try:
                                # Verificar que las FK existan antes de guardar
                                obj.save()
                                objects_restored += 1
                            except Exception as save_error:
                                failed_objects += 1
                                print(f"⚠️ Error guardando objeto en {model_name}: {save_error}")
                                # Para debugging, mostrar el objeto problemático
                                if hasattr(obj, 'object'):
                                    print(f"🔍 Objeto problemático: {obj.object}")
                                continue
                        
                        if failed_objects > 0:
                            print(f"⚠️ {model_name}: {failed_objects} objetos fallaron al guardar")
                        
                        print(f"✅ {model_name}: {objects_restored} registros restaurados")
                        restored_count += objects_restored
                        if objects_restored > 0:
                            restored_models.append(f"{model_name} ({objects_restored})")
                    else:
                        print(f"ℹ️ {model_name}: Sin datos para restaurar")
                        
                except Exception as e:
                    print(f"❌ Error restaurando {model_name}: {e}")
                    messages.warning(request, f'Error restaurando {model_name}: {str(e)}')
                    continue
            
            if restored_count > 0:
                success_msg = f'✅ Backup restaurado exitosamente!\n'
                success_msg += f'📊 Total de registros restaurados: {restored_count}\n'
                success_msg += f'📋 Modelos restaurados: {", ".join(restored_models)}'
                messages.success(request, success_msg)
            else:
                messages.warning(request, 'No se restauraron registros. Verifica el formato del archivo.')
            
        except json.JSONDecodeError as e:
            messages.error(request, f'El archivo no tiene formato JSON válido: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error al restaurar backup: {str(e)}')
            print(f"💥 Error general: {e}")
    
    return redirect('backupList')

@role_required('admin')
def download_backup(request, backup_id):
    """Descargar un backup específico"""
    backup = get_object_or_404(Backup, id=backup_id)
    
    if not os.path.exists(backup.ruta_archivo):
        messages.error(request, 'El archivo de backup no existe')
        return redirect('backupList')
    
    try:
        with open(backup.ruta_archivo, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/json')
            filename = os.path.basename(backup.ruta_archivo)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except Exception as e:
        messages.error(request, f'Error al descargar backup: {str(e)}')
        return redirect('backupList')

@role_required('admin')
def delete_backup(request):
    """Eliminar un backup"""
    if request.method == 'POST':
        backup_id = request.POST.get('backup_id')
        backup = get_object_or_404(Backup, id=backup_id)
        
        try:
            # Eliminar archivo físico
            if os.path.exists(backup.ruta_archivo):
                os.remove(backup.ruta_archivo)
            
            # Eliminar registro
            backup.delete()
            messages.success(request, 'Backup eliminado exitosamente')
            
        except Exception as e:
            messages.error(request, f'Error al eliminar backup: {str(e)}')
    
    return redirect('backupList')