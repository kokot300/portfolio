from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User

from .models import Institution, Donation


# Create your views here.

class IndexView(View):
    def get(self, request):
        donations = Donation.objects.all()
        bags = 0
        for donation in donations:
            bags += donation.quantity
        ctx = {
            'institution': Institution.objects.count(),
            'bags': bags,
            'foundations' : Institution.objects.filter(type=1),
            'non_governmental' : Institution.objects.filter(type=2),
            'locals' : Institution.objects.filter(type=3),
        }
        return render(request, 'index.html', ctx)


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', {})


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html', {})

    def post(self, request):
        msg = None
        print(request.POST['name'])
        print(request.POST['surname'])
        print(request.POST['email'])
        print(request.POST['password'])
        print(request.POST['password2'])

        if request.POST['name'] == '':
            msg = 'Imię nie może być puste!'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        if request.POST['surname'] == '':
            msg = 'Nazwisko nie może być puste!'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        if request.POST['email'] == '' or '@' not in request.POST['email']:
            msg = 'wpisz poprawny email!'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        if request.POST['password'] != request.POST['password2']:
            msg = 'Hasła muszą być takie same'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        if len(request.POST['password2']) < 8:
            msg = 'Za krótkie hasło'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        try:
            user = User.objects.create(username=request.POST['email'])
        except IntegrityError:
            msg = 'nie możesz utworzyć konta z tym emailem'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        user.first_name = request.POST['name']
        user.last_name = request.POST['surname']
        user.email = request.POST['email']
        user.set_password(request.POST['password'])
        print(f'\n\n {user.password} \n\n')
        # authentication should work with user.check_password()
        user.save()

        return redirect('login')


class FromView(View):
    def get(self, request):
        return render(request, 'form.html', {})
