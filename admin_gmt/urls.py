from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.get_all_students),
    path('vendors/', views.get_all_vendors),
    path('trainers/', views.get_all_trainers),
    path('student/', views.get_student_details),
    path('trainer/', views.get_trainer_details),
    path('vendor/', views.get_vendor_details),
    path('update/student/', views.update_student),
    path('update/trainer/', views.update_trainer),
    path('update/vendor/', views.update_vendor),
    path('update-vendor-status/',views.update_vendor_status, name='update_vendor_status'),
    path('update-trainer-status/',views.update_trainer_status, name='update_trainer_status'),
    path('user-category-counts/', views.get_user_category_counts, name='user-category-counts'),
    path('trainer-status-counts/',views.get_trainer_status_counts, name='trainer-status-counts'),
    path('vendor-status-counts/',views.get_vendor_status_counts, name='vendor-status-counts'),
    path('api/institutions/', views.institution_list_create, name='institution-list-create'),
    path('api/institutions/<int:pk>/get/', views.get_institution, name='institution-get'),
    path('api/institutions/<int:pk>/update/', views.update_institution, name='institution-update'),
    path('api/institutions/<int:pk>/delete/', views.delete_institution, name='institution-delete'),
]
