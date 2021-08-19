import datetime
import random
import string
from io import StringIO

import matplotlib.pyplot as plt
import transliterate
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.urls import reverse

from .forms import LoginForm, RegistrationForm, MainPageSortFormHospital, CovidForm, DateForm
from .models import Patient, PatientRecord


def translit(line):
    return transliterate.translit(line, reversed=True)


def checkCyrillic(line):
    for x in line:
        if x not in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ':
            return False
    return True


def log_in(request):
    if request.method == 'POST':
        logout(request)
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET['next'])
            else:
                form.add_error('username', 'Invalid credentials!')
    else:
        form = LoginForm()
    return render(request, 'shop/login.html', {'form': form})


def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            logout(request)
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_again = form.cleaned_data['password_again']
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'User already exists!')
            elif password != password_again:
                form.add_error('password_again', 'Password mismatch!')
            else:
                user = User.objects.create_user(username, email, password)
                login(request, user)
                return get_patient_list(request)
    else:
        form = RegistrationForm()
    return render(request, 'shop/signup.html', {'form': form})


def log_out(request):
    logout(request)
    redirect_url = request.GET.get('next') or reverse('shop_index')
    return redirect(redirect_url)


def get_patient_list(request):
    if request.user.is_authenticated:
        name = request.user.username
    else:
        name = "stranger"
    if request.method == 'GET':
        patients = Patient.objects.order_by('last_name')
        sort = '1'
        search_line = ''
    else:
        search_line = ''
        if 'search_line' in request.POST:
            search_line = request.POST['search_line']
        sortForm = MainPageSortFormHospital(request.POST)
        sort = 0
        if sortForm.is_valid():
            sort = sortForm.cleaned_data['sort_by']
        if not search_line or search_line.isspace():
            patients = Patient.objects.order_by('last_name')
        else:
            patients = Patient.objects.filter(last_name__contains=search_line).order_by('last_name')
        if int(sort) == 2:
            patients = patients.order_by('-created_at')

    sortForm = MainPageSortFormHospital()
    sortForm.fields['sort_by'].initial = sort
    context = {'patients': patients,
               'username': name,
               'sortForm': sortForm,
               'search_line': search_line
               }
    return render(request, 'shop/index_hospital.html', context)


def add_new_patient(request):
    if request.method == 'POST':
        return create_new_patient(request)
    else:
        return render_new_patient(request)


@login_required(login_url='/shop/login')
def create_new_patient(request):
    first_name = request.POST['first_name']
    first_name_error = None
    if not first_name or first_name.isspace():
        first_name_error = 'Please provide first_name'
    elif not checkCyrillic(first_name):
        first_name_error = 'Вводите ФИО в кириллице'

    last_name = request.POST['last_name']
    last_name_error = None
    if not last_name or last_name.isspace():
        last_name_error = 'Please provide last_name'
    elif not checkCyrillic(last_name):
        last_name_error = 'Вводите ФИО в кириллице'

    middle_name = request.POST['middle_name']
    middle_name_error = None
    if not middle_name or middle_name.isspace():
        middle_name_error = 'Please provide middle_name'
    elif not checkCyrillic(middle_name):
        middle_name_error = 'Вводите ФИО в кириллице'

    address = request.POST['address']
    address_error = None
    if not address or address.isspace():
        address_error = 'Please provide address'

    covidForm = CovidForm(request.POST)
    covid = 0
    if covidForm.is_valid():
        covid = covidForm.cleaned_data['covid']

    year = int(request.POST['date_year'])
    month = int(request.POST['date_month'])
    day = int(request.POST['date_day'])
    birth_date = datetime.datetime(year=year, month=month, day=day)
    lung_damage = request.POST['lung_damage']
    lung_damage_error = None
    if not lung_damage or lung_damage.isspace():
        lung_damage_error = 'Please provide address'

    if first_name_error or last_name_error or middle_name_error or address_error or lung_damage_error:
        error_context = {
            'first_name_error': first_name_error,
            'first_name': first_name,
            'last_name_error': last_name_error,
            'last_name': last_name,
            'middle_name_error': middle_name_error,
            'middle_name': middle_name,
            'address_error': address_error,
            'address': address,
            'lung_damage_error': lung_damage_error,
            'lung_damage': lung_damage,
            'birth_date': birth_date,

        }
        return render_new_patient(request, error_context)
    else:
        Patient(first_name=first_name, last_name=last_name, middle_name=middle_name,
                address=address, lung_damage=lung_damage, covid_grade=covid, birth=birth_date).save()
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        username = translit(first_name) + '.' + translit(last_name)
        count = 0
        tmp_username = username
        while User.objects.filter(username=tmp_username).exists():
            tmp_username = username
            count += 1
            tmp_username += str(count)
        username = tmp_username
        print(username, password)
        user = User.objects.create_user(username, password=password)
        return HttpResponseRedirect(reverse('hospital_index'))


