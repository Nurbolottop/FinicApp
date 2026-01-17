from django.urls import path

from apps.base import views as base_views


urlpatterns = [
    path("organizations/", base_views.OrganizationListView.as_view()),
    path("organizations/<int:pk>/", base_views.OrganizationDetailView.as_view()),

    path("campaigns/", base_views.CampaignListView.as_view()),

    path("donations/", base_views.DonationCreateView.as_view()),
    path("donations/my/", base_views.MyDonationsView.as_view()),

    path("campaigns/create/", base_views.CampaignCreateView.as_view()),
    path("campaigns/my/", base_views.MyCampaignsView.as_view()),
]
