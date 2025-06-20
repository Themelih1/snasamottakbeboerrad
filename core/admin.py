from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import *

class BaseAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_on_top = True

@admin.register(SiteOwner)
class SiteOwnerAdmin(BaseAdmin):
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'position', 'image','about_image', 'short_bio')
        }),
        ('Detaylı Bilgiler', {
            'fields': ('bio', 'quote', 'quote_author')
        }),
    )
    list_display = ('name', 'position', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Profil Görseli"

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

@admin.register(Service)
class ServiceAdmin(BaseAdmin):
    form = ServiceForm
    list_display = ('title', 'icon_display', 'is_featured', 'order', 'created_at')
    list_editable = ('is_featured', 'order')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'icon', 'excerpt', 'description', 'is_featured', 'order')
        }),
        ('Detaylı İçerik', {
            'fields': ('detailed_content', 'cover_image', 'cover_image_preview')
        }),
    )
    readonly_fields = ('cover_image_preview', 'created_at')

    def icon_display(self, obj):
        return format_html('<i class="{}"></i> {}', obj.icon, obj.get_icon_display())
    icon_display.short_description = "İkon"

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 200px;" />', obj.cover_image.url)
        return "-"
    cover_image_preview.short_description = "Kapak Görseli Önizleme"

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = '__all__'
        widgets = {
            'expertise_list': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Uzmanlık alanlarını virgülle ayırarak girin'}),
        }

@admin.register(TeamMember)
class TeamMemberAdmin(BaseAdmin):
    form = TeamMemberForm
    list_display = ('name', 'position', 'expertise', 'is_active', 'image_preview')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'position')
    search_fields = ('name', 'expertise', 'position')
    prepopulated_fields = {}
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': (
                'name', 'slug',
                'position', 'expertise', 'expertise_list',
                'image', 'image_preview', 'cover_image', 'cover_image_preview', 'is_active'
            )
        }),
        ('İletişim Bilgileri', {
            'fields': ('phone', 'email')
        }),
        ('Detaylı Bilgiler', {
            'fields': ('bio', 'education', 'experience')
        }),
    )
    
    readonly_fields = ('image_preview', 'cover_image_preview')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Düzenleme modunda slug readonly olsun
            return self.readonly_fields + ('slug',)
        return self.readonly_fields

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Profil Görseli"

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 200px;" />', obj.cover_image.url)
        return "-"
    cover_image_preview.short_description = "Kapak Görseli"

class BlogPostForm(forms.ModelForm):
    slug = forms.SlugField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Otomatik oluşturulacak',
            'readonly': True
        })
    )
    class Meta:
        model = BlogPost
        fields = '__all__'
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
        }

class BlogCategoryAdmin(BaseAdmin):
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {"slug": ("name",)}
    fields = ['name', 'slug']

    def post_count(self, obj):
        return obj.blogpost_set.count()
    post_count.short_description = "Yazı Sayısı"

class BlogTagAdmin(BaseAdmin):
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        return obj.blogpost_set.count()
    post_count.short_description = "Yazı Sayısı"

class BlogPostAdmin(BaseAdmin):
    form = BlogPostForm
    list_display = ('title', 'category', 'is_published', 'is_featured', 'publish_date', 'thumbnail_preview')
    list_editable = ('is_published', 'is_featured')
    list_filter = ('is_published', 'is_featured', 'category', 'tags', 'publish_date')
    search_fields = ('title', 'summary', 'content')
    filter_horizontal = ('tags',)
    date_hierarchy = 'publish_date'
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'category', 'tags', 'is_published', 'is_featured', 'publish_date')
        }),
        ('İçerik', {
            'fields': ('summary', 'content')
        }),
        ('Görseller', {
            'fields': ('thumbnail', 'thumbnail_preview', 'cover_image', 'cover_image_preview')
        }),
    )
    readonly_fields = ('publish_date', 'thumbnail_preview', 'cover_image_preview')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:  # Düzenleme modunda
            return readonly_fields + ('slug',)
        return readonly_fields
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = "Küçük Görsel"

    def cover_image_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="max-height: 200px;" />', obj.cover_image.url)
        return "-"
    cover_image_preview.short_description = "Kapak Görseli"
    
class BlogCommentAdmin(BaseAdmin):
    list_display = ('name', 'post_link', 'email', 'is_approved', 'created_at')
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'post', 'created_at')
    search_fields = ('name', 'email', 'content')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'post_link')

    def post_link(self, obj):
        url = reverse('admin:core_blogpost_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    post_link.short_description = "Yazı"

class ContactInfoAdmin(BaseAdmin):
    list_display = ('phone', 'email', 'address_short')
    fieldsets = (
        ('İletişim Bilgileri', {
            'fields': ('phone', 'email', 'address', 'working_hours')
        }),
        ('Harita Ayarları', {
            'fields': ('map_embed_url',)
        }),
    )

    def address_short(self, obj):
        return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
    address_short.short_description = "Adres"

    def has_add_permission(self, request):
        return not ContactInfo.objects.exists()

class KVKKContentAdmin(BaseAdmin):
    list_display = ('title', 'content_short')
    fieldsets = (
        ('KVKK İçeriği', {
            'fields': ('title', 'content')
        }),
    )

    def content_short(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_short.short_description = "İçerik"

    def has_add_permission(self, request):
        return not KVKKContent.objects.exists()

class ContactMessageAdmin(BaseAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_editable = ('is_read',)
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'name', 'email', 'phone', 'subject', 'message')
    fieldsets = (
        ('Mesaj Bilgileri', {
            'fields': ('name', 'email', 'phone', 'subject', 'message', 'created_at')
        }),
        ('Durum', {
            'fields': ('is_read',)
        }),
    )

    def has_add_permission(self, request):
        return False

@admin.register(ServiceProcess)
class ServiceProcessAdmin(BaseAdmin):
    list_display = ('title', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Görsel Önizleme"

@admin.register(TeamAbout)
class TeamAboutAdmin(BaseAdmin):
    list_display = ('title', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Görsel Önizleme"

admin.site.site_header = "Tuglacı Hukuk Danışmanlığı Yönetim Paneli"
admin.site.site_title = "Hukuk Danışmanlığı"
admin.site.index_title = "Site Yönetimi"

admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(BlogTag, BlogTagAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)
admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(KVKKContent, KVKKContentAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)