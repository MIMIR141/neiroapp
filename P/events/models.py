from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Event(models.Model):
    EVENT_TYPES = [
        ('conference', 'Конференция'),
        ('concert', 'Концерт'),
        ('meetup', 'Митап'),
        ('workshop', 'Мастер-класс'),
        ('other', 'Другое'),
    ]
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    description = models.TextField()
    type = models.CharField(max_length=20, choices=EVENT_TYPES)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class InviteLink(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='invite_links')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Приглашение на {self.event.title} ({self.uuid})"

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    invite_link = models.ForeignKey(InviteLink, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} на {self.event.title}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}: {self.message}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    organization = models.CharField(max_length=100, blank=True, verbose_name='Организация')
    position = models.CharField(max_length=100, blank=True, verbose_name='Должность')
    city = models.CharField(max_length=50, blank=True, verbose_name='Город')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')

    def __str__(self):
        return f'Профиль {self.user.email}'
