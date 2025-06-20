from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from cloudinary.uploader import upload
from django.utils import timezone


def home(request):
    site_owner = SiteOwner.objects.first()
    services = Service.objects.filter(is_featured=True)[:6]
    team_members = TeamMember.objects.filter(
        is_active=True,
        slug__isnull=False
    ).exclude(slug='').order_by('order')[:4]
    
    recent_posts = BlogPost.objects.filter(
        is_published=True,
        publish_date__lte=timezone.now(),
        slug__isnull=False
    ).exclude(slug='').order_by('-publish_date')[:3]
    contact_info = ContactInfo.objects.first()
    
    context = {
        'site_owner': site_owner,
        'services': services,
        'team_members': team_members,
        'recent_posts': recent_posts,
        'contact_info': contact_info,
    }
    return render(request, 'core/index.html', context)
def services(request):
    services = Service.objects.all().order_by('order')
    service_process = ServiceProcess.objects.first()
    
    context = {
        'services': services,
        'service_process': service_process,
    }
    return render(request, 'core/services.html', context)

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    related_services = Service.objects.exclude(id=service.id).filter(is_featured=True)[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'core/service_detail.html', context)

def team(request):
    team_members = TeamMember.objects.filter(is_active=True).order_by('order')
    team_about = TeamAbout.objects.first()
    
    context = {
        'team_members': team_members,
        'team_about': team_about,
    }
    return render(request, 'core/team.html', context)

def team_detail(request, slug):
    member = get_object_or_404(TeamMember, slug=slug, is_active=True)
    related_members = TeamMember.objects.exclude(id=member.id).filter(is_active=True).order_by('?')[:4]
    
    context = {
        'member': member,
        'related_members': related_members,
    }
    return render(request, 'core/team_detail.html', context)

def blog(request):
    posts_list = BlogPost.objects.filter(is_published=True).exclude(slug__isnull=True).exclude(slug='').order_by('-publish_date')
    categories = BlogCategory.objects.all()
    
    # Arama
    query = request.GET.get('q')
    if query:
        posts_list = posts_list.filter(title__icontains=query)
    
    # Kategori filtresi
    category_slug = request.GET.get('category')
    if category_slug:
        print("Filtering category slug:", category_slug)
        category = get_object_or_404(BlogCategory, slug=category_slug)
        posts_list = posts_list.filter(category=category)
    
    # Etiket filtresi
    tag_slug = request.GET.get('tag')
    if tag_slug:
        tag = get_object_or_404(BlogTag, slug=tag_slug)
        posts_list = posts_list.filter(tags=tag)
    
    # Sayfalama
    paginator = Paginator(posts_list, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'core/blog.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    related_posts = BlogPost.objects.exclude(id=post.id).filter(is_published=True).order_by('?')[:3]
    site_owner = SiteOwner.objects.first()
    comments = BlogComment.objects.filter(post=post)
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'site_owner': site_owner,
        'comments': comments
    }
    return render(request, 'core/blog_detail.html', context)



def add_comment(request, slug):
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, slug=slug)
        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('content')
        
        if not all([name, email, content]):
            messages.error(request, 'Lütfen tüm alanları doldurun.')
        else:
            BlogComment.objects.create(
                post=post,
                name=name,
                email=email,
                content=content,
                is_approved=False  # Yorumlar önce onay bekler
            )
            messages.success(request, 'Yorumunuz başarıyla gönderildi. Onaylandıktan sonra yayınlanacaktır.')
    
    return redirect('core:blog_detail', slug=slug) 


def contact(request):
    contact_info = ContactInfo.objects.first()
    kvkk_content = KVKKContent.objects.first()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if not all([name, email, subject, message]):
            messages.error(request, 'Lütfen zorunlu alanları doldurun.')
        else:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, 'Mesajınız başarıyla gönderildi. En kısa sürede dönüş yapılacaktır.')
            return redirect('core:contact')
    
    context = {
        'contact_info': contact_info,
        'kvkk_content': kvkk_content,
        'site_owner': SiteOwner.objects.first()
    }
    return render(request, 'core/contact.html', context)

@csrf_exempt
def tinymce_upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']
        try:
            upload_result = upload(image, folder="tinymce_uploads")
            return JsonResponse({'location': upload_result['secure_url']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)