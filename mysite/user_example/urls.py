from django.urls import path
from . import views, models
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.UserFormView2.as_view(), name='register'),
	path('autorzy', views.autorzy, name='autorzy'),
    path('admin_panel', views.admin_panel.as_view(), name='admin_panel'),
    path('wyswietl_przepisy', views.wyswietl_przepisy.as_view(), name='wyswietl_przepisy'),
    path('dodaj_przepis', views.dodaj_przepis, name='dodaj_przepis'),
    path('dodaj_przepis_test', views.dodaj_przepis_test, name='dodaj_przepis_test'),
    path('dodaj_skladnik', views.dodaj_skladnik.as_view(), name='dodaj_skladnik'),
    path('dodaj_skladnik_test', views.dodaj_skladnik_test.as_view(), name='dodaj_skladnik_test'),
    path('login/', views.login_view, name="login/"),
    path('accounts/login/', views.login_view, name="login/"),
    path('change_password', login_required(views.change_password), name='change_password'),
    path('activate/', views.activate, name='activate'),
    path('baza_skladnikow', views.baza_skladnikow.as_view(), name='baza_skladnikow'),
    path('moje_konto', login_required(views.moje_konto.as_view()), name='moje_konto'),
    path('nowy', views.PrzepisCreate.as_view(), name='nowy'),
    path('number', views.number, name='number'),
    path('ajax/', views.ajaxtest, name='test'),
    path('ajaxkk/', views.ajaxkom, name='kom'),
    path('ajaxpk/', views.ajaxpodkom, name='podkom'),
    path('ajaxkkl/', views.ajaxkomlike, name='komlike'),
    path('nowa', login_required(ListView.as_view(model=models.Przepis_skladnik)), name='nowa'),
]

#(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/
