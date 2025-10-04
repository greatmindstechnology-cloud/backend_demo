"""
URL configuration for project project.

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
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('signup_gmt.urls')),
    path('admin_gmt/', include('admin_gmt.urls')),
    path('trainer_gmt/', include('trainer_gmt.urls')),
    path('vendor_gmt/', include('vendor_gmt.urls')),
    path('student_gmt/', include('student_gmt.urls')),
    path('course_gmt/', include('course_gmt.urls')),
    path('super_admin_gmt/', include('super_admin_gmt.urls'))
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




