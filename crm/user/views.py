from django.shortcuts import render, HttpResponse, redirect
from user import models
from utils import md5_components
from django.http import JsonResponse
from utils.page_component import Paging
from django.urls import reverse
from django.db.models import Q
from django.views import View
from urllib.parse import urlencode
from user.formself.myform import RegForm, CustomerFrom, ConsultRecordFrom, EnrollMentFrom,CourseReFrom,StudyRecordFrom
from django.db import transaction
from django.forms.models import modelformset_factory
from collections import OrderedDict


# Create your views here.

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

            # md5加密
            md5_pwd = md5_components.md5_func(ret.get("password"))

            ret.update(password=md5_pwd)
            models.UserInfo.objects.create(**ret)
            return redirect(reverse('user:login'))
    return render(request, 'the_user/register.html', {'form_reg_obj': form_reg_obj})


def login(request):
    """
    登录
    :param request:
    :return:
    """
    info_msg = {"status": None, "errorinfo": None, "home": None}
    if request.method == "POST":
        ret = request.POST.dict()
        uname = ret.get("username")
        pwd = md5_components.md5_func(ret.get("password"))
        # 用户名和密码校验
        ret_info = models.UserInfo.objects.filter(username=uname, password=pwd).first()
        if ret_info:
            info_msg["status"] = 1
            info_msg["home"] = reverse('user:home')

            # 登录成功后提取用户权限注入到session中
            user_url = ret_info.role.values('permissions__pk','permissions__url','permissions__title',
                                            'permissions__menu__pk','permissions__parent__pk','permissions__menu__title',
                                            'permissions__menu__icon','permissions__menu__weight').distinct()
            # url列表信息
            permission_list = []

            # 左侧菜单信息
            menu_dict = {}

            for msg in user_url:
                permission_list.append({'url':msg["permissions__url"]})

                # 拼接数据
                if msg.get("permissions__menu__pk"):
                    if msg.get("permissions__menu__pk") in menu_dict:
                        menu_dict[msg.get('permissions__menu__pk')]['childen'].append(
                            {
                                'title':msg.get('permissions__title'),
                                'url':msg.get('permissions__url'),
                                'id':msg.get('permissions__pk'),
                                'class_msg': ''
                            }
                        )
                    else:
                        menu_dict[msg.get('permissions__menu__pk')] = {
                            'title':msg['permissions__menu__title'],
                            'icon':msg['permissions__menu__icon'],
                            'weight':msg['permissions__menu__weight'],
                            'childen':[
                                {
                                    'title': msg.get('permissions__title'),
                                    'url': msg.get('permissions__url'),
                                    'id': msg.get('permissions__pk'),
                                    'class_msg': ''
                                },
                            ]
                        }

            # 左侧菜单排序(有序字典排序)
            order_dict = OrderedDict()
            keys_list = sorted(menu_dict,key=lambda x:menu_dict[x]['weight'],reverse=True)
            for key in keys_list:
                order_dict[key] = menu_dict[key]

            request.session['permissions'] = permission_list
            request.session['menu_dict'] = order_dict
            request.session["uname"] = uname

            return JsonResponse(info_msg)
        else:
            info_msg["status"] = 0
            info_msg["errorinfo"] = "用户名或密码错误"
            return JsonResponse(info_msg)
    return render(request, 'the_user/login.html')


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    request.session.flush()
    return redirect(reverse("user:login"))


def home(request):
    """主页"""
    return render(request, 'customer_page/starter.html')


