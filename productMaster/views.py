from django.shortcuts import render, redirect
from productMaster.models import Product

# product_name=&description=&id_add=&id_modify=&idquota=&price=&datetimestart=&datetimeend=

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        data = Product.objects.all()

        if request.method == 'POST':

            if 'id_search' in request.POST:
                id = request.POST['id_search']
                if len(id) != 0:
                    data = Product.objects.filter(id=id)
                else:
                    data = Product.objects.all()

            if "id_add" in request.POST:
                productName = request.POST['product_name']
                description = request.POST['description']
                idQuota = request.POST['idquota']
                price = request.POST['price']
                id = request.POST['id_add']
                datetimestart = request.POST['datetimestart']
                datetimeend = request.POST['datetimeend']
                deleted = False
                try:
                    Product.objects.get(id=id)
                    message = "has been added"
                    # Redirect to the same page to show the updated data
                    data = Product.objects.all()
                    context = {'data': data, 'message': message}
                    if request.user.is_superuser:
                        return render(request, 'productMaster.html', context)
                    else:
                        return render(request, 'noAccess_app.html')
                except:
                    Product.objects.create(id=id, name=productName, description=description, price=price, idquota=idQuota, datetimestart=datetimestart, datetimeend=datetimeend, deleted=deleted)
                    # Redirect to the same page to show the updated data
                    data = Product.objects.all()
                    context = {'data': data}
                    if request.user.is_superuser:
                        return render(request, 'productMaster.html', context)
                    else:
                        return render(request, 'noAccess_app.html')
            elif "id_modify" in request.POST and "description" in request.POST:
                id = request.POST['id_modify']
                pt = Product.objects.get(id=id)
                pt.description = request.POST.get('description')
                pt.name = request.POST.get('product_name')
                pt.price = request.POST.get('price')
                pt.idquota = request.POST.get('idquota')
                pt.datetimestart = request.POST.get('datetimestart')
                pt.datetimeend = request.POST.get('datetimeend')
                pt.save()
                data = Product.objects.all()

        if request.user.is_superuser:
            return render(request, 'productMaster.html', {'data': data})
        else:
            return render(request, 'noAccess_app.html')
    else:
        return render(request, 'noAccess.html')

def delete(request, delete_id):
    pt = Product.objects.get(id=delete_id)
    if pt.deleted == False:
        deleted_value = True
    elif pt.deleted == True:
        deleted_value = False
    pt.deleted = deleted_value
    pt.save()
    # Redirect to the same page to show the updated data
    return redirect('productMaster:index')