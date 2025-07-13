from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from tinymce.models import HTMLField
from cloudinary.models import CloudinaryField
import uuid

class Activity(models.Model):
    title = models.CharField(_('Tittel'), max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now) 
    location = models.CharField(_('Sted'), max_length=200)
    image = CloudinaryField(_('Bilde'), folder='mottak/activities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Aktivitet')
        verbose_name_plural = _('Aktiviteter')
        ordering = ['-date']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs) 

class SiteSettings(models.Model):
    hero_image = CloudinaryField('hero_image', blank=True, null=True)
    
    def __str__(self):
        return "Innstillinger"

class BlogPost(models.Model):
    SECTION_CHOICES = [
        ('EDUCATION', _('Undervisningskalender')),
        ('GUIDE', _('Veiledning for nyankomne')),
        ('ANNOUNCEMENT', _('Kunngjøringstavle')),
    ]
    
    CATEGORY_CHOICES = [
        ('Generell', _('Generell kunngjøring')),
        ('Aktivitet', _('Aktivitet')),
        ('Viktige', _('Nødssituasjon')),
        ('Meny', _('Meny')),
        ('Annonser', _('Offisiell kunngjøring')),
    ]
    
    title = models.CharField(_('Tittel'), max_length=200)
    slug = models.SlugField(_('URL'), max_length=250, unique=True, blank=True)
    content = HTMLField(_('Innhold'))
    image = CloudinaryField(
        _('Bilde'), 
        folder='mottak/blog', 
        blank=True, 
        null=True,
        transformation=[
            {'width': 800, 'height': 600, 'crop': 'fill'},
            {'quality': 'auto'}
        ],
        format='webp'
    )
    created_at = models.DateTimeField(_('Opprettet'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Oppdatert'), auto_now=True)
    is_published = models.BooleanField(_('Publiser'), default=True)
    is_pinned = models.BooleanField(_('Fest til toppen'), default=False,
                                  help_text=_('Denne kunngjøringen vil vises øverst'))
    is_important = models.BooleanField(_('Viktig'), default=False,
                                     help_text=_('Viktige kunngjøringer vil bli fremhevet'))
    section = models.CharField(
        _('Seksjon'),
        max_length=15,
        choices=SECTION_CHOICES,
        default='ANNOUNCEMENT'
    )
    category = models.CharField(
        _('Kategori'), 
        max_length=10, 
        choices=CATEGORY_CHOICES, 
        default='GENEL'
    )
    view_count = models.PositiveIntegerField(_('Visninger'), default=0)
    author = models.ForeignKey(
        'auth.User',
        verbose_name=_('Forfatter'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('Kunngjøring')
        verbose_name_plural = _('Kunngjøringer')
        ordering = ['-is_important', '-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_published']),
            models.Index(fields=['category']),
            models.Index(fields=['section']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.title)}-{counter}"
                counter += 1
        
        if self.image:
            self.image.format = 'webp'
        
        super().save(*args, **kwargs)
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

class ModuleCalendar(models.Model):
    title = models.CharField(_('Tittel'), max_length=200)
    week_range = models.CharField(_('Ukeperiode'), max_length=100)
    schedule = models.JSONField(_('Timeplan'))
    is_active = models.BooleanField(_('Aktiv kalender'), default=True)
    start_date = models.DateField(_('Startdato'))
    end_date = models.DateField(_('Sluttdato'))
    created_at = models.DateTimeField(_('Opprettet'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Oppdatert'), auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.week_range}"
    
    def get_week_schedule(self):
        """Prosesserer JSON-data og returnerer ukeplan"""
        try:
            return {
                'monday': self.schedule.get('monday', []),
                'tuesday': self.schedule.get('tuesday', []),
                'wednesday': self.schedule.get('wednesday', []),
                'thursday': self.schedule.get('thursday', []),
                'friday': self.schedule.get('friday', []),
            }
        except:
            return {}
    
    class Meta:
        verbose_name = _('Modulkalender')
        verbose_name_plural = _('Modulkalendere')
        ordering = ['-start_date']

class ParticipationRequest(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name=_('Aktivitet'))
    first_name = models.CharField(_('Fornavn'), max_length=100)
    last_name = models.CharField(_('Etternavn'), max_length=100)
    room_number = models.CharField(_('Romnummer'), max_length=20)
    email = models.EmailField(_('E-post'), blank=True, null=True)
    phone = models.CharField(_('Telefonnummer'), max_length=20, blank=True, null=True)
    special_needs = models.TextField(_('Spesielle behov'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(_('Godkjent'), default=False)
    token = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        verbose_name = _('Deltakelsesforespørsel')
        verbose_name_plural = _('Deltakelsesforespørsler')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.activity.title}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"