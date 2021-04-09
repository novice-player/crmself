from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
import re

class PermissionCheck(MiddlewareMixin):
    """
    权限校验
    """

    def process_request(self, request):

        # 登录认证白名单
        white_list = [reverse("user:login"),reverse("user:register"),'/admin']
        request_path = request.path
        for path in white_list:
            path_re = r"^%s" % path
            if re.match(path_re,request_path):
             return


        # 权限认证
        permission_list = request.session.get('permissions')
        for reg in permission_list:
            reg_info = r"%s$"%reg['url']
            if re.match(reg_info,request_path):

                ret = request.session.get('menu_dict')
                if ret:
                    for menu_k, menu_v in ret.items():
                        menu_v['style_msg'] = ''

                        # 路径导航
                        breadcrumb_msg = []

                        for msg in menu_v.get('childen'):
                            msg['class_msg'] = ''
                            request.session['breadcrumb_msg'] = breadcrumb_msg
                            if request.path == msg.get('url') or reg['menu_id'] == msg['id']:   # 判断访问路径是否匹配或者非菜单路径所属菜单ID是否匹配

                                # 当非菜单路径所属菜单ID匹配时，添加路径信息到session中
                                if reg['menu_id'] == msg['id']:
                                    breadcrumb_msg.append(msg)
                                    breadcrumb_msg.append(reg)
                                    request.session['breadcrumb_msg'] = breadcrumb_msg
                                else:
                                    breadcrumb_msg.append(msg)
                                    request.session['breadcrumb_msg'] = breadcrumb_msg

                                # 左侧菜单选中效果及展开效果
                                msg['class_msg'] = 'active'
                                menu_v['style_msg'] = 'display: block'
                return
        else:
            return HttpResponse('权限不足。。。。')






