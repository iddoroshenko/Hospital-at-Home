from django.urls import path
from . import views


urlpatterns = [
    path('login', views.log_in, name='login'),
    path('signup', views.sign_up, name='signup'),
    path('logout', views.log_out, name='logout'),

    path('d/list_patient', views.get_patient_list, name='hospital_index'),
    path('d/patient/<int:patient_id>', views.patient, name='patient_by_id'),
    path('d/new_patient', views.add_new_patient, name='new_patient'),
    path('d/record/<int:record_id>', views.record, name='record_by_id'),

    path('p/mainpage', views.get_patient_mainpage, name='p_patient_index'),
    path('p/schedule', views.get_patient_schedule, name='p_patient_schedule'),
    path('p/condition', views.get_patient_condition, name='p_patient_condition'),
    path('p/exercises', views.get_patient_exercises, name='p_patient_exercises'),
]
