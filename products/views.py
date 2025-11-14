from django.shortcuts import render


def home(request):
    return render(request, "index.html")


def game(request):
    return render(request, "product/game.html")


def socialboost(request):
    return render(request, "product/socialboost.html")
