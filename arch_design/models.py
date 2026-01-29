# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField
import uuid

# Create your models here.

class TimeStampedModel(models.Model):
    """Abstract base model with automatic created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class SiteConfiguration(models.Model):
    """Global site settings that can be configured via admin"""
    site_name = models.CharField(max_length=200, default="Arch Design & Development")
    company_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='site/logo/', null=True, blank=True)
    favicon = models.ImageField(upload_to='site/favicon/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default="#1a365d")  # Dark Blue
    secondary_color = models.CharField(max_length=7, default="#2d3748")  # Gray
    accent_color = models.CharField(max_length=7, default="#3182ce")  # Light Blue
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    contact_address = models.TextField()
    facebook_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    google_map_embed = models.TextField(help_text="Embed code for Google Map")
    
    def __str__(self):
        return "Site Configuration"
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

class HomePageSlider(TimeStampedModel):
    """Slider/Banner images for home page"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='sliders/')
    button_text = models.CharField(max_length=50, default="View Projects")
    button_link = models.CharField(max_length=200, default="/projects")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Home Page Slider"
        verbose_name_plural = "Home Page Sliders"
    
    def __str__(self):
        return self.title

class ServiceCategory(models.Model):
    """Category for services (Exterior/Interior)"""
    CATEGORY_CHOICES = [
        ('exterior', 'Exterior Services'),
        ('interior', 'Interior Services'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category_type = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    icon_class = models.CharField(max_length=50, blank=True, null=True, 
                                  help_text="FontAwesome or custom icon class")
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Service(TimeStampedModel):
    """Individual services offered by the company"""
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, 
                                 related_name='services')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.TextField(max_length=300)
    full_description = RichTextField()
    icon = models.ImageField(upload_to='services/icons/', blank=True, null=True)
    featured_image = models.ImageField(upload_to='services/featured/')
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Service"
        verbose_name_plural = "Services"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProjectCategory(models.Model):
    """Categories for projects"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Project Category"
        verbose_name_plural = "Project Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Project(TimeStampedModel):
    """Portfolio projects"""
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('ongoing', 'Ongoing'),
        ('upcoming', 'Upcoming'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    client_name = models.CharField(max_length=200)
    categories = models.ManyToManyField(ProjectCategory, related_name='projects')
    service_type = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, 
                                     null=True, related_name='projects')
    location = models.CharField(max_length=200)
    area = models.CharField(max_length=100, help_text="e.g., 2500 sq ft")
    duration = models.CharField(max_length=100, help_text="e.g., 6 months")
    budget = models.CharField(max_length=100, blank=True, null=True)
    short_description = models.TextField(max_length=300)
    full_description = RichTextField()
    featured_image = models.ImageField(upload_to='projects/featured/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    start_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    show_on_homepage = models.BooleanField(default=False)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube/Vimeo URL for project video")
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-completion_date', '-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class ProjectImage(models.Model):
    """Multiple images for a project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order']
        verbose_name = "Project Image"
        verbose_name_plural = "Project Images"
    
    def __str__(self):
        return f"Image for {self.project.title}"

class ThreeDDesign(models.Model):
    """3D Design visualization files"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='three_d_designs')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='projects/3d-designs/')
    video_url = models.URLField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order']
        verbose_name = "3D Design"
        verbose_name_plural = "3D Designs"
    
    def __str__(self):
        return self.title

class GalleryCategory(models.Model):
    """Categories for gallery images"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class GalleryImage(TimeStampedModel):
    """Images for gallery section"""
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
    
    def __str__(self):
        return self.title or f"Gallery Image {self.id}"

class Testimonial(TimeStampedModel):
    """Client testimonials/reviews"""
    client_name = models.CharField(max_length=200)
    client_photo = models.ImageField(upload_to='testimonials/photos/', blank=True, null=True)
    client_designation = models.CharField(max_length=200, blank=True, null=True)
    client_company = models.CharField(max_length=200, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, 
                                related_name='testimonials')
    review_text = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    is_approved = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
    
    def __str__(self):
        return f"Testimonial by {self.client_name}"

class TeamMember(TimeStampedModel):
    """Team members for About Us page"""
    POSITION_CHOICES = [
        ('founder', 'Founder/CEO'),
        ('director', 'Director'),
        ('manager', 'Project Manager'),
        ('designer', 'Designer'),
        ('architect', 'Architect'),
        ('engineer', 'Engineer'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    custom_position = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='team/')
    bio = models.TextField()
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    expertise = models.CharField(max_length=300, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
    
    def __str__(self):
        return self.name

class BlogPost(TimeStampedModel):
    """Blog/News articles"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    excerpt = models.TextField(max_length=300)
    content = RichTextField()
    featured_image = models.ImageField(upload_to='blog/')
    categories = models.ManyToManyField('BlogCategory', related_name='posts')
    tags = models.ManyToManyField('BlogTag', related_name='posts', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_date = models.DateTimeField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-published_date', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        super().save(*args, **kwargs)

class BlogCategory(models.Model):
    """Categories for blog posts"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class BlogTag(models.Model):
    """Tags for blog posts"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Blog Tag"
        verbose_name_plural = "Blog Tags"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Inquiry(TimeStampedModel):
    """Client inquiries/quotations"""
    SERVICE_TYPE_CHOICES = [
        ('exterior', 'Exterior Design'),
        ('interior', 'Interior Design'),
        ('both', 'Both Exterior & Interior'),
        ('other', 'Other'),
    ]
    
    BUDGET_RANGE_CHOICES = [
        ('under_5', 'Under 5 Lakh'),
        ('5_10', '5-10 Lakh'),
        ('10_20', '10-20 Lakh'),
        ('20_50', '20-50 Lakh'),
        ('50_above', '50 Lakh+'),
        ('not_sure', 'Not Sure'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('quoted', 'Quoted'),
        ('follow_up', 'Follow Up'),
        ('converted', 'Converted'),
        ('rejected', 'Rejected'),
    ]
    
    inquiry_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    specific_service = models.ForeignKey(Service, on_delete=models.SET_NULL, 
                                         blank=True, null=True)
    budget_range = models.CharField(max_length=20, choices=BUDGET_RANGE_CHOICES)
    project_description = models.TextField()
    is_urgent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                    blank=True, null=True, related_name='assigned_inquiries')
    follow_up_date = models.DateField(blank=True, null=True)
    converted_to_project = models.ForeignKey(Project, on_delete=models.SET_NULL, 
                                             blank=True, null=True, related_name='inquiries')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Inquiry"
        verbose_name_plural = "Inquiries"
    
    def __str__(self):
        return f"Inquiry from {self.name} - {self.get_service_type_display()}"

class InquiryAttachment(models.Model):
    """File attachments for inquiries"""
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='inquiry_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Inquiry Attachment"
        verbose_name_plural = "Inquiry Attachments"
    
    def __str__(self):
        return f"Attachment for {self.inquiry.name}"

class CompanyInfo(TimeStampedModel):
    """Company information for About Us page"""
    SECTION_CHOICES = [
        ('mission', 'Mission'),
        ('vision', 'Vision'),
        ('values', 'Values'),
        ('history', 'History'),
        ('achievements', 'Achievements'),
    ]
    
    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    title = models.CharField(max_length=200)
    content = RichTextField()
    icon_class = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='company/', blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order']
        verbose_name = "Company Information"
        verbose_name_plural = "Company Information"
    
    def __str__(self):
        return f"{self.get_section_display()}: {self.title}"

class ContactMessage(TimeStampedModel):
    """Messages from contact form"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    reply_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
    
    def __str__(self):
        return f"Message from {self.name}: {self.subject}"

# Future Scalability Models (Commented out for now, can be enabled as needed)

# class CostCalculatorCategory(models.Model):
#     """Categories for cost calculator"""
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True, null=True)
#     base_price = models.DecimalField(max_digits=10, decimal_places=2)
#     unit = models.CharField(max_length=50, help_text="e.g., per sq ft, per item")
    
#     def __str__(self):
#         return self.name
# 
# class ClientDashboard(models.Model):
#     """Client dashboard for project tracking"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     client_id = models.CharField(max_length=50, unique=True)
#     phone = models.CharField(max_length=20)
#     address = models.TextField()
#     projects = models.ManyToManyField(Project, blank=True)
#     
#     def __str__(self):
#         return f"Dashboard for {self.user.get_full_name()}"
# 
# class OnlineBooking(models.Model):
#     """Online booking system"""
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('confirmed', 'Confirmed'),
#         ('cancelled', 'Cancelled'),
#         ('completed', 'Completed'),
#     ]
#     
#     booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     client = models.ForeignKey(User, on_delete=models.CASCADE)
#     service = models.ForeignKey(Service, on_delete=models.CASCADE)
#     booking_date = models.DateTimeField()
#     duration = models.PositiveIntegerField(help_text="Duration in hours")
#     notes = models.TextField(blank=True, null=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)
#     
#     def __str__(self):
#         return f"Booking {self.booking_id} for {self.service.name}"