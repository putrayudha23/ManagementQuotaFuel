from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from vehicleTypeMaster.models import VehicleType
from siteMaster.models import SiteMaster
from productMaster.models import Product
from kuotaMaster.models import Quota

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        data = Quota.objects.all()

        if request.method == 'POST':
            if 'site_registration' in request.POST:
                site_registration = request.POST['site_registration']
                if len(site_registration) != 0:
                    data = Quota.objects.filter(site_registration=site_registration)
                else:
                    data = Quota.objects.all()

            if "site_name" in request.POST and "provinsi_hidden" in request.POST and "site_regis_hidden" in request.POST and "id_modify" in request.POST:
                site_name = request.POST['site_name']
                provinsi = request.POST['provinsi_hidden']
                site_regis = request.POST['site_regis_hidden']
                vehicletype_id = request.POST['vehicle_type']
                volume_quota = request.POST['volume_quota']
                frequency_quota = request.POST['frequency_quota']
                id_product = request.POST['product_name']
                id_modify = request.POST['id_modify']
                deleted = False

                if id_modify == "":
                    #submit
                    Quota.objects.create(site_name=site_name, provinsi=provinsi, site_registration=site_regis, deleted=deleted,vehicletype_id=vehicletype_id, volume_quota=volume_quota, frequency_quota=frequency_quota, id_product=id_product)
                    data = Quota.objects.all()
                else:
                    #modify
                    id = request.POST['id_modify']
                    kt = Quota.objects.get(id=id)
                    kt.site_name = request.POST.get('site_name')
                    kt.provinsi = request.POST.get('provinsi_hidden')
                    kt.site_registration = request.POST.get('site_regis_hidden')
                    kt.vehicletype_id = request.POST.get('vehicle_type')
                    kt.volume_quota = request.POST.get('volume_quota')
                    kt.frequency_quota = request.POST.get('frequency_quota')
                    kt.id_product = request.POST.get('product_name')
                    kt.save()
                    data = Quota.objects.filter(id=id)

        vehicle_types = VehicleType.objects.filter(deleted=False)
        sites = SiteMaster.objects.filter(deleted=False)
        products = Product.objects.filter(deleted=False)

        paginator = Paginator(data, 10)  # Show 5 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'page_obj': page_obj, 'vehicle_types': vehicle_types, 'sites':sites, 'products':products}
        if request.user.is_superuser:
            return render(request, 'kuotaMaster.html', context)
        else:
            return render(request, 'noAccess_app.html')
    else:
        return render(request, 'noAccess.html')

def delete(request, delete_id):
    st = Quota.objects.get(id=delete_id)
    if st.deleted == False:
        deleted_value = True
    elif st.deleted == True:
        deleted_value = False
    st.deleted = deleted_value
    st.save()
    # Redirect to the same page to show the updated data
    data = Quota.objects.all()
    return redirect('kuotaMaster:index')

def get_site_data(request, site_name):
    site = get_object_or_404(SiteMaster, site_name=site_name, deleted=False)
    data = {
        'provinsi': site.provinsi,
        'site_registration': site.site_registration
    }
    return JsonResponse(data)
