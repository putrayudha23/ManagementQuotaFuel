from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from siteMaster.models import SiteMaster

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        data = SiteMaster.objects.all()

        if request.method == 'POST':
            if 'site_registration' in request.POST:
                site_registration = request.POST['site_registration']
                if len(site_registration) != 0:
                    data = SiteMaster.objects.filter(site_registration=site_registration)
                else:
                    data = SiteMaster.objects.all()

            if "site_name" in request.POST and "provinsi" in request.POST and "site_regis" in request.POST and "id_modify" in request.POST:
                site_name = request.POST['site_name']
                provinsi = request.POST['provinsi']
                site_regis = request.POST['site_regis']
                typeSpb = request.POST['typeSpb']
                id_modify = request.POST['id_modify']
                deleted = False

                if id_modify == "":
                    try:
                        SiteMaster.objects.get(site_registration=site_regis, typeSpb=typeSpb)
                        message = "has been added"
                        data = SiteMaster.objects.all()
                        paginator = Paginator(data, 10)  # Show 5 items per page
                        page_number = request.GET.get('page')
                        page_obj = paginator.get_page(page_number)
                        context = {'page_obj': page_obj, 'message': message}
                        if request.user.is_superuser:
                            return render(request, 'siteMaster.html', context)
                        else:
                            return render(request, 'noAccess_app.html')
                    except:
                        SiteMaster.objects.create(site_name=site_name, provinsi=provinsi, site_registration=site_regis, typeSpb=typeSpb, deleted=deleted)
                        data = SiteMaster.objects.all()
                        paginator = Paginator(data, 10)  # Show 5 items per page
                        page_number = request.GET.get('page')
                        page_obj = paginator.get_page(page_number)
                        context = {'page_obj': page_obj}
                        if request.user.is_superuser:
                            return render(request, 'siteMaster.html', context)
                        else:
                            return render(request, 'noAccess_app.html')
                else:
                    #modify
                    id = request.POST['id_modify']
                    st = SiteMaster.objects.get(id=id)
                    st.site_name = request.POST.get('site_name')
                    st.provinsi = request.POST.get('provinsi')
                    st.site_registration = request.POST.get('site_regis')
                    st.typeSpb = request.POST.get('typeSpb')
                    st.save()
                    data = SiteMaster.objects.filter(id=id)

        paginator = Paginator(data, 10)  # Show 5 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'page_obj': page_obj}
        if request.user.is_superuser:
            return render(request, 'siteMaster.html', context)
        else:
            return render(request, 'noAccess_app.html')
    else:
        return render(request, 'noAccess.html')

def delete(request, delete_id):
    st = SiteMaster.objects.get(id=delete_id)
    if st.deleted == False:
        deleted_value = True
    elif st.deleted == True:
        deleted_value = False
    st.deleted = deleted_value
    st.save()
    # Redirect to the same page to show the updated data
    return redirect('siteMaster:index')