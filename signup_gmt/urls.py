from django.urls import path
from . import views

urlpatterns = [
    path('signup/student/', views.student_signup),
    path('signup/vendor/', views.vendor_signup),
    path('signup/trainer/', views.trainer_signup),
    path('login/',views.login_view),
    path('otpsend/', views.signup_view),
    path('verifyotp/',views.verify_otp_view)
    ]