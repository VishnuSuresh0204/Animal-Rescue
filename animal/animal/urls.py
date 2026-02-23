"""
URL configuration for animal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('user_reg/', views.user_reg),
    path('rescue_reg/', views.rescue_reg),
    path('vet_reg/', views.vet_reg),
    
    # Home pages
    path('admin_home/', views.admin_home),
    path('user_home/', views.user_home),
    path('rescue_home/', views.rescue_home),
    path('vet_home/', views.vet_home),
    path('care_home/', views.care_home),

    # Admin actions
    path('admin_manage_users/', views.admin_manage_users),
    path('admin_view_rescue_teams/', views.admin_view_rescue_teams),
    path('admin_view_vets/', views.admin_view_vets),
    path('admin_view_users/', views.admin_view_users),
    path('admin_approve_team/', views.admin_approve_team),
    path('admin_reject_team/', views.admin_reject_team),
    path('admin_block_user/', views.admin_block_user),
    path('admin_unblock_user/', views.admin_unblock_user),
    path('admin_manage_care_centers/', views.admin_manage_care_centers),
    path('admin_add_care_center/', views.admin_add_care_center),
    path('admin_edit_care_center/', views.admin_edit_care_center),
    path('admin_delete_care_center/', views.admin_delete_care_center),
    path('admin_assign_rescue/', views.admin_assign_rescue),
    path('admin_assign_to_team/', views.admin_assign_to_team),
    path('admin_monitor_all/', views.admin_monitor_all),
    path('admin_report/', views.admin_report),

    # User actions
    path('user_report_animal/', views.user_report_animal),
    path('user_track_rescue/', views.user_track_rescue),
    path('user_request_adoption/', views.user_request_adoption),
    path('user_submit_adoption/', views.user_submit_adoption),

    # Rescue Team actions
    path('rescue_view_alerts/', views.rescue_view_alerts),
    path('rescue_respond/', views.rescue_respond),
    path('rescue_update_status/', views.rescue_update_status),
    path('rescue_transport/', views.rescue_transport),

    # Vet actions
    path('vet_view_animals/', views.vet_view_animals),
    path('vet_treatment/', views.vet_treatment),
    path('vet_add_medical_record/', views.vet_add_medical_record),
    path('vet_prescribe/', views.vet_prescribe),
    path('vet_mark_adoption/', views.vet_mark_adoption),

    # Care Center actions
    path('care_reg/', views.care_registration),
    path('care_view_pets/', views.care_view_pets),
    path('care_log_activity/', views.care_log_activity),
    path('care_list_adoption/', views.care_list_adoption),
    path('care_chat_vet/', views.care_chat_vet),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
