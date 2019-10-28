from django.contrib import admin
from user import models
# Register your models here.

class UserInfoAdmin(admin.ModelAdmin):
    list_display = ['username','phone_number','email']
    # list_editable = ['id','username','phone_number','email','state_employees','depart']

class Permissions(admin.ModelAdmin):
    list_display=['id','title', 'url', 'menu','parent']
    list_editable=['title', 'url', 'menu','parent']

admin.site.register(models.UserInfo,UserInfoAdmin)
admin.site.register(models.Department)
admin.site.register(models.Customer)
admin.site.register(models.Campuses)
admin.site.register(models.ClassList)
admin.site.register(models.ConsultRecord)
admin.site.register(models.Enrollment)
admin.site.register(models.CourseRecord)
admin.site.register(models.StudyRecord)
admin.site.register(models.Permissions,Permissions)
admin.site.register(models.Roles)
admin.site.register(models.Menu)