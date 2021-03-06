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

from .forms import LoginForm, RegistrationForm, PatientConditionForm, MainPageSortFormHospital, CovidForm, DateForm
from .models import Patient, PatientRecord, PatientSchedule, PatientExercises


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
                if request.user.first_name == 'doctor':
                    redirect_url = reverse('hospital_index')
                else:
                    redirect_url = reverse('p_patient_index')
                return redirect(redirect_url)

            else:
                form.add_error('username', 'Invalid credentials!')
    else:
        form = LoginForm()
    return render(request, 'hospital/login.html', {'form': form})


def log_out(request):
    logout(request)
    redirect_url = reverse('login')
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
               'search_linesearch_line': search_line
               }
    return render(request, 'hospital/index_hospital.html', context)


def add_new_patient(request):
    if request.method == 'POST':
        return create_new_patient(request)
    else:
        return render_new_patient(request)


@login_required(login_url='/hospital/login')
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
        user = User.objects.create_user(username, password=password, first_name='patient')
        patient = Patient(first_name=first_name, last_name=last_name, middle_name=middle_name,
                          address=address, lung_damage=lung_damage, covid_grade=covid, birth=birth_date,
                          doctor=request.user, patient=user)
        patient.save()
        user.last_name = str(patient.id)
        user.save()
        return HttpResponseRedirect(reverse('hospital_index'))


def render_new_patient(request, additional_context={}):
    covidForm = CovidForm()
    dateForm = DateForm()
    context = {
        'covidForm': covidForm,
        'dateForm': dateForm,
        **additional_context
    }

    return render(request, 'hospital/new_patient.html', context)


@login_required(login_url='/hospital/login')
def patient(request, patient_id):
    if request.method == 'POST':
        if 'schedule_text' in request.POST:
            return add_new_schedule(request, patient_id)
        if 'exercise_text' in request.POST:
            return add_new_exercise(request, patient_id)
    else:
        return render_patient(request, patient_id)


def render_patient(request, patient_id, additional_context={}):
    patient = get_object_or_404(Patient, id=patient_id)
    context = {'patient': patient,
               'records': patient.patientrecord_set.order_by('-created_at'),
               'schedule': patient.patientschedule_set.order_by('-id'),
               'exercises': patient.patientexercises_set.order_by('id'),
               **additional_context
               }

    return render(request, 'hospital/patient.html', context)


@login_required(login_url='/hospital/login')
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

    return render(request, 'hospital/record.html', context)


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


@login_required(login_url='/hospital/login')
def get_patient_mainpage(request):
    if request.method == 'POST':
        pass
    else:
        return render_patient_mainpage(request)


def render_patient_mainpage(request):
    return render(request, 'patient/index_patient.html')


@login_required(login_url='/hospital/login')
def get_patient_schedule(request):
    if request.method == 'POST':
        pass
    else:
        return render_patient_schedule(request)


def render_patient_schedule(request):
    patient_id = int(request.user.last_name)
    patient = get_object_or_404(Patient, id=patient_id)
    context = {'patient': patient,
               'actions': patient.patientschedule_set.order_by('-id')
               }
    return render(request, 'patient/patient_schedule.html', context)


@login_required(login_url='/hospital/login')
def get_patient_condition(request):
    if request.method == 'POST':
        return create_patient_condition(request)
    else:
        return render_patient_condition(request)


def create_patient_condition(request):
    patient_id = int(request.user.last_name)
    patient = get_object_or_404(Patient, id=patient_id)

    temperature_list = request.POST['temperature_list']
    temperature_list_error = None
    if not temperature_list or temperature_list.isspace():
        temperature_list_error = 'Please provide temperature'

    heart_rate = request.POST['heart_rate']
    heart_rate_error = None
    if not heart_rate or heart_rate.isspace():
        heart_rate_error = 'Please provide heart_rate'

    last_saturation = request.POST['last_saturation']
    last_saturation_error = None
    if not last_saturation or last_saturation.isspace():
        last_saturation_error = 'Please provide last_saturation'

    form_condition = PatientConditionForm(request.POST)
    condition = None
    condition_error = None
    if form_condition.is_valid():
        condition = form_condition.cleaned_data.get('condition')
    else:
        condition_error = 'Please provide full data'

    shortness_of_breath = 'shortness_of_breath' in condition
    chest_tightness = 'chest_tightness' in condition
    vomiting = 'vomiting' in condition
    dizziness = 'dizziness' in condition
    headache = 'headache' in condition
    blurred_consciousness = 'blurred_consciousness' in condition
    sweating = 'sweating' in condition
    violation_of_balance_and_coordination = 'violation_of_balance_and_coordination' in condition
    need_oxygen_support = 'need_oxygen_support' in condition

    if temperature_list_error or heart_rate_error or last_saturation_error or condition_error:
        error_context = {
            'temperature_list_error': temperature_list_error,
            'temperature_list': temperature_list,
            'heart_rate_error': heart_rate_error,
            'heart_rate': heart_rate,
            'last_saturation_error': last_saturation_error,
            'last_saturation': last_saturation,
            'condition_error': condition_error

        }
        return render_patient_condition(request, error_context)
    else:
        record = PatientRecord(patient=patient, temperature_list=temperature_list, heart_rate=heart_rate,
                               last_saturation=last_saturation, shortness_of_breath=shortness_of_breath,
                               chest_tightness=chest_tightness, vomiting=vomiting, dizziness=dizziness,
                               headache=headache, blurred_consciousness=blurred_consciousness,
                               sweating=sweating,
                               violation_of_balance_and_coordination=violation_of_balance_and_coordination,
                               need_oxygen_support=need_oxygen_support)
        record.save()
        return HttpResponseRedirect(reverse('p_patient_index'))


