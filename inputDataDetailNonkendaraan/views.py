from django.shortcuts import render
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import json
from django.http import JsonResponse
import uuid

from uploadExcelNonkendaraan.models import NonVehicleMaster
from siteMaster.models import SiteMaster
from dataBph.models import NonTransportasiBPHMigas, JenisBbmMaster, JenisUsahaMaster, SektorKonsumenMaster

def index(request):
    if request.user.is_authenticated:
        sites = SiteMaster.objects.filter(deleted=False)
        jenis_usahalist = JenisUsahaMaster.objects.all()
        sektor_konsumenlist = SektorKonsumenMaster.objects.all()
        jenis_bbmlist = JenisBbmMaster.objects.all()
        if request.user.is_superuser:
            return render(request, 'inputDataDetailNonkendaraan.html',{'sites':sites, 'jenis_usahalist':jenis_usahalist, 'sektor_konsumenlist':sektor_konsumenlist, 'jenis_bbmlist':jenis_bbmlist})
        else:
            return render(request, 'inputDataDetailNonkendaraan_cabang.html',{'sites':sites, 'jenis_usahalist':jenis_usahalist, 'sektor_konsumenlist':sektor_konsumenlist, 'jenis_bbmlist':jenis_bbmlist})
    else:
        return render(request, 'noAccess.html')

