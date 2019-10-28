from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
import re

class PermissionCheck(MiddlewareMixin):
    """
    权限校验
    """

    def process_request(self, request):

        # 左侧菜单选中效果及展开效果
        ret = request.session.get('menu_dict')

        if ret:
            for menu_k,menu_v in ret.items():
                menu_v['style_msg'] = ''
                for msg in menu_v.get('childen'):
                    msg['class_msg'] = ''
                    if request.path == msg.get('url'):
                        msg['class_msg'] = 'active'
                        menu_v['style_msg'] = 'display: block'


        # 登录认证白名单
        white_list = [reverse("user:login"),reverse("user:register")]
        request_path = request.path
        if request_path in white_list:
            return


        # 权限认证
        permission_list = request.session.get('permissions')
        for reg in permission_list:
            reg = r"^%s"%reg['url']
            if re.match(reg,request_path):
                return
        else:
            return HttpResponse('权限不足。。。。')






