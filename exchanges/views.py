from django.shortcuts import render, redirect

def requests_page(request):
    return render(
        request,
        "exchanges/requests.html"
    )

def accept_request(request, request_id):
    return redirect('requests')

def reject_request(request, request_id):
    return redirect('requests')

def my_exchanges(request):
    return render(
        request,
        "exchanges/my_exchanges.html"
    )