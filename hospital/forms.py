from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=64)
    password = forms.CharField(label='Password', max_length=128, widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=64)
    email = forms.EmailField(label='E-Mail', max_length=128)
    password = forms.CharField(label='Password', min_length=3, max_length=128, widget=forms.PasswordInput)
    password_again = forms.CharField(label='Password, again', min_length=3, max_length=128, widget=forms.PasswordInput)


class NewPatientForm(forms.Form):
    first_name = forms.CharField(label='Имя', max_length=40)
    last_name = forms.CharField(label='Фамилия', max_length=40)
    middle_name = forms.CharField(label='Отчество', max_length=40)
    address = forms.CharField(label='Адрес', max_length=200)
    covid = forms.ChoiceField(widget=forms.RadioSelect, choices=[
        ('1', 'ковид лёгкой степени'),
        ('2', 'ковид средней степени'),
        ('3', 'ковид тяжёлой степени')])
    lung_damage = forms.FloatField(label='Процент поражения лёгочной ткани')


class CovidForm(forms.Form):
    covid = forms.ChoiceField(widget=forms.RadioSelect, choices=[
        ('1', 'ковид лёгкой степени'),
        ('2', 'ковид средней степени'),
        ('3', 'ковид тяжёлой степени')])


class MainPageSortFormHospital(forms.Form):
    sort_by = forms.ChoiceField(widget=forms.RadioSelect, choices=[('1', 'ФИО'), ('2', 'Время поступления')],
                                initial='1')


BIRTH_YEAR_CHOICES = range(1920, 2022)
BIRTH_MOUTH_CHOICES = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь', 7: 'Июль',
                       8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}


class DateForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES, months=BIRTH_MOUTH_CHOICES))


class PatientConditionForm(forms.Form):
    OPTIONS = (
        ("shortness_of_breath", "Наличие одышки"),
        ("chest_tightness", "Чувство стеснения в груди"),
        ("vomiting", "Рвота"),
    )
    condition = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          choices=OPTIONS)
