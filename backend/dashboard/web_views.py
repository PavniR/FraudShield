from django.shortcuts import render

def dashboard_home(request):
    return render(request, "dashboard.html")

def transactions_view(request):
    return render(request, "transactions.html")

def evaluate_tester_view(request):
    return render(request, "tester.html")

def login_register_view(request):
    return render(request, "auth.html")
