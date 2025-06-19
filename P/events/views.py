from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event, EventRegistration, InviteLink, Notification, UserProfile
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from .forms import EventForm, EventRegistrationForm
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import csv
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import default_storage
from datetime import datetime

# Create your views here.

@login_required
def event_list(request):
    events = Event.objects.all().order_by('date')
    event_type = request.GET.get('type')
    if event_type:
        events = events.filter(type=event_type)
    q = request.GET.get('q')
    if q:
        events = events.filter(title__icontains=q)
    date = request.GET.get('date')
    if date:
        events = events.filter(date__date=date)
    organizer = request.GET.get('organizer')
    if organizer:
        events = events.filter(organizer__email__icontains=organizer)
    return render(request, 'events/event_list.html', {'events': events})

@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            create_notification(request.user, f'Вы создали мероприятие: {event.title}', url=f'/events/{event.id}/')
            # Email уведомление организатору
            send_mail(
                subject=f'Мероприятие создано: {event.title}',
                message=f'Вы успешно создали мероприятие "{event.title}" на {event.date}.',
                from_email=None,
                recipient_list=[request.user.email],
            )
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})

@login_required
def register_participant(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            registration.user = request.user
            registration.save()
            create_notification(request.user, f'Вы зарегистрировались на мероприятие: {event.title}', url=f'/events/{event.id}/')
            create_notification(event.organizer, f'Новый участник на {event.title}: {registration.name}', url=f'/events/{event.id}/')
            # Email участнику
            send_mail(
                subject=f'Регистрация на {event.title}',
                message=f'Вы зарегистрированы на мероприятие "{event.title}". Дата: {event.date}.',
                from_email=None,
                recipient_list=[registration.email],
            )
            # Email организатору
            send_mail(
                subject=f'Новый участник на {event.title}',
                message=f'{registration.name} ({registration.email}) зарегистрировался на ваше мероприятие.',
                from_email=None,
                recipient_list=[event.organizer.email],
            )
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventRegistrationForm()
    return render(request, 'events/registration_form.html', {'form': form, 'event': event})

@login_required
def generate_invite_link(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    invite = InviteLink.objects.create(event=event)
    link = request.build_absolute_uri(reverse('register_participant', args=[event.id])) + f'?invite={invite.uuid}'
    return render(request, 'events/invite_link.html', {'link': link, 'event': event})

@login_required
def home(request):
    events = Event.objects.order_by('date')[:5]
    total_events = Event.objects.count()
    total_participants = EventRegistration.objects.count()
    return render(request, 'events/home.html', {
        'events': events,
        'total_events': total_events,
        'total_participants': total_participants,
    })

@login_required
def events_json(request):
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    data = [
        {
            'id': e.id,
            'title': e.title,
            'start': e.date.isoformat(),
            'end': e.date.isoformat(),
            'url': f'/events/{e.id}/',
        } for e in events
    ]
    return JsonResponse(data, safe=False)

@login_required
def calendar_view(request):
    return render(request, 'events/calendar.html')

@csrf_exempt
@login_required
def calendar_create_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        date = parse_datetime(request.POST.get('date'))
        description = request.POST.get('description', '')
        type = request.POST.get('type', 'other')
        event = Event.objects.create(
            title=title,
            date=date,
            description=description,
            type=type,
            organizer=request.user
        )
        return JsonResponse({'success': True, 'event_id': event.id})
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
@login_required
def calendar_update_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        event.date = parse_datetime(request.POST.get('date'))
        event.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def guests_list(request):
    guests = EventRegistration.objects.select_related('event').order_by('-registered_at')
    return render(request, 'events/guests_list.html', {'guests': guests})

@login_required
@require_http_methods(["GET", "POST"])
def import_events(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        imported, errors = 0, 0
        for row in reader:
            try:
                event, _ = Event.objects.get_or_create(
                    title=row.get('title', '').strip(),
                    defaults={
                        'date': row.get('date'),
                        'description': row.get('description', ''),
                        'type': row.get('type', 'other'),
                        'organizer': request.user
                    }
                )
                if row.get('participant_name') and row.get('participant_email'):
                    EventRegistration.objects.get_or_create(
                        event=event,
                        email=row['participant_email'],
                        defaults={
                            'name': row['participant_name'],
                            'user': request.user
                        }
                    )
                imported += 1
            except Exception as e:
                errors += 1
        messages.success(request, f'Импортировано записей: {imported}, ошибок: {errors}')
        return redirect('event_list')
    return render(request, 'events/import_form.html')

@login_required
def event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user != event.organizer and not request.user.is_superuser:
        return HttpResponseForbidden('Удалять может только организатор или администратор.')
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Мероприятие успешно удалено.')
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

def create_notification(user, message, url=''):
    Notification.objects.create(user=user, message=message, url=url)

@login_required
def google_calendar_export(request):
    events = Event.objects.order_by('date')
    return render(request, 'events/google_calendar_export.html', {'events': events})

def help_view(request):
    return render(request, 'events/help.html')

def notification_delete(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id)
    if request.user != notif.user and not request.user.is_superuser:
        return HttpResponseForbidden('Удалять может только владелец или администратор.')
    notif.delete()
    messages.success(request, 'Уведомление удалено.')
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def account_settings(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    password_form = PasswordChangeForm(user)
    if request.method == 'POST':
        if 'save_profile' in request.POST:
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            organization = request.POST.get('organization', '').strip()
            position = request.POST.get('position', '').strip()
            city = request.POST.get('city', '').strip()
            birth_date = request.POST.get('birth_date', '').strip()
            if name:
                user.first_name = name
            if email and email != user.email:
                user.email = email
            user.save()
            profile.phone = phone
            profile.organization = organization
            profile.position = position
            profile.city = city
            if birth_date:
                try:
                    profile.birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
                except ValueError:
                    profile.birth_date = None
            else:
                profile.birth_date = None
            if request.FILES.get('avatar'):
                profile.avatar = request.FILES['avatar']
            profile.save()
            messages.success(request, 'Данные профиля обновлены.')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль успешно изменён.')
            else:
                messages.error(request, 'Ошибка смены пароля. Проверьте введённые данные.')
    return render(request, 'events/account_settings.html', {
        'user': user,
        'profile': profile,
        'password_form': password_form,
    })
