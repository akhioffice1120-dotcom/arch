# dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import csv
from datetime import datetime, timedelta
from decimal import Decimal

from arch_design.models import *
from .forms import *

# Check if user is staff/admin
def is_staff_user(user):
    return user.is_staff or user.is_superuser

# Dashboard Authentication
def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('dashboard_home')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions')
    
    return render(request, 'dashboard/auth/login.html')

def dashboard_logout(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('dashboard_login')

# Dashboard Home
@login_required
@user_passes_test(is_staff_user)
def dashboard_home(request):
    # Statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(status='ongoing').count(),
        'total_inquiries': Inquiry.objects.count(),
        'new_inquiries': Inquiry.objects.filter(status='new').count(),
        'total_services': Service.objects.count(),
        'total_blog_posts': BlogPost.objects.count(),
        'pending_contact_messages': ContactMessage.objects.filter(is_read=False).count(),
        'total_testimonials': Testimonial.objects.count(),
    }
    
    # Recent activities
    recent_inquiries = Inquiry.objects.all().order_by('-created_at')[:5]
    recent_projects = Project.objects.all().order_by('-created_at')[:5]
    recent_messages = ContactMessage.objects.all().order_by('-created_at')[:5]
    
    # Chart data
    projects_by_status = Project.objects.values('status').annotate(count=Count('id'))
    inquiries_by_status = Inquiry.objects.values('status').annotate(count=Count('id'))
    
    # Weekly stats
    weekly_inquiries = []
    for i in range(7, 0, -1):
        date = today - timedelta(days=i)
        count = Inquiry.objects.filter(created_at__date=date).count()
        weekly_inquiries.append({
            'date': date.strftime('%a'),
            'count': count
        })
    
    context = {
        'stats': stats,
        'recent_inquiries': recent_inquiries,
        'recent_projects': recent_projects,
        'recent_messages': recent_messages,
        'projects_by_status': list(projects_by_status),
        'inquiries_by_status': list(inquiries_by_status),
        'weekly_inquiries': weekly_inquiries,
    }
    
    return render(request, 'dashboard/home.html', context)

# Site Configuration
@login_required
@user_passes_test(is_staff_user)
def site_configuration(request):
    config = SiteConfiguration.objects.first()
    if not config:
        config = SiteConfiguration.objects.create()
    
    if request.method == 'POST':
        form = SiteConfigurationForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site configuration updated successfully!')
            return redirect('site_configuration')
    else:
        form = SiteConfigurationForm(instance=config)
    
    return render(request, 'dashboard/site_configuration.html', {'form': form})

# Homepage Sliders Management
@login_required
@user_passes_test(is_staff_user)
def slider_list(request):
    sliders = HomePageSlider.objects.all().order_by('display_order', '-created_at')
    return render(request, 'dashboard/sliders/list.html', {'sliders': sliders})

@login_required
@user_passes_test(is_staff_user)
def slider_create(request):
    if request.method == 'POST':
        form = HomePageSliderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slider created successfully!')
            return redirect('slider_list')
    else:
        form = HomePageSliderForm()
    
    return render(request, 'dashboard/sliders/form.html', {'form': form, 'title': 'Create New Slider'})

@login_required
@user_passes_test(is_staff_user)
def slider_edit(request, pk):
    slider = get_object_or_404(HomePageSlider, pk=pk)
    
    if request.method == 'POST':
        form = HomePageSliderForm(request.POST, request.FILES, instance=slider)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slider updated successfully!')
            return redirect('slider_list')
    else:
        form = HomePageSliderForm(instance=slider)
    
    return render(request, 'dashboard/sliders/form.html', {'form': form, 'title': 'Edit Slider'})

@login_required
@user_passes_test(is_staff_user)
def slider_delete(request, pk):
    slider = get_object_or_404(HomePageSlider, pk=pk)
    if request.method == 'POST':
        slider.delete()
        messages.success(request, 'Slider deleted successfully!')
        return redirect('slider_list')
    
    return render(request, 'dashboard/sliders/delete.html', {'slider': slider})

@login_required
@user_passes_test(is_staff_user)
def slider_reorder(request):
    if request.method == 'POST':
        try:
            order_data = json.loads(request.POST.get('order', '[]'))
            for item in order_data:
                slider = HomePageSlider.objects.get(pk=item['id'])
                slider.display_order = item['order']
                slider.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

# Services Management
@login_required
@user_passes_test(is_staff_user)
def service_category_list(request):
    categories = ServiceCategory.objects.all().order_by('display_order')
    return render(request, 'dashboard/services/categories.html', {'categories': categories})