class Customer(View):
    """
    客户信息
    """

    def get(self, request):
        cust_obj = models.Customer.objects.all()
        path = request.path
        request.session["page"] = ''
        if request.GET.get('page'):
            request.session["page"] = request.GET.get('page')
        request.session["search_url"] = ''
        if path == reverse('user:customer'):
            # 公户信息
            cust_obj = cust_obj.filter(consultant__isnull=True)
            header_info = "公共客户信息展示"
            change_info = "gs"
        else:
            # 私户信息
            cust_obj = cust_obj.filter(consultant__username=request.session.get("uname"))
            header_info = "我的客户信息展示"
            change_info = "sg"

        # 搜索
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')
        base_url = ''
        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field + "__contains", kw))
            cust_obj = cust_obj.filter(q_obj)

            # 搜索关键字进行url编码
            base_url = {}
            base_url["search_field"] = search_field
            base_url["kw"] = kw
            base_url = urlencode(base_url)
            request.session["search_url"] = base_url
        page = Paging(request.GET.get("page"), cust_obj.count(), base_url)
        return render(request, 'customer_page/customer.html',
                      {"header_info": header_info, "cust_obj": cust_obj[page.start:page.end],
                       "page_html": page.page_html, "change_info": change_info, "search_field": search_field,
                       "kw": kw})

    def post(self, request):
        change_of_owner = request.POST.get('change_of_owner')
        change_msg = request.POST.getlist('change_msg')
        current_user = models.UserInfo.objects.filter(username=request.session.get("uname")).first()
        # 公户转私户
        if change_of_owner == "gs":
            with transaction.atomic():
                customers = models.Customer.objects.filter(id__in=change_msg, consultant__isnull=True)
                if customers.count() != len(change_msg):
                    lst = []
                    for obj in customers:
                        change_msg.remove(str(obj.id))
                    customers = models.Customer.objects.filter(id__in=change_msg)
                    for cust_obj in customers:
                        lst.append(cust_obj.name)
                    error_msg = ','.join(lst)
                    return render(request, 'customer_page/customer.html', {'error_msg': error_msg, 'show_msg': 'show'})
                customers.update(consultant_id=current_user.id)
            return redirect(reverse('user:customer'))
        # 私户转公户
        elif change_of_owner == "sg":
            models.Customer.objects.filter(id__in=change_msg).update(consultant_id=None)
            return redirect(reverse('user:mycustomer'))


# def customer(request):
#     """
#     客户信息
#     :param request:
#     :return:
#     """
#     cust_obj = models.Customer.objects.all()
#     path = request.path
#     if path == reverse('customer'):
#         # 公户信息
#         cust_obj = cust_obj.filter(consultant__isnull=True)
#         header_info = "公共客户信息展示"
#         change_info = "gs"
#     else:
#         # 私户信息
#         cust_obj = cust_obj.filter(consultant__username=request.session.get("uname"))
#         header_info = "我的客户信息展示"
#         change_info = "sg"
#
#     get_data = request.GET.copy()
#     search_field = request.GET.get('search_field')
#     kw = request.GET.get('kw')
#     print(search_field, kw)
#     if kw:
#         kw = kw.strip()
#         q_obj = Q()
#         q_obj.children.append((search_field, kw))
#         cust_obj = cust_obj.filter(q_obj)
#
#
#     # # 获取第几页
#     # try:
#     #     page_num = int(request.GET.get("page"))
#     #     if page_num <= 0:
#     #         page_num = 1
#     # except Exception:
#     #     page_num = 1
#     #
#     # # 每页条数
#     # number_each_page = 2
#     #
#     # # 总数据量
#     # total_number = cust_obj.count()
#     #
#     # # 总页数
#     # # divmod(a,b) 返回一个包含商和余数的元组
#     # page_count,more = divmod(total_number,number_each_page)
#     # if more:
#     #     page_count += 1
#     #
#     #  # 最大显示页码数量
#     # max_page = 3
#     # half_page= max_page // 2
#     #
#     # # 控制显示页码数量
#     # if page_count <= max_page:
#     #     page_start = 1
#     #     page_end = page_count
#     # else:
#     #     if page_num <= half_page:
#     #         page_start = 1
#     #         page_end = max_page
#     #     elif page_num + half_page >= page_count:
#     #         page_start = page_count - max_page + 1
#     #         page_end = page_count
#     #     else:
#     #         page_start = page_num - half_page
#     #         page_end = page_num + half_page
#     #
#     # # 控制页数不低于1,利用列表生成HTML，在前端展示
#     # page_list = []
#     # if page_num == 1:
#     #     page_list.append(f'<li class="disabled"><a href="?page={page_num}">上一页</a></li>')
#     # else:
#     #     page_list.append(f'<li><a href="?page={page_num - 1}">上一页</a></li>')
#     #
#     # for page in range(page_start,page_end + 1):
#     #     page_list.append(f'<li><a href="?page={page}">{page}</a></li>')
#     #
#     # # 控制页数不超过总页数
#     # if page_num == page_count:
#     #     page_list.append(f'<li class="disabled"><a href="?page={page_count}">下一页</a></li>')
#     # else:
#     #     page_list.append(f'<li ><a href="?page={page_num + 1}">下一页</a></li>')
#     #
#     # page_html = "".join(page_list)
#     page = Paging(request.GET.get("page"),cust_obj.count())
#
#     return render(request, 'home/customer.html', {"header_info":header_info,"cust_obj": cust_obj[page.start:page.end],
#                                                   "page_html":page.page_html,"change_info":change_info})

