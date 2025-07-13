from django.contrib import admin
from django.http import HttpResponse
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from tinymce.widgets import TinyMCE
from import_export.admin import ExportActionMixin
from import_export import resources
from .models import Activity, BlogPost, ParticipationRequest, SiteSettings
import openpyxl
from django.db.models import Count, Q
from io import BytesIO

def save_virtual_workbook(workbook):
    virtual_workbook = BytesIO()
    workbook.save(virtual_workbook)
    return virtual_workbook.getvalue()

class ParticipationRequestResource(resources.ModelResource):
    class Meta:
        model = ParticipationRequest
        fields = ('activity__title', 'first_name', 'last_name', 'room_number', 'email', 'phone', 'special_needs', 'created_at')
        export_order = fields

##@admin.register(ParticipationRequest)
class ParticipationRequestAdmin(ExportActionMixin, admin.ModelAdmin):
    # Ana liste görünümü ayarları
    list_display = ('activity_link', 'participant_info', 'status_badge', 'created_at')
    list_filter = ('is_approved', 'activity', 'created_at')
    search_fields = ('first_name', 'last_name', 'room_number', 'activity__title')
    list_select_related = ('activity',)
    actions = ['approve_selected', 'export_to_excel']
    
    # Özel alanlar
    def activity_link(self, obj):
        return format_html(
            '<a href="{}?activity__id__exact={}">{}</a>',
            reverse('admin:core_participationrequest_changelist'),
            obj.activity.id,
            obj.activity.title
        )
    activity_link.short_description = 'Aktivite'
    activity_link.admin_order_field = 'activity__title'

    def participant_info(self, obj):
        return format_html(
            '<strong>{} {}</strong><br>'
            '<small>Rom: {} | Tel: {}</small>',
            obj.first_name, obj.last_name,
            obj.room_number, obj.phone or '-'
        )
    participant_info.short_description = 'Katılımcı Bilgisi'

    def status_badge(self, obj):
        color = 'green' if obj.is_approved else 'orange'
        text = 'Onaylandı' if obj.is_approved else 'Bekliyor'
        return format_html(
            '<span style="background:{}; color:white; padding:2px 6px; border-radius:10px;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Durum'

    # Gruplandırılmış görünüm
    change_list_template = 'core/admin/participation_requests_changelist.html'
    
    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        activities = Activity.objects.annotate(
            total_requests=Count('participationrequest'),
            approved_requests=Count('participationrequest', filter=Q(participationrequest__is_approved=True)),
            pending_requests=Count('participationrequest', filter=Q(participationrequest__is_approved=False))
        ).order_by('-date')

        extra_context.update({
        '   activities': activities,
            'total_requests': ParticipationRequest.objects.count(),
            'approved_requests': ParticipationRequest.objects.filter(is_approved=True).count(),
    })

        response = super().changelist_view(request, extra_context=extra_context)

    # Eğer response context dict ise (TemplateResponse gibi) içeriğine extra_context ekle
        if hasattr(response, 'context_data'):
            response.context_data.update(extra_context)

        return response
    # Action'lar
    def approve_selected(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} katılımcı onaylandı.")
    approve_selected.short_description = "Seçilenleri onayla"

    def export_to_excel(self, request, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Deltakere"
        
        headers = [
            'Aktivitet', 'Fornavn', 'Etternavn', 'Romnummer', 
            'E-post', 'Telefon', 'Spesielle behov', 'Godkjent', 'Registrert'
        ]
        ws.append(headers)
        
        for obj in queryset:
            ws.append([
                obj.activity.title,
                obj.first_name,
                obj.last_name,
                obj.room_number,
                obj.email or '',
                obj.phone or '',
                obj.special_needs or '',
                'Ja' if obj.is_approved else 'Nei',
                obj.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        response = HttpResponse(
            save_virtual_workbook(wb),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=deltakere.xlsx'
        return response
    export_to_excel.short_description = "Eksporter valgte til Excel"

  
##@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location')
    list_filter = ('date',)
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['description'].widget = TinyMCE()
        return form


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'get_category_display', 'created_at', 'is_published', 'is_pinned', 'is_important')
    list_filter = ('section', 'category', 'is_published', 'is_pinned', 'is_important', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    list_editable = ('is_pinned', 'is_important')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'image', 'section', 'category')
        }),
        ('Ayarlar', {
            'fields': ('is_published', 'is_pinned', 'is_important'),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['content'].widget = TinyMCE()
        return form

admin.site.register(SiteSettings)