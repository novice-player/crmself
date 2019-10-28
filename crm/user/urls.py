from django.conf.urls import url
from user import views

urlpatterns = [
    url(r'^login/$', views.login,name="login"),
    url(r'^logout/$', views.logout,name="logout"),
    url(r'^register/$', views.register,name="register"),
    url(r'^home/$', views.home,name="home"),
    url(r'^home/edit/(\d+)$', views.edit,name="edit"),
    url(r'^home/customer/$', views.Customer.as_view(),name="customer"),
    url(r'^home/mycustomer/$', views.Customer.as_view(),name="mycustomer"),
    url(r'^home/add/$', views.add,name="add"),
    url(r'^followuprecords/$', views.ConsultRe.as_view(),name="followuprecords"),
    url(r'^followuprecords/add/$', views.followupadd,name="followupadd"),
    url(r'^followuprecords/edit/(\d+)$', views.followupedit,name="followupedit"),
    url(r'^enrollment/$', views.Enroll.as_view(),name="enrollment"),
    url(r'^enrollment/add/$', views.enrolladd,name="enrolladd"),
    url(r'^enrollment/edit/(\d+)$', views.enrolledit,name="enrolledit"),
    url(r'^courserecord/$', views.CourseRe.as_view(),name="courserecord"),
    url(r'^courserecord/add/$', views.courserecordadd,name="courserecordadd"),
    url(r'^courserecord/edit/(\d+)$', views.courserecordedit,name="courserecordedit"),
    url(r'^studyrecord/$', views.StudyRe.as_view(), name="studyrecord"),
]