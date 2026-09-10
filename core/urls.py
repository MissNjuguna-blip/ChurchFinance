from django.urls import path,include
from core import views
 
urlpatterns = [
    path('register/',views.register),
    path('login/',views.login),
    path('logout/',views.logout),
    path('admin-dashboard/',views.admin_dashboard)
]