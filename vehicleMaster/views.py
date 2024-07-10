from django.shortcuts import render, redirect
from datetime import datetime
from django.core.paginator import Paginator
import uuid
from django.http import Http404, HttpResponse, FileResponse

from django.conf import settings
from PIL import Image
import os
from django.http import HttpResponse


from vehicleMaster.models import VehicleTypeMaster, LogVehicleTypeMaster, VehicleMasterView
from vehicleTypeMaster.models import VehicleType
from quotaTransaction.models import QuotaTransaction

# Create your views here.
def index(request):
    message_modify = None
    if request.user.is_authenticated:
        data = VehicleMasterView.objects.all().order_by('-ChangedDate')
        username = request.user.get_full_name()
        vehicle_types = VehicleType.objects.filter(deleted=False)

        if request.method == 'POST':
            
            if 'number_plat_search' in request.POST:
                number_plat = request.POST['number_plat_search']
                if len(number_plat) != 0:
                    data = VehicleMasterView.objects.filter(number_plat=number_plat)
                else:
                    data = VehicleMasterView.objects.all().order_by('-ChangedDate')

            if "number_plat" in request.POST and "vehicle_id" in request.POST and "id_modify" in request.POST:
                number_plat = request.POST['number_plat']
                number_plat = number_plat.replace(' ', '')
                MerkKendaraan = request.POST["MerkKendaraan"]
                JenisKendaraan = request.POST["jenisKendaraan"]
                Warna = request.POST["warna"]
                NamaPemilik = request.POST["NamaPemilik"]
                AlamatPemilik = request.POST["AlamatPemilik"]
                JumlahRoda = request.POST["JumlahRoda"]
                TahunPembuatan = request.POST["TahunPembuatan"]
                KapasitasCylinder = request.POST["KapasitasCylinder"]
                STNKReady = request.POST["STNKReady"]
                try:
                    DateValidSTNK = request.POST["masaBerlakuSTNK"]
                except:
                    DateValidSTNK = None
                RekomReady = request.POST["RekomReady"]
                vehicletype_id = request.POST['vehicle_id']
                Typekendaraan = request.POST['Typekendaraan']
                id_modify = request.POST['id_modify']
                deleted = False
                date_create = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                if TahunPembuatan.strip() != '':
                    TahunPembuatan = int(TahunPembuatan)
                else:
                    TahunPembuatan = None
                if KapasitasCylinder.strip() != '':
                    KapasitasCylinder = int(KapasitasCylinder)
                else:
                    KapasitasCylinder = None

                if id_modify == "":
                    #submit
                    try:
                        VehicleMasterView.objects.get(number_plat=number_plat)
                        message = "no_plat"
                        data = VehicleMasterView.objects.all().order_by('-ChangedDate')
                        paginator = Paginator(data, 5)  # Show 10 items per page
                        page_number = request.GET.get('page')
                        page_obj = paginator.get_page(page_number)
                        context = {'page_obj': page_obj, 'vehicle_types': vehicle_types,'message': message}
                        if request.user.is_superuser:
                            return render(request, 'vehicleMaster.html', context)
                        else:
                            return render(request, 'vehicleMaster_cabang.html', context)
                    except:
                        ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
                        # save image
                        if 'STNKImageDepan' in request.FILES:
                            number_plat = request.POST['number_plat']
                            number_plat = number_plat.replace(' ', '')
                            stnk_image = request.FILES['STNKImageDepan']
                            
                            # Perform file type validation
                            filename, file_extension = os.path.splitext(stnk_image.name)
                            if file_extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                                # Handle invalid file type error
                                return HttpResponse('<script>'
                                'alert("GAGAL MENYIMPAN DATA.\nHanya data berformat JPG/JPEG/PNG yang dapat disimpan");'
                                'window.history.back();'
                                '</script>')

                            # Open the image using PIL
                            image = Image.open(stnk_image)
                            # Resize the image to 50% of its original size
                            resized_image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
                            # Convert the image to RGB mode (remove alpha channel)
                            resized_image = resized_image.convert("RGB")
                            # Construct the file path using MEDIA_ROOT
                            file_path = os.path.join(settings.MEDIA_ROOT, f'stnk_images/{number_plat}_STNK_DEPAN.jpg')
                            # Save the resized image as JPEG
                            resized_image.save(file_path, "JPEG")
                        if 'STNKImageBelakang' in request.FILES:
                            number_plat = request.POST['number_plat']
                            number_plat = number_plat.replace(' ', '')
                            stnk_image = request.FILES['STNKImageBelakang']
                            
                            # Perform file type validation
                            filename, file_extension = os.path.splitext(stnk_image.name)
                            if file_extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                                # Handle invalid file type error
                                return HttpResponse('<script>'
                                'alert("GAGAL MENYIMPAN DATA.\nHanya data berformat JPG/JPEG/PNG yang dapat disimpan");'
                                'window.history.back();'
                                '</script>')
                            
                            # Open the image using PIL
                            image = Image.open(stnk_image)
                            # Resize the image to 50% of its original size
                            resized_image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
                            # Convert the image to RGB mode (remove alpha channel)
                            resized_image = resized_image.convert("RGB")
                            # Construct the file path using MEDIA_ROOT
                            file_path = os.path.join(settings.MEDIA_ROOT, f'stnk_images/{number_plat}_STNK_BELAKANG.jpg')
                            # Save the resized image as JPEG
                            resized_image.save(file_path, "JPEG")
                        if 'SuratRekomendasi' in request.FILES:
                            number_plat = request.POST['number_plat']
                            number_plat = number_plat.replace(' ', '')
                            rekom_image = request.FILES['SuratRekomendasi']
                            
                            # Perform file type validation
                            filename, file_extension = os.path.splitext(rekom_image.name)
                            if file_extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                                # Handle invalid file type error
                                return HttpResponse('<script>'
                                'alert("GAGAL MENYIMPAN DATA.\nHanya data berformat JPG/JPEG/PNG yang dapat disimpan");'
                                'window.history.back();'
                                '</script>')
                            
                            # Open the image using PIL
                            image = Image.open(rekom_image)
                            # Resize the image to 50% of its original size
                            resized_image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
                            # Convert the image to RGB mode (remove alpha channel)
                            resized_image = resized_image.convert("RGB")
                            # Construct the file path using MEDIA_ROOT
                            file_path = os.path.join(settings.MEDIA_ROOT, f'rekom_images/{number_plat}_SURAT_REKOMENDASI.jpg')
                            # Save the resized image as JPEG
                            resized_image.save(file_path, "JPEG")

                        # save data
                        RowID = str(uuid.uuid4())
                        vehicle = VehicleType.objects.get(id=vehicletype_id)
                        VehicleTypeNameKF = vehicle.description
                        SettingSystem = vehicle.SettingSystem
                        VehicleTypeMaster.objects.create(RowID = RowID,
                                                        number_plat = number_plat,
                                                        MerkKendaraan = MerkKendaraan,
                                                        TypeKendaraan = Typekendaraan,
                                                        JenisKendaraan = JenisKendaraan,
                                                        Warna = Warna,
                                                        NamaPemilik = NamaPemilik,
                                                        AlamatPemilik = AlamatPemilik,
                                                        JumlahRoda = JumlahRoda,
                                                        TahunPembuatan = TahunPembuatan,
                                                        KapasitasCylinder = KapasitasCylinder,
                                                        STNKReady = STNKReady,
                                                        vehicletype_kf = VehicleTypeNameKF,
                                                        vehicletype_id = vehicletype_id,
                                                        SettingSystem = SettingSystem,
                                                        Deleted = deleted,
                                                        UploadedBy = username,
                                                        UploadedDate = date_create,
                                                        ChangedBy = username,
                                                        ChangedDate = date_create,
                                                        RekomReady = RekomReady,
                                                        DateValidSTNK = DateValidSTNK)
                        # save log
                        LogVehicleTypeMaster.objects.create(RowID = RowID,
                                                        number_plat = number_plat,
                                                        MerkKendaraan = MerkKendaraan,
                                                        TypeKendaraan = Typekendaraan,
                                                        JenisKendaraan = JenisKendaraan,
                                                        Warna = Warna,
                                                        NamaPemilik = NamaPemilik,
                                                        AlamatPemilik = AlamatPemilik,
                                                        JumlahRoda = JumlahRoda,
                                                        TahunPembuatan = TahunPembuatan,
                                                        KapasitasCylinder = KapasitasCylinder,
                                                        STNKReady = STNKReady,
                                                        vehicletype_kf = VehicleTypeNameKF,
                                                        vehicletype_id = vehicletype_id,
                                                        SettingSystem = SettingSystem,
                                                        Deleted = deleted,
                                                        ChangedBy = username,
                                                        ChangedDate = date_create,
                                                        RekomReady = RekomReady,
                                                        DateValidSTNK = DateValidSTNK)
                        data = VehicleMasterView.objects.filter(number_plat=number_plat)
                        paginator = Paginator(data, 5)  # Show 10 items per page
                        page_number = request.GET.get('page')
                        page_obj = paginator.get_page(page_number)
                        context = {'page_obj': page_obj, 'vehicle_types': vehicle_types}
                        if request.user.is_superuser:
                            return render(request, 'vehicleMaster.html', context)
                        else:
                            return render(request, 'vehicleMaster_cabang.html', context)
            elif request.POST and "vehicle_id" in request.POST and "id_modify" in request.POST:
                id = request.POST['id_modify']
                vt = VehicleTypeMaster.objects.get(RowID=id)
                qt = QuotaTransaction.objects.filter(number_plat=vt.number_plat)

                # Check if the vehicle is deleted
                if vt.Deleted == False and qt.exists():
                    message_modify = "Tidak bisa melakukan modifikasi data. Kendaraan sudah melakukan transaksi hari ini"
                    data = VehicleMasterView.objects.filter(RowID=id)
                    paginator = Paginator(data, 5)  # Show 10 items per page
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                elif vt.Deleted == False and not qt.exists():
                    message_modify = "Tidak bisa melakukan modifikasi data. Inactive kendaraan terlebih dahulu"
                    data = VehicleMasterView.objects.filter(RowID=id)
                    paginator = Paginator(data, 5)  # Show 10 items per page
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                else:
                    # modify
                    vt.MerkKendaraan = request.POST.get('MerkKendaraan')
                    
                    vt.MerkKendaraan = request.POST.get('MerkKendaraan')
                    vt.JenisKendaraan = request.POST.get('jenisKendaraan')
                    vt.Warna = request.POST.get('warna')
                    vt.NamaPemilik = request.POST.get('NamaPemilik')
                    vt.AlamatPemilik = request.POST.get('AlamatPemilik')


                    JumlahRoda = request.POST["JumlahRoda"]
                    TahunPembuatan = request.POST["TahunPembuatan"]
                    KapasitasCylinder = request.POST["KapasitasCylinder"]
                    if JumlahRoda.strip() != '':
                        vt.JumlahRoda = JumlahRoda
                    else:
                        vt.JumlahRoda = None
                    if TahunPembuatan.strip() != '':
                        vt.TahunPembuatan = int(TahunPembuatan)
                    else:
                        vt.TahunPembuatan = None
                    if KapasitasCylinder.strip() != '':
                        vt.KapasitasCylinder = int(KapasitasCylinder)
                    else:
                        vt.KapasitasCylinder = None
                    vt.STNKReady = request.POST.get('STNKReady')
                    try:
                        DateValidSTNK = request.POST["masaBerlakuSTNK"]
                    except:
                        DateValidSTNK = None
                    RekomReady = request.POST["RekomReady"]
                    vt.DateValidSTNK = DateValidSTNK
                    vt.RekomReady = request.POST.get('RekomReady')

                    vt.vehicletype_id = request.POST['vehicle_id']
                    vehicle = VehicleType.objects.get(id=request.POST['vehicle_id'])
                    vt.vehicletype_kf = vehicle.description
                    vt.SettingSystem = vehicle.SettingSystem
                    vt.TypeKendaraan = request.POST['Typekendaraan']

                    vt.ChangedBy = username
                    vt.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    vt.save()
                    message_modify = "Berhasil melakukan modifikasi data"
                    data = VehicleMasterView.objects.filter(RowID=id)
                    paginator = Paginator(data, 5)  # Show 10 items per page
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)

                    # save image
                    ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
                    if 'STNKImageDepan' in request.FILES:
                        number_plat = request.POST['number_plat_hidden']
                        number_plat = number_plat.replace(' ', '')
                        stnk_image = request.FILES['STNKImageDepan']
                        
                        # Perform file type validation
                        filename, file_extension = os.path.splitext(stnk_image.name)
                        if file_extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                            # Handle invalid file type error
                            return HttpResponse('<script>'
                                'alert("GAGAL MENYIMPAN FOTO STNK.\nHanya data berformat JPG/JPEG/PNG yang dapat disimpan");'
                                'window.history.back();'
                                '</script>')
                        
                        # Open the image using PIL
                        image = Image.open(stnk_image)
                        # Resize the image to 50% of its original size
                        resized_image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
                        # Convert the image to RGB mode (remove alpha channel)
                        resized_image = resized_image.convert("RGB")
                        # Construct the file path using MEDIA_ROOT
                        file_path = os.path.join(settings.MEDIA_ROOT, f'stnk_images/{number_plat}_STNK_DEPAN.jpg')
                        # Save the resized image as JPEG
                        resized_image.save(file_path, "JPEG")
                    if 'STNKImageBelakang' in request.FILES:
                        number_plat = request.POST['number_plat_hidden']
                        number_plat = number_plat.replace(' ', '')
                        stnk_image = request.FILES['STNKImageBelakang']
                        
                        # Perform file type validation
                        filename, file_extension = os.path.splitext(stnk_image.name)
                        if file_extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                            # Handle invalid file type error
                            return HttpResponse('<script>'
                                'alert("GAGAL MENYIMPAN FOTO STNK.\nHanya data berformat JPG/JPEG/PNG yang dapat disimpan");'
                                'window.history.back();'
                                '</script>')
                        
                        # Open the image using PIL
                        image = Image.open(stnk_image)
                        # Resize the image to 50% of its original size
                        resized_image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
                        # Convert the image to RGB mode (remove alpha channel)
                        resized_image = resized_image.convert("RGB")
                        # Construct the file path using MEDIA_ROOT
                        file_path = os.path.join(settings.MEDIA_ROOT, f'stnk_images/{number_plat}_STNK_BELAKANG.jpg')
                        # Save the resized image as JPEG
                        resized_image.save(file_path, "JPEG")
                    if 'SuratRekomendasi' in request.FILES:
                        number_plat = request.POST['number_plat_hidden']
                        number_plat = number_plat.replace(' ', '')
                        rekom_image = request.FILES['SuratRekomendasi']
                        
                        # Perform file type validation
                        filename, file_extension = os.path.splitext(rekom_image.name)
                        if file_extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
                            # Handle invalid file type error
                            return HttpResponse('<script>'
                            'alert("GAGAL MENYIMPAN FOTO SURAT REKOMENDASI.\nHanya data berformat JPG/JPEG/PNG yang dapat disimpan");'
                            'window.history.back();'
                            '</script>')
                        
                        # Open the image using PIL
                        image = Image.open(rekom_image)
                        # Resize the image to 50% of its original size
                        resized_image = image.resize((int(image.width * 0.5), int(image.height * 0.5)))
                        # Convert the image to RGB mode (remove alpha channel)
                        resized_image = resized_image.convert("RGB")
                        # Construct the file path using MEDIA_ROOT
                        file_path = os.path.join(settings.MEDIA_ROOT, f'rekom_images/{number_plat}_SURAT_REKOMENDASI.jpg')
                        # Save the resized image as JPEG
                        resized_image.save(file_path, "JPEG")

                    # save log
                    LogVehicleTypeMaster.objects.create(RowID = vt.RowID,
                                                        number_plat = vt.number_plat,
                                                        MerkKendaraan = vt.MerkKendaraan,
                                                        TypeKendaraan = vt.vehicletype_kf,
                                                        JenisKendaraan = vt.JenisKendaraan,
                                                        Warna = vt.Warna,
                                                        NamaPemilik = vt.NamaPemilik,
                                                        AlamatPemilik = vt.AlamatPemilik,
                                                        JumlahRoda = vt.JumlahRoda,
                                                        TahunPembuatan = vt.TahunPembuatan,
                                                        KapasitasCylinder = vt.KapasitasCylinder,
                                                        STNKReady = vt.STNKReady,
                                                        vehicletype_kf = vt.vehicletype_kf,
                                                        vehicletype_id = vt.vehicletype_id,
                                                        SettingSystem = vt.SettingSystem,
                                                        Deleted = vt.Deleted,
                                                        ChangedBy = username,
                                                        ChangedDate = vt.ChangedDate,
                                                        RekomReady = vt.RekomReady,
                                                        DateValidSTNK = vt.DateValidSTNK)
            

        paginator = Paginator(data, 5)  # Show 10 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj, 'vehicle_types': vehicle_types, 'message_modify': message_modify}
        if request.user.is_superuser:
            return render(request, 'vehicleMaster.html', context)
        else:
            return render(request, 'vehicleMaster_cabang.html', context)
    else:
        return render(request, 'noAccess.html')

