# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.dashboard_login, name='dashboard_login'),
    path('logout/', views.dashboard_logout, name='dashboard_logout'),
    
    # Dashboard Home
    path('', views.dashboard_home, name='dashboard_home'),
    path('settings/', views.dashboard_settings, name='dashboard_settings'),
    
    # Site Configuration
    path('site-configuration/', views.site_configuration, name='site_configuration'),
    
    # Homepage Sliders
    path('sliders/', views.slider_list, name='slider_list'),
    path('sliders/create/', views.slider_create, name='slider_create'),
    path('sliders/<int:pk>/edit/', views.slider_edit, name='slider_edit'),
    path('sliders/<int:pk>/delete/', views.slider_delete, name='slider_delete'),
    path('sliders/reorder/', views.slider_reorder, name='slider_reorder'),
    
    # Services
    path('services/categories/', views.service_category_list, name='service_category_list'),
    path('services/categories/create/', views.service_category_edit, name='service_category_create'),
    path('services/categories/<int:pk>/edit/', views.service_category_edit, name='service_category_edit'),
    
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.service_edit, name='service_create'),
    path('services/<int:pk>/edit/', views.service_edit, name='service_edit'),
    
    # Projects
    path('projects/categories/', views.project_category_list, name='project_category_list'),
    path('projects/categories/create/', views.project_category_edit, name='project_category_create'),
    path('projects/categories/<int:pk>/edit/', views.project_category_edit, name='project_category_edit'),
    
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/images/', views.project_images, name='project_images'),
    path('projects/images/<int:pk>/delete/', views.project_image_delete, name='project_image_delete'),
    path('projects/images/reorder/', views.project_image_reorder, name='project_image_reorder'),
    
    # 3D Designs
    path('3d-designs/', views.three_d_design_list, name='three_d_design_list'),
    path('3d-designs/project/<int:project_pk>/', views.three_d_design_list, name='project_3d_designs'),
    path('3d-designs/create/', views.three_d_design_edit, name='three_d_design_create'),
    path('3d-designs/project/<int:project_pk>/create/', views.three_d_design_edit, name='project_3d_design_create'),
    path('3d-designs/<int:pk>/edit/', views.three_d_design_edit, name='three_d_design_edit'),
    
    # Gallery
    path('gallery/categories/', views.gallery_category_list, name='gallery_category_list'),
    path('gallery/categories/create/', views.gallery_category_edit, name='gallery_category_create'),
    path('gallery/categories/<int:pk>/edit/', views.gallery_category_edit, name='gallery_category_edit'),
    
    path('gallery/images/', views.gallery_image_list, name='gallery_image_list'),
    path('gallery/images/create/', views.gallery_image_edit, name='gallery_image_create'),
    path('gallery/images/<int:pk>/edit/', views.gallery_image_edit, name='gallery_image_edit'),
    path('gallery/bulk-upload/', views.gallery_bulk_upload, name='gallery_bulk_upload'),
    
    # Testimonials
    path('testimonials/', views.testimonial_list, name='testimonial_list'),
    path('testimonials/create/', views.testimonial_edit, name='testimonial_create'),
    path('testimonials/<int:pk>/edit/', views.testimonial_edit, name='testimonial_edit'),
    path('testimonials/<int:pk>/toggle-approve/', views.testimonial_toggle_approve, name='testimonial_toggle_approve'),
    
    # Team
    path('team/', views.team_list, name='team_list'),
    path('team/create/', views.team_edit, name='team_create'),
    path('team/<int:pk>/edit/', views.team_edit, name='team_edit'),
    
    # Blog
    path('blog/categories/', views.blog_category_list, name='blog_category_list'),
    path('blog/categories/create/', views.blog_category_edit, name='blog_category_create'),
    path('blog/categories/<int:pk>/edit/', views.blog_category_edit, name='blog_category_edit'),
    
    path('blog/tags/', views.blog_tag_list, name='blog_tag_list'),
    path('blog/tags/create/', views.blog_tag_edit, name='blog_tag_create'),
    path('blog/tags/<int:pk>/edit/', views.blog_tag_edit, name='blog_tag_edit'),
    
    path('blog/posts/', views.blog_post_list, name='blog_post_list'),
    path('blog/posts/create/', views.blog_post_create, name='blog_post_create'),
    path('blog/posts/<int:pk>/edit/', views.blog_post_edit, name='blog_post_edit'),
    path('blog/posts/<int:pk>/preview/', views.blog_post_preview, name='blog_post_preview'),
    
    # Company Info
    path('company-info/', views.company_info_list, name='company_info_list'),
    path('company-info/create/', views.company_info_edit, name='company_info_create'),
    path('company-info/<int:pk>/edit/', views.company_info_edit, name='company_info_edit'),
    
    # Inquiries
    path('inquiries/', views.inquiry_list, name='inquiry_list'),
    path('inquiries/<int:pk>/', views.inquiry_detail, name='inquiry_detail'),
    path('inquiries/export/', views.inquiry_export, name='inquiry_export'),
    
    # Contact Messages
    path('contact-messages/', views.contact_message_list, name='contact_message_list'),
    path('contact-messages/<int:pk>/', views.contact_message_detail, name='contact_message_detail'),
    
    # AJAX Endpoints
    path('ajax/update-status/<str:model>/<int:pk>/', views.update_status, name='update_status'),
    path('ajax/toggle-featured/<str:model>/<int:pk>/', views.toggle_featured, name='toggle_featured'),
    path('ajax/dashboard-stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
]