from django.shortcuts import render
import requests

from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    # Token = 'DEVICE-TEST'
    Token = 'AKR-KF2023062141882525793'
    SMToken = request.GET.get('token')
    userId = request.GET.get('id')
    appId = request.GET.get('app')

    if SMToken != None and userId != None:
        # save the values in the session
        request.session['Token'] = Token
        request.session['SMToken'] = SMToken
        request.session['userId'] = userId
        request.session['appId'] = appId
        # make a GET request to the API with token and app values
        # url = f'http://172.20.100.131:400/api/SMService/UserTokenValidation?Token={Token}&UserID={userId}&SMToken={SMToken}' #TES
        url = f'http://api.akr.co.id/api/SMService/UserTokenValidation?Token={Token}&UserID={userId}&SMToken={SMToken}'
        try:
            response = requests.get(url, timeout=10)
        except:
            return render(request, 'timeOut.html')
        # get the JSON data from the response
        json_data = response.json()
        if json_data['data'] != None:
            UFlag = json_data['data']['UFlag']
            USts = json_data['data']['USts']
            UName = json_data['data']['UName']
            UID = json_data['data']['UID']

            if UFlag == 'True':
                return render(request, 'noAccess.html')
            elif USts == 'False':
                return render(request, 'noAccess.html')
            else:
                # Next langsung login internal app -> simpan sessionnya (agar kalo masuk ke home lagi cek nya tidak pake api tapi pake session login internal aplikasinya)
                user = authenticate(request, username=UName, password=UID)

                # new treatment ///////!!!!!!!
                if not user:
                    user = authenticate(request, username=UName, password=UName)

                if user is not None:
                    login(request, user)
                    if request.user.is_superuser:
                        return render(request, 'home.html')
                    else:
                        return render(request, 'home_cabang.html')
                else:
                    return render(request, 'noAccess.html')
        else:
            return render(request, 'noAccess.html')
    else:
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return render(request, 'home.html')
            else:
                return render(request, 'home_cabang.html')
        else:
            return render(request, 'noAccess.html')
    

def logout_view(request):
    logout(request)
    return render(request, 'logout.html')