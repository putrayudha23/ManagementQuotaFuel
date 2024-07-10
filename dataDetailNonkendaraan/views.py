from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import os
from django.http import Http404, HttpResponse, FileResponse
from django.conf import settings
from django.http import JsonResponse
import pandas as pd
from django.db.models import Q
from datetime import datetime
import json
from django.core.mail import EmailMessage

from uploadExcelNonkendaraan.models import NonVehicleMaster, ViewNonVehicleMaster
from siteMaster.models import SiteMaster
from dataBph.models import JenisBbmMaster, JenisUsahaMaster, SektorKonsumenMaster
from dataBph.models import NonTransportasiBPHMigas
from userSetting.models import UserSiteMapping
from django.contrib.auth.models import User
from transactionNonkendaraan.models import nonVehicleTransaction


def index(request):
    if request.user.is_authenticated:
        sites = SiteMaster.objects.filter(deleted=False)
        unique_provinces = SiteMaster.objects.filter(deleted=False).values('provinsi').distinct()
        current_date = datetime.now().date()
        jenis_usahalist = JenisUsahaMaster.objects.all()
        sektor_konsumenlist = SektorKonsumenMaster.objects.all()
        jenis_bbmlist = JenisBbmMaster.objects.all()

        if request.method == 'POST':
            search_logic = request.POST.get('searchLogic')
            query = Q()
            no_penyalur = request.POST.get('searchNoPenyalur')
            sektor_konsumen = request.POST.get('searchSektor')
            provinsi = request.POST.get('searchProvinsi')
            status = request.POST.get('searchStatus')
            search_month_year = request.POST.get('searchMonthYear')

            if provinsi == 'All' and no_penyalur == 'All':
                # Get all data
                query = Q()

            elif provinsi != 'All' and no_penyalur != 'All':
                # Filter by Provinsi
                query = Q(site_registration=no_penyalur)

            elif provinsi != 'All' and no_penyalur == 'All':
                # Retrieve [typeSpb] and [site_registration] based on provinsi
                # Assuming SiteMaster is your model
                penyalur_data = SiteMaster.objects.filter(provinsi=provinsi).values_list('typeSpb', 'site_registration')

                # Construct list_penyalur string
                list_penyalur = ', '.join([f"{penyalur[0]} {penyalur[1]}" for penyalur in penyalur_data if all(penyalur)])

                # Splitting the list_penyalur string into individual values
                individual_penyalur = list_penyalur.split(', ')

                # Creating a Q object with OR conditions for each value
                q_objects = Q()
                for penyalur in individual_penyalur:
                    q_objects |= Q(site_registration__icontains=penyalur)

                # Applying AND logic to the Q objects
                query = q_objects

            # Add Sector filter
            if sektor_konsumen:
                if search_logic == 'AND':
                    query &= Q(sektor_konsumen=sektor_konsumen)
                else:  # search_logic == 'OR'
                    query |= Q(sektor_konsumen=sektor_konsumen)

            # Add Sector filter
            if status:
                if search_logic == 'AND':
                    if status == "Perlu Validasi":
                        query &= Q(approved_status=False, disapproved_status=False)
                    elif status == "Approved":
                        query &= Q(approved_status=True)
                    elif status == "Rejected":
                        query &= Q(disapproved_status=True)
                else:  # search_logic == 'OR'
                    if status == "Perlu Validasi":
                        query |= Q(approved_status=False, disapproved_status=False)
                    elif status == "Approved":
                        query |= Q(approved_status=True)
                    elif status == "Rejected":
                        query |= Q(disapproved_status=True)

            # Add Month filter
            if search_month_year:
                if search_logic == 'AND':
                    year, month = search_month_year.split('-')
                    month = int(month)
                    year = int(year)
                    query &= Q(tgl_akhir_rekom__month=month, tgl_akhir_rekom__year=year)
                else:  # search_logic == 'OR'
                    year, month = search_month_year.split('-')
                    month = int(month)
                    year = int(year)
                    query |= Q(tgl_akhir_rekom__month=month, tgl_akhir_rekom__year=year)

            data = ViewNonVehicleMaster.objects.filter(query).order_by('ChangedDate') # dari baru -> lama '-ChangedDate'
            paginator = Paginator(data, 500)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'page_obj': page_obj, 'sites':sites, 'unique_provinces':unique_provinces,'current_date':current_date, 'jenis_usahalist':jenis_usahalist, 'sektor_konsumenlist':sektor_konsumenlist, 'jenis_bbmlist':jenis_bbmlist}
            
            if request.user.is_superuser == True and request.user.is_approver == True:
                return render(request, 'dataDetailNonkendaraan_approver.html', context)
            elif request.user.is_superuser == True and request.user.is_approver == False:
                return render(request, 'dataDetailNonkendaraan.html', context)
            elif request.user.is_superuser == False and request.user.is_approver == True:
                return render(request, 'dataDetailNonkendaraan_cabangApprover.html', context)
            elif request.user.is_superuser == False and request.user.is_approver == False:
                return render(request, 'dataDetailNonkendaraan_cabang.html', context)

        else:
            data = ViewNonVehicleMaster.objects.filter(approved_status=False, disapproved_status=False).order_by('ChangedDate') # dari baru -> lama '-ChangedDate'
            paginator = Paginator(data, 100)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'page_obj': page_obj, 'sites':sites, 'unique_provinces':unique_provinces, 'current_date':current_date, 'jenis_usahalist':jenis_usahalist, 'sektor_konsumenlist':sektor_konsumenlist, 'jenis_bbmlist':jenis_bbmlist}

            if request.user.is_superuser == True and request.user.is_approver == True:
                return render(request, 'dataDetailNonkendaraan_approver.html', context)
            elif request.user.is_superuser == True and request.user.is_approver == False:
                return render(request, 'dataDetailNonkendaraan.html', context)
            elif request.user.is_superuser == False and request.user.is_approver == True:
                return render(request, 'dataDetailNonkendaraan_cabangApprover.html', context)
            elif request.user.is_superuser == False and request.user.is_approver == False:
                return render(request, 'dataDetailNonkendaraan_cabang.html', context)
    else:
        return render(request, 'noAccess.html')
    
