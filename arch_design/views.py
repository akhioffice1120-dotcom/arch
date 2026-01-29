# arch_design/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import (
    HomePageSlider, Service, ServiceCategory, Project,
    ProjectCategory, GalleryCategory, GalleryImage, 
    Testimonial, TeamMember, BlogPost, BlogCategory,
    CompanyInfo, Inquiry, ContactMessage, SiteConfiguration,
    ThreeDDesign
)
from .forms import InquiryForm, ContactMessageForm

class HomeView(TemplateView):
    """Enhanced Home Page View with all sections"""
    template_name = 'arch_design/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Hero Slider
        context['sliders'] = HomePageSlider.objects.filter(
            is_active=True
        ).order_by('display_order')
        
        # Company Info
        try:
            context['company_info'] = CompanyInfo.objects.filter(
                section__in=['mission', 'vision']
            ).order_by('display_order')[:2]
        except:
            context['company_info'] = []
        
        # Services Highlight
        context['exterior_services'] = Service.objects.filter(
            category__category_type='exterior',
            is_featured=True
        ).order_by('display_order')[:3]

        context['interior_services'] = Service.objects.filter(
            category__category_type='interior',
            is_featured=True
        ).order_by('display_order')[:3]
        
        # Featured Projects
        context['featured_projects'] = Project.objects.filter(
            is_featured=True,
            show_on_homepage=True
        ).order_by('-completion_date')[:6]
        
        # Statistics
        context['projects_count'] = Project.objects.filter(status='completed').count()
        context['services_count'] = Service.objects.count()
        context['clients_count'] = Testimonial.objects.filter(is_approved=True).count()
        context['team_count'] = TeamMember.objects.filter(is_active=True).count()
        
        # Testimonials
        context['testimonials'] = Testimonial.objects.filter(
            is_approved=True,
            is_featured=True
        ).order_by('display_order')[:5]
        
        # Latest Blog Posts
        context['latest_posts'] = BlogPost.objects.filter(
            status='published'
        ).order_by('-published_date')[:3]
        
        # 3D Designs Highlight
        context['three_d_designs'] = ThreeDDesign.objects.all().order_by('display_order')[:4]
        
        return context

class AboutView(TemplateView):
    """About Us Page View"""
    template_name = 'arch_design/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Company Info Sections
        context['company_sections'] = CompanyInfo.objects.all().order_by('display_order')
        
        # Team Members
        context['team_members'] = TeamMember.objects.filter(
            is_active=True
        ).order_by('display_order')
        
        # Company Statistics
        context['completed_projects'] = Project.objects.filter(status='completed').count()
        context['years_experience'] = 10  # You can calculate this dynamically
        context['happy_clients'] = Testimonial.objects.filter(is_approved=True).count()
        
        # Recent Projects
        context['recent_projects'] = Project.objects.filter(
            status='completed'
        ).order_by('-completion_date')[:4]
        
        return context

