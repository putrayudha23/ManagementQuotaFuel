from django.shortcuts import render
from django.core.paginator import Paginator

from siteMaster.models import SiteMaster
from transactionNonkendaraan.models import nonVehicleTransaction

def index(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if 'id' in request.POST:
                id = request.POST.get('id')
                nonvehicle_transaction = nonVehicleTransaction.objects.get(id=id)
                # update the object with the new data from the form
                nonvehicle_transaction.volume_quotaavailable = request.POST.get('volume_quotaavailable')
                nonvehicle_transaction.frequency_quota = request.POST.get('frequency_quota')
                nonvehicle_transaction.trnrec = request.POST.get('trnrec')
                # save the updated object to the database
                nonvehicle_transaction.save()

                data = nonVehicleTransaction.objects.filter(id=id)
            else:
                # search data
                no_konsumen = request.POST['id_konsumen_search']
                site_registration = request.POST['site_Search']

                if len(no_konsumen) != 0 and len(site_registration) != 0:
                    # use the ORM to retrieve data from the database
                    data = nonVehicleTransaction.objects.filter(no_konsumen=no_konsumen, site_registration=site_registration)
                elif len(no_konsumen) == 0 and len(site_registration) != 0:
                    # use the ORM to retrieve data from the database
                    data = nonVehicleTransaction.objects.filter(site_registration=site_registration)
                    paginator = Paginator(data, 1000)  # Show 5 items per page
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    sites = SiteMaster.objects.filter(deleted=False)
                    if request.user.is_superuser:
                        return render(request, 'transactionNonkendaraan.html', {'page_obj': page_obj, 'sites':sites})
                    else:
                        return render(request, 'noAccess_app.html')
                elif len(no_konsumen) != 0 and len(site_registration) == 0:
                    # use the ORM to retrieve data from the database
                    data = nonVehicleTransaction.objects.filter(no_konsumen=no_konsumen)
                else:
                    # Retrieve all data from the database
                    data = nonVehicleTransaction.objects.all()
        else:
            data = nonVehicleTransaction.objects.all()
        
        sites = SiteMaster.objects.filter(deleted=False)
        paginator = Paginator(data, 10)  # Show 5 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        sites = SiteMaster.objects.filter(deleted=False)
        if request.user.is_superuser:
            return render(request, 'transactionNonkendaraan.html', {'page_obj': page_obj, 'sites':sites})
        else:
            return render(request, 'noAccess_app.html')
    else:
        return render(request, 'noAccess.html')