from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
import re


class LoginCheck(MiddlewareMixin):
    """
    登录验证
    """

    def process_request(self, request):
        white_list = [reverse("user:login"),reverse("user:register"),'/admin']
        request_path = request.path
        for path in white_list:
            path_re = r"%s" % path
            if re.match(path_re,request_path):
                return
        ret = request.session.get("uname")
        if not ret:
            return redirect(reverse('user:login'))