def add(request):
    """
    客户添加
    :param request:
    :return:
    """
    header_info = {"add": "客户信息添加", "edit": "客户信息修改"}
    customer_obj = CustomerFrom()
    if request.method == "POST":
        addret = request.POST.dict()
        addret.pop("csrfmiddlewaretoken")
        models.Customer.objects.create(**addret)
        return redirect(reverse('user:customer'))
    return render(request, 'customer_page/write.html',
                  {"header_info": header_info['add'], "customer_obj": customer_obj})


def edit(request, id=None):
    """
    客户信息修改
    :param request:
    :param id:
    :return:
    """
    header_info = {"add": "客户信息添加", "edit": "客户信息修改"}
    model_obj = models.Customer.objects.filter(id=id).first()
    use_status = model_obj.consultant  # 获取销售信息
    customer_obj = CustomerFrom(instance=model_obj)  # 不写instance是创建，写了是更新
    if request.method == "POST":
        customer_obj = CustomerFrom(request.POST, instance=model_obj)
        customer_obj.save()
        customer_url = reverse('user:customer')

        # 判断销售是否为空，确定返回的URL
        if use_status:
            customer_url = reverse('user:mycustomer')

        # 拼接URL(页码+搜索关键字)，保证返回上一次的页面
        customer_url = f"{customer_url}?page={request.session.get('page')}&{request.session.get('search_url')}"
        return redirect(customer_url)
    return render(request, 'customer_page/write.html',
                  {"header_info": header_info['edit'], "customer_obj": customer_obj})


def followup(request):
    return render(request, 'consul_trecord/followup.html')


class ConsultRe(View):
    """
    跟进记录展示
    """

    def get(self, request):
        record_obj = models.ConsultRecord.objects.filter(consultant__username=request.session.get('uname'),
                                                         delete_status=False)
        request.session["page"] = ''
        if request.GET.get('page'):
            request.session["page"] = request.GET.get('page')
        request.session["search_url"] = ''
        base_url = ''
        # 单个用户跟进详情(根据名字进行筛选)
        cname = request.GET.get('cname')
        if cname:
            qid_obj = Q()
            qid_obj.children.append(('customer__name', cname))
            record_obj = record_obj.filter(qid_obj)
            base_url = {}
            base_url["cname"] = cname
            base_url = urlencode(base_url)
            request.session["search_url"] = base_url

        # 搜索
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')

        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field + "__contains", kw))
            record_obj = record_obj.filter(q_obj)

            # 搜索关键字进行url编码
            base_url = {}
            base_url["search_field"] = search_field
            base_url["kw"] = kw
            base_url = urlencode(base_url)
            request.session["search_url"] = base_url
        page = Paging(request.GET.get("page"), record_obj.count(), base_url)
        return render(request, 'consul_trecord/followup.html',
                      {"record_obj": record_obj[page.start:page.end], "page_html": page.page_html,
                       "search_field": search_field, "kw": kw})

    def post(self, request):
        change_of_owner = request.POST.get('change_of_owner')
        change_msg = request.POST.getlist('change_msg')
        # 更改客户跟进状态
        if change_of_owner == "delete":
            models.ConsultRecord.objects.filter(id__in=change_msg).update(delete_status=True)
            return redirect(reverse('user:followuprecords'))