@login_required
@user_passes_test(is_staff_user)
def service_category_edit(request, pk=None):
    if pk:
        category = get_object_or_404(ServiceCategory, pk=pk)
    else:
        category = None
    
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category {"updated" if pk else "created"} successfully!')
            return redirect('service_category_list')
    else:
        form = ServiceCategoryForm(instance=category)
    
    return render(request, 'dashboard/services/category_form.html', {'form': form, 'category': category})

@login_required
@user_passes_test(is_staff_user)
def service_list(request):
    services = Service.objects.all().order_by('category__display_order', 'display_order')
    return render(request, 'dashboard/services/list.html', {'services': services})

@login_required
@user_passes_test(is_staff_user)
def service_edit(request, pk=None):
    if pk:
        service = get_object_or_404(Service, pk=pk)
    else:
        service = None
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f'Service {"updated" if pk else "created"} successfully!')
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'dashboard/services/form.html', {'form': form, 'service': service})

# Projects Management
@login_required
@user_passes_test(is_staff_user)
def project_category_list(request):
    categories = ProjectCategory.objects.all().order_by('display_order')
    return render(request, 'dashboard/projects/categories.html', {'categories': categories})

@login_required
@user_passes_test(is_staff_user)
def project_category_edit(request, pk=None):
    if pk:
        category = get_object_or_404(ProjectCategory, pk=pk)
    else:
        category = None
    
    if request.method == 'POST':
        form = ProjectCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category {"updated" if pk else "created"} successfully!')
            return redirect('project_category_list')
    else:
        form = ProjectCategoryForm(instance=category)
    
    return render(request, 'dashboard/projects/category_form.html', {'form': form, 'category': category})

@login_required
@user_passes_test(is_staff_user)
def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        projects = projects.filter(status=status_filter)
    if category_filter:
        projects = projects.filter(categories__id=category_filter)
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(client_name__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ProjectCategory.objects.all()
    
    return render(request, 'dashboard/projects/list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
    })

@login_required
@user_passes_test(is_staff_user)
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            
            # Handle multiple images upload
            images = request.FILES.getlist('additional_images')
            for i, image in enumerate(images):
                ProjectImage.objects.create(
                    project=project,
                    image=image,
                    display_order=i
                )
            
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'dashboard/projects/form.html', {'form': form, 'title': 'Create New Project'})

@login_required
@user_passes_test(is_staff_user)
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            
            # Handle additional images
            images = request.FILES.getlist('additional_images')
            for i, image in enumerate(images):
                ProjectImage.objects.create(
                    project=project,
                    image=image,
                    display_order=project.images.count() + i
                )
            
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'dashboard/projects/form.html', {
        'form': form,
        'project': project,
        'title': 'Edit Project'
    })

