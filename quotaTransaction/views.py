from django.shortcuts import render
from quotaTransaction.models import QuotaTransaction, LogQuotaTransaction
from django.core.paginator import Paginator
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from siteMaster.models import SiteMaster

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        if request.method == 'POST':

            if 'volume_quotaavailable' in request.POST and 'frequency_quota' in request.POST and 'trnrec' in request.POST:
                # get the id of the selected QuotaTransaction object
                quota_transaction_id = request.POST.get('quota_transaction_id')
                number_plat = request.POST.get('number_plat')

                # use the ORM to retrieve the QuotaTransaction object with the given id
                quota_transaction = QuotaTransaction.objects.get(id=quota_transaction_id)

                # update the object with the new data from the form
                quota_transaction.volume_quotaavailable = request.POST.get('volume_quotaavailable')
                quota_transaction.frequency_quota = request.POST.get('frequency_quota')
                quota_transaction.trnrec = request.POST.get('trnrec')

                # save the updated object to the database
                quota_transaction.save()

                # SAVE LOG
                LogQuotaTransaction.objects.create(
                    number_plat=number_plat,
                    volume_quotaavailable_before=request.POST['volume_quotaavailable_before'],
                    volume_quotaavailable_new=request.POST['volume_quotaavailable'],
                    frequency_quota_before=request.POST['frequency_quota_before'],
                    frequency_quota_new=request.POST['frequency_quota'],
                    trnrec_before=request.POST['trnrec_before'],
                    trnrec_new=request.POST['trnrec'],
                    ChangedBy=request.user.get_full_name(),
                    ChangedDate=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                )

                data = QuotaTransaction.objects.filter(id=quota_transaction_id)
            else:
                number_plat = request.POST['plat-number-input']
                site_registration = request.POST['side-regis-input']
                if len(number_plat) != 0 and len(site_registration) != 0:
                    # use the ORM to retrieve data from the database
                    data = QuotaTransaction.objects.filter(number_plat=number_plat, site_registration=site_registration)
                elif len(number_plat) == 0 and len(site_registration) != 0:
                    # use the ORM to retrieve data from the database
                    data = QuotaTransaction.objects.filter(site_registration=site_registration)
                    paginator = Paginator(data, 1000)  # Show 5 items per page
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    sites = SiteMaster.objects.filter(deleted=False)
                    if request.user.is_superuser:
                        return render(request, 'quotaTransaction.html', {'page_obj': page_obj, 'sites':sites})
                    else:
                        return render(request, 'noAccess_app.html')
                elif len(number_plat) != 0 and len(site_registration) == 0:
                    # use the ORM to retrieve data from the database
                    data = QuotaTransaction.objects.filter(number_plat=number_plat)
                else:
                    # Retrieve all data from the database
                    data = QuotaTransaction.objects.all()
        else:
            data = QuotaTransaction.objects.all()

        paginator = Paginator(data, 10)  # Show 5 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        sites = SiteMaster.objects.filter(deleted=False)
        if request.user.is_superuser:
            return render(request, 'quotaTransaction.html', {'page_obj': page_obj, 'sites':sites})
        else:
            return render(request, 'noAccess_app.html')
    else:
        return render(request, 'noAccess.html')

