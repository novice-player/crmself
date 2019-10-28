from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse


class LoginCheck(MiddlewareMixin):

    def process_request(self, request):
        white_list = [reverse("user:login"),reverse("user:register")]
        if request.path not in  white_list:
            ret = request.session.get("uname")
            if not ret:
                return redirect(reverse('user:login'))