def delete(request, delete_id):
    st = VehicleTypeMaster.objects.get(RowID=delete_id)
    username = request.user.get_full_name()
    ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    if st.Deleted == False:
        deleted_value = True
    elif st.Deleted == True:
        deleted_value = False
    st.Deleted = deleted_value
    st.ChangedBy = username
    st.ChangedDate = ChangedDate
    st.save()

    # save log
    LogVehicleTypeMaster.objects.create(RowID = st.RowID,
                                            number_plat = st.number_plat,
                                            MerkKendaraan = st.MerkKendaraan,
                                            TypeKendaraan = st.vehicletype_kf,
                                            JenisKendaraan = st.JenisKendaraan,
                                            Warna = st.Warna,
                                            NamaPemilik = st.NamaPemilik,
                                            AlamatPemilik = st.AlamatPemilik,
                                            JumlahRoda = st.JumlahRoda,
                                            TahunPembuatan = st.TahunPembuatan,
                                            KapasitasCylinder = st.KapasitasCylinder,
                                            STNKReady = st.STNKReady,
                                            vehicletype_kf = st.vehicletype_kf,
                                            vehicletype_id = st.vehicletype_id,
                                            SettingSystem = st.SettingSystem,
                                            Deleted = st.Deleted,
                                            ChangedBy = username,
                                            ChangedDate = ChangedDate,
                                            RekomReady = st.RekomReady,
                                            DateValidSTNK = st.DateValidSTNK,
                                            block = st.block)

    # Redirect to the same page to show the updated data
    return redirect('vehicleMaster:index')

