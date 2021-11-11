from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from olympic.settings import BASE_DIR
from django.contrib.auth import logout

# Create your views here.

def log_out(request):
    logout(request)
    return HttpResponseRedirect("/menu/find")


def index(request):
    # if request.method == 'POST':
    #     keywords_dict = request.POST
    #     if keywords_dict:
    #         payload = {'drilldown' : 'athletes|games'}  
    #         r = req.get('http://localhost:5000/cube/medal/aggregate', params=payload)
    #         print(keywords_dict)
    #         test = hr.ReceivedDataAggregator()
    #         data = test.get_processed_data(keywords_dict)
    #         print(data)
    #         print('\n\n', BASE_DIR, '\n\n')
    #         data_str = '{\n'
    #         print('data.items()', data.items())
    #         return render(request, 'menu/result.html', {'keywords_dict': r.text})

    # print("menu:", request.user.email, request.user.username, request.user.is_superuser)
    # logout(request)
    # print("menu2:", request.user)
    return render(request, 'menu/index.html', {"user": request.user})


def test(request):
    pass
#     payload = {'drilldown' : 'athletes|games'}  
#     r = req.get('http://localhost:5000/cube/medal/aggregate', params=payload)
#     return render(request, 'menu/result.html', {'keywords_dict': r})
