from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import *
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models


class Patient(Model):
    doctor = ForeignKey(User, on_delete=CASCADE, default=1)
    patient = ForeignKey(User, on_delete=CASCADE, default=1, related_name='user_patient')

    first_name = CharField('Имя', max_length=40)
    last_name = CharField('Фамилия', max_length=40)
    middle_name = CharField('Отчество', max_length=40)
    birth = DateTimeField('Дата рождения')
    created_at = DateTimeField('Создание пациента', auto_now_add=True)
    address = TextField('Адрес', max_length=100)
    covid_grade = models.CharField('Степень тяжести', max_length=1, choices=[
        ('1', 'low'),
        ('2', 'middle'),
        ('3', 'high')])
    lung_damage = FloatField('Процент поражения лёгочной ткани', default=0.0)


class PatientRecord(Model):
    patient = ForeignKey(Patient, on_delete=CASCADE)
    created_at = DateTimeField('Время создания записи', auto_now_add=True)

    temperature_list = TextField('Температура тела каждую минуту', default='-1')
    heart_rate = TextField('Частота сердечных сокращений каждую минуту', default='-1')
    last_saturation = TextField('Сатурация каждую минуту', default='-1')

    shortness_of_breath = BooleanField('Наличие одышки', default=False)
    chest_tightness = BooleanField('Чувство стеснения в груди', default=False)
    vomiting = BooleanField('Рвота', default=False)
    dizziness = BooleanField('Головокружения', default=False)
    headache = BooleanField('Головная боль', default=False)
    blurred_consciousness = BooleanField('Помутнение сознания', default=False)
    sweating = BooleanField('Потливость', default=False)
    violation_of_balance_and_coordination = BooleanField('Нарушение равновесия и координации', default=False)
    need_oxygen_support = BooleanField('Потребность в кислородной поддержке', default=False)