def followupadd(request):
    """
    跟踪记录添加
    :param request:
    :return:
    """
    header_info = {"add": "客户跟踪记录添加", "edit": "客户跟踪记录修改"}
    consul_obj = ConsultRecordFrom(request)
    if request.method == "POST":
        addret = request.POST.dict()
        addret.pop("csrfmiddlewaretoken")

        # 获取customer和consultant的Queryset对象
        customer_obj = models.Customer.objects.filter(id=addret['customer']).first()
        consultant_obj = models.UserInfo.objects.filter(id=addret['consultant']).first()

        # 替换数据
        addret['customer'] = customer_obj
        addret['consultant'] = consultant_obj

        # 增加记录
        models.ConsultRecord.objects.create(**addret)
        return redirect(reverse('user:followuprecords'))
    return render(request, 'consul_trecord/write.html',
                  {"header_info": header_info['add'], "consultre_obj": consul_obj})


def followupedit(request, id=None):
    """
    跟踪记录修改
    :param request:
    :param id:
    :return:
    """
    header_info = {"add": "客户跟踪记录添加", "edit": "客户跟踪记录修改"}
    model_obj = models.ConsultRecord.objects.filter(id=id).first()
    consultre_obj = ConsultRecordFrom(request, instance=model_obj)  # 不写instance是创建，写了是更新
    if request.method == "POST":
        customer_obj = ConsultRecordFrom(request, request.POST, instance=model_obj)
        customer_obj.save()
        customer_url = reverse('user:followuprecords')

        # 拼接URL(页码+搜索关键字)，保证返回上一次的页面
        customer_url = f"{customer_url}?page={request.session.get('page')}&{request.session.get('search_url')}"
        return redirect(customer_url)
    return render(request, 'consul_trecord/write.html',
                  {"header_info": header_info['edit'], "consultre_obj": consultre_obj})


class Enroll(View):
    """
    报名表记录
    """

    def get(self, request):
        enroll_objs = models.Enrollment.objects.filter(delete_status=False)
        request.session["page"] = ''
        if request.GET.get('page'):
            request.session["page"] = request.GET.get('page')
        request.session["search_url"] = ''
        base_url = ''

        # 搜索
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')

        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field + "__contains", kw))
            enroll_objs = enroll_objs.filter(q_obj)

            # 搜索关键字进行url编码
            base_url = {}
            base_url["search_field"] = search_field
            base_url["kw"] = kw
            base_url = urlencode(base_url)
            request.session["search_url"] = base_url
        page = Paging(request.GET.get("page"), enroll_objs.count(), base_url)
        return render(request, 'enroll/enrollment.html',
                      {"enroll_objs": enroll_objs[page.start:page.end], "page_html": page.page_html,
                       "search_field": search_field, "kw": kw})

    def post(self, request):
        change_of_owner = request.POST.get('change_of_owner')
        change_msg = request.POST.getlist('change_msg')
        # 更改客户跟进状态
        if change_of_owner == "delete":
            models.Enrollment.objects.filter(id__in=change_msg).update(delete_status=True)
            return redirect(reverse('user:enrollment'))