def render_new_patient(request, additional_context={}):
    covidForm = CovidForm()
    dateForm = DateForm()
    context = {
        'covidForm': covidForm,
        'dateForm': dateForm,
        **additional_context
    }

    return render(request, 'shop/new_patient.html', context)


def patient(request, patient_id):
    return render_patient(request, patient_id)


def render_patient(request, patient_id, additional_context={}):
    patient = get_object_or_404(Patient, id=patient_id)
    context = {'patient': patient,
               'records': patient.patientrecord_set.order_by('-created_at'),
               **additional_context
               }

    return render(request, 'shop/patient.html', context)


def record(request, record_id):
    if request.method == 'POST':
        # return create_review(request, product_id)
        pass
    else:
        return render_record(request, record_id)


def render_record(request, record_id, additional_context={}):
    record = get_object_or_404(PatientRecord, id=record_id)

    context = {'record': record,
               'graph_temp': temp_graph(temperature=record.temperature_list, start_time=record.created_at),
               'graph_saturation': saturation_graph(saturation=record.last_saturation, start_time=record.created_at),
               'graph_heart_rate': heart_rate_graph(heart_rate=record.heart_rate, start_time=record.created_at),
               **additional_context
               }

    return render(request, 'shop/record.html', context)


def temp_graph(temperature, start_time):
    y = parse_graph_data(temperature)
    x = create_time_interval_graph(start_time, len(y))
    fig = plt.figure()
    plt.ylim(36.0, 39.0)
    plt.grid()
    plt.xticks(rotation=45)
    plt.title('Температура тела')
    plt.plot(x, y)

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data


def saturation_graph(saturation, start_time):
    y = parse_graph_data(saturation)
    x = create_time_interval_graph(start_time, len(y))
    fig = plt.figure()
    plt.ylim(80, 101)
    plt.grid()
    plt.xticks(rotation=45)
    plt.title('Сатурация')
    plt.plot(x, y)

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data


def heart_rate_graph(heart_rate, start_time):
    y = parse_graph_data(heart_rate)
    x = create_time_interval_graph(start_time, len(y))
    fig = plt.figure()
    plt.ylim(50, 200)
    plt.grid()
    plt.xticks(rotation=45)
    plt.title('Частота сердечных сокращений')
    plt.plot(x, y)

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)

    data = imgdata.getvalue()
    return data


def parse_graph_data(data):
    return list(map(float, data.split(';')))


def create_time_interval_graph(time, num):
    minute = str(time.minute)
    if len(minute) == 1:
        minute = '0' + minute
    hour = str(time.hour)
    if len(hour) == 1:
        hour = '0' + hour
    result = [hour + ':' + minute]
    for i in range(num - 1):
        minute_added = datetime.timedelta(minutes=1)
        time = minute_added + time
        minute = str(time.minute)
        if len(minute) == 1:
            minute = '0' + minute
        hour = str(time.hour)
        if len(hour) == 1:
            hour = '0' + hour
        result.append(hour + ':' + minute)
    return result
