from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts import views as accounts_views


urlpatterns = [
    path("auth/register/donor/", accounts_views.RegisterDonorView.as_view()),
    path("auth/register/org/", accounts_views.RegisterOrgView.as_view()),

    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),

    path("me/donor-profile/", accounts_views.DonorProfileView.as_view()),
]