@login_required
@user_passes_test(is_staff_user)
def project_images(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        # Handle image upload
        images = request.FILES.getlist('images')
        for image in images:
            ProjectImage.objects.create(
                project=project,
                image=image,
                display_order=project.images.count()
            )
        messages.success(request, 'Images uploaded successfully!')
        return redirect('project_images', pk=pk)
    
    return render(request, 'dashboard/projects/images.html', {'project': project})

@login_required
@user_passes_test(is_staff_user)
def project_image_delete(request, pk):
    image = get_object_or_404(ProjectImage, pk=pk)
    project_pk = image.project.pk
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('project_images', pk=project_pk)
    
    return render(request, 'dashboard/projects/image_delete.html', {'image': image})

@login_required
@user_passes_test(is_staff_user)
def project_image_reorder(request):
    if request.method == 'POST':
        try:
            order_data = json.loads(request.POST.get('order', '[]'))
            for item in order_data:
                image = ProjectImage.objects.get(pk=item['id'])
                image.display_order = item['order']
                image.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

# 3D Designs Management
@login_required
@user_passes_test(is_staff_user)
def three_d_design_list(request, project_pk=None):
    if project_pk:
        project = get_object_or_404(Project, pk=project_pk)
        designs = project.three_d_designs.all().order_by('display_order')
    else:
        project = None
        designs = ThreeDDesign.objects.all().order_by('display_order')
    
    return render(request, 'dashboard/3d_designs/list.html', {
        'designs': designs,
        'project': project
    })

@login_required
@user_passes_test(is_staff_user)
def three_d_design_edit(request, pk=None, project_pk=None):
    if pk:
        design = get_object_or_404(ThreeDDesign, pk=pk)
        project = design.project
    else:
        design = None
        project = get_object_or_404(Project, pk=project_pk) if project_pk else None
    
    if request.method == 'POST':
        form = ThreeDDesignForm(request.POST, request.FILES, instance=design)
        if form.is_valid():
            if not design and project:
                form.instance.project = project
            design = form.save()
            messages.success(request, f'3D Design {"updated" if pk else "created"} successfully!')
            return redirect('three_d_design_list', project_pk=design.project.pk if design.project else None)
    else:
        form = ThreeDDesignForm(instance=design)
        if project:
            form.fields['project'].initial = project
    
    return render(request, 'dashboard/3d_designs/form.html', {'form': form, 'design': design})

# Gallery Management
@login_required
@user_passes_test(is_staff_user)
def gallery_category_list(request):
    categories = GalleryCategory.objects.all().order_by('display_order')
    return render(request, 'dashboard/gallery/categories.html', {'categories': categories})

@login_required
@user_passes_test(is_staff_user)
def gallery_category_edit(request, pk=None):
    if pk:
        category = get_object_or_404(GalleryCategory, pk=pk)
    else:
        category = None
    
    if request.method == 'POST':
        form = GalleryCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category {"updated" if pk else "created"} successfully!')
            return redirect('gallery_category_list')
    else:
        form = GalleryCategoryForm(instance=category)
    
    return render(request, 'dashboard/gallery/category_form.html', {'form': form, 'category': category})

@login_required
@user_passes_test(is_staff_user)
def gallery_image_list(request):
    images = GalleryImage.objects.all().order_by('-created_at')
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        images = images.filter(category_id=category_filter)
    
    paginator = Paginator(images, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = GalleryCategory.objects.all()
    
    return render(request, 'dashboard/gallery/images.html', {
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
    })

@login_required
@user_passes_test(is_staff_user)
def gallery_image_edit(request, pk=None):
    if pk:
        image = get_object_or_404(GalleryImage, pk=pk)
    else:
        image = None
    
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, f'Image {"updated" if pk else "created"} successfully!')
            return redirect('gallery_image_list')
    else:
        form = GalleryImageForm(instance=image)
    
    return render(request, 'dashboard/gallery/image_form.html', {'form': form, 'image': image})

@login_required
@user_passes_test(is_staff_user)
def gallery_bulk_upload(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = get_object_or_404(GalleryCategory, pk=category_id) if category_id else None
        
        images = request.FILES.getlist('images')
        uploaded = 0
        
        for image in images:
            GalleryImage.objects.create(
                category=category,
                image=image,
                title=image.name.split('.')[0]
            )
            uploaded += 1
        
        messages.success(request, f'{uploaded} images uploaded successfully!')
        return redirect('gallery_image_list')
    
    categories = GalleryCategory.objects.all()
    return render(request, 'dashboard/gallery/bulk_upload.html', {'categories': categories})

# Testimonials Management
@login_required
@user_passes_test(is_staff_user)
def testimonial_list(request):
    testimonials = Testimonial.objects.all().order_by('-created_at')
    
    approved_filter = request.GET.get('approved', '')
    if approved_filter == 'yes':
        testimonials = testimonials.filter(is_approved=True)
    elif approved_filter == 'no':
        testimonials = testimonials.filter(is_approved=False)
    
    paginator = Paginator(testimonials, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/testimonials/list.html', {
        'page_obj': page_obj,
        'approved_filter': approved_filter,
    })

@login_required
@user_passes_test(is_staff_user)
def testimonial_edit(request, pk=None):
    if pk:
        testimonial = get_object_or_404(Testimonial, pk=pk)
    else:
        testimonial = None
    
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, f'Testimonial {"updated" if pk else "created"} successfully!')
            return redirect('testimonial_list')
    else:
        form = TestimonialForm(instance=testimonial)
    
    return render(request, 'dashboard/testimonials/form.html', {'form': form, 'testimonial': testimonial})

@login_required
@user_passes_test(is_staff_user)
def testimonial_toggle_approve(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    testimonial.is_approved = not testimonial.is_approved
    testimonial.save()
    
    action = "approved" if testimonial.is_approved else "unapproved"
    messages.success(request, f'Testimonial {action} successfully!')
    return redirect('testimonial_list')

# Team Management
@login_required
@user_passes_test(is_staff_user)
def team_list(request):
    team = TeamMember.objects.all().order_by('display_order')
    return render(request, 'dashboard/team/list.html', {'team': team})

@login_required
@user_passes_test(is_staff_user)
def team_edit(request, pk=None):
    if pk:
        member = get_object_or_404(TeamMember, pk=pk)
    else:
        member = None
    
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f'Team member {"updated" if pk else "created"} successfully!')
            return redirect('team_list')
    else:
        form = TeamMemberForm(instance=member)
    
    return render(request, 'dashboard/team/form.html', {'form': form, 'member': member})

