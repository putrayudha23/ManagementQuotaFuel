from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
import requests
from django.http import HttpResponse
from django.http import JsonResponse

from siteMaster.models import SiteMaster
from .models import UserSiteMapping

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        userdata = User.objects.all()
        sites = SiteMaster.objects.filter(deleted=False)
        users = User.objects.all()

        user_mappings = UserSiteMapping.objects.all()  # Retrieve user mappings
        selected_sites_per_user = {}
        for mapping in user_mappings:
            if mapping.username not in selected_sites_per_user:
                selected_sites_per_user[mapping.username] = {mapping.site_registration}
            else:
                selected_sites_per_user[mapping.username].add(mapping.site_registration)

        # untuk get data user yang belum regis ke app, tapi sudah di SM
        Token = request.session.get('Token')
        ApplicationID = request.session.get('appId')
        UserID = request.session.get('userId')
        SMToken = request.session.get('SMToken')
        url = f'http://172.20.100.131:400/api/SMService/GetListUserSM?Token={Token}&ApplicationID={ApplicationID}&UserID={UserID}&SMToken={SMToken}' # TES
        # url = f'http://api.akr.co.id/api/SMService/GetListUserSM?Token={Token}&ApplicationID={ApplicationID}&UserID={UserID}&SMToken={SMToken}'
        response = requests.get(url)
        json_string = response.text
        data = json.loads(json_string)

        if request.method == 'POST':
            if 'username_search' in request.POST:
                username_search = request.POST['username_search']
                if len(username_search) != 0:
                    userdata = User.objects.filter(username=username_search)
                else:
                    userdata = User.objects.all()
            
            if "username" in request.POST:
                username = request.POST['username']
                uid = None
                for user in data['data']:
                    if user['UName'] == username:
                        uid = user['UID']
                        first_name = user['FullName']
                        break

                # new treatment ///////!!!!!!!
                if uid !=0:
                    password = str(uid)
                else:
                    password = request.POST['username']

                email = request.POST['email']
                is_superuser = request.POST['user_status']
                is_approver = request.POST['approver']
                is_active = True
                is_staff = True
                id_modify = request.POST['id_modify']

                if id_modify == "":
                    #submit
                    new_user = User.objects.create(username=username, email=email, first_name=first_name, is_superuser=is_superuser, is_active=is_active, is_approver=is_approver, is_staff=is_staff)
                    new_user.set_password(password) # hash and set the password
                    new_user.save() # save the new user
                    userdata = User.objects.all()
                    #submit in usersitemapping
                    UserSiteMapping.objects.create(username=username)
            elif "email" in request.POST:
                #modify
                id = request.POST['id_modify']
                ut = User.objects.get(id=id)
                ut.email = request.POST.get('email')
                ut.is_superuser = request.POST.get('user_status')
                ut.is_approver = request.POST.get('approver')
                ut.save()
                userdata = User.objects.all()

        # uname_list = [user['UName'] for user in data['data']]
        existing_usernames = User.objects.values_list('username', flat=True)
        uname_list = [user['UName'] for user in data['data'] if user['UName'] not in existing_usernames]
        # Pass uname_list to the template context
        paginator = Paginator(userdata, 10)  # Show 5 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj, 'uname_list': uname_list, 'sites':sites, 'users':users, 'selected_sites_per_user': selected_sites_per_user}
        if request.user.is_superuser:
            return render(request, 'userSetting.html',context)
        else:
            return render(request, 'noAccess_app.html')
    else:
        return render(request, 'noAccess.html')
    
def delete(request, delete_id):
    ut = User.objects.get(id=delete_id)
    if ut.is_active == False:
        is_active = True
    elif ut.is_active == True:
        is_active = False
    ut.is_active = is_active
    ut.save()
    # Redirect to the same page to show the updated data
    return redirect('userSetting:index')

def site_mapping(request):
    if request.method == 'POST':
        username = request.POST.get('entryUsername')
        site_list = request.POST.getlist(f'site_list_{username}')

        # Delete entries that are not in new data
        UserSiteMapping.objects.filter(username=username).delete()

        # Check for existing combinations
        if len(site_list) != 0:
            for site_registration in site_list:
                UserSiteMapping.objects.create(username=username, site_registration=site_registration)
        else:
            UserSiteMapping.objects.create(username=username, site_registration=None)
        
        return redirect('userSetting:index') 