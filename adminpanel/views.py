import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.http import JsonResponse, HttpResponse
from accounts.permissions import control_center_required
from .models import AdminAuditLog, PlatformSetting
from skills.models import Category, Skill, SkillReview
from matching.models import AIMatchWeight, AIMatch
from exchanges.models import ExchangeRequest, XPLedger, CreditTransaction
from certificates.models import Certificate
from community.models import CommunityPost
from events.models import Event, EventRegistration
from support.models import SupportTicket, SupportMessage
from reports.models import ContentReport

User = get_user_model()

def log_admin_action(admin_user, action, target_model, target_id="", details="", request=None):
    ip = request.META.get('REMOTE_ADDR') if request else None
    AdminAuditLog.objects.create(
        admin=admin_user,
        action=action,
        target_model=target_model,
        target_object_id=str(target_id),
        details=details,
        ip_address=ip
    )

def control_center_login(request):
    if request.user.is_authenticated:
        if request.user.has_control_panel_access():
            return redirect('adminpanel:dashboard')
        return redirect('dashboard:home')
    return redirect('/accounts/login/?next=/control-center/')

def control_center_logout(request):
    if request.user.is_authenticated:
        log_admin_action(request.user, "ADMIN_LOGOUT", "User", request.user.id, "Admin logged out", request)
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('/')

@control_center_required()
def dashboard(request):
    # Real DB statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True, is_suspended=False).count()
    mentors_count = User.objects.filter(is_verified_mentor=True).count()
    total_skills = Skill.objects.count()
    total_categories = Category.objects.count()
    pending_exchanges = ExchangeRequest.objects.filter(status='pending').count()
    completed_exchanges = ExchangeRequest.objects.filter(status='completed').count()
    total_certificates = Certificate.objects.count()
    open_tickets = SupportTicket.objects.filter(status__in=['open', 'in_progress']).count()
    pending_reports = ContentReport.objects.filter(status='pending').count()
    total_xp_issued = XPLedger.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    recent_audit_logs = AdminAuditLog.objects.select_related('admin')[:10]
    recent_tickets = SupportTicket.objects.select_related('user')[:5]

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'mentors_count': mentors_count,
        'total_skills': total_skills,
        'total_categories': total_categories,
        'pending_exchanges': pending_exchanges,
        'completed_exchanges': completed_exchanges,
        'total_certificates': total_certificates,
        'open_tickets': open_tickets,
        'pending_reports': pending_reports,
        'total_xp_issued': total_xp_issued,
        'recent_audit_logs': recent_audit_logs,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'adminpanel/dashboard.html', context)

@control_center_required()
def user_list(request):
    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '')
    users = User.objects.select_related('profile').all()

    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(first_name__icontains=query))
    if role_filter:
        users = users.filter(role=role_filter)

    if request.method == 'POST':
        action = request.POST.get('action')
        target_user_id = request.POST.get('user_id')
        target_user = get_object_or_404(User, id=target_user_id)

        if action == 'toggle_suspend':
            target_user.is_suspended = not target_user.is_suspended
            if target_user.is_suspended:
                target_user.suspended_at = timezone.now()
                target_user.suspension_reason = request.POST.get('reason', 'Violation of terms')
                log_admin_action(request.user, "USER_SUSPENDED", "User", target_user.id, f"Suspended @{target_user.username}", request)
                messages.warning(request, f"User @{target_user.username} has been suspended.")
            else:
                target_user.is_suspended = False
                log_admin_action(request.user, "USER_RESTORED", "User", target_user.id, f"Restored @{target_user.username}", request)
                messages.success(request, f"User @{target_user.username} restored.")
            target_user.save()

        elif action == 'verify_mentor':
            target_user.is_verified_mentor = not target_user.is_verified_mentor
            target_user.save()
            status_str = "verified as Mentor" if target_user.is_verified_mentor else "unverified"
            log_admin_action(request.user, "USER_VERIFIED", "User", target_user.id, f"Mentor status changed for @{target_user.username}", request)
            messages.success(request, f"User @{target_user.username} is now {status_str}.")

        elif action == 'change_role':
            new_role = request.POST.get('new_role')
            if new_role in User.Role.values:
                target_user.role = new_role
                target_user.save()
                log_admin_action(request.user, "USER_ROLE_CHANGED", "User", target_user.id, f"Role set to {new_role}", request)
                messages.success(request, f"Role updated for @{target_user.username}.")

        return redirect('adminpanel:users')

    return render(request, 'adminpanel/users.html', {'users': users, 'query': query, 'role_filter': role_filter, 'roles': User.Role.choices})