# Blog Management
@login_required
@user_passes_test(is_staff_user)
def blog_category_list(request):
    categories = BlogCategory.objects.all()
    return render(request, 'dashboard/blog/categories.html', {'categories': categories})

@login_required
@user_passes_test(is_staff_user)
def blog_category_edit(request, pk=None):
    if pk:
        category = get_object_or_404(BlogCategory, pk=pk)
    else:
        category = None
    
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category {"updated" if pk else "created"} successfully!')
            return redirect('blog_category_list')
    else:
        form = BlogCategoryForm(instance=category)
    
    return render(request, 'dashboard/blog/category_form.html', {'form': form, 'category': category})

@login_required
@user_passes_test(is_staff_user)
def blog_tag_list(request):
    tags = BlogTag.objects.all()
    return render(request, 'dashboard/blog/tags.html', {'tags': tags})

@login_required
@user_passes_test(is_staff_user)
def blog_tag_edit(request, pk=None):
    if pk:
        tag = get_object_or_404(BlogTag, pk=pk)
    else:
        tag = None
    
    if request.method == 'POST':
        form = BlogTagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tag {"updated" if pk else "created"} successfully!')
            return redirect('blog_tag_list')
    else:
        form = BlogTagForm(instance=tag)
    
    return render(request, 'dashboard/blog/tag_form.html', {'form': form, 'tag': tag})

@login_required
@user_passes_test(is_staff_user)
def blog_post_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        posts = posts.filter(status=status_filter)
    if category_filter:
        posts = posts.filter(categories__id=category_filter)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = BlogCategory.objects.all()
    
    return render(request, 'dashboard/blog/posts.html', {
        'page_obj': page_obj,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
    })

@login_required
@user_passes_test(is_staff_user)
def blog_post_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if post.status == 'published' and not post.published_date:
                post.published_date = timezone.now()
            post.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Blog post created successfully!')
            return redirect('blog_post_list')
    else:
        form = BlogPostForm(initial={'author': request.user})
    
    return render(request, 'dashboard/blog/post_form.html', {'form': form, 'title': 'Create New Post'})

@login_required
@user_passes_test(is_staff_user)
def blog_post_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if post.status == 'published' and not post.published_date:
                post.published_date = timezone.now()
            post.save()
            form.save_m2m()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('blog_post_list')
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'dashboard/blog/post_form.html', {'form': form, 'post': post, 'title': 'Edit Post'})

@login_required
@user_passes_test(is_staff_user)
def blog_post_preview(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'dashboard/blog/preview.html', {'post': post})

# Company Info Management
@login_required
@user_passes_test(is_staff_user)
def company_info_list(request):
    sections = CompanyInfo.objects.all().order_by('display_order')
    return render(request, 'dashboard/company_info/list.html', {'sections': sections})

@login_required
@user_passes_test(is_staff_user)
def company_info_edit(request, pk=None):
    if pk:
        section = get_object_or_404(CompanyInfo, pk=pk)
    else:
        section = None
    
    if request.method == 'POST':
        form = CompanyInfoForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, f'Section {"updated" if pk else "created"} successfully!')
            return redirect('company_info_list')
    else:
        form = CompanyInfoForm(instance=section)
    
    return render(request, 'dashboard/company_info/form.html', {'form': form, 'section': section})

# Inquiries Management
@login_required
@user_passes_test(is_staff_user)
def inquiry_list(request):
    inquiries = Inquiry.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status', '')
    service_filter = request.GET.get('service', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if status_filter:
        inquiries = inquiries.filter(status=status_filter)
    if service_filter:
        inquiries = inquiries.filter(service_type=service_filter)
    if date_from:
        inquiries = inquiries.filter(created_at__date__gte=date_from)
    if date_to:
        inquiries = inquiries.filter(created_at__date__lte=date_to)
    
    paginator = Paginator(inquiries, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/inquiries/list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'service_filter': service_filter,
        'date_from': date_from,
        'date_to': date_to,
    })

