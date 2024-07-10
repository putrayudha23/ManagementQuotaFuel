from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from uploadExcelNonkendaraan.models import NonVehicleMaster, ViewNonVehicleMaster
from userSetting.models import UserSiteMapping

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        q1 = Q(flag_status=1)
        result = q1

        # get site user
        username = request.user.username
        user_item_mappings = UserSiteMapping.objects.filter(username=username)
        site_registrations = list(user_item_mappings.values_list('site_registration', flat=True))

        if request.method == 'POST':
            id_konsumen_search = request.POST.get('id_konsumen_search')
            data = ViewNonVehicleMaster.objects.filter(inactive_status=False, site_registration__in=site_registrations, no_konsumen=id_konsumen_search).filter(result).order_by('-ChangedDate')

            paginator = Paginator(data, 100)  # Show 10 items per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'page_obj': page_obj}

            if request.user.is_superuser:
                return render(request, 'dataOffline.html', context)
            else:
                return render(request, 'dataOffline_cabang.html', context)
        else:
            data = ViewNonVehicleMaster.objects.filter(inactive_status=False, site_registration__in=site_registrations).filter(result).order_by('-ChangedDate')

            paginator = Paginator(data, 100)  # Show 10 items per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'page_obj': page_obj}

            if request.user.is_superuser:
                return render(request, 'dataOffline.html', context)
            else:
                return render(request, 'dataOffline_cabang.html', context)
    else:
        return render(request, 'noAccess.html')
    
def update_uuid(request, row_id):
    if request.method == 'POST':
        # Retrieve the instance based on the row_id
        try:
            non_vehicle_instance = NonVehicleMaster.objects.get(id=row_id)
        except NonVehicleMaster.DoesNotExist:
            # Handle the case where the instance with the given ID doesn't exist
            return JsonResponse({'success': False, 'message': 'Instance not found'})
        
        uuid = request.POST.get('entryUuid')
        uuidKapal = request.POST.get('entryUuidKapal')

        non_vehicle_instance.uuid = uuid
        non_vehicle_instance.uuid_kapal = uuidKapal

        # Save the instance to persist the changes
        non_vehicle_instance.save()

        return JsonResponse({'success': True, 'message': 'Instance updated successfully'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})