def view_file(request, filename):
    try:
        # Define a dictionary to map file extensions to content types
        content_type_mapping = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }

        # Extract the file extension from the filename
        file_extension = filename.split('.')[-1].lower()

        # Check if the file extension is in the mapping
        if file_extension in content_type_mapping:
            # Construct the file path
            file_path = os.path.join(settings.MEDIA_ROOT, 'RekomDokumen_Nontransportasi', filename)

            # Check if the file exists
            if os.path.exists(file_path):
                # Open the file and read its content
                with open(file_path, 'rb') as file:
                    file_data = file.read()

                # Set the content type based on the file extension
                content_type = content_type_mapping[file_extension]

                # Check if it's a doc, DOC, docx, or DOCX file
                if file_extension in ['doc', 'docx']:
                    response = HttpResponse(file_data, content_type=content_type)
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response
                else:
                    # For other file types, open in the browser
                    return HttpResponse(file_data, content_type=content_type)
            else:
                raise Http404("File not found")
        else:
            raise Http404("File type not supported")
    except Http404:
        return custom_404(request, Http404)
    
def custom_404(request, exception):
    return render(request, '404.html', status=404)

def delete(request, delete_id):
    nv = NonVehicleMaster.objects.get(id=delete_id)
    if nv.inactive_status == False and nv.approved_status == True:
        inactive_value = True
        approved_value = False
        disapproved_value = True
    elif nv.inactive_status == True and nv.disapproved_status == True:
        inactive_value = False
        approved_value = True
        disapproved_value = False
    elif nv.inactive_status == True and nv.approved_status == False and nv.disapproved_status == False:
        inactive_value = True
        approved_value = False
        disapproved_value = True
    nv.inactive_status = inactive_value
    nv.approved_status = approved_value
    nv.disapproved_status = disapproved_value
    nv.ChangedBy = request.user.get_full_name()
    nv.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    nv.save()

    # Delete data in nonVehicleTransaction where no_konsumen=nv.no_konsumen
    nonVehicleTransaction.objects.filter(no_konsumen=nv.no_konsumen).delete()

    # Redirect to the same page to show the updated data
    data = NonVehicleMaster.objects.all()
    return redirect('dataDetailNonkendaraan:index')