@login_required
@user_passes_test(is_staff_user)
def inquiry_detail(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk)
    
    if request.method == 'POST':
        form = InquiryStatusForm(request.POST, instance=inquiry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inquiry updated successfully!')
            return redirect('inquiry_detail', pk=pk)
    else:
        form = InquiryStatusForm(instance=inquiry)
    
    return render(request, 'dashboard/inquiries/detail.html', {
        'inquiry': inquiry,
        'form': form
    })

@login_required
@user_passes_test(is_staff_user)
def inquiry_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inquiries.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Inquiry ID', 'Name', 'Email', 'Phone', 'Service Type',
        'Budget Range', 'Status', 'Created At', 'Follow Up Date'
    ])
    
    inquiries = Inquiry.objects.all().order_by('-created_at')
    
    for inquiry in inquiries:
        writer.writerow([
            inquiry.inquiry_id,
            inquiry.name,
            inquiry.email,
            inquiry.phone,
            inquiry.get_service_type_display(),
            inquiry.get_budget_range_display(),
            inquiry.get_status_display(),
            inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            inquiry.follow_up_date.strftime('%Y-%m-%d') if inquiry.follow_up_date else ''
        ])
    
    return response

# Contact Messages
@login_required
@user_passes_test(is_staff_user)
def contact_message_list(request):
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    
    read_filter = request.GET.get('read', '')
    replied_filter = request.GET.get('replied', '')
    
    if read_filter == 'yes':
        messages_list = messages_list.filter(is_read=True)
    elif read_filter == 'no':
        messages_list = messages_list.filter(is_read=False)
    
    if replied_filter == 'yes':
        messages_list = messages_list.filter(replied=True)
    elif replied_filter == 'no':
        messages_list = messages_list.filter(replied=False)
    
    paginator = Paginator(messages_list, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/contact_messages/list.html', {
        'page_obj': page_obj,
        'read_filter': read_filter,
        'replied_filter': replied_filter,
    })

@login_required
@user_passes_test(is_staff_user)
def contact_message_detail(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    
    if not message.is_read:
        message.is_read = True
        message.save()
    
    if request.method == 'POST':
        reply_notes = request.POST.get('reply_notes', '')
        if reply_notes:
            message.reply_notes = reply_notes
            message.replied = True
            message.save()
            messages.success(request, 'Reply notes saved successfully!')
        return redirect('contact_message_detail', pk=pk)
    
    return render(request, 'dashboard/contact_messages/detail.html', {'message': message})

# Dashboard Settings
@login_required
@user_passes_test(is_staff_user)
def dashboard_settings(request):
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard_settings')
    
    return render(request, 'dashboard/settings.html')

# AJAX endpoints for dashboard
@login_required
@user_passes_test(is_staff_user)
def update_status(request, model, pk):
    if request.method == 'POST' and request.is_ajax():
        try:
            status = request.POST.get('status')
            
            if model == 'project':
                obj = get_object_or_404(Project, pk=pk)
                obj.status = status
            elif model == 'inquiry':
                obj = get_object_or_404(Inquiry, pk=pk)
                obj.status = status
            elif model == 'blog':
                obj = get_object_or_404(BlogPost, pk=pk)
                obj.status = status
            
            obj.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff_user)
def toggle_featured(request, model, pk):
    if request.method == 'POST' and request.is_ajax():
        try:
            if model == 'project':
                obj = get_object_or_404(Project, pk=pk)
                obj.is_featured = not obj.is_featured
            elif model == 'service':
                obj = get_object_or_404(Service, pk=pk)
                obj.is_featured = not obj.is_featured
            elif model == 'testimonial':
                obj = get_object_or_404(Testimonial, pk=pk)
                obj.is_featured = not obj.is_featured
            elif model == 'blog':
                obj = get_object_or_404(BlogPost, pk=pk)
                obj.is_featured = not obj.is_featured
            elif model == 'gallery':
                obj = get_object_or_404(GalleryImage, pk=pk)
                obj.is_featured = not obj.is_featured
            
            obj.save()
            return JsonResponse({'success': True, 'is_featured': obj.is_featured})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

@login_required
@user_passes_test(is_staff_user)
def get_dashboard_stats(request):
    if request.is_ajax():
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        stats = {
            'inquiries_today': Inquiry.objects.filter(created_at__date=today).count(),
            'inquiries_week': Inquiry.objects.filter(created_at__date__gte=week_ago).count(),
            'messages_unread': ContactMessage.objects.filter(is_read=False).count(),
            'projects_ongoing': Project.objects.filter(status='ongoing').count(),
        }
        
        return JsonResponse(stats)
    
    return JsonResponse({})