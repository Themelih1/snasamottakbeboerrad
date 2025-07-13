from .models import Activity
import datetime


def navbar_context(request):
    upcoming_activities = Activity.objects.filter(date__gte=datetime.datetime.now()).order_by('date')[:5]
    return {
        'upcoming_activities_nav': upcoming_activities
    }