@control_center_required()
def skill_list(request):
    skills = Skill.objects.select_related('user', 'category').all()
    categories = Category.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            title = request.POST.get('title')
            cat_id = request.POST.get('category_id')
            desc = request.POST.get('description')
            cat = Category.objects.filter(id=cat_id).first()
            skill = Skill.objects.create(user=request.user, title=title, category=cat, description=desc)
            log_admin_action(request.user, "SKILL_CREATED", "Skill", skill.id, f"Created skill {title}", request)
            messages.success(request, f"Skill '{title}' created successfully.")

        elif action == 'toggle_active':
            skill_id = request.POST.get('skill_id')
            skill = get_object_or_404(Skill, id=skill_id)
            skill.is_active = not skill.is_active
            skill.save()
            log_admin_action(request.user, "SKILL_STATUS_TOGGLED", "Skill", skill.id, f"Set active={skill.is_active}", request)
            messages.info(request, f"Skill '{skill.title}' status updated.")

        return redirect('adminpanel:skills')

    return render(request, 'adminpanel/skills.html', {'skills': skills, 'categories': categories})

@control_center_required()
def category_list(request):
    categories = Category.objects.annotate(skill_count=Count('skills')).all()
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon', 'bi-code-slash')
        desc = request.POST.get('description', '')
        cat = Category.objects.create(name=name, icon=icon, description=desc)
        log_admin_action(request.user, "CATEGORY_CREATED", "Category", cat.id, f"Created category {name}", request)
        messages.success(request, f"Category '{name}' created.")
        return redirect('adminpanel:categories')

    return render(request, 'adminpanel/categories.html', {'categories': categories})

@control_center_required()
def ai_matches_analytics(request):
    weights = AIMatchWeight.objects.first()
    if not weights:
        weights = AIMatchWeight.objects.create()

    if request.method == 'POST':
        weights.skill_overlap_weight = int(request.POST.get('skill_overlap', 35))
        weights.wanted_offered_weight = int(request.POST.get('wanted_offered', 25))
        weights.experience_weight = int(request.POST.get('experience', 10))
        weights.availability_weight = int(request.POST.get('availability', 10))
        weights.learning_mode_weight = int(request.POST.get('learning_mode', 5))
        weights.language_weight = int(request.POST.get('language', 5))
        weights.rating_weight = int(request.POST.get('rating', 5))
        weights.activity_weight = int(request.POST.get('activity', 5))
        weights.save()

        log_admin_action(request.user, "AI_WEIGHTS_UPDATED", "AIMatchWeight", weights.id, "Updated AI match scoring weights", request)
        messages.success(request, "AI Matching Weights updated successfully!")
        return redirect('adminpanel:ai_matches')

    return render(request, 'adminpanel/ai_matches.html', {'weights': weights})

@control_center_required()
def exchange_list(request):
    exchanges = ExchangeRequest.objects.select_related('sender', 'receiver').all()
    if request.method == 'POST':
        ex_id = request.POST.get('exchange_id')
        action = request.POST.get('action')
        ex = get_object_or_404(ExchangeRequest, id=ex_id)

        if action == 'force_complete':
            from exchanges.services import complete_exchange
            complete_exchange(ex.id, request.user)
            log_admin_action(request.user, "EXCHANGE_FORCE_COMPLETED", "ExchangeRequest", ex.id, f"Admin resolved exchange #{ex.id}", request)
            messages.success(request, f"Exchange #{ex.id} forcibly marked completed with XP awards.")
        elif action == 'cancel':
            ex.status = 'cancelled'
            ex.save()
            log_admin_action(request.user, "EXCHANGE_CANCELLED", "ExchangeRequest", ex.id, f"Cancelled exchange #{ex.id}", request)
            messages.warning(request, f"Exchange #{ex.id} cancelled.")

        return redirect('adminpanel:exchanges')

    return render(request, 'adminpanel/exchanges.html', {'exchanges': exchanges})

