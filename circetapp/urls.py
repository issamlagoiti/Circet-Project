"""
URL configuration for circet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
#from .views import demande_details_view, question_details_view, fin_questionnaire_view, sign_in, signout, sign_up_view, enregistrer_parcours_view
#from .views import CustomPasswordChangeView


urlpatterns = [
    
    path('sign_in/', sign_in, name='sign_in'),
    path('signout/', signout, name='signout'),
    path('sign_up/', sign_up_view, name='sign_up'),
    path('changer-mot-de-passe/', change_password_view, name='change_password'),
    path('profil/', profile_view, name='profile_view'),
    path('demande/', demande_details_view, name='demande_details'),
    path('demande/<int:demande_id>/', demande_details_view, name='demande_details'),
    path('question/<int:question_id>/', question_details_view, name='question_details'),
    path('fin_questionnaire/', fin_questionnaire_view, name='fin_questionnaire'),
    path('enregistrer_parcours/', enregistrer_parcours_view, name='enregistrer_parcours'),
    path('parcours/', parcours_view, name='parcours_view'),
    path('add_demande/', add_demande, name='add_demande'),
    path('calendrier/', calendrier, name='calendrier'),
    path('contacts', contacts, name='contacts'),
    path('search_demandes/', search_demandes, name='search_demandes'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)