def enrolladd(request):
    """
    报名表记录添加
    :param request:
    :return:
    """
    header_info = {"add": "报名记录添加", "edit": "报名记录修改"}
    enrolment_obj = EnrollMentFrom(request)
    if request.method == "POST":
        addret = request.POST.dict()
        addret.pop("csrfmiddlewaretoken")

        # 获取customer和Campuses和ClassList的Queryset对象
        customer_obj = models.Customer.objects.filter(id=addret['customer']).first()
        school_obj = models.Campuses.objects.filter(id=addret['school']).first()
        enrolment_class_obj = models.ClassList.objects.filter(id=addret['enrolment_class']).first()

        # 替换数据
        addret['customer'] = customer_obj
        addret['school'] = school_obj
        addret['enrolment_class'] = enrolment_class_obj

        # 增加记录
        models.Enrollment.objects.create(**addret)
        return redirect(reverse('user:enrollment'))
    return render(request, 'enroll/write.html',
                  {"header_info": header_info['add'], "enrolment_obj": enrolment_obj})


def enrolledit(request, id=None):
    """
    报名表记录修改
    :param request:
    :param id:
    :return:
    """
    header_info = {"add": "客户跟踪记录添加", "edit": "客户跟踪记录修改"}
    model_obj = models.Enrollment.objects.filter(id=id).first()
    enrolment_obj = EnrollMentFrom(request, instance=model_obj)  # 不写instance是创建，写了是更新
    if request.method == "POST":
        enroll_obj = EnrollMentFrom(request, request.POST, instance=model_obj)
        enroll_obj.save()
        enroll_url = reverse('user:enrollment')

        # 拼接URL(页码+搜索关键字)，保证返回上一次的页面
        enroll_url = f"{enroll_url}?page={request.session.get('page')}&{request.session.get('search_url')}"
        return redirect(enroll_url)
    return render(request, 'enroll/write.html',
                  {"header_info": header_info['edit'], "enrolment_obj": enrolment_obj})


class CourseRe(View):
    """
    课程记录
    """

    def get(self, request):
        coursere_obj = models.CourseRecord.objects.all()
        request.session["page"] = ''
        if request.GET.get('page'):
            request.session["page"] = request.GET.get('page')
        request.session["search_url"] = ''
        base_url = ''

        # 搜索
        search_field = request.GET.get('search_field')
        kw = request.GET.get('kw')

        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field + "__contains", kw))
            coursere_obj = coursere_obj.filter(q_obj)

            # 搜索关键字进行url编码
            base_url = {}
            base_url["search_field"] = search_field
            base_url["kw"] = kw
            base_url = urlencode(base_url)
            request.session["search_url"] = base_url
        page = Paging(request.GET.get("page"), coursere_obj.count(), base_url)
        return render(request, 'courserecord/courserecor.html',
                      {"coursere_obj": coursere_obj[page.start:page.end], "page_html": page.page_html,
                       "search_field": search_field, "kw": kw})

    def post(self, request):
        change_of_owner = request.POST.get('change_of_owner')
        change_msg = request.POST.getlist('change_msg')
        # 批量创建学习记录
        if hasattr(self,change_of_owner):
            getattr(self,change_of_owner)(request,change_msg)

            return redirect(reverse('user:courserecord'))

    def bulk_create(self,request,cids):
        """
        批量生产学习记录
        :param request:
        :param cids:
        :return:
        """
        for id in cids:
            ret_obj = models.CourseRecord.objects.filter(pk=id).first()
            studings = ret_obj.re_class.customer_set.filter(status='signed')
            obj_lst = []
            for student in studings:
                obj = models.StudyRecord(
                    course_record_id = id,
                    student = student
                )
                obj_lst.append(obj)
            models.StudyRecord.objects.bulk_create(obj_lst)


