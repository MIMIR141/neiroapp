from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/register/', views.register_participant, name='register_participant'),
    path('<int:event_id>/invite/', views.generate_invite_link, name='generate_invite_link'),
    path('api/calendar/', views.events_json, name='events_json'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/calendar/create/', views.calendar_create_event, name='calendar_create_event'),
    path('api/calendar/update/<int:event_id>/', views.calendar_update_event, name='calendar_update_event'),
    path('guests/', views.guests_list, name='guests_list'),
    path('import/', views.import_events, name='import_events'),
    path('<int:event_id>/delete/', views.event_delete, name='event_delete'),
    path('google-calendar/', views.google_calendar_export, name='google_calendar_export'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),
    path('account/settings/', views.account_settings, name='account_settings'),
] 