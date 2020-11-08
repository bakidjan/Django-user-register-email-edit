"""diallo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponseRedirect

from . import view

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # Les deux pages HTML demandées
    path(r'index/', csrf_exempt(view.HTMLPages.index)),
    path(r'authentified/', csrf_exempt(view.HTMLPages.authentified)),

    # API
    path(r'create_user/', csrf_exempt(view.Server.create_user)),
    path(r'change_email/', csrf_exempt(view.Server.change_email)),
    path(r'loggin/', csrf_exempt(view.Server.loggin)),
    path(r'loggout/', csrf_exempt(view.Server.loggout)),

    # Default redirection
    path(r'', lambda r: HttpResponseRedirect('index/')),
] 

