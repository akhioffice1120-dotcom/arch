# arch_design/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteConfiguration, HomePageSlider, ServiceCategory, Service,
    ProjectCategory, Project, ProjectImage, ThreeDDesign,
    GalleryCategory, GalleryImage, Testimonial, TeamMember,
    BlogPost, BlogCategory, BlogTag, Inquiry, InquiryAttachment,
    CompanyInfo, ContactMessage
)

# Custom Admin Site
class ArchDesignAdminSite(admin.AdminSite):
    site_header = 'Arch Design & Development Admin'
    site_title = 'Admin Panel'
    index_title = 'Dashboard'

# Register models with custom admin classes
@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Allow only one configuration object
        count = SiteConfiguration.objects.count()
        if count == 0:
            return True
        return False

@admin.register(HomePageSlider)
class HomePageSliderAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'subtitle']

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'display_order', 'slug']
    list_filter = ['category_type']
    search_fields = ['name']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_featured', 'display_order']
    list_filter = ['category', 'is_featured']
    search_fields = ['name', 'short_description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'display_order']

class ThreeDDesignInline(admin.TabularInline):
    model = ThreeDDesign
    extra = 1
    fields = ['title', 'image', 'video_url', 'display_order']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'client_name', 'location', 'completion_date']
    list_filter = ['status', 'is_featured', 'show_on_homepage']
    search_fields = ['title', 'client_name', 'location']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline, ThreeDDesignInline]
    filter_horizontal = ['categories']

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'display_order']
    list_filter = ['category', 'is_featured']
    search_fields = ['title', 'description']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'rating', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['is_approved', 'is_featured', 'rating']
    search_fields = ['client_name', 'review_text']

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'is_active', 'display_order']
    list_filter = ['position', 'is_active']
    search_fields = ['name', 'bio']

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'author', 'published_date', 'is_featured']
    list_filter = ['status', 'is_featured', 'categories']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['categories', 'tags']
    date_hierarchy = 'published_date'

class InquiryAttachmentInline(admin.TabularInline):
    model = InquiryAttachment
    extra = 1

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'service_type', 'status', 'created_at']
    list_filter = ['status', 'service_type', 'is_urgent']
    search_fields = ['name', 'email', 'phone', 'project_description']
    readonly_fields = ['inquiry_id', 'created_at', 'updated_at']
    inlines = [InquiryAttachmentInline]

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['section', 'title', 'display_order']
    list_filter = ['section']
    search_fields = ['title', 'content']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'replied', 'created_at']
    list_filter = ['is_read', 'replied']
    search_fields = ['name', 'email', 'subject', 'message']

# Register all models
admin.site.site_header = 'Arch Design & Development Admin'
admin.site.site_title = 'Admin Panel'
admin.site.index_title = 'Dashboard'