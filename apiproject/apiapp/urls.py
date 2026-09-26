from django.urls import path
from apiapp import views

urlpatterns = [
    # Dashboard & UI
    path('', views.index, name='index'),

    # Student REST Endpoints
    path('getall/', views.getall, name='getall'),
    path('getall', views.getall),
    path('getid/<int:id>/', views.getid, name='getid'),
    path('getid/<int:id>', views.getid),
    path('addstudent/', views.addstudent, name='addstudent'),
    path('addstudent', views.addstudent),
    path('updateid/<int:id>/', views.updateid, name='updateid'),
    path('updateid/<int:id>', views.updateid),
    path('deleteid/<int:id>/', views.deleteid, name='deleteid'),
    path('deleteid/<int:id>', views.deleteid),

    # Course REST Endpoints
    path('getcourse/', views.getcourse, name='getcourse'),
    path('getcourse', views.getcourse),
    path('getcourseid/<int:id>/', views.getcourseid, name='getcourseid'),
    path('getcourseid/<int:id>', views.getcourseid),
    path('addcourse/', views.addcourse, name='addcourse'),
    path('addcourse', views.addcourse),
    path('updatecourse/<int:id>/', views.updatecourse, name='updatecourse'),
    path('updatecourse/<int:id>', views.updatecourse),
    path('deletecourse/<int:id>/', views.deletecourse, name='deletecourse'),
    path('deletecourse/<int:id>', views.deletecourse),

    # Real-time System Analytics & API Docs
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/stats', views.api_stats),
    path('api-docs/', views.api_docs_view, name='api_docs'),
    path('api-docs', views.api_docs_view),
]



