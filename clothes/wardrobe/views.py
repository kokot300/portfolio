from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views import View

from .models import Institution, Donation, Category


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
            'foundations': Institution.objects.filter(type=1),
            'non_governmental': Institution.objects.filter(type=2),
            'locals': Institution.objects.filter(type=3),
        }
        return render(request, 'index.html', ctx)


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return redirect('register')


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('index')


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
            user = User.objects.create_user(username=request.POST['email'], email=request.POST['email'],
                                            password=request.POST['password'])
        except IntegrityError:
            msg = 'nie możesz utworzyć konta z tym emailem'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        user.first_name = request.POST['name']
        user.last_name = request.POST['surname']
        user.save()

        return redirect('login')


class FromView(LoginRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.all()
        institutions = Institution.objects.all()

        ctx = {
            'categories': categories,
            'institutions': institutions,
        }
        return render(request, 'form.html', ctx)

    def post(self, request):
        try:
            institution = Institution.objects.get(pk=request.POST['organization'])

            donation = Donation.objects.create(
                quantity=int(request.POST['bags']),
                institution=institution,
                address=request.POST['address'],
                phone_number=request.POST['phone'],
                city=request.POST['city'],
                zip_code=request.POST['postcode'],
                pick_up_date=request.POST['data'],
                pick_up_time=request.POST['time'],
                pick_up_comment=request.POST['more_info'],
                user=request.user,
            )

            for cat in request.POST['categories']:
                donation.categories.add(int(cat))
            donation.save()
            return redirect('confirmation')
        except:
            return redirect('form')


class FormSubmitConfirmationView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'form-confirmation.html', {})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        donations = Donation.objects.all().filter(user=user).order_by('is_taken', 'pick_up_date', 'pick_up_time')
        ctx = {
            'donations': donations,
        }
        return render(request, 'profile.html', ctx)

    def post(self, request):
        print(request.POST)
        for donation_id in request.POST['donation']:
            donation = Donation.objects.get(pk=donation_id)
            donation.is_taken = True
            donation.save()
        return redirect('profile')
