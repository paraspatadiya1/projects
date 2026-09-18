from django.urls import path
from patientapp import views
urlpatterns = [
    path('',views.home,name='home'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    
]
