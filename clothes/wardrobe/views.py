import string

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.datastructures import MultiValueDictKeyError
from django.views import View
from django.views.generic import FormView
from django_registration.backends.activation.views import RegistrationView

from .forms import UpdateUserForm
from .models import Institution, Donation, Category, UserActivation


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

    def post(self, request):
        print(request.POST)
        su = User.objects.filter(is_superuser=True)
        superusers = [x.email for x in su]
        try:
            send_mail(recipient_list=superusers, message=request.POST.get('message'),
                      subject=request.POST.get('name') + request.POST.get('surname'), from_email='poesiaco@gmail.com')
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return redirect('index')


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


class RegisterView(RegistrationView):
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

        if len(request.POST['password']) < 8:
            msg = 'Za krótkie hasło'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        lower_flag = False
        upper_flag = False
        digit_flag = False
        special_flag = False
        for char in request.POST['password']:
            if char in string.ascii_lowercase:
                lower_flag = True
            if char in string.ascii_uppercase:
                upper_flag = True
            if char in string.digits:
                digit_flag = True
            if char in string.punctuation:
                special_flag = True

        if not lower_flag:
            msg = 'W haśle brakuje małej litery!'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        if not upper_flag:
            msg = 'W haśle brakuje dużej litery!'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        if not digit_flag:
            msg = 'W haśle brakuje cyfry!'
            ctx = {
                'msg': msg,
            }
            return render(request, 'register.html', ctx)

        if not special_flag:
            msg = 'W haśle brakuje znaku specjalnego!'
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
        user.is_active = False
        user.save()
        activation = UserActivation(user=user)
        activation.save()

        email = EmailMessage('Aktywuj Konto', 'http://127.0.0.1:8000/activate/?code=' + str(activation.activation),
                             to=[user.email, ])
        email.send()

        return redirect('login')


class AccountActivationView(View):
    def get(self, request):
        print(request.GET)
        activation = get_object_or_404(UserActivation, activation=request.GET['code'])
        user = get_object_or_404(User, username=activation.user)
        user.is_active = True
        user.save()
        activation.delete()
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
            int(request.POST['organization'])
        except MultiValueDictKeyError as e:
            print(e)
            categories = Category.objects.all()
            institutions = Institution.objects.all()
            msg = 'No such institution!'
            ctx = {
                'categories': categories,
                'institutions': institutions,
                'msg': msg,
            }
            return render(request, 'form.html', ctx)

        try:
            institution = Institution.objects.get(pk=request.POST['organization'])
        except ObjectDoesNotExist or MultiValueDictKeyError as e:
            print(e)
            categories = Category.objects.all()
            institutions = Institution.objects.all()
            msg = 'No such institution!'
            ctx = {
                'categories': categories,
                'institutions': institutions,
                'msg': msg,
            }
            return render(request, 'form.html', ctx)

        try:
            bags = int(request.POST['bags'])
        except ValueError as e:
            print(e)
            categories = Category.objects.all()
            institutions = Institution.objects.all()
            msg = 'Amount of bags incorrect!'
            ctx = {
                'categories': categories,
                'institutions': institutions,
                'msg': msg,
            }
            return render(request, 'form.html', ctx)

        try:
            phone = int(request.POST['phone'])
        except ValueError as e:
            print(e)
            categories = Category.objects.all()
            institutions = Institution.objects.all()
            msg = 'Phone must be a number!'
            ctx = {
                'categories': categories,
                'institutions': institutions,
                'msg': msg,
            }
            return render(request, 'form.html', ctx)

        try:
            postcode = request.POST['postcode'].replace('-', '')
            postcode = int(postcode)
        except ValueError as e:
            print(e)
            categories = Category.objects.all()
            institutions = Institution.objects.all()
            msg = 'Zip code must be a number!'
            ctx = {
                'categories': categories,
                'institutions': institutions,
                'msg': msg,
            }
            return render(request, 'form.html', ctx)

        # print(type(request.POST['data']))
        # print(type(request.POST['time']))

        #  address, city and comment should be always ok
        #  user is taken from session so there is low possibility for user to mess up
        #  only things left to validate are date and time
        try:
            donation = Donation.objects.create(
                quantity=bags,
                institution=institution,
                address=request.POST['address'],
                phone_number=phone,
                city=request.POST['city'],
                zip_code=postcode,
                pick_up_date=request.POST['data'],
                pick_up_time=request.POST['time'],
                pick_up_comment=request.POST['more_info'],
                user=request.user,
            )
        except ValidationError or TypeError as e:
            print(e)
            categories = Category.objects.all()
            institutions = Institution.objects.all()
            msg = 'Date and time incorrect!'
            ctx = {
                'categories': categories,
                'institutions': institutions,
                'msg': msg,
            }
            return render(request, 'form.html', ctx)

        try:
            for cat in request.POST['categories']:
                donation.categories.add(int(cat))
            donation.save()
        except IntegrityError or TypeError or MultiValueDictKeyError as e:
            print(e)
            categories = Category.objects.all()
            institutions = Institution.objects.all()
            msg = 'Categories are incorrect!'
            ctx = {
                'categories': categories,
                'institutions': institutions,
                'msg': msg,
            }
            return render(request, 'form.html', ctx)

        return redirect('confirmation')


class FormSubmitConfirmationView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        return render(request, 'form-confirmation.html', {})

    def test_func(self):
        return self.request.META.get('HTTP_REFERER') == 'http://127.0.0.1:8000/donate/'


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        donations = Donation.objects.all().filter(user=user).order_by('is_taken', 'pick_up_date', 'pick_up_time')
        ctx = {
            'donations': donations,
        }
        return render(request, 'profile.html', ctx)

    def post(self, request):
        donations = request.POST.getlist('donation')
        print('\n\n\n', donations, '\n\n\n')
        # if isinstance(request.POST['donation'], str):
        #     donation = Donation.objects.get(pk=int(request.POST['donation']))
        #     donation.is_taken = True
        #     donation.save()
        # else:
        for donation_id in donations:
            print('\n\n\n', donation_id, '\n\n\n')
            donation = Donation.objects.get(pk=int(donation_id))
            donation.is_taken = True
            donation.save()
        return redirect('profile')


class UpdateProfileView(LoginRequiredMixin, FormView):
    form_class = UpdateUserForm
    template_name = 'update_profile.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        """
        overrides default form_valid method
        """
        form = UpdateUserForm(self.request.POST)
        if form.is_valid():
            user = authenticate(username=self.request.user.email, password=self.request.POST['password'])
            if user is not None:
                user.first_name = self.request.POST['first_name']
                user.last_name = self.request.POST['last_name']
                user.email = self.request.POST['email']
                user.save()
            else:
                return render(self.request, 'update_profile.html', {'msg': 'dane nieprawidłowe!'})
        return super().form_valid(form)