class ServiceListView(ListView):
    """Services List Page"""
    model = Service
    template_name = 'arch_design/services.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        category_type = self.kwargs.get('category_type', None)
        if category_type:
            return Service.objects.filter(
                category__category_type=category_type
            ).order_by('display_order')
        return Service.objects.all().order_by('display_order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.all().order_by('display_order')
        context['selected_category'] = self.kwargs.get('category_type', 'all')
        return context

class ServiceDetailView(DetailView):
    """Service Detail Page"""
    model = Service
    template_name = 'arch_design/service_detail.html'
    context_object_name = 'service'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.get_object()
        
        # Related services
        context['related_services'] = Service.objects.filter(
            category=service.category
        ).exclude(id=service.id).order_by('display_order')[:4]
        
        # Related projects for this service
        context['related_projects'] = Project.objects.filter(
            service_type=service.category
        ).order_by('-completion_date')[:3]
        
        return context

class ProjectListView(ListView):
    """Projects Portfolio Page with Filtering"""
    model = Project
    template_name = 'arch_design/projects.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Project.objects.all().order_by('-completion_date', '-created_at')
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by service type
        service_type = self.request.GET.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type__category_type=service_type)
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(client_name__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProjectCategory.objects.all().order_by('name')
        context['project_statuses'] = Project.STATUS_CHOICES
        context['service_types'] = ServiceCategory.CATEGORY_CHOICES
        
        # Get filter values
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_service_type'] = self.request.GET.get('service_type', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        return context

class ProjectDetailView(DetailView):
    """Project Detail Page"""
    model = Project
    template_name = 'arch_design/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Get project images
        context['project_images'] = project.images.all().order_by('display_order')
        
        # Get 3D designs
        context['three_d_designs'] = project.three_d_designs.all().order_by('display_order')
        
        # Related projects
        context['related_projects'] = Project.objects.filter(
            categories__in=project.categories.all()
        ).exclude(id=project.id).distinct()[:4]
        
        return context

class GalleryView(TemplateView):
    """Gallery Page"""
    template_name = 'arch_design/gallery.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # All gallery categories
        context['categories'] = GalleryCategory.objects.all().order_by('display_order')
        
        # Featured images from all categories
        context['featured_images'] = GalleryImage.objects.filter(
            is_featured=True
        ).order_by('display_order')[:20]
        
        # Category with images for grid
        categories_with_images = []
        for category in context['categories']:
            images = category.images.filter(is_featured=True)[:8]
            if images:
                categories_with_images.append({
                    'category': category,
                    'images': images
                })
        
        context['categories_with_images'] = categories_with_images[:3]
        
        return context

class GalleryCategoryView(DetailView):
    """Gallery Images by Category"""
    model = GalleryCategory
    template_name = 'arch_design/gallery_category.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        
        # Get all images for this category
        images = category.images.all().order_by('display_order')
        
        # Pagination
        paginator = Paginator(images, 20)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context['all_categories'] = GalleryCategory.objects.all().order_by('display_order')
        
        return context

class TestimonialListView(ListView):
    """Testimonials Page"""
    model = Testimonial
    template_name = 'arch_design/testimonials.html'
    context_object_name = 'testimonials'
    paginate_by = 10
    
    def get_queryset(self):
        return Testimonial.objects.filter(
            is_approved=True
        ).order_by('-created_at', 'display_order')

class BlogListView(ListView):
    """Blog/News List Page"""
    model = BlogPost
    template_name = 'arch_design/blog.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(status='published').order_by('-published_date')
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
        
        # Filter by tag
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Blog categories
        context['categories'] = BlogCategory.objects.all()
        
        # Recent posts
        context['recent_posts'] = BlogPost.objects.filter(
            status='published'
        ).order_by('-published_date')[:5]
        
        # Popular posts (by views)
        context['popular_posts'] = BlogPost.objects.filter(
            status='published'
        ).order_by('-views_count')[:5]
        
        # Filter values
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_tag'] = self.request.GET.get('tag', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        return context

class BlogDetailView(DetailView):
    """Blog Post Detail Page"""
    model = BlogPost
    template_name = 'arch_design/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Related posts
        context['related_posts'] = BlogPost.objects.filter(
            status='published',
            categories__in=post.categories.all()
        ).exclude(id=post.id).distinct()[:3]
        
        # Next and previous posts
        context['next_post'] = BlogPost.objects.filter(
            status='published',
            published_date__lt=post.published_date
        ).order_by('-published_date').first()
        
        context['prev_post'] = BlogPost.objects.filter(
            status='published',
            published_date__gt=post.published_date
        ).order_by('published_date').first()
        
        return context

class ContactView(FormView):
    """Contact Page with Form"""
    template_name = 'arch_design/contact.html'
    form_class = ContactMessageForm
    success_url = reverse_lazy('contact')
    
    def form_valid(self, form):
        # Save the contact message
        contact_message = form.save()
        
        # Send email notification (optional)
        try:
            site_config = SiteConfiguration.objects.first()
            if site_config and site_config.contact_email:
                send_mail(
                    subject=f'New Contact Message: {contact_message.subject}',
                    message=f'''
                    Name: {contact_message.name}
                    Email: {contact_message.email}
                    Subject: {contact_message.subject}
                    Message: {contact_message.message}
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[site_config.contact_email],
                    fail_silently=True,
                )
        except:
            pass
        
        messages.success(self.request, 'Thank you for your message! We will contact you soon.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get site configuration for contact info
        try:
            context['site_config'] = SiteConfiguration.objects.first()
        except:
            context['site_config'] = None
        
        return context

class InquiryCreateView(CreateView):
    """Inquiry/Quotation Form View"""
    model = Inquiry
    form_class = InquiryForm
    template_name = 'arch_design/inquiry_form.html'
    success_url = reverse_lazy('inquiry_success')
    
    def form_valid(self, form):
        # Save the inquiry
        inquiry = form.save()
        
        # Send email notification
        try:
            site_config = SiteConfiguration.objects.first()
            if site_config and site_config.contact_email:
                send_mail(
                    subject=f'New Project Inquiry: {inquiry.name}',
                    message=f'''
                    New Project Inquiry Received!
                    
                    Inquiry ID: {inquiry.inquiry_id}
                    Name: {inquiry.name}
                    Email: {inquiry.email}
                    Phone: {inquiry.phone}
                    Service Type: {inquiry.get_service_type_display()}
                    Budget Range: {inquiry.get_budget_range_display()}
                    Project Description: {inquiry.project_description}
                    
                    Login to admin panel to view details.
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[site_config.contact_email],
                    fail_silently=True,
                )
        except:
            pass
        
        # Send confirmation email to client
        try:
            send_mail(
                subject='Thank you for your inquiry - Arch Design & Development',
                message=f'''
                Dear {inquiry.name},
                
                Thank you for your inquiry. We have received your request for {inquiry.get_service_type_display()}.
                
                Our team will review your project details and contact you within 24-48 hours.
                
                Inquiry ID: {inquiry.inquiry_id}
                Service Type: {inquiry.get_service_type_display()}
                
                Best regards,
                Arch Design & Development Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inquiry.email],
                fail_silently=True,
            )
        except:
            pass
        
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get services for dropdown
        context['services'] = Service.objects.filter(is_featured=True).order_by('name')
        
        return context

def inquiry_success(request):
    """Inquiry Success Page"""
    return render(request, 'arch_design/inquiry_success.html')

# AJAX views for dynamic content
def get_service_details(request, service_id):
    """Get service details for AJAX requests"""
    try:
        service = Service.objects.get(id=service_id)
        data = {
            'name': service.name,
            'description': service.short_description,
            'category': service.category.name,
            'image_url': service.featured_image.url if service.featured_image else '',
        }
        return JsonResponse(data)
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)

def search_autocomplete(request):
    """Search autocomplete for AJAX requests"""
    query = request.GET.get('q', '')
    
    if query:
        # Search in projects
        projects = Project.objects.filter(
            Q(title__icontains=query) |
            Q(client_name__icontains=query) |
            Q(location__icontains=query)
        )[:5]
        
        # Search in services
        services = Service.objects.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query)
        )[:5]
        
        # Search in blog posts
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query)
        )[:5]
        
        results = []
        
        for project in projects:
            results.append({
                'type': 'Project',
                'title': project.title,
                'url': reverse_lazy('project_detail', kwargs={'slug': project.slug}),
                'description': project.short_description[:100] + '...' if len(project.short_description) > 100 else project.short_description
            })
        
        for service in services:
            results.append({
                'type': 'Service',
                'title': service.name,
                'url': reverse_lazy('service_detail', kwargs={'slug': service.slug}),
                'description': service.short_description[:100] + '...' if len(service.short_description) > 100 else service.short_description
            })
        
        for post in posts:
            results.append({
                'type': 'Blog',
                'title': post.title,
                'url': reverse_lazy('blog_detail', kwargs={'slug': post.slug}),
                'description': post.excerpt[:100] + '...' if len(post.excerpt) > 100 else post.excerpt
            })
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})

def get_projects_by_service(request, service_id):
    """Get projects by service for AJAX requests"""
    try:
        service = Service.objects.get(id=service_id)
        projects = Project.objects.filter(service_type=service.category)[:6]
        
        project_list = []
        for project in projects:
            project_list.append({
                'id': project.id,
                'title': project.title,
                'slug': project.slug,
                'image': project.featured_image.url if project.featured_image else '',
                'short_description': project.short_description[:150] + '...' if len(project.short_description) > 150 else project.short_description,
                'status': project.get_status_display(),
            })
        
        return JsonResponse({'projects': project_list})
    except Service.DoesNotExist:
        return JsonResponse({'projects': []})