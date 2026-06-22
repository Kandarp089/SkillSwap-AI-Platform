from django.shortcuts import render

def leaderboard(request):
    return render(
        request,
        "leaderboard/leaderboard.html"
    )