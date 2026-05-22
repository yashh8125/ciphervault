from django.urls import path
from . import views

urlpatterns = [
    path('',                views.dashboard,         name='dashboard'),
    path('register/',       views.register_view,     name='register'),
    path('login/',          views.login_view,        name='login'),
    path('logout/',         views.logout_view,       name='logout'),
    path('add/',            views.add_password,      name='add_password'),
    path('delete/<int:pk>/',views.delete_password,   name='delete_password'),
    path('generate/',       views.generate_password, name='generate_password'),
    path('breach/',         views.check_breach,      name='check_breach'),
]
