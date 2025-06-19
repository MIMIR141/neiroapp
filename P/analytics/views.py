from django.shortcuts import render
from events.models import Event, EventRegistration
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
import pandas as pd
from django.http import HttpResponse
import csv

def analytics_dashboard(request):
    # График: количество регистраций по датам
    regs = EventRegistration.objects.all().values('registered_at')
    df = pd.DataFrame(list(regs))
    if not df.empty:
        df['date'] = pd.to_datetime(df['registered_at']).dt.date
        reg_counts = df.groupby('date').size()
        fig, ax = plt.subplots()
        reg_counts.plot(kind='bar', ax=ax, color='#007bff')
        ax.set_title('Регистрации по дням')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Кол-во регистраций')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
    else:
        chart = None
    # Статистика по событиям
    events = Event.objects.all()
    return render(request, 'analytics/dashboard.html', {
        'chart': chart,
        'events': events,
    })

def analytics_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="events.csv"'
    writer = csv.writer(response)
    writer.writerow(['Название', 'Дата', 'Тип', 'Кол-во участников'])
    for event in Event.objects.all():
        writer.writerow([
            event.title,
            event.date.strftime('%d.%m.%Y %H:%M'),
            event.get_type_display(),
            event.registrations.count()
        ])
    return response
