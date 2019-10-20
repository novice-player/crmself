from django.shortcuts import render,HttpResponse,redirect
from django import forms
from django.core.validators import RegexValidator
from user import models
from django.core.exceptions import ValidationError
from utils import md5_components
from django.http import JsonResponse
from multiselectfield.forms.fields import MultiSelectFormField

# Create your views here.
class CustomerFrom(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ['name','sex','birthday','qq','phone','course','status']
        labels = {
            'name':'姓名',
            'sex':'性别',
            'birthday':'出生日期',
            'qq':'QQ',
            'phone':'电话',
            'course':'咨询课程',
            'status':'状态'
        }
        widgets = {
           'birthday':forms.widgets.DateInput({"type":"date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})

class RegForm(forms.Form):
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

def register(request):
    """
    注册
    :param request:
    :return:
    """
    form_reg_obj = RegForm()
    if request.method == "POST":
        form_reg_obj = RegForm(request.POST)
        if form_reg_obj.is_valid():
            ret = request.POST.dict()
            ret.pop("csrfmiddlewaretoken")
            ret.pop("confirm_password")
            md5_pwd = md5_components.md5_func(ret.get("password"))
            ret.update(password=md5_pwd)
            models.UserInfo.objects.create(**ret)
            return redirect("login")
    return render(request, 'register.html', {'form_reg_obj': form_reg_obj})

def login(request):
    """
    登录
    :param request:
    :return:
    """
    info_msg = {"status":None,"errorinfo":None,"home":None}
    if request.method == "POST":
        ret = request.POST.dict()
        # 用户名和密码校验
        ret_info = models.UserInfo.objects.filter(username=ret.get("username"),password=md5_components.md5_func(ret.get("password"))).first()
        if ret_info:
            info_msg["status"] = 1
            info_msg["home"] = "/home"
            return JsonResponse(info_msg)
        else:
            info_msg["status"] = 0
            info_msg["errorinfo"] = "用户名或密码错误"
            return JsonResponse(info_msg)
    return render(request, 'login.html')

def home(request):
    """主页"""
    return render(request,'home/starter.html')

def index(request):
    """
    客户信息
    :param request:
    :return:
    """
    cust_obj = models.Customer.objects.all()
    return render(request, 'home/index.html', {"cust_obj": cust_obj})

def add(request):
    """
    客户添加
    :param request:
    :return:
    """
    header_info = {"add":"客户信息添加","edit":"客户信息修改"}
    customer_obj = CustomerFrom()
    if request.method == "POST":
        addret = request.POST.dict()
        print(addret)
        addret.pop("csrfmiddlewaretoken")
        models.Customer.objects.create(**addret)
        return redirect("/home/index")
    return render(request, 'home/write.html', {"header_info": header_info, "customer_obj": customer_obj})

def edit(request,id=None):
    """
    客户信息修改
    :param request:
    :param id:
    :return:
    """
    header_info = {"add":"客户信息添加","edit":"客户信息修改"}
    model_obj = models.Customer.objects.filter(id=id).first()
    customer_obj = CustomerFrom(instance=model_obj)     # 不写instance是创建，写了是更新
    if request.method == "POST":
        customer_obj = CustomerFrom(request.POST,instance=model_obj)
        customer_obj.save()
        return redirect("/home/index")
    return render(request, 'home/write.html', {"header_info": header_info, "customer_obj": customer_obj})



