from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Activity, BlogPost, ParticipationRequest, SiteSettings
from .forms import ParticipationRequestForm
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from django.conf import settings
import datetime
import qrcode
import base64
from io import BytesIO
from django.views.generic import ListView, TemplateView
from .models import BlogPost, ModuleCalendar


def index(request):
    featured_activities = Activity.objects.filter(date__gte=timezone.now()).order_by('date')[:3]
    latest_posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')[:3]
    
    site_settings = SiteSettings.objects.first()  # İlk SiteSettings objesini çek
    
    context = {
        'featured_activities': featured_activities,
        'latest_posts': latest_posts,
        'hero_image': site_settings.hero_image if site_settings else None,
    }
    return render(request, 'core/index.html', context)

class ActivityListView(ListView):
    model = Activity
    template_name = 'core/activities.html'
    context_object_name = 'activities'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Activity.objects.filter(date__gte=timezone.now()).order_by('date')
        
        # Arama filtresi
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        # Tarih filtresi
        date_filter = self.request.GET.get('date')
        if date_filter:
            try:
                filter_date = datetime.datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(date__date=filter_date)
            except ValueError:
                pass
                
        # Lokasyon filtresi
        location_filter = self.request.GET.get('location')
        if location_filter:
            queryset = queryset.filter(location__icontains=location_filter)
            
        return queryset

class ActivityDetailView(DetailView):
    model = Activity
    template_name = 'core/activity_detail.html'
    context_object_name = 'activity'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['approved_participants'] = ParticipationRequest.objects.filter(
            activity=self.object,
            is_approved=True
        ).order_by('created_at')
        return context
    

class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'core/announcements.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True)
        
        # Section filter
        section = self.request.GET.get('section')
        if section:
            queryset = queryset.filter(section=section)
        else:
            # Default to showing all sections but ordered by section
            queryset = queryset.order_by('section')
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Special filters
        filter_type = self.request.GET.get('filter')
        if filter_type == 'important':
            queryset = queryset.filter(is_important=True)
        elif filter_type == 'pinned':
            queryset = queryset.filter(is_pinned=True)
        
        return queryset.order_by('-is_important', '-is_pinned', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Active module calendar
        context['active_calendar'] = ModuleCalendar.objects.filter(
            is_active=True
        ).first()
        
        # Section choices
        context['sections'] = BlogPost.SECTION_CHOICES
        
        # Category choices
        context['categories'] = BlogPost.CATEGORY_CHOICES
        
        # Selected filters
        context['selected_section'] = self.request.GET.get('section')
        context['selected_category'] = self.request.GET.get('category')
        
        # Get important posts for each section if no filters are applied
        if not any([self.request.GET.get('section'), 
                   self.request.GET.get('category'), 
                   self.request.GET.get('filter')]):
            
            context['education_posts'] = BlogPost.objects.filter(
                is_published=True, 
                section='EDUCATION',
                is_important=True
            ).order_by('-created_at')[:3]
            
            context['guide_posts'] = BlogPost.objects.filter(
                is_published=True, 
                section='GUIDE',
                is_important=True
            ).order_by('-created_at')[:3]
            
            context['announcement_posts'] = BlogPost.objects.filter(
                is_published=True, 
                section='ANNOUNCEMENT',
                is_important=True
            ).order_by('-created_at')[:3]
            
        return context

class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'core/blog_detail.html'
    context_object_name = 'post'

class ParticipationCreateView(CreateView):
    model = ParticipationRequest
    form_class = ParticipationRequestForm
    template_name = 'core/participation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activity'] = get_object_or_404(Activity, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        form.instance.activity = get_object_or_404(Activity, pk=self.kwargs['pk'])
        response = super().form_valid(form)
        self.object = form.save()  # kayıt edilen participation objesi
        return response

    def get_success_url(self):
        return reverse('core:participation_success', kwargs={'pk': self.object.pk})
    
def participation_success(request, pk):
    participation = get_object_or_404(ParticipationRequest, pk=pk)
    activity = participation.activity

    # QR kod için içerik belirle (örneğin, katılım ID'si ve etkinlik bilgisi)
    qr_data = request.build_absolute_uri(
    reverse('core:verify_participation', args=[participation.pk, participation.token])
)
    # QR kod oluştur
    qr = qrcode.make(qr_data)

    # QR kodu base64 string'e çevir (PNG formatında)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_b64 = base64.b64encode(buffered.getvalue()).decode()

    context = {
        'participation': participation,
        'activity': activity,
        'qr_code': qr_b64,  # base64 olarak gönderiyoruz
    }
    return render(request, 'core/participation_success.html', context)



def calendar_view(request):
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    try:
        # Service account credentials
        creds = service_account.Credentials.from_service_account_file(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=SCOPES
        )
        
        service = build('calendar', 'v3', credentials=creds)

        # Zaman aralığı belirle (önümüzdeki 3 ay)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        future = (datetime.datetime.utcnow() + datetime.timedelta(days=90)).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId=getattr(settings, 'GOOGLE_CALENDAR_ID', 'primary'),
            timeMax=future,
            maxResults=50,
            singleEvents=True,  
            orderBy='startTime'
        ).execute()

        events = []
        for event in events_result.get('items', []):
            # Etkinlik başlangıç ve bitiş zamanlarını işle
            start = event['start'].get('dateTime') or event['start'].get('date')
            end = event['end'].get('dateTime') or event['end'].get('date')
            
            events.append({
                'id': event.get('id'),
                'summary': event.get('summary', 'No Title'),
                'start': start,
                'end': end,
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'color': event.get('colorId', '')  # Renk ID'si (isteğe bağlı)
            })

        context = {
            'events': events,
            'calendar_id': getattr(settings, 'GOOGLE_CALENDAR_ID', 'primary'),
        }

    except Exception as e:
        # Hata durumunda boş bir takvim göster
        context = {
            'events': [],
            'error': str(e)
        }

    return render(request, 'core/calendar.html', context)


def verify_participation(request, pk, token):
    participation = get_object_or_404(ParticipationRequest, pk=pk, token=token)

    return render(request, "core/verify_success.html", {"participation": participation})  