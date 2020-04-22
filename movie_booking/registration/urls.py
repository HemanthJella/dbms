from .views import *
from django.urls import path
from .views import (
    MovieListView,
    MovieDetailView,
)
from django.conf.urls.static import static

urlpatterns = [
    path('login/', user_login,name='login'),
    path('signup/',signup,name='signup'),

    path('home/logout/',user_logout,name='logout'),
    #path('home/',home,name='home'),
    path('viewprofile/',viewprofile,name='viewprofile'),
    path('viewprofile/editprofile/',edit_profile,name='editprofile'),
    path('viewprofile/password/',change_password, name='change_password'),
    path('',city,name='city'),
    path('<str:city>/', main_page, name='main_page'),
    path('home/', MovieListView.as_view(), name='home'),
   # path('', MovieListView.as_view(), name='main_page'),
    path('Movie/<int:pk>/', MovieDetailView.as_view(), name='Movie-detail'),
    path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate,name='activate'),
    path('about/',about_page , name='about'),
    path('movies_events/',movies_events , name='movies_events'),
    path('contact/', contact, name='contact'),


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

