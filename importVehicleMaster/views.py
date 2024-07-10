from django.shortcuts import render
import os
from django.http import FileResponse
import pandas as pd
# from django.template.loader import render_to_string
# from django.http import JsonResponse
import json
import uuid
from datetime import datetime
from django.http import HttpResponse, FileResponse

from vehicleMaster.models import VehicleTypeMaster
from vehicleTypeMaster.models import VehicleType

# Create your views here.
def index(request):
    data = []
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'importVehicleMaster.html', {'data': data})
        else:
            return render(request, 'importVehicleMaster_cabang.html', {'data': data})
    else:
        return render(request, 'noAccess.html')
    
def download_template(request):
    template_path = os.path.join(os.path.dirname(__file__), 'vehicleMaster.xlsx')
    with open(template_path, 'rb') as f:
        response = HttpResponse(f, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="vehicleMaster.xlsx"'
        return response
    
import pandas as pd

def import_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES['excelFile']
        
        try:
            # Read the Excel file using pandas with openpyxl as the engine
            df = pd.read_excel(excel_file, engine='openpyxl')
            
            # Normalize column names
            df.columns = df.columns.str.replace(' ', '_')  # Replace spaces with underscores

            # Remove unnecessary unnamed columns
            df = df.loc[:, ~df.columns.str.startswith('Unnamed:')]

            # Check for empty cell
            df['is_empty_cell'] = df.isnull().any(axis=1)

            # Check for empty rows
            df['is_empty_row'] = df.isnull().all(axis=1)
            
            # Check for duplicate data in 'Nomor Kendaraan' column
            df['is_duplicate'] = df.duplicated('Nomor_Kendaraan', keep='first')
            
            # # Check if 'Nomor Kendaraan' already exists in the database (case-insensitive)
            # existing_numbers = VehicleTypeMaster.objects.values_list('number_plat', flat=True)
            # existing_numbers = [number.lower() for number in existing_numbers]  # Convert to lowercase
            # try:
            #     df['is_existed'] = df['Nomor_Kendaraan'].str.lower().isin(existing_numbers)  # Convert to lowercase before comparison
            # except:
            #     pass

            # Define the allowed values for Warna_TNKB
            allowed_values_warna = ["PUTIH-HITAM", "HITAM", "KUNING", "MERAH"]
            allowed_values_roda = [4, 6, ">6"]
            allowed_values_tipe_kendaraan = ["Mobil | ID: 3", "Truk/Bus ≥ 6 | ID: 8", "Truk/Bus 4 | ID: 9"]

            # Define the conditions and corresponding error messages
            conditions = [
                (~df['Warna_TNKB'].isin(allowed_values_warna), "Warna salah"),
                (~df['Tipe_Kendaraan'].isin(allowed_values_tipe_kendaraan), "Tipe kendaraan system salah"),
                (~df['Jumlah_Roda'].isin(allowed_values_roda), "Jumlah roda salah"),
                (~df['Tahun_Pembuatan'].apply(lambda x: isinstance(x, int)), "Tahun pembuatan harus berupa angka"),
                (~df['Isi_Silinder'].apply(lambda x: isinstance(x, int)), "Isi silinder harus berupa angka")
            ]
            # Create a new column to store the error messages
            df['error_messages'] = ''
            # Iterate over the conditions and update the error_messages column
            for condition, message in conditions:
                df.loc[condition, 'error_messages'] += message + ', '
            # Remove trailing commas from error messages
            df['error_messages'] = df['error_messages'].str.rstrip(', ')
            
            # Convert the DataFrame to a list of dictionaries
            data = df.to_dict(orient='records')
            
            # Render the HTML template with the imported data
            if request.user.is_superuser:
                return render(request, 'importVehicleMaster.html', {'data': data})
            else:
                return render(request, 'importVehicleMaster_cabang.html', {'data': data})
        
        except Exception as e:
            # Handle any exceptions that occur during file reading or processing
            # You can display an error message or take appropriate action
            return HttpResponse(f'Error: {str(e)}')

    if request.user.is_superuser:
        return render(request, 'importVehicleMaster.html')
    else:
        return render(request, 'importVehicleMaster_cabang.html')

def add_data(request):
    if request.method == 'POST':
        form_data = json.loads(request.POST['form_data'])
        
        # Iterate through the form data and add it to the VEHICLETYPEMASTER table
        for data in form_data:
            number_plat = data['Nomor_Kendaraan']
            existing_vehicle = VehicleTypeMaster.objects.filter(number_plat=number_plat).first()

            if existing_vehicle:
                # Retrieve the corresponding VehicleType object
                description=data['Tipe_Kendaraan']
                vehicle_type = VehicleType.objects.get(description=description[:-8])

                # Update the existing VehicleTypeMaster object
                existing_vehicle.MerkKendaraan = data['Merk_Kendaraan']
                existing_vehicle.TypeKendaraan = data['Tipe_Kendaraan_STNK']
                existing_vehicle.JenisKendaraan = data['Jenis_Model_Kendaraan_STNK']
                existing_vehicle.Warna=data['Warna_TNKB']
                existing_vehicle.NamaPemilik=data['Nama_Pemilik']
                existing_vehicle.AlamatPemilik=data['Alamat_Pemilik']
                existing_vehicle.JumlahRoda=data['Jumlah_Roda']
                existing_vehicle.TahunPembuatan=data['Tahun_Pembuatan']
                existing_vehicle.KapasitasCylinder=data['Isi_Silinder']
                existing_vehicle.vehicletype_kf=description[:-8]
                existing_vehicle.vehicletype_id=vehicle_type.id
                existing_vehicle.SettingSystem=vehicle_type.SettingSystem
                existing_vehicle.ChangedBy=request.user.get_full_name()
                existing_vehicle.ChangedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                existing_vehicle.save()
            else:
                # Retrieve the corresponding VehicleType object
                description=data['Tipe_Kendaraan']
                vehicle_type = VehicleType.objects.get(description=description[:-8])

                # Create the VehicleTypeMaster object with the retrieved values
                VehicleTypeMaster.objects.create(
                    RowID=str(uuid.uuid4()),
                    number_plat=data['Nomor_Kendaraan'],
                    MerkKendaraan=data['Merk_Kendaraan'],
                    TypeKendaraan=data['Tipe_Kendaraan_STNK'],
                    JenisKendaraan=data['Jenis_Model_Kendaraan_STNK'],
                    Warna=data['Warna_TNKB'],
                    NamaPemilik=data['Nama_Pemilik'],
                    AlamatPemilik=data['Alamat_Pemilik'],
                    JumlahRoda=data['Jumlah_Roda'],
                    TahunPembuatan=data['Tahun_Pembuatan'],
                    KapasitasCylinder=data['Isi_Silinder'],
                    STNKReady=False,
                    vehicletype_kf=description[:-8],
                    vehicletype_id=vehicle_type.id, 
                    SettingSystem=vehicle_type.SettingSystem,
                    Deleted=False,
                    UploadedBy=request.user.get_full_name(),
                    UploadedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                    ChangedBy=request.user.get_full_name(),
                    ChangedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                    RekomReady=False,
                    DateValidSTNK = None
                )

        if request.user.is_superuser:
            return render(request, 'importVehicleMaster.html')
        else:
            return render(request, 'importVehicleMaster_cabang.html')




