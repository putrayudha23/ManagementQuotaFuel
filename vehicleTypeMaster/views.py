from django.shortcuts import render, redirect
from vehicleTypeMaster.models import VehicleType
from django.core.paginator import Paginator

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        data = VehicleType.objects.all()
        if request.method == 'POST':

            if 'id_search' in request.POST:
                id = request.POST['id_search']
                if len(id) != 0:
                    data = VehicleType.objects.filter(id=id)
                else:
                    data = VehicleType.objects.all()

            if "id_add" in request.POST and "description" in request.POST:
                # submit if "id_add" not exist in database
                id = request.POST['id_add']
                description = request.POST['description']
                SettingSystem = request.POST['SettingSystem']
                deleted = False
                try:
                    VehicleType.objects.get(id=id)
                    message = "has been added"
                    # Redirect to the same page to show the updated data
                    data = VehicleType.objects.all()
                    paginator = Paginator(data, 10)  # Show 5 items per page
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    context = {'page_obj': page_obj, 'message': message}
                    if request.user.is_superuser:
                        return render(request, 'vehicleTypeMaster.html', context)
                    else:
                        return render(request, 'noAccess_app.html')
                except:
                    VehicleType.objects.create(id=id, description=description, SettingSystem=SettingSystem, deleted=deleted)
                    # Redirect to the same page to show the updated data
                    data = VehicleType.objects.all()
                    paginator = Paginator(data, 10)  # Show 5 items per page
                    page_number = request.GET.get('page')
                    page_obj = paginator.get_page(page_number)
                    context = {'page_obj': page_obj}
                    if request.user.is_superuser:
                        return render(request, 'vehicleTypeMaster.html', context)
                    else:
                        return render(request, 'noAccess_app.html')
            elif "id_modify" in request.POST and "description" in request.POST:
                id = request.POST['id_modify']
                vt = VehicleType.objects.get(id=id)
                vt.description = request.POST.get('description')
                vt.SettingSystem = request.POST.get('SettingSystem')
                vt.save()
                data = VehicleType.objects.all()

        paginator = Paginator(data, 10)  # Show 5 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if request.user.is_superuser:
            return render(request, 'vehicleTypeMaster.html', {'page_obj': page_obj})
        else:
            return render(request, 'noAccess_app.html')
    else:
        return render(request, 'noAccess.html')

def delete(request, delete_id):
    vt = VehicleType.objects.get(id=delete_id)
    if vt.deleted == False:
        deleted_value = True
    elif vt.deleted == True:
        deleted_value = False
    vt.deleted = deleted_value
    vt.save()
    # Redirect to the same page to show the updated data
    return redirect('vehicleTypeMaster:index')