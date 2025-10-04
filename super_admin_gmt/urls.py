from django.urls import path
from . import views

urlpatterns = [
    path('add/student/', views.superadmin_add_student),
    path('add/vendor/', views.superadmin_add_vendor),
    path('add/trainer/', views.superadmin_add_trainer),
    path('add/admin/' , views.superadmin_add_admin),
    path('admin/count/' , views.get_admin_count),
    path('admins/',views.get_all_admins),
    ]