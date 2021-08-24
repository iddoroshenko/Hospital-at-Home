from django.urls import path
from . import views


urlpatterns = [
    path('login', views.log_in, name='login'),
    path('logout', views.log_out, name='logout'),

    path('d/list_patient', views.get_patient_list, name='hospital_index'),
    path('d/patient/<int:patient_id>', views.patient, name='patient_by_id'),
    path('d/new_patient', views.add_new_patient, name='new_patient'),
    path('d/record/<int:record_id>', views.record, name='record_by_id'),

    path('d/change_schedule/<int:schedule_id>', views.change_schedule, name='change_schedule'),
    path('d/remove_schedule/<int:schedule_id>', views.remove_schedule, name='remove_schedule'),

    path('d/change_exercise/<int:exercise_id>', views.change_exercise, name='change_exercise'),
    path('d/remove_exercise/<int:exercise_id>', views.remove_exercise, name='remove_exercise'),

    path('p/mainpage', views.get_patient_mainpage, name='p_patient_index'),
    path('p/schedule', views.get_patient_schedule, name='p_patient_schedule'),
    path('p/condition', views.get_patient_condition, name='p_patient_condition'),
    path('p/exercises', views.get_patient_exercises, name='p_patient_exercises'),
]
