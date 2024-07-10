from django.shortcuts import render
from django.http import HttpResponse
import os
from datetime import datetime

from django.conf import settings
from django.core.files.storage import default_storage
from uploadExcelNonkendaraan.models import NonVehicleMaster

def index(request):
    success_message = None
    error_message = None

    if request.user.is_authenticated:
        if request.method == 'POST':
            date_upload = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            selected_options = request.POST.getlist('nomor_surat')

            # Remove the empty string from selected_options
            selected_options = [option for option in selected_options if option]

            # Update the database records where nomor_surat is in selected_options
            try:
                # Upload file rekom
                ALLOWED_DOCUMENT_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']
                rekom_file = request.FILES['rekomFile']
                
                # Perform file type validation
                filename, file_extension = os.path.splitext(rekom_file.name)
                if file_extension.lower() not in ALLOWED_DOCUMENT_EXTENSIONS:
                    error_message = "Upload Gagal: Extensi File Salah"
                else:
                    documentFile_name = f"{date_upload}{file_extension.lower()}"
                    # Save File
                    file_path = os.path.join(settings.MEDIA_ROOT, f'RekomDokumen_Nontransportasi/{documentFile_name}')
                    with default_storage.open(file_path, 'wb') as destination:
                        for chunk in rekom_file.chunks():
                            destination.write(chunk)
                    # Update the database records where nomor_surat is in selected_options
                    NonVehicleMaster.objects.filter(nomor_surat__in=selected_options).update(dokumen_status=True, dokumen_name=documentFile_name)
                    success_message = "Upload Berhasil"
            except Exception as e:
                error_message = f"Upload Gagal: {e}"

            # You can now work with the filtered selected options as needed
        # Query for unique nomor_surat values with dokumen_status = 0
        unique_nomor_surat = NonVehicleMaster.objects.filter(dokumen_status=0).values_list('nomor_surat', flat=True).distinct()
        context = {
            'unique_nomor_surat': unique_nomor_surat,
            'success_message': success_message,
            'error_message': error_message,
        }
        if request.user.is_superuser:
            return render(request, 'uploadSuratRekomNonkendaraan.html', context)
        else:
            return render(request, 'uploadSuratRekomNonkendaraan_cabang.html', context)
    else:
        return render(request, 'noAccess.html')