def courserecordadd(request):
    """
    课程记录添加
    :param request:
    :return:
    """
    header_info = {"add": "课程记录添加", "edit": "课程记录修改"}
    coursere_obj = CourseReFrom(request)
    if request.method == "POST":
        addret = request.POST.dict()
        addret.pop("csrfmiddlewaretoken")

        # 获取customer和Campuses和ClassList的Queryset对象
        class_obj = models.ClassList.objects.filter(id=addret['re_class']).first()
        teacher_obj = models.UserInfo.objects.filter(id=addret['teacher']).first()
        if addret['has_homework'] == '2':
            addret['has_homework'] = True
        else:
            addret['has_homework'] = False

        # 替换数据
        addret['re_class'] = class_obj
        addret['teacher'] = teacher_obj

        # 增加记录
        models.CourseRecord.objects.create(**addret)
        return redirect(reverse('user:courserecord'))
    return render(request, 'courserecord/write.html',
                  {"header_info": header_info['add'], "coursere_obj": coursere_obj})


def courserecordedit(request,id=None):
    """
    报名表记录修改
    :param request:
    :param id:
    :return:
    """
    header_info = {"add": "课程记录添加", "edit": "课程记录修改"}
    model_obj = models.CourseRecord.objects.filter(id=id).first()
    coursere_obj = CourseReFrom(request, instance=model_obj)  # 不写instance是创建，写了是更新
    if request.method == "POST":
        coursere_obj = CourseReFrom(request, request.POST, instance=model_obj)
        coursere_obj.save()
        coursere_url = reverse('user:courserecord')

        # 拼接URL(页码+搜索关键字)，保证返回上一次的页面
        coursere_url = f"{coursere_url}?page={request.session.get('page')}&{request.session.get('search_url')}"
        return redirect(coursere_url)
    return render(request, 'courserecord/write.html',
                  {"header_info": header_info['edit'], "coursere_obj": coursere_obj})


class StudyRe(View):
    """
    学习记录
    """
    def get(self,request):
        coursere_id = request.GET.get('coursere_id')    # 获取课程记录的pk
        study_record = models.StudyRecord.objects.filter(course_record_id=coursere_id)       # 根据课程记录的ID进行筛选
        formset = modelformset_factory(model=models.StudyRecord,form=StudyRecordFrom,extra=0)   # modelform加工厂,加工数据
        formset = formset(queryset=study_record)        # 把筛选后的结果放入到modelformset_factory进行加工
        # request.session["page"] = ''
        # if request.GET.get('page'):
        #     request.session["page"] = request.GET.get('page')
        # request.session["search_url"] = ''
        # base_url = f'coursere_id={coursere_id}'
        # page = Paging(request.GET.get("page"), formset.total_form_count(), base_url)
        return render(request,'studyrecord/studtrecord.html',{'formset':formset})
        # studyre_obj = models.StudyRecord.objects.all()
        # request.session["page"] = ''
        # if request.GET.get('page'):
        #     request.session["page"] = request.GET.get('page')
        # request.session["search_url"] = ''
        # base_url = ''
        #
        # # 搜索
        # search_field = request.GET.get('search_field')
        # kw = request.GET.get('kw')
        #
        # if kw:
        #     kw = kw.strip()
        #     q_obj = Q()
        #     q_obj.children.append((search_field + "__contains", kw))
        #     studyre_obj = studyre_obj.filter(q_obj)
        #
        #     # 搜索关键字进行url编码
        #     base_url = {}
        #     base_url["search_field"] = search_field
        #     base_url["kw"] = kw
        #     base_url = urlencode(base_url)
        #     request.session["search_url"] = base_url
        # page = Paging(request.GET.get("page"), studyre_obj.count(), base_url)
        # return render(request, 'studyrecord/studtrecord.html',
        #               {"studyre_obj": studyre_obj[page.start:page.end], "page_html": page.page_html,
        #                "search_field": search_field, "kw": kw})

    def post(self, request):
        coursere_id = request.GET.get('coursere_id')
        formret = modelformset_factory(model=models.StudyRecord,form=StudyRecordFrom,extra=0)
        form_set = formret(request.POST)
        if form_set.is_valid():
            form_set.save()
        return redirect(reverse('user:studyrecord'))