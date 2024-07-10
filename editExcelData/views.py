from django.shortcuts import render
import os
from django.http import HttpResponse, FileResponse
import pandas as pd
from datetime import datetime
import json

from editExcelData.models import EditExcelData

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        # get site user
        username = request.user.username
        allowed_usernames = ['rizky.febrian', 'jaka.brahmana']

        if request.user.is_superuser:
            return render(request, 'editExcelData.html')
        else:
            if username in allowed_usernames:
                return render(request, 'editExcelData_cabang.html')
            else:
                return render(request, 'noAccess.html')
    else:
        return render(request, 'noAccess.html')
    
def download_template(request):
    template_path = os.path.join(os.path.dirname(__file__), 'editExcelData.xlsx')
    with open(template_path, 'rb') as f:
        response = HttpResponse(f, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="editExcelData.xlsx"'
        return response
    
def import_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES['excelFile']
        
        try:
            # Read the Excel file using pandas with openpyxl as the engine
            df = pd.read_excel(excel_file, engine='openpyxl')
            # if there is empty cell input it 0
            df.fillna(0, inplace=True)
            
            # Normalize column names
            df.columns = df.columns.str.replace(' ', '_')  # Replace spaces with underscores

            # Remove unnecessary unnamed columns
            df = df.loc[:, ~df.columns.str.startswith('Unnamed:')]

            # Check for empty rows
            df['is_empty_row'] = df.isnull().all(axis=1)
            
            # Define the conditions and corresponding error messages
            df['Tanggal_Akhir_Surat_Rekomendasi'] = pd.to_datetime(df['Tanggal_Akhir_Surat_Rekomendasi'], format='%Y-%m-%d')

            conditions = [
                (df['Tanggal_Akhir_Surat_Rekomendasi'] < datetime.now(), "Tanggal surat rekomendasi sudah tidak berlaku"),
            ]

            # Check for duplicate data
            duplicate_condition = (
                df.duplicated(['ID_Konsumen', 'NIK'], keep=False),
                'Terdapat data yang sama'
            )
            conditions.append(duplicate_condition)
            
            # Create a new column to store the error messages
            df['error_messages'] = ''
            # Iterate over the conditions and update the error_messages column
            for condition, message in conditions:
                df.loc[condition, 'error_messages'] += message + ', '
            # Remove trailing commas from error messages
            df['error_messages'] = df['error_messages'].str.rstrip(', ')
            
            # Convert the DataFrame to a list of dictionaries
            df = df.applymap(lambda x: None if x == 0 else x)
            data = df.to_dict(orient='records')
            
            # Render the HTML template with the imported data
            # get site user
            username = request.user.username
            allowed_usernames = ['rizky.febrian', 'jaka.brahmana']

            if request.user.is_superuser:
                return render(request, 'editExcelData.html', {'data': data})
            else:
                if username in allowed_usernames:
                    return render(request, 'editExcelData_cabang.html', {'data': data})
                else:
                    return render(request, 'noAccess.html')
        
        except Exception as e:
            # Handle any exceptions that occur during file reading or processing
            # You can display an error message or take appropriate action
            return HttpResponse(f'Error: {str(e)}')

    if request.user.is_superuser:
        return render(request, 'editExcelData.html')
    else:
        return render(request, 'editExcelData_cabang.html')
    
def add_data(request):
    if request.method == 'POST':
        form_data = json.loads(request.POST['form_data'])

        # Iterate through the form data and add it to the NONVEHICLEMASTER table
        for data in form_data:
            # (nan data kosong -> None)
            for key, value in data.items():
                # Convert 'nan' to None for non-numeric fields
                if value == 'None':
                    data[key] = None

            # get uuidValue, uuidValue kapal, status, url file di databph based on (nosurat, siteregis, nik, tglawal, tglakhir, namakapal, alokasivolume) file excel
            no_konsumen = data["ID_Konsumen"]
            site_registration = data['No_Penyalur']
            nama = data['Nama']
            nik = data['NIK']
            tgl_akhir_rekom=data['Tanggal_Akhir_Surat_Rekomendasi']
            tgl_efektif=data['Tanggal_Efektif']

            existing_EditExcelData = EditExcelData.objects.filter(site_registration=site_registration, no_konsumen=no_konsumen, nik=nik, nama=nama, status=0).first()

            if existing_EditExcelData:
                existing_EditExcelData.tgl_akhir_rekom=tgl_akhir_rekom
                existing_EditExcelData.tgl_efektif=tgl_efektif
                existing_EditExcelData.save()
            else:
                EditExcelData.objects.create(
                    site_registration = site_registration,
                    no_konsumen = no_konsumen,
                    nama = nama,
                    nik = nik,
                    tgl_akhir_rekom=tgl_akhir_rekom,
                    tgl_efektif=tgl_efektif,
                    status = 0   
                )

            # # next insert
            # try:
            #     EditExcelData.objects.create(
            #         site_registration = site_registration,
            #         no_konsumen = no_konsumen,
            #         nama = nama,
            #         nik = nik,
            #         tgl_akhir_rekom=tgl_akhir_rekom,
            #         tgl_efektif=tgl_efektif,
            #         status = 0   
            #     )
            #     success_message = "Submit Berhasil."
            #     print(success_message)
            # except:
            #     error_message = "Submit Gagal."
            #     print(error_message)

        # get site user
        username = request.user.username
        allowed_usernames = ['rizky.febrian', 'jaka.brahmana']

        if request.user.is_superuser:
            return render(request, 'editExcelData.html')
        else:
            if username in allowed_usernames:
                return render(request, 'editExcelData_cabang.html')
            else:
                return render(request, 'noAccess.html')

