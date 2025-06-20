from django.db import models
from cloudinary.models import CloudinaryField
from tinymce.models import HTMLField
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

class SiteOwner(models.Model):
    name = models.CharField("Ad Soyad", max_length=100)
    position = models.CharField("Pozisyon/Ünvan", max_length=100)
    image = CloudinaryField("Profil Fotoğrafı", folder="lawyer_profile")
    about_image = CloudinaryField("Hakkımda Görseli", folder="lawyer_about", blank=True, null=True)
    short_bio = models.TextField("Kısa Bio", max_length=200)
    bio = HTMLField("Detaylı Bio")
    quote = HTMLField("Özlü Söz", blank=True, null=True)
    quote_author = models.CharField("Söz Sahibi", max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = "Site Sahibi"
        verbose_name_plural = "Site Sahibi"
    
    def __str__(self):
        return self.name

class Service(models.Model):
    ICON_CHOICES = (
        ('fas fa-gavel', 'Ceza Hukuku'),
        ('fas fa-home', 'Gayrimenkul Hukuku'),
        ('fas fa-briefcase', 'İş Hukuku'),
        ('fas fa-users', 'Aile Hukuku'),
        ('fas fa-file-contract', 'Sözleşmeler'),
        ('fas fa-landmark', 'Ticaret Hukuku'),
        ('fas fa-university', 'İdare Hukuku'),
        ('fas fa-heartbeat', 'Sağlık Hukuku'),
        ('fas fa-balance-scale', 'Miras Hukuku'),
        ('fas fa-plane-departure', 'Göçmenlik Hukuku'),
        ('fas fa-shield-alt', 'Sigorta Hukuku'),
        ('fas fa-globe', 'Uluslararası Hukuk'),
        ('fas fa-shield-virus', 'Tüketici Hukuku'),
        ('fas fa-child', 'Çocuk Hukuku'),
        ('fas fa-industry', 'Enerji ve Maden Hukuku'),
        ('fas fa-leaf', 'Çevre Hukuku'),
        )
    
    title = models.CharField("Başlık", max_length=100)
    slug = models.SlugField("SEO URL", unique=True)
    icon = models.CharField("İkon", max_length=50, choices=ICON_CHOICES)
    excerpt = models.CharField("Kısa Açıklama", max_length=200)
    description = HTMLField("Kısa Açıklama")
    detailed_content = HTMLField("Detaylı İçerik")
    cover_image = CloudinaryField("Kapak Görseli", folder="service_covers", blank=True, null=True)
    is_featured = models.BooleanField("Öne Çıkan", default=False)
    order = models.PositiveIntegerField("Sıralama", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    
    
    class Meta:
        verbose_name = "Hizmet"
        verbose_name_plural = "Hizmetler"
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'slug': self.slug})

class ServiceProcess(models.Model):
    title = models.CharField("Başlık", max_length=100)
    content = HTMLField("İçerik")
    image = CloudinaryField("Görsel", folder="service_process")
    
    class Meta:
        verbose_name = "Hizmet Süreci"
        verbose_name_plural = "Hizmet Süreci"
    
    def __str__(self):
        return self.title

class TeamMember(models.Model):
    name = models.CharField("Ad Soyad", max_length=100)
    position = models.CharField("Pozisyon", max_length=100)
    expertise = models.CharField("Uzmanlık Alanı", max_length=200)
    expertise_list = models.TextField("Uzmanlık Listesi", help_text="Virgülle ayırarak girin")
    image = CloudinaryField("Fotoğraf", folder="team_members")
    cover_image = CloudinaryField("Kapak Fotoğrafı", folder="team_covers", blank=True, null=True)
    bio = HTMLField("Biyografi")
    education = HTMLField("Eğitim", blank=True, null=True)
    experience = HTMLField("Deneyim", blank=True, null=True)
    phone = models.CharField("Telefon", max_length=20)
    email = models.EmailField("E-posta")
    slug = models.SlugField(unique=True, blank=True, null=True, help_text="Bu alan otomatik olarak oluşturulacaktır")
    is_active = models.BooleanField("Aktif Mi?", default=True)
    order = models.PositiveIntegerField("Sıralama", default=0)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            while TeamMember.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class TeamAbout(models.Model):
    title = models.CharField("Başlık", max_length=100)
    content = HTMLField("İçerik")
    image = CloudinaryField("Görsel", folder="team_about")
    
    class Meta:
        verbose_name = "Ekip Hakkında"
        verbose_name_plural = "Ekip Hakkında"
    
    def __str__(self):
        return self.title