def update_non_vehicle(request, row_id):
    if request.method == 'POST':
        # Retrieve the instance based on the row_id
        try:
            non_vehicle_instance = NonVehicleMaster.objects.get(id=row_id)
        except NonVehicleMaster.DoesNotExist:
            # Handle the case where the instance with the given ID doesn't exist
            return JsonResponse({'success': False, 'message': 'Instance not found'})

        # Update all fields based on the form data
        non_vehicle_instance.no_konsumen = request.POST.get('entryNoPenyalur')
        non_vehicle_instance.site_registration = request.POST.get('entryIdKonsumen')
        non_vehicle_instance.nama = request.POST.get('entryNama')
        non_vehicle_instance.nik = request.POST.get('entryNik')
        non_vehicle_instance.alamat = request.POST.get('entryAlamat')

        sektor_konsumen = SektorKonsumenMaster.objects.get(sektor_konsumen=request.POST.get('entrySektor'))
        non_vehicle_instance.sektor_konsumen = sektor_konsumen.id

        non_vehicle_instance.nama_kapal = request.POST.get('entryNamaKapal')
        non_vehicle_instance.jenis_mesin = request.POST.get('entryJenisMesin')
        non_vehicle_instance.jumlah_mesin = request.POST.get('entryJumlahMesin')
        non_vehicle_instance.jumlah_dayaMesin = request.POST.get('entryJumlahDayaMesin')
        non_vehicle_instance.jam_penggunaan = request.POST.get('entryJamPerHari')
        non_vehicle_instance.klasifikasi_gt = request.POST.get('entryKlasifikasiKapasitasGT')
        non_vehicle_instance.lama_operasi = request.POST.get('entryLamaOperasi')
        non_vehicle_instance.konsumsi_jbt = request.POST.get('entryKonsumsiJbt')
        non_vehicle_instance.alokasi_volume = request.POST.get('entryAlokasiKuota')
        non_vehicle_instance.tgl_awal_rekom = request.POST.get('entryTanggalAwalRekomendasi')
        non_vehicle_instance.tgl_akhir_rekom = request.POST.get('entryTanggalAkhirRekomendasi')
        non_vehicle_instance.nomor_surat = request.POST.get('entryNoSuratRekom')

        non_vehicle_instance.badan_usaha = request.POST.get('entryBadanUsaha')
        non_vehicle_instance.nama_usaha = request.POST.get('entryNamaUsaha')

        jenis_bbm = JenisBbmMaster.objects.get(jenis_bbm=request.POST.get('entryJenisBbm'))
        non_vehicle_instance.jenis_bbm = jenis_bbm.id
        jenis_usaha = JenisUsahaMaster.objects.get(jenis_usaha=request.POST.get('entryJenisUsaha'))
        non_vehicle_instance.jenis_usaha = jenis_usaha.id

        non_vehicle_instance.kode_provinsi = request.POST.get('entryKodeProvinsi')
        non_vehicle_instance.kode_kabkota = request.POST.get('entryKodeKabKota')
        non_vehicle_instance.kode_kecamatan = request.POST.get('entryKodeKecamatan')
        non_vehicle_instance.kode_keldesa = request.POST.get('entryKodeKelDesa')
        non_vehicle_instance.penerbit = request.POST.get('entryPenerbit')

        non_vehicle_instance.ChangedBy = request.user.get_full_name()
        non_vehicle_instance.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        # Save the instance to persist the changes
        non_vehicle_instance.save()

        return JsonResponse({'success': True, 'message': 'Instance updated successfully'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def export_data_to_excel(request):
    # Define a custom header
    field_labels = {
        'no_konsumen': 'ID Konsumen',
        'site_registration': 'No Penyalur',
        'nama': 'Nama',
        'nik': 'NIK',
        'alamat': 'Alamat',

        'sektor_konsumen_desc': 'Sektor Konsumen Pengguna',

        'nama_kapal': 'Nama Kapal',
        'jenis_mesin': 'Jenis Mesin',
        'jumlah_mesin': 'Jumlah Mesin',
        'jumlah_dayaMesin': 'Jumlah Daya Mesin (PK)',
        'jam_penggunaan': 'Jam Penggunaan Mesin per hari',
        'klasifikasi_gt': 'Klasifikasi/Kapasitas GT',
        'lama_operasi': 'Lama Operasi (hari per bulan)',
        'konsumsi_jbt': 'Konsumsi JBT (Bulan)',
        'alokasi_volume': 'Alokasi Volume',
        'tgl_awal_rekom': 'Tanggal Awal Surat Rekomendasi',
        'tgl_akhir_rekom': 'Tanggal Akhir Surat Rekomendasi',
        'nomor_surat': 'Nomor Surat Rekomendasi',

        'badan_usaha': 'Badan Usaha',
        'nama_usaha': 'Nama Usaha',

        'jenis_bbm_desc': 'Jenis BBM',
        'jenis_usaha_desc': 'Jenis Usaha',
        'kode_provinsi': 'Kode Provinsi',
        'kode_kabkota': 'Kode Kabupaten Kota',
        'kode_kecamatan': 'Kode Kecamatan',
        'kode_keldesa': 'Kode Kelurahan Desa',
        'penerbit': 'Penerbit',
    }

    # Retrieve data from the NONVEHICLEMASTER model, excluding certain columns
    data = ViewNonVehicleMaster.objects.values(
        'no_konsumen', 'site_registration', 'nama', 'nik', 'alamat', 'sektor_konsumen_desc',
        'nama_kapal', 'jenis_mesin', 'jumlah_mesin', 'jumlah_dayaMesin', 'jam_penggunaan',
        'klasifikasi_gt', 'lama_operasi', 'konsumsi_jbt', 'alokasi_volume',
        'tgl_awal_rekom', 'tgl_akhir_rekom', 'nomor_surat', 'badan_usaha', 'nama_usaha',
        'jenis_bbm_desc', 'jenis_usaha_desc', 'kode_provinsi', 'kode_kabkota', 'kode_kecamatan',
        'kode_keldesa', 'penerbit',
    )

    # Create a Pandas DataFrame from the data
    df = pd.DataFrame(data)

    # Rename the columns using the custom header
    df = df.rename(columns=field_labels)

    # Create a response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="non_vehicle_data.xlsx"'

    # Save the DataFrame to an Excel file and write it to the response
    df.to_excel(response, index=False)

    return response

def update_approved_status(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        selected_row_ids_checked = data.get("selectedRowIdsChecked")
        selected_row_ids_unchecked = data.get("selectedRowIdsUnchecked")

        for row_id in selected_row_ids_checked:
            non_vehicle = NonVehicleMaster.objects.get(id=row_id)
            if non_vehicle:
                # Check if the data exists in NonTransportasiBPHMigas
                if NonTransportasiBPHMigas.objects.filter(
                    uuid=non_vehicle.uuid,
                    uuid_kapal=non_vehicle.uuid_kapal,
                    nik=non_vehicle.nik,
                    site_registration=non_vehicle.site_registration
                ).exists():
                    # set flag_status = 0 (data ada di bph)
                    non_vehicle.flag_status = 0
                    non_vehicle.approved_status = True
                    non_vehicle.disapproved_status = False
                    non_vehicle.inactive_status = False
                    non_vehicle.ChangedBy = request.user.get_full_name()
                    non_vehicle.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    non_vehicle.save()
                else:
                    # set flag_status = 1 (data tidak ada di bph)
                    non_vehicle.flag_status = 1
                    non_vehicle.approved_status = True
                    non_vehicle.disapproved_status = False
                    non_vehicle.inactive_status = False
                    non_vehicle.ChangedBy = request.user.get_full_name()
                    non_vehicle.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    non_vehicle.save()

        # ini untuk data yang di uncheck. INI TIDAK DIGUNAKAN
        for row_id in selected_row_ids_unchecked:
            non_vehicle = NonVehicleMaster.objects.get(id=row_id)
            if non_vehicle:
                non_vehicle.approved_status = False
                non_vehicle.disapproved_status = False
                non_vehicle.inactive_status = True
                non_vehicle.ChangedBy = request.user.get_full_name()
                non_vehicle.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                non_vehicle.save()

        return JsonResponse({"message": "Status updated successfully"})
    return JsonResponse({"message": "Invalid request method"}, status=400)

# def update_disapproved_status(request):
#     if request.method == "POST":
#         data = json.loads(request.body.decode("utf-8"))
#         selected_row_ids_checked = data.get("selectedRowIdsChecked")
#         selected_row_ids_unchecked = data.get("selectedRowIdsUnchecked")

#         # update status rejectnya
#         for row_id in selected_row_ids_checked:
#             non_vehicle = NonVehicleMaster.objects.get(id=row_id)
#             if non_vehicle:
#                 non_vehicle.disapproved_status = True
#                 non_vehicle.approved_status = False
#                 non_vehicle.inactive_status = True
#                 non_vehicle.ChangedBy = request.user.get_full_name()
#                 non_vehicle.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
#                 non_vehicle.save()

#         # # count site_registration
#         # total_amount_per_site = {}
#         # for row_id in selected_row_ids_checked:
#         #     non_vehicle = NonVehicleMaster.objects.get(id=row_id)
#         #     # get site_registration and count save count in total_amount_per_site = {}
#         #     if non_vehicle.site_registration in total_amount_per_site:
#         #         total_amount_per_site[non_vehicle.site_registration] += 1
#         #     else:
#         #         total_amount_per_site[non_vehicle.site_registration] = 1

#         # count site_registration and keep track of nomor_surat
#         total_amount_per_site = {}
#         for row_id in selected_row_ids_checked:
#             non_vehicle = NonVehicleMaster.objects.get(id=row_id)
            
#             # get site_registration and nomor_surat
#             site_registration = non_vehicle.site_registration
#             nomor_surat = non_vehicle.nomor_surat
            
#             # check if site_registration is already in the dictionary
#             if site_registration in total_amount_per_site:
#                 total_amount_per_site[site_registration]['count'] += 1
#                 total_amount_per_site[site_registration]['nomor_surat'].append(nomor_surat)
#             else:
#                 # if site_registration is not in the dictionary, add it
#                 total_amount_per_site[site_registration] = {'count': 1, 'nomor_surat': [nomor_surat]}

#         # Create a dictionary to hold email content per username
#         email_content_per_username = {}

#         # Loop through each site_registration and aggregate data for each username
#         for site, total_amount in total_amount_per_site.items():
#             user_mappings = UserSiteMapping.objects.filter(site_registration=site)
#             usrnames = list(set([usr.username for usr in user_mappings]))

#             for username in usrnames:
#                 if username not in email_content_per_username:
#                     email_content_per_username[username] = {
#                         'table_content': "",
#                         'email_addresses': [],
#                     }
#                 email_content_per_username[username]['email_addresses'].extend(
#                     [user.email for user in User.objects.filter(username=username)]
#                 )

#                 # Splitting site_registration into typeSpb and site_registration parts
#                 type_spb, site_registration = site.split(" ")

#                 # Fetch site_name from SiteMaster based on site_registration
#                 site_master_entry = SiteMaster.objects.filter(typeSpb=type_spb, site_registration=site_registration).first()
#                 if site_master_entry:
#                     site_name = site_master_entry.site_name
#                     # Include nomor_surat in table_content
#                     nomor_surat_list = total_amount_per_site[site]['nomor_surat']
#                     nomor_surat_content = "<br>".join(nomor_surat_list)
#                     # email_content_per_username[username]['table_content'] += f"<tr><td><center>{username}</center></td><td><center>{site}</center></td><td><center>{site_name}</center></td><td><center>{total_amount['count']}</center></td><td><center>{nomor_surat_content}</center></td></tr>"
#                     email_content_per_username[username]['table_content'] += f"<tr><td><center>{username}</center></td><td><center>{site}</center></td><td><center>{site_name}</center></td><td><center>{nomor_surat_content}</center></td></tr>"
#                 else:
#                     site_name = ""
#                     # email_content_per_username[username]['table_content'] += f"<tr><td><center>{username}</center></td><td><center>{site}</center></td><td><center>{site_name}</center></td><td><center>{total_amount['count']}</center></td><td></td></tr>"
#                     email_content_per_username[username]['table_content'] += f"<tr><td><center>{username}</center></td><td><center>{site}</center></td><td><center>{site_name}</center></td><td><center>{nomor_surat_content}</center></td></tr>"

#         # Send emails for each unique username with its aggregated table content
#         for username, email_content in email_content_per_username.items():
#             subject = 'Knowflow web Notification'
#             # table_content = f"<table border='1'><tr><th>PIC</th><th>No Penyalur</th><th>Nama Penyalur</th><th>Jumlah Surat Rekomendasi</th><th>Nomor Surat</th></tr>{email_content['table_content']}</table>"
#             table_content = f"<table border='1'><tr><th>PIC</th><th>No Penyalur</th><th>Nama Penyalur</th><th>Nomor Surat</th></tr>{email_content['table_content']}</table>"
#             email_addresses = email_content['email_addresses']

#             # Construct email message
#             message = f'''
#             Dear Bapak/Ibu,
#             <br>
#             <br>
#             Berikut data yang di-reject, mohon untuk ditinjau kembali
#             <br>
#             <br>
#             {table_content}
#             <br>
#             Klik link ini untuk membuka data system manager: http://systemmanager.akr.co.id/login
#             <br>
#             <br>
#             Terima Kasih,
#             <br>
#             This email sent automatically by system. Do not reply this Email.
#             '''

#             email_message = EmailMessage(
#                 subject,
#                 message,
#                 settings.EMAIL_HOST_USER,
#                 email_addresses,
#                 cc=['putra.pranata@akr.co.id']  # Adding CC recipients
#             )
#             email_message.content_subtype = "html"  # Set content type to HTML

#             try:
#                 email_message.send()
#                 success_message = f"Reject Berhasil. Email telah terkirim untuk {username}."
#                 print(success_message)
#             except Exception as e:
#                 error_message = f"Reject Gagal: {e}. Email gagal terkirim untuk {username}."
#                 print(error_message)

#         # for row_id in selected_row_ids_unchecked:
#         #     non_vehicle = NonVehicleMaster.objects.get(id=row_id)
#         #     if non_vehicle:
#         #         non_vehicle.disapproved_status = False
#         #         non_vehicle.approved_status = False
#         #         non_vehicle.inactive_status = True
#         #         non_vehicle.ChangedBy = request.user.get_full_name()
#         #         non_vehicle.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
#         #         non_vehicle.save()

#         return JsonResponse({"message": "Status updated successfully"})
#     return JsonResponse({"message": "Invalid request method"}, status=400)

def update_disapproved_status(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        selected_row_ids_checked = data.get("selectedRowIdsChecked")
        selected_row_ids_unchecked = data.get("selectedRowIdsUnchecked")

        # update status rejectnya
        for row_id in selected_row_ids_checked:
            non_vehicle = NonVehicleMaster.objects.get(id=row_id)
            if non_vehicle:
                non_vehicle.disapproved_status = True
                non_vehicle.approved_status = False
                non_vehicle.inactive_status = True
                non_vehicle.ChangedBy = request.user.get_full_name()
                non_vehicle.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                non_vehicle.save()

        # # count site_registration
        # total_amount_per_site = {}
        # for row_id in selected_row_ids_checked:
        #     non_vehicle = NonVehicleMaster.objects.get(id=row_id)
        #     # get site_registration and count save count in total_amount_per_site = {}
        #     if non_vehicle.site_registration in total_amount_per_site:
        #         total_amount_per_site[non_vehicle.site_registration] += 1
        #     else:
        #         total_amount_per_site[non_vehicle.site_registration] = 1

        # count site_registration and keep track of nomor_surat
        total_amount_per_site = {}
        for row_id in selected_row_ids_checked:
            non_vehicle = NonVehicleMaster.objects.get(id=row_id)
            
            # get site_registration and nomor_surat
            site_registration = non_vehicle.site_registration
            nomor_surat = non_vehicle.nomor_surat
            
            # check if site_registration is already in the dictionary
            if site_registration in total_amount_per_site:
                total_amount_per_site[site_registration]['count'] += 1
                total_amount_per_site[site_registration]['nomor_surat'].append(nomor_surat)
            else:
                # if site_registration is not in the dictionary, add it
                total_amount_per_site[site_registration] = {'count': 1, 'nomor_surat': [nomor_surat]}

        # Create a dictionary to hold email content per username
        email_content_per_username = {}

        # Loop through each site_registration and aggregate data for each username
        for site, total_amount in total_amount_per_site.items():
            user_mappings = UserSiteMapping.objects.filter(site_registration=site)
            usrnames = list(set([usr.username for usr in user_mappings]))

            for username in usrnames:
                if username not in email_content_per_username:
                    email_content_per_username[username] = {
                        'table_content': "",
                        'email_addresses': [],
                    }
                email_content_per_username[username]['email_addresses'].extend(
                    [user.email for user in User.objects.filter(username=username)]
                )

                # Splitting site_registration into typeSpb and site_registration parts
                type_spb, site_registration = site.split(" ")

                # Fetch site_name from SiteMaster based on site_registration
                site_master_entry = SiteMaster.objects.filter(typeSpb=type_spb, site_registration=site_registration).first()
                if site_master_entry:
                    site_name = site_master_entry.site_name
                    # Include nomor_surat in table_content
                    nomor_surat_list = total_amount_per_site[site]['nomor_surat']
                    nomor_surat_content = "<br>".join(nomor_surat_list)
                    # email_content_per_username[username]['table_content'] += f"<tr><td><center>{username}</center></td><td><center>{site}</center></td><td><center>{site_name}</center></td><td><center>{total_amount['count']}</center></td><td><center>{nomor_surat_content}</center></td></tr>"
                    email_content_per_username[username]['table_content'] += f"<tr><td><center>{username}</center></td><td><center>{site}</center></td><td><center>{site_name}</center></td><td><center>{nomor_surat_content}</center></td></tr>"
                else:
                    site_name = ""
                    # email_content_per_username[username]['table_content'] += f"<tr><td><center>{username}</center></td><td><center>{site}</center></td><td><center>{site_name}</center></td><td><center>{total_amount['count']}</center></td><td></td></tr>"
                    email_content_per_username[username]['table_content'] += f"<tr><td><center>{username}</center></td><td><center>{site}</center></td><td><center>{site_name}</center></td><td><center>{nomor_surat_content}</center></td></tr>"

        # Send emails for each unique username with its aggregated table content
        for username, email_content in email_content_per_username.items():
            subject = 'Knowflow web Notification'
            # table_content = f"<table border='1'><tr><th>PIC</th><th>No Penyalur</th><th>Nama Penyalur</th><th>Jumlah Surat Rekomendasi</th><th>Nomor Surat</th></tr>{email_content['table_content']}</table>"
            table_content = f"<table border='1'><tr><th>PIC</th><th>No Penyalur</th><th>Nama Penyalur</th><th>Nomor Surat</th></tr>{email_content['table_content']}</table>"
            email_addresses = email_content['email_addresses']

            # Construct email message
            message = f'''
            Dear Bapak/Ibu,
            <br>
            <br>
            Berikut data yang di-reject, mohon untuk ditinjau kembali
            <br>
            <br>
            {table_content}
            <br>
            Klik link ini untuk membuka data system manager: http://systemmanager.akr.co.id/login
            <br>
            <br>
            Terima Kasih,
            <br>
            This email sent automatically by system. Do not reply this Email.
            '''

            email_message = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                email_addresses,
                cc=['putra.pranata@akr.co.id']  # Adding CC recipients
            )
            email_message.content_subtype = "html"  # Set content type to HTML

            try:
                email_message.send()
                success_message = f"Reject Berhasil. Email telah terkirim untuk {username}."
                print(success_message)
            except Exception as e:
                error_message = f"Reject Gagal: {e}. Email gagal terkirim untuk {username}."
                print(error_message)

        # for row_id in selected_row_ids_unchecked:
        #     non_vehicle = NonVehicleMaster.objects.get(id=row_id)
        #     if non_vehicle:
        #         non_vehicle.disapproved_status = False
        #         non_vehicle.approved_status = False
        #         non_vehicle.inactive_status = True
        #         non_vehicle.ChangedBy = request.user.get_full_name()
        #         non_vehicle.ChangedDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        #         non_vehicle.save()

        # delete data from NonVehicleMaster
        for row_id in selected_row_ids_checked:
            try:
                non_vehicle = NonVehicleMaster.objects.get(id=row_id)
                if non_vehicle:
                    non_vehicle.delete()
            except NonVehicleMaster.DoesNotExist:
                continue

        return JsonResponse({"message": "Status updated successfully"})
    return JsonResponse({"message": "Invalid request method"}, status=400)
