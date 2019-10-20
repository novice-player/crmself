"""crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.pulgin, name='pulgin')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='pulgin')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from user import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', views.login,name="login"),
    url(r'^register/$', views.register,name="register"),
    url(r'^home/$', views.home,name="home"),
    url(r'^home/edit/(\d)$', views.edit,name="edit"),
    url(r'^home/index/$', views.index,name="index"),
    url(r'^home/add/$', views.add,name="add"),
]

