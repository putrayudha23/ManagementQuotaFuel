from django.shortcuts import render
import os
from django.http import HttpResponse, FileResponse
import pandas as pd
import json
from datetime import datetime
import uuid
import math
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
import numpy as np

from uploadExcelNonkendaraan.models import NonVehicleMaster
from dataBph.models import NonTransportasiBPHMigas, JenisBbmMaster, JenisUsahaMaster, SektorKonsumenMaster
from userSetting.models import UserSiteMapping
from django.contrib.auth.models import User
from siteMaster.models import SiteMaster

def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'uploadExcelNonkendaraan.html')
        else:
            return render(request, 'uploadExcelNonkendaraan_cabang.html')
    else:
        return render(request, 'noAccess.html')
    
def download_template(request):
    template_path = os.path.join(os.path.dirname(__file__), 'nonVehicleMaster.xlsx')
    with open(template_path, 'rb') as f:
        response = HttpResponse(f, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="nonVehicleMaster.xlsx"'
        return response
    
def convert_to_int(value):
    if pd.isnull(value):  # Check if value is NaN
        return math.nan  # Return NaN

    try:
        return int(float(value))  # Convert to float first, then to int
    except (ValueError, TypeError):
        return value

def convert_to_float(value):
    try:
        # Convert input to string before processing
        value_str = str(value)

        # Replacing comma with dot if present
        if ',' in value_str:
            value_str = value_str.replace(',', '.')

        result  = float(value_str)

        # result = str(result)

        # if '.' in result:
        #     result = result.replace('.', ',')

        return result
    except (ValueError, TypeError):
       pass

def capitalize_each_word(text):
    return ' '.join(word.capitalize() for word in text.lower().split())
    
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

            # Check for empty cell
            # df['is_empty_cell'] = df.isnull().any(axis=1)

            # Check for empty rows
            df['is_empty_row'] = df.isnull().all(axis=1)
            

            # Define the allowed values for Warna_TNKB
            sektor_konsumen_values = SektorKonsumenMaster.objects.values_list('sektor_konsumen', flat=True)
            allowed_values_sektor = list(sektor_konsumen_values)

            # Define the conditions and corresponding error messages
            df['Tanggal_Akhir_Surat_Rekomendasi'] = pd.to_datetime(df['Tanggal_Akhir_Surat_Rekomendasi'], format='%Y-%m-%d')

            # data treatment
            df['Jumlah_Mesin'] = df['Jumlah_Mesin'].apply(convert_to_int)
            df['Jumlah_Daya_Mesin_PK_atau_HP'] = df['Jumlah_Daya_Mesin_PK_atau_HP'].apply(convert_to_float)
            df['Penggunaan_Mesin_Jam_per_hari'] = df['Penggunaan_Mesin_Jam_per_hari'].apply(convert_to_int)
            df['Klasifikasi_atau_Kapasitas_GT'] = df['Klasifikasi_atau_Kapasitas_GT'].apply(convert_to_int)
            df['Lama_Operasi_hari_per_bulan'] = df['Lama_Operasi_hari_per_bulan'].apply(convert_to_int)
            df['Konsumsi_JBT_Bulan_per_bulan'] = df['Konsumsi_JBT_Bulan_per_bulan'].apply(convert_to_int)
            df['Alokasi_Volume'] = df['Alokasi_Volume'].apply(convert_to_int)
            df['Sektor_Konsumen_Pengguna'] = df['Sektor_Konsumen_Pengguna'].apply(capitalize_each_word)
            

            conditions = [
                (~df['Sektor_Konsumen_Pengguna'].isin(allowed_values_sektor), "Sektor konsumen pengguna salah"),
                (~df['Jumlah_Mesin'].apply(lambda x: isinstance(x, int)), "Jumlah mesin harus berupa angka"),
                (~df['Jumlah_Daya_Mesin_PK_atau_HP'].apply(lambda x: isinstance(x, float)), "Jumlah daya mesin harus berupa angka"),
                (~df['Penggunaan_Mesin_Jam_per_hari'].apply(lambda x: isinstance(x, int)), "Jam penggunaan mesin per hari harus berupa angka"),
                (~df['Klasifikasi_atau_Kapasitas_GT'].apply(lambda x: isinstance(x, int)), "Klasifikasi Kapasitas GT harus berupa angka"),
                (~df['Lama_Operasi_hari_per_bulan'].apply(lambda x: isinstance(x, int)), "Lama Operasi hari per bulan harus berupa angka"),
                (~df['Konsumsi_JBT_Bulan_per_bulan'].apply(lambda x: isinstance(x, int)), "Konsumsi JBT Bulan harus berupa angka"),
                (~df['Alokasi_Volume'].apply(lambda x: isinstance(x, int)), "Alokasi Volume harus berupa angka"),
                (df['Alokasi_Volume'] > df['Konsumsi_JBT_Bulan_per_bulan'], "Alokasi Volume tidak boleh lebih besar dari Konsumsi JBT per Bulan"),
                (df['Tanggal_Akhir_Surat_Rekomendasi'] < datetime.now(), "Tanggal surat rekomendasi sudah tidak berlaku"),
            ]

            # Check for duplicate data
            duplicate_condition = (
                df.duplicated(['No_Penyalur', 'ID_Konsumen', 'Nomor_Surat_Rekomendasi', 'NIK'], keep=False),
                'Terdapat data yang sama'
            )
            conditions.append(duplicate_condition)


            # Check for exsist data in NonVehicleMaster based on 'No_Penyalur', 'ID_Konsumen', 'Nomor_Surat_Rekomendasi', 'NIK' GA PAKE UUID
            for index, row in df.iterrows():
                # Check for existing data in NonVehicleMaster based on the current row values and uuids
                existing_data = NonVehicleMaster.objects.filter(
                    site_registration=row['No_Penyalur'],
                    no_konsumen=row['ID_Konsumen'],
                    nomor_surat=row['Nomor_Surat_Rekomendasi'],
                    nik=row['NIK']
                ).exists()

                # Assign the result to the 'is_existed' column for the current row
                df.at[index, 'is_existed'] = existing_data
            
            # Create a new column to store the error messages
            df['error_messages'] = ''
            # Iterate over the conditions and update the error_messages column
            for condition, message in conditions:
                df.loc[condition, 'error_messages'] += message + ', '
            # Remove trailing commas from error messages
            df['error_messages'] = df['error_messages'].str.rstrip(', ')
            
            # Convert the DataFrame to a list of dictionaries
            # df.replace(0, None, inplace=True)
            # df.replace(0, np.nan, inplace=True)
            df = df.applymap(lambda x: None if x == 0 else x)
            print(df['NIK'])
            data = df.to_dict(orient='records')
            
            # Render the HTML template with the imported data
            if request.user.is_superuser:
                return render(request, 'uploadExcelNonkendaraan.html', {'data': data})
            else:
                return render(request, 'uploadExcelNonkendaraan_cabang.html', {'data': data})
        
        except Exception as e:
            # Handle any exceptions that occur during file reading or processing
            # You can display an error message or take appropriate action
            return HttpResponse(f'Error: {str(e)}')

    if request.user.is_superuser:
        return render(request, 'uploadExcelNonkendaraan.html')
    else:
        return render(request, 'uploadExcelNonkendaraan_cabang.html')
    
def add_data(request):
    if request.method == 'POST':
        form_data = json.loads(request.POST['form_data'])
        
        total_amount_per_site = {}
        # Iterate through the form data and add it to the NONVEHICLEMASTER table
        for data in form_data:
            # (nan data kosong -> None)
            for key, value in data.items():
                # Convert 'nan' to None for non-numeric fields
                if value == 'None':
                    data[key] = None

            # get uuidValue, uuidValue kapal, status, url file di databph based on (nosurat, siteregis, nik, tglawal, tglakhir, namakapal, alokasivolume) file excel
            Nomor_Surat_Rekomendasi = data['Nomor_Surat_Rekomendasi']
            No_Penyalur = data['No_Penyalur']
            nik = data['NIK']
            Tanggal_Awal = data['Tanggal_Awal_Surat_Rekomendasi']
            Tanggal_Akhir = data['Tanggal_Akhir_Surat_Rekomendasi']
            Nama_Kapal = data['Nama_Kapal']
            Alokasi_Volume = data['Alokasi_Volume']

            # Get uuidValue, uuidValue_kapal, status, url_file
            data_nonTransportasiBph = NonTransportasiBPHMigas.objects.filter(no_surat_rekomendasi=Nomor_Surat_Rekomendasi, site_registration=No_Penyalur, nik=nik, tanggal_terbit=Tanggal_Awal, tanggal_berakhir=Tanggal_Akhir, nama_kapal=Nama_Kapal, alokasi_volume=Alokasi_Volume).first()

            if data_nonTransportasiBph: # Kalo datanya ada di NonTransportasiBPHMigas
                uuidValue = data_nonTransportasiBph.uuid
                uuidValue_kapal = data_nonTransportasiBph.uuid_kapal

                data_nonTransportasiBph = NonTransportasiBPHMigas.objects.filter(uuid=uuidValue, uuid_kapal=uuidValue_kapal, no_surat_rekomendasi=Nomor_Surat_Rekomendasi, site_registration=No_Penyalur, nik=nik, tanggal_terbit=Tanggal_Awal, tanggal_berakhir=Tanggal_Akhir, nama_kapal=Nama_Kapal, alokasi_volume=Alokasi_Volume, data_release=None).first()

                existing_nonvehicle = NonVehicleMaster.objects.filter(uuid=uuidValue,uuid_kapal=uuidValue_kapal).first()

                if existing_nonvehicle:
                    status = data_nonTransportasiBph.status
                    flag_status = None
                    try:
                        Jumlah_Daya_Mesin_PK_atau_HP=float(data['Jumlah_Daya_Mesin_PK_atau_HP'])
                    except:
                        Jumlah_Daya_Mesin_PK_atau_HP=data['Jumlah_Daya_Mesin_PK_atau_HP']

                    if status == 5: # jika pencabutan maka langsung inactive tanpa update data lg
                        existing_nonvehicle.status=status
                        existing_nonvehicle.inactive_status=True
                        existing_nonvehicle.save()

                        # update data_release nonTransportasiBph
                        data_nonTransportasiBph.data_release=True
                        data_nonTransportasiBph.save()
                    else:
                        # next update data nonvehicle
                        existing_nonvehicle.no_konsumen = data["ID_Konsumen"]
                        existing_nonvehicle.site_registration = data['No_Penyalur']
                        existing_nonvehicle.nama = data['Nama']
                        existing_nonvehicle.nik = data['NIK']
                        existing_nonvehicle.alamat=data['Alamat']

                        sektor_konsumen = SektorKonsumenMaster.objects.get(sektor_konsumen=data['Sektor_Konsumen_Pengguna'])
                        existing_nonvehicle.sektor_konsumen=sektor_konsumen.id

                        existing_nonvehicle.nama_kapal=data['Nama_Kapal']
                        existing_nonvehicle.jenis_mesin=data['Jenis_Mesin']
                        existing_nonvehicle.jumlah_mesin=data['Jumlah_Mesin']
                        existing_nonvehicle.jumlah_dayaMesin=Jumlah_Daya_Mesin_PK_atau_HP
                        existing_nonvehicle.jam_penggunaan=data['Penggunaan_Mesin_Jam_per_hari']
                        existing_nonvehicle.klasifikasi_gt=data['Klasifikasi_atau_Kapasitas_GT']
                        existing_nonvehicle.lama_operasi=data['Lama_Operasi_hari_per_bulan']
                        existing_nonvehicle.konsumsi_jbt=data['Konsumsi_JBT_Bulan_per_bulan']
                        existing_nonvehicle.alokasi_volume=data['Alokasi_Volume']
                        existing_nonvehicle.tgl_awal_rekom=data['Tanggal_Awal_Surat_Rekomendasi']
                        existing_nonvehicle.tgl_akhir_rekom=data['Tanggal_Akhir_Surat_Rekomendasi']
                        existing_nonvehicle.nomor_surat=data['Nomor_Surat_Rekomendasi']

                        existing_nonvehicle.badan_usaha=data['Badan_Usaha']
                        existing_nonvehicle.nama_usaha=data['Nama_Usaha']

                        # get id jenis bbm
                        jenis_bbm = JenisBbmMaster.objects.get(jenis_bbm=data['Jenis_BBM'])
                        existing_nonvehicle.jenis_bbm=jenis_bbm.id

                        # get id jenis usaha
                        jenis_usaha = JenisUsahaMaster.objects.get(jenis_usaha=data['Jenis_Usaha'])
                        existing_nonvehicle.jenis_usaha=jenis_usaha.id

                        existing_nonvehicle.kode_provinsi=data['Kode_Provinsi']
                        existing_nonvehicle.kode_kabkota=data['Kode_Kabupaten_Kota']
                        existing_nonvehicle.kode_kecamatan=data['Kode_Kecamatan']
                        existing_nonvehicle.kode_keldesa=data['Kode_Kelurahan_Desa']
                        existing_nonvehicle.penerbit=data['Penerbit']

                        existing_nonvehicle.status=status
                        
                        existing_nonvehicle.url_file=data_nonTransportasiBph.url_file
                        existing_nonvehicle.flag_status=flag_status

                        existing_nonvehicle.ChangedBy=request.user.get_full_name()
                        existing_nonvehicle.ChangedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        existing_nonvehicle.save()

                        # update data_release nonTransportasiBph
                        data_nonTransportasiBph.data_release=True
                        data_nonTransportasiBph.save()

                else:
                    url_file = data_nonTransportasiBph.url_file
                    status = data_nonTransportasiBph.status # nilai ini 2 (data baru) atau 4 (data update)
                    flag_status = None
                    jenis_bbm = JenisBbmMaster.objects.get(jenis_bbm=data['Jenis_BBM'])
                    jenis_usaha = JenisUsahaMaster.objects.get(jenis_usaha=data['Jenis_Usaha'])
                    sektor_konsumen = SektorKonsumenMaster.objects.get(sektor_konsumen=data['Sektor_Konsumen_Pengguna'])

                    try:
                        Jumlah_Daya_Mesin_PK_atau_HP=float(data['Jumlah_Daya_Mesin_PK_atau_HP'])
                    except:
                        Jumlah_Daya_Mesin_PK_atau_HP=data['Jumlah_Daya_Mesin_PK_atau_HP']

                    # next insert
                    NonVehicleMaster.objects.create(
                        site_registration = data['No_Penyalur'],
                        no_konsumen = data['ID_Konsumen'],
                        nama = data['Nama'],
                        nik = data['NIK'],
                        alamat=data['Alamat'],
                        sektor_konsumen=sektor_konsumen.id,
                        nama_kapal=data['Nama_Kapal'],
                        jenis_mesin=data['Jenis_Mesin'],
                        jumlah_mesin=data['Jumlah_Mesin'],
                        jumlah_dayaMesin=Jumlah_Daya_Mesin_PK_atau_HP,
                        jam_penggunaan=data['Penggunaan_Mesin_Jam_per_hari'],
                        klasifikasi_gt=data['Klasifikasi_atau_Kapasitas_GT'],
                        lama_operasi=data['Lama_Operasi_hari_per_bulan'],
                        konsumsi_jbt=data['Konsumsi_JBT_Bulan_per_bulan'],
                        alokasi_volume=data['Alokasi_Volume'],
                        tgl_awal_rekom=data['Tanggal_Awal_Surat_Rekomendasi'],
                        tgl_akhir_rekom=data['Tanggal_Akhir_Surat_Rekomendasi'],
                        nomor_surat=data['Nomor_Surat_Rekomendasi'],
                        vehicletype_id = 14,
                        id_product = 51,
                        dokumen_status=False,
                        approved_status = False,
                        disapproved_status = False,
                        inactive_status=True,
                        UploadedBy=request.user.get_full_name(),
                        UploadedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                        ChangedBy=request.user.get_full_name(),
                        ChangedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                        dokumen_name=None,

                        uuid=uuidValue, 
                        uuid_kapal=uuidValue_kapal,
                        badan_usaha=data['Badan_Usaha'],
                        nama_usaha=data['Nama_Usaha'],
                        jenis_bbm=jenis_bbm.id,
                        jenis_usaha=jenis_usaha.id,
                        kode_provinsi=data['Kode_Provinsi'],
                        kode_kabkota=data['Kode_Kabupaten_Kota'],
                        kode_kecamatan=data['Kode_Kecamatan'],
                        kode_keldesa=data['Kode_Kelurahan_Desa'],
                        penerbit=data['Penerbit'],
                        status=status,
                        url_file=url_file,
                        flag_status=flag_status
                    )

                    # update data_release nonTransportasiBph
                    data_nonTransportasiBph.data_release=True
                    data_nonTransportasiBph.save()

                # EMAIL /////////////////////////////////////
                # Calculate total amount for each 'No_Penyalur'
                if data['No_Penyalur'] in total_amount_per_site:
                    total_amount_per_site[data['No_Penyalur']] += 1
                else:
                    total_amount_per_site[data['No_Penyalur']] = 1

                # Get user emails and send emails
                user_mappings = UserSiteMapping.objects.filter(site_registration=data['No_Penyalur'])
                usrnames = list(set([usr.username for usr in user_mappings]))

                email_addresses = []
                for username in usrnames:
                    users = User.objects.filter(username=username)
                    for user in users:
                        email_addresses.append(user.email)

            else:
                # kondisi manual data bph pake kertas ////
                # status -> cek di NonVehicleMaster kalo ada maka status = 4 (update), tidak ada maka status = 2 (insert)
                existing_nonvehicle = NonVehicleMaster.objects.filter(nomor_surat=Nomor_Surat_Rekomendasi, site_registration=No_Penyalur, nik=nik, tgl_awal_rekom=Tanggal_Awal, tgl_akhir_rekom=Tanggal_Akhir, nama_kapal=Nama_Kapal, alokasi_volume=Alokasi_Volume).first()

                if existing_nonvehicle:
                    # update
                    status = 4 # 4 = update data
                    flag_status = None

                    try:
                        Jumlah_Daya_Mesin_PK_atau_HP=float(data['Jumlah_Daya_Mesin_PK_atau_HP'])
                    except:
                        Jumlah_Daya_Mesin_PK_atau_HP=data['Jumlah_Daya_Mesin_PK_atau_HP']

                    # next update data nonvehicle
                    existing_nonvehicle.no_konsumen = data["ID_Konsumen"]
                    existing_nonvehicle.site_registration = data['No_Penyalur']
                    existing_nonvehicle.nama = data['Nama']
                    existing_nonvehicle.nik = data['NIK']
                    existing_nonvehicle.alamat=data['Alamat']

                    sektor_konsumen = SektorKonsumenMaster.objects.get(sektor_konsumen=data['Sektor_Konsumen_Pengguna'])
                    existing_nonvehicle.sektor_konsumen=sektor_konsumen.id

                    existing_nonvehicle.nama_kapal=data['Nama_Kapal']
                    existing_nonvehicle.jenis_mesin=data['Jenis_Mesin']
                    existing_nonvehicle.jumlah_mesin=data['Jumlah_Mesin']
                    existing_nonvehicle.jumlah_dayaMesin=Jumlah_Daya_Mesin_PK_atau_HP
                    existing_nonvehicle.jam_penggunaan=data['Penggunaan_Mesin_Jam_per_hari']
                    existing_nonvehicle.klasifikasi_gt=data['Klasifikasi_atau_Kapasitas_GT']
                    existing_nonvehicle.lama_operasi=data['Lama_Operasi_hari_per_bulan']
                    existing_nonvehicle.konsumsi_jbt=data['Konsumsi_JBT_Bulan_per_bulan']
                    existing_nonvehicle.alokasi_volume=data['Alokasi_Volume']
                    existing_nonvehicle.tgl_awal_rekom=data['Tanggal_Awal_Surat_Rekomendasi']
                    existing_nonvehicle.tgl_akhir_rekom=data['Tanggal_Akhir_Surat_Rekomendasi']
                    existing_nonvehicle.nomor_surat=data['Nomor_Surat_Rekomendasi']

                    existing_nonvehicle.badan_usaha=data['Badan_Usaha']
                    existing_nonvehicle.nama_usaha=data['Nama_Usaha']

                    # get id jenis bbm
                    jenis_bbm = JenisBbmMaster.objects.get(jenis_bbm=data['Jenis_BBM'])
                    existing_nonvehicle.jenis_bbm=jenis_bbm.id

                    # get id jenis usaha
                    jenis_usaha = JenisUsahaMaster.objects.get(jenis_usaha=data['Jenis_Usaha'])
                    existing_nonvehicle.jenis_usaha=jenis_usaha.id

                    existing_nonvehicle.kode_provinsi=data['Kode_Provinsi']
                    existing_nonvehicle.kode_kabkota=data['Kode_Kabupaten_Kota']
                    existing_nonvehicle.kode_kecamatan=data['Kode_Kecamatan']
                    existing_nonvehicle.kode_keldesa=data['Kode_Kelurahan_Desa']
                    existing_nonvehicle.penerbit=data['Penerbit']

                    existing_nonvehicle.status=status
                    existing_nonvehicle.url_file=data_nonTransportasiBph.url_file
                    existing_nonvehicle.flag_status=flag_status

                    existing_nonvehicle.ChangedBy=request.user.get_full_name()
                    existing_nonvehicle.ChangedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    existing_nonvehicle.save()
                else:
                    # buat uuidValue, uuidValue_kapal
                    uuidValue=str(uuid.uuid4())
                    if data['Nama_Kapal'] != None:
                        uuidValue_kapal=str(uuid.uuid4())
                    else:
                        uuidValue_kapal = None
                    flag_status = None
                    url_file = None
                    status = 2
                    jenis_bbm = JenisBbmMaster.objects.get(jenis_bbm=data['Jenis_BBM'])
                    jenis_usaha = JenisUsahaMaster.objects.get(jenis_usaha=data['Jenis_Usaha'])
                    sektor_konsumen = SektorKonsumenMaster.objects.get(sektor_konsumen=data['Sektor_Konsumen_Pengguna'])

                    try:
                        Jumlah_Daya_Mesin_PK_atau_HP=float(data['Jumlah_Daya_Mesin_PK_atau_HP'])
                    except:
                        Jumlah_Daya_Mesin_PK_atau_HP=data['Jumlah_Daya_Mesin_PK_atau_HP']

                    # insert
                    NonVehicleMaster.objects.create(
                        site_registration = data['No_Penyalur'],
                        no_konsumen = data['ID_Konsumen'],
                        nama = data['Nama'],
                        nik = data['NIK'],
                        alamat=data['Alamat'],
                        sektor_konsumen=sektor_konsumen.id,
                        nama_kapal=data['Nama_Kapal'],
                        jenis_mesin=data['Jenis_Mesin'],
                        jumlah_mesin=data['Jumlah_Mesin'],
                        jumlah_dayaMesin=Jumlah_Daya_Mesin_PK_atau_HP,
                        jam_penggunaan=data['Penggunaan_Mesin_Jam_per_hari'],
                        klasifikasi_gt=data['Klasifikasi_atau_Kapasitas_GT'],
                        lama_operasi=data['Lama_Operasi_hari_per_bulan'],
                        konsumsi_jbt=data['Konsumsi_JBT_Bulan_per_bulan'],
                        alokasi_volume=data['Alokasi_Volume'],
                        tgl_awal_rekom=data['Tanggal_Awal_Surat_Rekomendasi'],
                        tgl_akhir_rekom=data['Tanggal_Akhir_Surat_Rekomendasi'],
                        nomor_surat=data['Nomor_Surat_Rekomendasi'],
                        vehicletype_id = 14,
                        id_product = 51,
                        dokumen_status=False,
                        approved_status = False,
                        disapproved_status = False,
                        inactive_status=True,
                        UploadedBy=request.user.get_full_name(),
                        UploadedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                        ChangedBy=request.user.get_full_name(),
                        ChangedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                        dokumen_name=None,

                        uuid=uuidValue, 
                        uuid_kapal=uuidValue_kapal,
                        badan_usaha=data['Badan_Usaha'],
                        nama_usaha=data['Nama_Usaha'],

                        jenis_bbm=jenis_bbm.id,
                        jenis_usaha=jenis_usaha.id,
                        kode_provinsi=data['Kode_Provinsi'],
                        kode_kabkota=data['Kode_Kabupaten_Kota'],
                        kode_kecamatan=data['Kode_Kecamatan'],
                        kode_keldesa=data['Kode_Kelurahan_Desa'],
                        penerbit=data['Penerbit'],
                        status=status,
                        url_file=url_file,
                        flag_status=flag_status
                    )

                # EMAIL /////////////////////////////////////
                # Calculate total amount for each 'No_Penyalur'
                if data['No_Penyalur'] in total_amount_per_site:
                    total_amount_per_site[data['No_Penyalur']] += 1
                else:
                    total_amount_per_site[data['No_Penyalur']] = 1

                # Get user emails and send emails
                user_mappings = UserSiteMapping.objects.filter(site_registration=data['No_Penyalur'])
                usrnames = list(set([usr.username for usr in user_mappings]))

                email_addresses = []
                for username in usrnames:
                    users = User.objects.filter(username=username)
                    for user in users:
                        email_addresses.append(user.email)

        # Create a dictionary to hold email content per site_registration
        email_content_per_site = {}

        # Loop through each site_registration and aggregate data for all usernames
        for site, total_amount in total_amount_per_site.items():
            user_mappings = UserSiteMapping.objects.filter(site_registration=site)
            usernames = list(set([usr.username for usr in user_mappings]))

            # Create a dictionary to hold content per unique combination of No Penyalur, Nama Penyalur, and Jumlah Surat Rekomendasi
            content_per_combination = {}

            # Iterate over usernames and aggregate content
            for username in usernames:
                # Splitting site_registration into typeSpb and site_registration parts
                type_spb, site_registration = site.split(" ")

                # Fetch site_name from SiteMaster based on site_registration
                site_master_entry = SiteMaster.objects.filter(typeSpb=type_spb, site_registration=site_registration).first()
                if site_master_entry:
                    site_name = site_master_entry.site_name
                else:
                    site_name = ""

                # Construct key based on No Penyalur, Nama Penyalur, and Jumlah Surat Rekomendasi
                key = (site, site_name, total_amount)

                # Create or update content for the combination
                if key not in content_per_combination:
                    content_per_combination[key] = {
                        'PICs': set(),
                        'site_registration': site,
                        'site_name': site_name,
                        'total_amount': total_amount
                    }
                content_per_combination[key]['PICs'].add(username)

            # Store content for the site
            email_content_per_site[site] = list(content_per_combination.values())

        # Send emails for each unique site_registration with its aggregated table content
        for site, content_list in email_content_per_site.items():
            subject = 'Knowflow web Notification'

            # Construct email message
            message = f'''
            Dear Bapak/Ibu,
            <br>
            <br>
            Mohon untuk melakukan pengecekan data dan validasi data yang sudah dilengkapi oleh Cabang:
            <br>
            <br>
            <table border='1' style='text-align: center;'>
                <tr><th>PIC</th><th>No Penyalur</th><th>Nama Penyalur</th><th>Jumlah Surat Rekomendasi</th></tr>
                {''.join([f"<tr><td style='vertical-align: middle;'>{', '.join(content['PICs'])}</td><td style='vertical-align: middle;'>{content['site_registration']}</td><td style='vertical-align: middle;'>{content['site_name']}</td><td style='vertical-align: middle;'>{content['total_amount']}</td></tr>" for content in content_list])}
            </table>
            <br>
            Klik link ini untuk membuka data system manager: http://systemmanager.akr.co.id/login
            <br>
            <br>
            Terima Kasih,
            <br>
            This email sent automatically by the system. Do not reply this Email.
            '''

            # kirim email hanya untuk approver
            approvers = User.objects.filter(is_approver=True)
            approver_emails = approvers.values_list('email', flat=True)

            email_message = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                approver_emails,
                cc=['rizky.febrian@akr.co.id']  # Adding CC recipients
            )
            email_message.content_subtype = "html"  # Set content type to HTML

            try:
                email_message.send()
                success_message = f"Submit Berhasil. Email telah terkirim untuk {site}."
                print(success_message)
            except Exception as e:
                error_message = f"Submit Gagal: {e}. Email gagal terkirim untuk {site}."
                print(error_message)


        if request.user.is_superuser:
            return render(request, 'uploadExcelNonkendaraan.html')
        else:
            return render(request, 'uploadExcelNonkendaraan_cabang.html')