def save_non_vehicle_data(request):
    if request.method == 'POST':
        try:
            # Get the JSON data from the request
            data = json.loads(request.body)

            # Assuming data is a list of dictionaries
            for item in data:
                Nomor_Surat_Rekomendasi = item.get('nomor_surat')
                No_Penyalur = item.get('site_registration')
                nik = int(item.get('nik'))
                Tanggal_Awal = item.get('tgl_awalRekom')
                Tanggal_Akhir = item.get('tgl_akhirRekom')
                Nama_Kapal = item.get('nama_kapal')
                Alokasi_Volume = float(item.get('alokasi_volume'))

                # Get uuidValue, uuidValue_kapal, status, url_file
                data_nonTransportasiBph = NonTransportasiBPHMigas.objects.filter(no_surat_rekomendasi=Nomor_Surat_Rekomendasi, nik=nik, tanggal_terbit=Tanggal_Awal, tanggal_berakhir=Tanggal_Akhir, nama_kapal=Nama_Kapal, alokasi_volume=Alokasi_Volume).first()

                if data_nonTransportasiBph: # Kalo datanya ada di NonTransportasiBPHMigas
                    uuidValue = data_nonTransportasiBph.uuid
                    uuidValue_kapal = data_nonTransportasiBph.uuid_kapal

                    existing_nonvehicle = NonVehicleMaster.objects.filter(uuid=uuidValue,uuid_kapal=uuidValue_kapal).first()

                    if existing_nonvehicle:
                        status = data_nonTransportasiBph.status
                        flag_status = 0 # 0 = data ada di bph
                        try:
                            Jumlah_Daya_Mesin_PK_atau_HP=float(item.get('jumlah_dayaMesin'))
                        except:
                            Jumlah_Daya_Mesin_PK_atau_HP=item.get('jumlah_dayaMesin')

                        if status == 5: # jika pencabutan maka langsung inactive tanpa update data lg
                            existing_nonvehicle.status=status
                            existing_nonvehicle.inactive_status=True
                            existing_nonvehicle.save()

                            # update data_release nonTransportasiBph
                            data_nonTransportasiBph.data_release=True
                            data_nonTransportasiBph.save()
                        else:
                            # next update data nonvehicle
                            existing_nonvehicle.no_konsumen = item.get('id_konsumen')
                            existing_nonvehicle.site_registration = item.get('site_registration')
                            existing_nonvehicle.nama = item.get('nama')
                            existing_nonvehicle.nik = int(item.get('nik'))
                            existing_nonvehicle.alamat=item.get('alamat')

                            sektor_konsumen = SektorKonsumenMaster.objects.get(sektor_konsumen=item.get('sektor_konsumen'))
                            existing_nonvehicle.sektor_konsumen=sektor_konsumen.id

                            existing_nonvehicle.nama_kapal=item.get('nama_kapal')
                            existing_nonvehicle.jenis_mesin=item.get('jenis_mesin')
                            existing_nonvehicle.jumlah_mesin=int(item.get('jumlah_mesin'))
                            existing_nonvehicle.jumlah_dayaMesin=Jumlah_Daya_Mesin_PK_atau_HP
                            existing_nonvehicle.jam_penggunaan=int(item.get('jam_penggunaan'))
                            existing_nonvehicle.klasifikasi_gt=int(item.get('klasifikasi_gt')) 
                            existing_nonvehicle.lama_operasi=int(item.get('lama_operasi'))
                            existing_nonvehicle.konsumsi_jbt=float(item.get('konsumsi_jbt'))
                            existing_nonvehicle.alokasi_volume=float(item.get('alokasi_volume'))
                            existing_nonvehicle.tgl_awal_rekom=item.get('tgl_awalRekom')
                            existing_nonvehicle.tgl_akhir_rekom=item.get('tgl_akhirRekom')
                            existing_nonvehicle.nomor_surat=item.get('nomor_surat')

                            existing_nonvehicle.badan_usaha=item.get('badan_usaha')
                            existing_nonvehicle.nama_usaha=item.get('nama_usaha')

                            # get id jenis bbm
                            jenis_bbm = JenisBbmMaster.objects.get(jenis_bbm=item.get('jenis_bbm'))
                            existing_nonvehicle.jenis_bbm=jenis_bbm.id

                            # get id jenis usaha
                            jenis_usaha = JenisUsahaMaster.objects.get(jenis_usaha=item.get('jenis_usaha'))
                            existing_nonvehicle.jenis_usaha=jenis_usaha.id

                            existing_nonvehicle.kode_provinsi=item.get('kode_provinsi')
                            existing_nonvehicle.kode_kabkota=item.get('kode_kabkota')
                            existing_nonvehicle.kode_kecamatan=item.get('kode_kecamatan')
                            existing_nonvehicle.kode_keldesa=item.get('kode_keldesa')
                            existing_nonvehicle.penerbit=item.get('penerbit')

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
                        flag_status = 0 # 0 = ada di bph
                        jenis_bbm = JenisBbmMaster.objects.get(jenis_bbm=item.get('jenis_bbm'))
                        jenis_usaha = JenisUsahaMaster.objects.get(jenis_usaha=item.get('jenis_usaha'))
                        sektor_konsumen = SektorKonsumenMaster.objects.get(sektor_konsumen=item.get('sektor_konsumen'))

                        try:
                            Jumlah_Daya_Mesin_PK_atau_HP=float(item.get('jumlah_dayaMesin'))
                        except:
                            Jumlah_Daya_Mesin_PK_atau_HP=item.get('jumlah_dayaMesin')

                        # next insert
                        NonVehicleMaster.objects.create(
                            site_registration = item.get('site_registration'),
                            no_konsumen = item.get('id_konsumen'),
                            nama = item.get('nama'),
                            nik = int(item.get('nik')),
                            alamat=item.get('alamat'),
                            sektor_konsumen=sektor_konsumen.id,
                            nama_kapal=item.get('nama_kapal'),
                            jenis_mesin=item.get('jenis_mesin'),
                            jumlah_mesin=int(item.get('jumlah_mesin')),
                            jumlah_dayaMesin=Jumlah_Daya_Mesin_PK_atau_HP,
                            jam_penggunaan=int(item.get('jam_penggunaan')),
                            klasifikasi_gt=int(item.get('klasifikasi_gt')) ,
                            lama_operasi=int(item.get('lama_operasi')),
                            konsumsi_jbt=float(item.get('konsumsi_jbt')),
                            alokasi_volume=float(item.get('alokasi_volume')),
                            tgl_awal_rekom=item.get('tgl_awalRekom'),
                            tgl_akhir_rekom=item.get('tgl_akhirRekom'),
                            nomor_surat=item.get('nomor_surat'),
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
                            badan_usaha=item.get('badan_usaha'),
                            nama_usaha=item.get('nama_usaha'),
                            jenis_bbm=jenis_bbm.id,
                            jenis_usaha=jenis_usaha.id,
                            kode_provinsi=item.get('kode_provinsi'),
                            kode_kabkota=item.get('kode_kabkota'),
                            kode_kecamatan=item.get('kode_kecamatan'),
                            kode_keldesa=item.get('kode_keldesa'),
                            penerbit=item.get('penerbit'),
                            status=status,
                            url_file=url_file,
                            flag_status=flag_status
                        )

                        # update data_release nonTransportasiBph
                        data_nonTransportasiBph.data_release=True
                        data_nonTransportasiBph.save()
                else:
                    # kondisi manual data bph pake kertas ////
                    # status -> cek di NonVehicleMaster kalo ada maka status = 4 (update), tidak ada maka status = 2 (insert)
                    existing_nonvehicle = NonVehicleMaster.objects.filter(nomor_surat=Nomor_Surat_Rekomendasi, site_registration=No_Penyalur, nik=nik, tgl_awal_rekom=Tanggal_Awal, tgl_akhir_rekom=Tanggal_Akhir, nama_kapal=Nama_Kapal, alokasi_volume=Alokasi_Volume).first()

                    if existing_nonvehicle:
                        # update
                        status = 4 # 4 = update data
                        flag_status = 1 # 1 = perlu dikirim

                        try:
                            Jumlah_Daya_Mesin_PK_atau_HP=float(item.get('jumlah_dayaMesin'))
                        except:
                            Jumlah_Daya_Mesin_PK_atau_HP=item.get('jumlah_dayaMesin')

                        # next update data nonvehicle
                        existing_nonvehicle.no_konsumen = item.get('id_konsumen')
                        existing_nonvehicle.site_registration = item.get('site_registration')
                        existing_nonvehicle.nama = item.get('nama')
                        existing_nonvehicle.nik = int(item.get('nik'))
                        existing_nonvehicle.alamat=item.get('alamat')

                        sektor_konsumen = SektorKonsumenMaster.objects.get(sektor_konsumen=item.get('sektor_konsumen'))
                        existing_nonvehicle.sektor_konsumen=sektor_konsumen.id

                        existing_nonvehicle.nama_kapal=item.get('nama_kapal')
                        existing_nonvehicle.jenis_mesin=item.get('jenis_mesin')
                        existing_nonvehicle.jumlah_mesin=int(item.get('jumlah_mesin'))
                        existing_nonvehicle.jumlah_dayaMesin=Jumlah_Daya_Mesin_PK_atau_HP
                        existing_nonvehicle.jam_penggunaan=int(item.get('jam_penggunaan'))
                        existing_nonvehicle.klasifikasi_gt=int(item.get('klasifikasi_gt')) 
                        existing_nonvehicle.lama_operasi=int(item.get('lama_operasi'))
                        existing_nonvehicle.konsumsi_jbt=float(item.get('konsumsi_jbt'))
                        existing_nonvehicle.alokasi_volume=float(item.get('alokasi_volume'))
                        existing_nonvehicle.tgl_awal_rekom=item.get('tgl_awalRekom')
                        existing_nonvehicle.tgl_akhir_rekom=item.get('tgl_akhirRekom')
                        existing_nonvehicle.nomor_surat=item.get('nomor_surat')

                        existing_nonvehicle.badan_usaha=item.get('badan_usaha')
                        existing_nonvehicle.nama_usaha=item.get('nama_usaha')

                        # get id jenis bbm
                        jenis_bbm = JenisBbmMaster.objects.get(jenis_bbm=item.get('jenis_bbm'))
                        existing_nonvehicle.jenis_bbm=jenis_bbm.id

                        # get id jenis usaha
                        jenis_usaha = JenisUsahaMaster.objects.get(jenis_usaha=item.get('jenis_usaha'))
                        existing_nonvehicle.jenis_usaha=jenis_usaha.id

                        existing_nonvehicle.kode_provinsi=item.get('kode_provinsi')
                        existing_nonvehicle.kode_kabkota=item.get('kode_kabkota')
                        existing_nonvehicle.kode_kecamatan=item.get('kode_kecamatan')
                        existing_nonvehicle.kode_keldesa=item.get('kode_keldesa')
                        existing_nonvehicle.penerbit=item.get('penerbit')

                        existing_nonvehicle.status=status
                        existing_nonvehicle.url_file=data_nonTransportasiBph.url_file
                        existing_nonvehicle.flag_status=flag_status

                        existing_nonvehicle.ChangedBy=request.user.get_full_name()
                        existing_nonvehicle.ChangedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        existing_nonvehicle.save()
                    else:
                        # buat uuidValue, uuidValue_kapal
                        uuidValue=str(uuid.uuid4())
                        if item.get('nama_kapal') != "":
                            uuidValue_kapal=str(uuid.uuid4())
                        else:
                            uuidValue_kapal = None
                        flag_status = 1 # (1 perlu dikirim)
                        url_file = None
                        status = 2
                        jenis_bbm = JenisBbmMaster.objects.get(jenis_bbm=item.get('jenis_bbm'))
                        jenis_usaha = JenisUsahaMaster.objects.get(jenis_usaha=item.get('jenis_usaha'))
                        sektor_konsumen = SektorKonsumenMaster.objects.get(sektor_konsumen=item.get('sektor_konsumen'))

                        try:
                            Jumlah_Daya_Mesin_PK_atau_HP=float(item.get('jumlah_dayaMesin'))
                        except:
                            Jumlah_Daya_Mesin_PK_atau_HP=item.get('jumlah_dayaMesin')

                        # insert
                        NonVehicleMaster.objects.create(
                            site_registration = item.get('site_registration'),
                            no_konsumen = item.get('id_konsumen'),
                            nama = item.get('nama'),
                            nik = int(item.get('nik')),
                            alamat=item.get('alamat'),
                            sektor_konsumen=sektor_konsumen.id,
                            nama_kapal=item.get('nama_kapal'),
                            jenis_mesin=item.get('jenis_mesin'),
                            jumlah_mesin=int(item.get('jumlah_mesin')),
                            jumlah_dayaMesin=Jumlah_Daya_Mesin_PK_atau_HP,
                            jam_penggunaan=int(item.get('jam_penggunaan')),
                            klasifikasi_gt=int(item.get('klasifikasi_gt')) ,
                            lama_operasi=int(item.get('lama_operasi')),
                            konsumsi_jbt=float(item.get('konsumsi_jbt')),
                            alokasi_volume=float(item.get('alokasi_volume')),
                            tgl_awal_rekom=item.get('tgl_awalRekom'),
                            tgl_akhir_rekom=item.get('tgl_akhirRekom'),
                            nomor_surat=item.get('nomor_surat'),
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
                            badan_usaha=item.get('badan_usaha'),
                            nama_usaha=item.get('nama_usaha'),

                            jenis_bbm=jenis_bbm.id,
                            jenis_usaha=jenis_usaha.id,
                            kode_provinsi=item.get('kode_provinsi'),
                            kode_kabkota=item.get('kode_kabkota'),
                            kode_kecamatan=item.get('kode_kecamatan'),
                            kode_keldesa=item.get('kode_keldesa'),
                            penerbit=item.get('penerbit'),
                            status=status,
                            url_file=url_file,
                            flag_status=flag_status
                        )

            return JsonResponse({'message': 'Data saved successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'message': 'Invalid request method'}, status=405)
