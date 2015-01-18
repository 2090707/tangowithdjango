from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says hey there world! <br/> <a href='/rango/about'>About</a>")

def about(request):
    return HttpResponse("<h2>This tutorial has been put together by Aleksandar Ilov, 2090707</h2> <br/> Rango says here is the about page. <br/> <a href='/rango/'>Index</a>")
