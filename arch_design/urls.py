# arch_design/urls.py
from django.urls import path
from . import views


urlpatterns = [
    # Public Pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/<str:category_type>/', views.ServiceListView.as_view(), name='services'),
    path('services/exterior/', views.ServiceListView.as_view(), {'category_type': 'exterior'}, name='exterior_services'),
    path('services/interior/', views.ServiceListView.as_view(), {'category_type': 'interior'}, name='interior_services'),
    path('service/<slug:slug>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('project/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    path('gallery/<slug:slug>/', views.GalleryCategoryView.as_view(), name='gallery_category'),
    path('testimonials/', views.TestimonialListView.as_view(), name='testimonials'),
    path('blog/', views.BlogListView.as_view(), name='blog'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Forms
    path('inquiry/', views.InquiryCreateView.as_view(), name='inquiry_create'),
    path('inquiry/success/', views.inquiry_success, name='inquiry_success'),
    
    # AJAX Endpoints
    path('ajax/service/<int:service_id>/', views.get_service_details, name='get_service_details'),
    path('ajax/projects/service/<int:service_id>/', views.get_projects_by_service, name='get_projects_by_service'),
    path('search-autocomplete/', views.search_autocomplete, name='search_autocomplete'),
]