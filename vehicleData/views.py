from django.shortcuts import render, redirect
from datetime import datetime
from django.core.paginator import Paginator
import uuid
from django.http import Http404, HttpResponse, FileResponse
from django.contrib.auth.models import User

from django.conf import settings
from PIL import Image
import os
from django.http import HttpResponse
import pandas as pd
from django.db.models import Q


from vehicleMaster.models import VehicleMasterView

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        data = VehicleMasterView.objects.all().order_by('-ChangedDate')

        query = Q()
        search_logic = request.GET.get('searchLogic', 'AND')
        number_plat = request.GET.get('number_plat_search')
        user_create = request.GET.get('user_create_search')
        statusSTNK = request.GET.get('searchStatusSTNK')
        warnaTNKB = request.GET.get('searchWarnaTNKB')
        jumlahRoda = request.GET.get('searchJumlahRoda')

        if number_plat:
            query &= Q(number_plat=number_plat) if search_logic == 'AND' else Q(number_plat=number_plat)

        if user_create:
            query &= Q(UploadedBy=user_create) if search_logic == 'AND' else Q(UploadedBy=user_create)

        if statusSTNK:
            query &= Q(STNKReady=statusSTNK) if search_logic == 'AND' else Q(STNKReady=statusSTNK)

        if warnaTNKB:
            query &= Q(Warna=warnaTNKB) if search_logic == 'AND' else Q(Warna=warnaTNKB)

        if jumlahRoda:
            query &= Q(JumlahRoda=jumlahRoda) if search_logic == 'AND' else Q(JumlahRoda=jumlahRoda)

        if any([number_plat, user_create, statusSTNK, warnaTNKB, jumlahRoda]):
            data = VehicleMasterView.objects.filter(query).order_by('-ChangedDate')

        paginator = Paginator(data, 100)  # Show 100 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        users_create = VehicleMasterView.objects.values('UploadedBy').distinct().order_by('UploadedBy')
        # context = {'page_obj': page_obj, 'users_create': users_create}
        context = {
            'page_obj': page_obj,
            'users_create': users_create,
            'search_logic': search_logic,
            'number_plat_search': number_plat,
            'user_create_search': user_create,
            'searchStatusSTNK': statusSTNK,
            'searchWarnaTNKB': warnaTNKB,
            'searchJumlahRoda': jumlahRoda,
        }

        if request.user.is_superuser:
            return render(request, 'vehicleData.html', context)
        else:
            return render(request, 'vehicleData_cabang.html', context)
    else:
        return render(request, 'noAccess.html')

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def view_file(request, filename):
    try:
        # Construct the file paths for both .jpg and .JPG extensions
        file_path_jpg = os.path.join('/volume/media', 'stnk_images', f"{filename}.jpg")
        file_path_JPG = os.path.join('/volume/media', 'stnk_images', f"{filename}.JPG")
        
        if os.path.exists(file_path_jpg):
            # If the .jpg file exists, read its content
            with open(file_path_jpg, 'rb') as file:
                image_data = file.read()
            content_type = 'image/jpeg'
        elif os.path.exists(file_path_JPG):
            # If the .jpg file doesn't exist, but .JPG does, read its content
            with open(file_path_JPG, 'rb') as file:
                image_data = file.read()
            content_type = 'image/jpeg'
        else:
            raise Http404("File tidak ditemukan")
            
        # Return the image content in the response with the appropriate content type
        return HttpResponse(image_data, content_type=content_type)
    
    except Http404:
        return custom_404(request, Http404)
    
def view_file2(request, filename):
    try:
        # Construct the file path
        file_path = os.path.join('/volume/media', 'rekom_images', filename)

        if os.path.exists(file_path):
            # If the file exists, read its content
            with open(file_path, 'rb') as file:
                image_data = file.read()
            # Set the content type based on the image file format
            content_type = 'image/jpeg'  # Adjust according to your file format
            
            # Return the image content in the response with the appropriate content type
            return HttpResponse(image_data, content_type=content_type)
        else:
            # If the file does not exist, raise Http404 exception
            raise Http404("File tidak ditemukan")
    except Http404:
        return custom_404(request, Http404)
    
def export_to_excel(request):
    # Get the model's field names and labels
    field_labels = {
        'number_plat': 'Nomor Kendaraan',
        'MerkKendaraan': 'Merk Kendaraan',
        'TypeKendaraan': 'Tipe Kendaraan STNK',
        'JenisKendaraan': 'Jenis/Model Kendaraan STNK',
        'Warna': 'Warna TNKB',
        'NamaPemilik': 'Nama Pemilik',
        'AlamatPemilik': 'Alamat Pemilik',
        'JumlahRoda': 'Jumlah Roda',
        'TahunPembuatan': 'Tahun Pembuatan',
        'KapasitasCylinder': 'Isi Silinder',
        'STNKReady': 'STNK Status',
        'vehicletype_id': 'Vehicle Type ID',
        'SettingSystem': 'Setting System',
        'Deleted': 'Inactive Status',
        'UploadedBy': 'User Create',
        'UploadedDate': 'Date Create',
        'ChangedBy': 'User Update',
        'ChangedDate': 'Date Update',
        'description': 'Tipe Kendaraan System',
        'RekomReady': 'Rekom Status',
        'DateValidSTNK': 'Batas Masa Berlaku STNK',
    }

    # Retrieve search parameters from GET request
    search_logic = request.GET.get('searchLogic', 'AND')
    number_plat = request.GET.get('number_plat_search')
    user_create = request.GET.get('user_create_search')
    statusSTNK = request.GET.get('searchStatusSTNK')
    warnaTNKB = request.GET.get('searchWarnaTNKB')
    jumlahRoda = request.GET.get('searchJumlahRoda')

    # Prepare query based on search parameters
    query = Q()
    if number_plat:
        query &= Q(number_plat=number_plat) if search_logic == 'AND' else Q(number_plat=number_plat)

    if user_create:
        query &= Q(UploadedBy=user_create) if search_logic == 'AND' else Q(UploadedBy=user_create)

    if statusSTNK:
        query &= Q(STNKReady=statusSTNK) if search_logic == 'AND' else Q(STNKReady=statusSTNK)

    if warnaTNKB:
        query &= Q(Warna=warnaTNKB) if search_logic == 'AND' else Q(Warna=warnaTNKB)

    if jumlahRoda:
        query &= Q(JumlahRoda=jumlahRoda) if search_logic == 'AND' else Q(JumlahRoda=jumlahRoda)

    if any([number_plat, user_create, statusSTNK, warnaTNKB, jumlahRoda]):
        data = VehicleMasterView.objects.filter(query).order_by('-ChangedDate')
    else:
        data = VehicleMasterView.objects.order_by('-ChangedDate')

    # Create a DataFrame from the queryset
    df = pd.DataFrame(data.values(), columns=field_labels.keys())

    # Rename columns using the field labels
    df.rename(columns=field_labels, inplace=True)

    # Create a response object with the appropriate content type
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=vehicle_all_data.xlsx'

    # Write the DataFrame to an Excel file in the response
    df.to_excel(response, index=False)

    return response