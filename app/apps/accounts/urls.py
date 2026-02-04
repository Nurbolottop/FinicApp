from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts import views as accounts_views


urlpatterns = [
    path("auth/donor/register/", accounts_views.DonorRegisterView.as_view()),
    path("auth/donor/verify/", accounts_views.DonorVerifyView.as_view()),
    path("auth/donor/login/", accounts_views.DonorLoginView.as_view()),
    path("auth/donor/login/verify/", accounts_views.DonorLoginVerifyView.as_view()),

    path("auth/org/login/", accounts_views.OrgLoginView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),

    path("profile/donor/", accounts_views.DonorProfileEditView.as_view()),
    path("profile/org/", accounts_views.OrganizationProfileEditView.as_view()),
]