@control_center_required()
def certificate_list(request):
    certificates = Certificate.objects.select_related('user').all()
    if request.method == 'POST':
        action = request.POST.get('action')
        cert_id = request.POST.get('certificate_db_id')
        cert = get_object_or_404(Certificate, id=cert_id)

        if action == 'revoke':
            cert.status = 'revoked'
            cert.save()
            log_admin_action(request.user, "CERTIFICATE_REVOKED", "Certificate", cert.certificate_id, f"Revoked certificate {cert.certificate_id}", request)
            messages.warning(request, f"Certificate {cert.certificate_id} revoked.")
        elif action == 'approve':
            cert.status = 'active'
            cert.save()
            log_admin_action(request.user, "CERTIFICATE_APPROVED", "Certificate", cert.certificate_id, f"Approved certificate {cert.certificate_id}", request)
            messages.success(request, f"Certificate {cert.certificate_id} verified and active.")

        return redirect('adminpanel:certificates')

    return render(request, 'adminpanel/certificates.html', {'certificates': certificates})

@control_center_required()
def support_tickets(request):
    tickets = SupportTicket.objects.select_related('user', 'assigned_to').all()
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_db_id')
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        reply_text = request.POST.get('reply_text', '').strip()
        new_status = request.POST.get('status')

        if reply_text:
            SupportMessage.objects.create(ticket=ticket, sender=request.user, message=reply_text)

        if new_status and new_status in dict(SupportTicket.STATUS_CHOICES):
            ticket.status = new_status

        ticket.assigned_to = request.user
        ticket.save()
        log_admin_action(request.user, "SUPPORT_TICKET_UPDATED", "SupportTicket", ticket.ticket_id, f"Updated ticket #{ticket.ticket_id}", request)
        messages.success(request, f"Support Ticket #{ticket.ticket_id} updated.")
        return redirect('adminpanel:support')

    return render(request, 'adminpanel/support.html', {'tickets': tickets})

@control_center_required()
def reports_list(request):
    reports = ContentReport.objects.select_related('reported_by', 'resolved_by').all()
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        action = request.POST.get('action')
        rep = get_object_or_404(ContentReport, id=report_id)

        if action == 'resolve':
            rep.status = 'resolved'
            rep.resolved_by = request.user
            rep.resolution_notes = request.POST.get('notes', 'Action taken.')
            rep.save()
            log_admin_action(request.user, "REPORT_RESOLVED", "ContentReport", rep.id, f"Resolved report #{rep.id}", request)
            messages.success(request, f"Report #{rep.id} resolved.")

        return redirect('adminpanel:reports')

    return render(request, 'adminpanel/reports.html', {'reports': reports})

@control_center_required()
def audit_logs(request):
    logs = AdminAuditLog.objects.select_related('admin').all()[:100]
    return render(request, 'adminpanel/audit_logs.html', {'logs': logs})

@control_center_required()
def system_health(request):
    import sys
    from django.db import connection

    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    m_mode = PlatformSetting.objects.filter(key='MAINTENANCE_MODE').first()
    maintenance_active = m_mode.value.lower() == 'true' if m_mode else False

    if request.method == 'POST' and 'toggle_maintenance' in request.POST:
        new_val = 'false' if maintenance_active else 'true'
        PlatformSetting.objects.update_or_create(key='MAINTENANCE_MODE', defaults={'value': new_val, 'description': 'Global platform maintenance toggle'})
        log_admin_action(request.user, "MAINTENANCE_MODE_TOGGLED", "PlatformSetting", 0, f"Maintenance set to {new_val}", request)
        messages.warning(request, f"Maintenance mode set to {new_val.upper()}.")
        return redirect('adminpanel:system_health')

    health_info = {
        'python_version': sys.version,
        'django_version': '4.2.19',
        'db_ok': db_ok,
        'maintenance_active': maintenance_active,
        'environment': 'Production (Vercel/Render Ready)',
    }
    return render(request, 'adminpanel/system_health.html', {'health': health_info})
