from django.shortcuts import render, get_object_or_404
from .models import Certificate

def verify_certificate(request, certificate_id):
    cert = get_object_or_404(Certificate.objects.select_related('user', 'user__profile'), certificate_id=certificate_id)
    return render(request, 'certificates/verify.html', {'certificate': cert})