class BlogCategory(models.Model):
    name = models.CharField("Kategori Adı", max_length=100)
    slug = models.SlugField("SEO URL", unique=True)
    
    class Meta:
        verbose_name = "Blog Kategorisi"
        verbose_name_plural = "Blog Kategorileri"
    
    def __str__(self):
        return self.name

class BlogTag(models.Model):
    name = models.CharField("Etiket Adı", max_length=50)
    slug = models.SlugField("SEO URL", unique=True)
    
    class Meta:
        verbose_name = "Blog Etiketi"
        verbose_name_plural = "Blog Etiketleri"
    
    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField("Başlık", max_length=200)
    slug = models.SlugField("SEO URL", unique=True, blank=False,
                          max_length=200, help_text="Bu alan otomatik olarak oluşturulacaktır")
    thumbnail = CloudinaryField("Kapak Görseli", folder="blog_thumbnails")
    cover_image = CloudinaryField("Detay Görseli", folder="blog_covers", blank=True, null=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, verbose_name="Kategori")
    tags = models.ManyToManyField(BlogTag, blank=True, verbose_name="Etiketler")
    summary = HTMLField("Özet")
    content = HTMLField("İçerik")
    publish_date = models.DateTimeField("Yayın Tarihi", auto_now_add=True)
    is_published = models.BooleanField("Yayında Mı?", default=True)
    is_featured = models.BooleanField("Öne Çıkan", default=False)
    
    class Meta:
        verbose_name = "Blog Yazısı"
        verbose_name_plural = "Blog Yazıları"
        ordering = ['-publish_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            base_slug = slugify(self.title)
            self.slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        if self.is_published and not self.publish_date:
            self.publish_date = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField("Ad Soyad", max_length=100)
    email = models.EmailField("E-posta")
    content = models.TextField("Yorum")
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    is_approved = models.BooleanField("Onaylandı Mı?", default=True)
    
    class Meta:
        verbose_name = "Blog Yorumu"
        verbose_name_plural = "Blog Yorumları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.post.title}"

class ContactInfo(models.Model):
    address = models.TextField("Adres")
    phone = models.CharField("Telefon", max_length=20)
    email = models.EmailField("E-posta")
    working_hours = models.TextField("Çalışma Saatleri")
    map_embed_url = models.TextField("Harita Embed URL")
    
    class Meta:
        verbose_name = "İletişim Bilgisi"
        verbose_name_plural = "İletişim Bilgileri"
    
    def __str__(self):
        return "İletişim Bilgileri"

class KVKKContent(models.Model):
    title = models.CharField("Başlık", max_length=100)
    content = HTMLField("İçerik")
    
    class Meta:
        verbose_name = "KVKK İçeriği"
        verbose_name_plural = "KVKK İçeriği"
    
    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField("Ad Soyad", max_length=100)
    email = models.EmailField("E-posta")
    phone = models.CharField("Telefon", max_length=20, blank=True, null=True)
    subject = models.CharField("Konu", max_length=100)
    message = models.TextField("Mesaj")
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)
    is_read = models.BooleanField("Okundu Mu?", default=False)
    
    class Meta:
        verbose_name = "İletişim Mesajı"
        verbose_name_plural = "İletişim Mesajları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"