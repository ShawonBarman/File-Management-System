from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Folder, File
from django.contrib import messages
import os
import zipfile
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

@login_required
def index(request):
    folders = Folder.objects.filter(owner=request.user, parent=None)
    files = File.objects.filter(owner=request.user, folder=None)
    return render(request, 'home.html', {'folders': folders, 'files': files})

@login_required
def open_folder(request, folder_name, folder_id):
    folder = Folder.objects.get(id=folder_id)

    folder_path = get_folder_path(folder)

    sub_folders = folder.children.all()
    files = folder.file_set.all()

    return render(request, 'folder_view.html', {'folder': folder, 'folder_path': folder_path, 'sub_folders': sub_folders, 'files': files})

def get_folder_path(folder):
    path = []
    current_folder = folder
    while current_folder is not None:
        path.insert(0, (current_folder.name, current_folder.id))
        current_folder = current_folder.parent
    return path

@login_required
def create_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        parent_id = request.POST.get('parent_id')
        parent_folder = None
        if parent_id:
            parent_folder = Folder.objects.get(id=parent_id)
            
        if folder_name.strip() and parent_folder is not None:
            Folder.objects.create(name=folder_name, owner=request.user, parent=parent_folder)
            messages.success(request, 'Folder created.')
            return redirect('open_folder', folder_name=parent_folder.name, folder_id=parent_folder.id)
        else:
            Folder.objects.create(name=folder_name, owner=request.user, parent=parent_folder)
            messages.success(request, 'Folder created.')
            return redirect('home')
    return redirect('home')

@login_required
def upload_file(request):
    if request.method == 'POST':
        parent_folder_id = request.POST.get('parent_folder_id', None)
        uploaded_file = request.FILES['file']
        if parent_folder_id:
            parent_folder = Folder.objects.get(id=parent_folder_id)
            File.objects.create(name=uploaded_file.name, file=uploaded_file, owner=request.user, folder=parent_folder)
            return redirect('open_folder', folder_name=parent_folder.name, folder_id=parent_folder.id)
        else:
            File.objects.create(name=uploaded_file.name, file=uploaded_file, owner=request.user)
    return redirect('home')

@login_required
def rename_item(request):
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        new_name = request.POST.get('new_name')
        parent_folder_id = request.POST.get('parent_folder_id') or None
        
        if item_type == 'folder':
            item = Folder.objects.get(id=item_id)
        else:
            item = File.objects.get(id=item_id)
        
        item.name = new_name
        item.save()
        
        messages.success(request, f'{item_type} renamed successfully.')
        if parent_folder_id is not None:
            folder = Folder.objects.get(id=parent_folder_id)
            return redirect('open_folder', folder_name=folder.name, folder_id=folder.id)
        else:
            return redirect('home')
    else:
        return redirect('home')
    
@login_required
def delete_item(request):
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        item_name = request.POST.get('item_name')
        parent_folder_id = request.POST.get('parent_folder_id') or None
        
        if item_type == 'folder':
            folder = Folder.objects.get(id=item_id, owner=request.user)
            folder.delete()
            messages.success(request, f'{item_name} {item_type} deleted successfully.')
            if parent_folder_id is not None:
                folder = Folder.objects.get(id=parent_folder_id)
                return redirect('open_folder', folder_name=folder.name, folder_id=folder.id)
            else:
                return redirect('home')
        elif item_type == 'file':
            file = File.objects.get(id=item_id, owner=request.user)
            file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
            if os.path.exists(file_path):
                os.remove(file_path)
            file.delete()
            messages.success(request, f'{item_name} {item_type} deleted successfully.')
            if parent_folder_id is not None:
                folder = Folder.objects.get(id=parent_folder_id)
                return redirect('open_folder', folder_name=folder.name, folder_id=folder.id)
            else:
                return redirect('home')
        else:
            messages.success(request, f'Error. Please try again.')
            if parent_folder_id is not None:
                folder = Folder.objects.get(id=parent_folder_id)
                return redirect('open_folder', folder_name=folder.name, folder_id=folder.id)
            else:
                return redirect('home')
    else:
        return redirect('home')

@login_required
def download_item(request, item_type, item_id):
    try:
        if item_type == 'folder':
            folder = get_object_or_404(Folder, id=item_id, owner=request.user)
            zip_filename = f'{folder.name}.zip'
            memory_zip = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, zip_filename), 'w', zipfile.ZIP_DEFLATED)
            add_files_to_zip(memory_zip, folder, folder.name)
            memory_zip.close()

            with open(os.path.join(settings.MEDIA_ROOT, zip_filename), 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                return response

        elif item_type == 'file':
            file = get_object_or_404(File, id=item_id, owner=request.user)
            zip_filename = f'{file.name}.zip'
            memory_zip = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, zip_filename), 'w', zipfile.ZIP_DEFLATED)
            memory_zip.write(os.path.join(settings.MEDIA_ROOT, str(file.file)), arcname=file.name)
            memory_zip.close()

            with open(os.path.join(settings.MEDIA_ROOT, zip_filename), 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                return response

    except Exception as e:
        return HttpResponse(str(e), status=500)

def add_files_to_zip(zip_file, folder, base_path):
    for file in folder.file_set.all():
        zip_file.write(os.path.join(settings.MEDIA_ROOT, str(file.file)), arcname=os.path.join(base_path, file.name))

    for subfolder in folder.children.all():
        add_files_to_zip(zip_file, subfolder, os.path.join(base_path, subfolder.name))

@login_required
def search_items(request):
    search_text = request.GET.get('search_text', None)
    print(search_text)
    if search_text:
        sub_folders = Folder.objects.filter(name__icontains=search_text)
        files = File.objects.filter(name__icontains=search_text)

        sub_folders_data = [{'id': folder.id, 'name': folder.name} for folder in sub_folders]
        files_data = [{'id': file.id, 'name': file.name} for file in files]

        return JsonResponse({'sub_folders': sub_folders_data, 'files': files_data})
    else:
        sub_folders = Folder.objects.filter(owner=request.user, parent=None)
        files = File.objects.filter(owner=request.user, folder=None)

        sub_folders_data = [{'id': folder.id, 'name': folder.name} for folder in sub_folders]
        files_data = [{'id': file.id, 'name': file.name} for file in files]
        return JsonResponse({'sub_folders': sub_folders_data, 'files': files_data})