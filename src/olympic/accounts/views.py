from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.urls import reverse
from django.contrib.auth.models import User
import accounts.db as db

# Create your views here.

def conn_db(dbname, user, password, host):
    return db.OlympicDataBase(
        dbname=dbname, 
        user=user, 
        password=password, 
        host=host
    )


def get_user_page(request):
    context = {}

    if request.user.is_superuser:
        olympic_db = conn_db('olympic', 'user_serv', 'admin', 'localhost')
        olympic_db.connect()
        context["list_users"] = olympic_db.users_info()
        olympic_db.close()

    return render(request, "accounts/acc.html", context)

def comments(request):
    olympic_db = db.OlympicDataBase(
        dbname='olympic', 
        user='postgres', 
        password='paw.toporkov', 
        host='localhost'
    )
    olympic_db.connect()
    data = {}

    if request.method == 'POST':
        username = request.user.username
        comment = request.POST['field_comments']
        if comment:
            olympic_db.append_comment(username, comment)
        else:
            data["error"] = "Введите текст комментария!"

    data["comments"] = olympic_db.get_commets()
    olympic_db.close()

    return render(request, "accounts/comments.html", data)


def delete_comment(request, pk):
    olympic_db = db.OlympicDataBase(
        dbname='olympic', 
        user='postgres', 
        password='paw.toporkov', 
        host='localhost'
    )
    olympic_db.connect()
    
    olympic_db.delete_comment(pk)
    olympic_db.close()

    return redirect(reverse('comments'))


def delete_user(request, pk):
    olympic_db = db.OlympicDataBase(
        dbname='olympic', 
        user='postgres', 
        password='paw.toporkov', 
        host='localhost'
    )
    olympic_db.connect()

    print("delete user id: ", pk)
    olympic_db.delete_user(pk)
    # olympic_db.delete_comment(pk)
    olympic_db.close()

    return redirect(reverse('acc'))


class LoginView(TemplateView):
    template_name = "accounts/login.html"

    def dispatch(self, request, *args, **kwargs):
        context = {}
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            print(request.user)
            if user is not None:
                login(request, user)
                return redirect("/menu/find")
            else:
                context['error'] = "Логин или пароль неправильные"
        return render(request, self.template_name, context)


class RegisterView(TemplateView):
    template_name = "accounts/registration.html"

    def dispatch(self, request, *args, **kwargs):
        context = {}
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')

            check = username and email and password and password2
            if check and password == password2:
                # print(User.objects.filter(username=username, email=email))
                if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                    context["error"] = 'Пользователь с таким именем пользователя или почтой уже существует!'
                    return render(request, self.template_name, context)
                
                User.objects.create_user(username, email, password)
                context["success"] = "Пользователь " + str(username) + " успешно создан!"
                return render(request, self.template_name, context)

            context["error"] = 'Поля "Имя пользователя", "Email", "Пароль"' +\
                               ' и "Подтвердите пароль" должны быть заполнены обязательно!'
            
            context["error_password"] = 'Поля "Пароль" и "Подтвердите пароль" должны быть заполнены одинаково!'

        return render(request, self.template_name, context)
