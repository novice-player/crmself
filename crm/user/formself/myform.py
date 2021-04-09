from django.shortcuts import render, HttpResponse, redirect
from django import forms
from user import models
from django.core.exceptions import ValidationError
from multiselectfield.forms.fields import MultiSelectFormField


class CustomerFrom(forms.ModelForm):
    """
    客户信息展示
    """

    class Meta:
        model = models.Customer
        fields = '__all__'
        widgets = {
            'birthday': forms.widgets.DateInput({"type": "date"}),
            'date': forms.widgets.DateInput({"type": "date"}),
            'last_consult_date': forms.widgets.DateInput({"type": "date"}),
            'next_date': forms.widgets.DateInput({"type": "date"}),
            'deal_date': forms.widgets.DateInput({"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})


class RegForm(forms.Form):
    """
    注册信息展示
    """
    username = forms.CharField(
        required=True,
        label="",
        min_length=4,
        max_length=10,
        widget=forms.widgets.TextInput(
            attrs={"class": "username", "placeholder": "您的用户名", "autocomplete": "off",
                   "oncontextmenu": "return false"}),
        error_messages={
            "min_length": "长度最短4位",
            "max_length": "长度最长10位",
            'required': '内容不能为空'
        }
    )

    password = forms.CharField(
        label="",
        min_length=6,
        max_length=10,
        widget=forms.widgets.TextInput(
            attrs={"class": "password", "placeholder": "输入密码", "oncontextmenu": "return false"}),
        error_messages={
            "min_length": "长度最短6位",
            "max_length": "长度最长10位",
            'required': '内容不能为空'
        }
    )
    confirm_password = forms.CharField(
        label="",
        widget=forms.widgets.TextInput(
            attrs={"class": "confirm_password", "placeholder": "再次输入密码", "oncontextmenu": "return false",
                   "onpaste": "return false"}),
        error_messages={
            'required': '内容不能为空'
        }
    )
    phone_number = forms.CharField(
        label="",
        max_length=11,
        min_length=11,
        widget=forms.widgets.TextInput(
            attrs={"class": "phone_number", "placeholder": "输入手机号码", "autocomplete": "off"}),
        error_messages={
            "min_length": "长度最短11位",
            "max_length": "长度最长11位",
            'required': '内容不能为空'
        }
    )
    email = forms.EmailField(
        label="",
        widget=forms.widgets.EmailInput(
            attrs={"class": "email", "placeholder": "输入邮箱地址", "oncontextmenu": "return false"}),
        error_messages={
            "invalid": "邮箱格式不符合",
            'required': '内容不能为空'
        }
    )

    # def __init__(self,*args,**kwargs):
    #     super().__init__(*args,**kwargs)
    #     for field in self.fields.values():
    #         field.error_messages = {'required':'内容不能为空'}

    # 校验两次密码输入是否相同
    def clean(self):
        password_value = self.cleaned_data.get("password")
        confirm_password_value = self.cleaned_data.get("confirm_password")
        if password_value == confirm_password_value:
            return self.cleaned_data
        else:
            self.add_error('confirm_password', '两次密码不一致')
            raise ValidationError('两次密码不一致')


class ConsultRecordFrom(forms.ModelForm):
    """
    客户跟踪记录展示
    """

    class Meta:
        model = models.ConsultRecord
        fields = '__all__'
        exclude = ['delete_status', ]
        labels = {
            'customer': '咨询客户',
            'note': '跟进内容',
            'status': '跟进状态',
            'consultant': '跟进人',
            'date': '跟进时间',
        }
        widgets = {
            'date': forms.widgets.DateInput({"type": "date"}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

            # 根据销售名称筛选客户名称
            if field_name == 'customer':
                field.queryset = models.Customer.objects.filter(consultant__username=request.session.get('uname'))

            # 根据登录用户筛选销售名称
            if field_name == 'consultant':
                field.queryset = models.UserInfo.objects.filter(username=request.session.get('uname'))


class EnrollMentFrom(forms.ModelForm):
    """
    报名记录信息展示
    """

    class Meta:
        model = models.Enrollment
        fields = '__all__'
        exclude = ['delete_status', 'contract_approved']

        widgets = {
            'enrolled_date': forms.widgets.DateInput({"type": "date"}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class CourseReFrom(forms.ModelForm):
    """
    课程记录展示
    """

    class Meta:
        model = models.CourseRecord
        fields = '__all__'
        widgets = {
            'date': forms.widgets.DateInput({"type": "date"}),
            'has_homework': forms.widgets.NullBooleanSelect(),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class StudyRecordFrom(forms.ModelForm):
    """
    学习记录
    """

    class Meta:
        model = models.StudyRecord
        fields = '__all__'



class RoleFrom(forms.ModelForm):
    """
    角色管理
    """

    class Meta:
        model = models.Roles
        fields = '__all__'
        labels = {
            'name':'名称',
            'permissions':'权限'
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class MenuFrom(forms.ModelForm):
    """
    菜单管理
    """

    class Meta:
        model = models.Menu
        fields = '__all__'
        labels = {
            'title':'名称',
            'icon':'图标',
            'weight':'权重'
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class PermissionsForm(forms.ModelForm):
    """
    权限信息管理
    """

    class Meta:
        model = models.Permissions
        fields = '__all__'
        widgets = {
            'menus':forms.widgets.NullBooleanSelect(),
            'parent':forms.widgets.SelectMultiple()
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})