def render_patient_condition(request, additional_context={}):
    patient_id = int(request.user.last_name)
    patient = get_object_or_404(Patient, id=patient_id)
    patientConditionForm = PatientConditionForm()
    context = {'patient': patient,
               'patientConditionForm': patientConditionForm,
               'actions': patient.patientschedule_set.order_by('-id'),
               **additional_context
               }
    return render(request, 'patient/patient_condition.html', context)


@login_required(login_url='/hospital/login')
def get_patient_exercises(request):
    if request.method == 'POST':
        pass
    else:
        return render_patient_exercises(request)


def render_patient_exercises(request):
    patient_id = int(request.user.last_name)
    patient = get_object_or_404(Patient, id=patient_id)
    context = {'patient': patient,
               'exercises': patient.patientexercises_set.order_by('-id')
               }
    return render(request, 'patient/patient_exercises.html', context)


def change_schedule(request, schedule_id):
    if request.method == 'POST':
        schedule = get_object_or_404(PatientSchedule, id=schedule_id)
        schedule_text = request.POST['schedule']
        schedule_error = None
        if not schedule_text or schedule_text.isspace():
            schedule_error = 'Please provide schedule'

        if schedule_error:
            error_context = {
                'schedule_error': schedule_error,
            }
            return render(request, 'hospital/schedule_change.html', error_context)
        else:
            schedule.schedule = schedule_text
            schedule.save()
            return HttpResponseRedirect(reverse('patient_by_id', kwargs={'patient_id': schedule.patient.id}))
    if request.method == 'GET':
        schedule = get_object_or_404(PatientSchedule, id=schedule_id)

        context = {'schedule': schedule,
                   }
        return render(request, 'hospital/schedule_change.html', context)


def remove_schedule(request, schedule_id):
    schedule = get_object_or_404(PatientSchedule, id=schedule_id)
    patient_id = schedule.patient.id
    schedule.delete()
    return HttpResponseRedirect(reverse('patient_by_id', kwargs={'patient_id': patient_id}))


def add_new_schedule(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    schedule_text = request.POST['schedule_text']
    schedule_text_error = None
    if not schedule_text or schedule_text.isspace():
        schedule_text_error = 'Please provide text'
    if schedule_text_error:
        error_context = {
            'schedule_text_error': schedule_text_error,
            'schedule_text': schedule_text,
        }
        return render_patient(request, patient.id, error_context)
    else:
        PatientSchedule(patient=patient, schedule=schedule_text).save()
        return HttpResponseRedirect(reverse('patient_by_id', kwargs={'patient_id': patient.id}))


def change_exercise(request, exercise_id):
    if request.method == 'POST':
        exercise = get_object_or_404(PatientExercises, id=exercise_id)
        exercise_text = request.POST['exercise']
        exercise_text_error = None
        if not exercise_text or exercise_text.isspace():
            exercise_text_error = 'Please provide exercise'

        if exercise_text_error:
            error_context = {
                'exercise_text_error': exercise_text_error,
            }
            return render(request, 'hospital/exercise_change.html', error_context)
        else:
            exercise.exercise = exercise_text
            exercise.save()
            return HttpResponseRedirect(reverse('patient_by_id', kwargs={'patient_id': exercise.patient.id}))
    if request.method == 'GET':
        exercise = get_object_or_404(PatientExercises, id=exercise_id)

        context = {'exercise': exercise,
                   }
        return render(request, 'hospital/exercise_change.html', context)


def remove_exercise(request, exercise_id):
    exercise = get_object_or_404(PatientExercises, id=exercise_id)
    patient_id = exercise.patient.id
    exercise.delete()
    return HttpResponseRedirect(reverse('patient_by_id', kwargs={'patient_id': patient_id}))


def add_new_exercise(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    exercise_text = request.POST['exercise_text']
    exercise_text_error = None
    if not exercise_text or exercise_text.isspace():
        exercise_text_error = 'Please provide text'
    if exercise_text_error:
        error_context = {
            'exercise_text_error': exercise_text_error,
            'exercise_text': exercise_text,
        }
        return render_patient(request, patient.id, error_context)
    else:
        PatientExercises(patient=patient, exercise=exercise_text).save()
        return HttpResponseRedirect(reverse('patient_by_id', kwargs={'patient_id': patient.id}))


def remove_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    u = User.objects.get(username=patient.patient.username)

    patient.delete()
    u.delete()
    return HttpResponseRedirect(reverse('hospital_index'))
