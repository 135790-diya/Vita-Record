from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.landing,           name='landing'),
    path('register/',                 views.register,          name='register'),
    path('login/',                    views.user_login,        name='login'),
path('logout/',                   views.user_logout,       name='logout'),
    path('dashboard/',                views.dashboard_redirect, name='dashboard_redirect'),
    path('patient/dashboard/',        views.patient_dashboard,  name='patient_dashboard'),
    path('doctor/dashboard/',         views.doctor_dashboard,   name='doctor_dashboard'),
    path('search/',                   views.search_patient,     name='search_patient'),
    path('consultation/<str:unique_id>/', views.consultation,   name='consultation'),
]
