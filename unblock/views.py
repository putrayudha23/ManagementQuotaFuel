from django.shortcuts import render, redirect
from datetime import datetime
from django.core.paginator import Paginator

from vehicleMaster.models import VehicleTypeMaster, LogVehicleTypeMaster, VehicleMasterView

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        data = VehicleMasterView.objects.filter(block=True).order_by('-ChangedDate')
        # get site user
        username = request.user.username
        allowed_usernames = ['rizky.febrian', 'jaka.brahmana']

        if request.method == 'POST':
            
            if 'number_plat_search' in request.POST:
                number_plat = request.POST['number_plat_search']
                if len(number_plat) != 0:
                    data = VehicleMasterView.objects.filter(number_plat=number_plat, block=True)
                else:
                    data = VehicleMasterView.objects.filter(block=True).order_by('-ChangedDate')

        paginator = Paginator(data, 100)  # Show 10 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj}
        if request.user.is_superuser:
            return render(request, 'unblock.html', context)
        else:
            if username in allowed_usernames:
                return render(request, 'unblock_cabang.html', context)
            else:
                return render(request, 'noAccess.html')
    else:
        return render(request, 'noAccess.html')
    
def unblock(request, unblock_id):
    st = VehicleTypeMaster.objects.get(RowID=unblock_id)
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
    return redirect('unblock:index')