from django.shortcuts import render

def chat_home(request):
    return render(
        request,
        "chatapp/chat.html"
    )