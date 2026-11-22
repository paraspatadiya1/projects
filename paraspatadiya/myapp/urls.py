from django.urls import path
from . import views
from .views import contact_submit


urlpatterns = [
    path('', views.index, name='index'),
    path("contact/", contact_submit, name="contact_submit"),

    

]