def block(request, block_id):
    st = VehicleTypeMaster.objects.get(RowID=block_id)
    username = request.user.get_full_name()
    ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    if st.block == False:
        block_value = True
        st.block = block_value
        st.Deleted = True
    elif st.block == True:
        block_value = False
        st.block = block_value
    else:
        block_value = True
        st.block = block_value
        st.Deleted == True
    st.ChangedBy = username
    st.ChangedDate = ChangedDate
    st.save()

    # save log
    LogVehicleTypeMaster.objects.create(RowID = st.RowID,
                                            number_plat = st.number_plat,
                                            MerkKendaraan = st.MerkKendaraan,
                                            TypeKendaraan = st.vehicletype_kf,
                                            JenisKendaraan = st.JenisKendaraan,
                                            Warna = st.Warna,
                                            NamaPemilik = st.NamaPemilik,
                                            AlamatPemilik = st.AlamatPemilik,
                                            JumlahRoda = st.JumlahRoda,
                                            TahunPembuatan = st.TahunPembuatan,
                                            KapasitasCylinder = st.KapasitasCylinder,
                                            STNKReady = st.STNKReady,
                                            vehicletype_kf = st.vehicletype_kf,
                                            vehicletype_id = st.vehicletype_id,
                                            SettingSystem = st.SettingSystem,
                                            Deleted = st.Deleted,
                                            ChangedBy = username,
                                            ChangedDate = ChangedDate,
                                            RekomReady = st.RekomReady,
                                            DateValidSTNK = st.DateValidSTNK,
                                            block = st.block)
    
    # Redirect to the same page to show the updated data
    return redirect('vehicleMaster:index')

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