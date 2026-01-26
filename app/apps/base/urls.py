from django.urls import path

from apps.base import views as base_views


urlpatterns = [
    path("organizations/", base_views.OrganizationListView.as_view()),
    path("organizations/<int:pk>/", base_views.OrganizationDetailView.as_view()),

    path("campaigns/", base_views.CampaignListView.as_view()),
    path("campaigns/<int:pk>/", base_views.CampaignUpdateView.as_view()),

    path("donations/", base_views.DonationCreateView.as_view()),
    path("donations/my/", base_views.MyDonationsView.as_view()),
    path("donor/bank-details/", base_views.DonorBankDetailsView.as_view()),
    path("donor/recurring/", base_views.RecurringDonationListCreateView.as_view()),
    path("donor/recurring/<int:pk>/", base_views.RecurringDonationUpdateView.as_view()),

    path("campaigns/create/", base_views.CampaignCreateView.as_view()),
    path("campaigns/my/", base_views.MyCampaignsView.as_view()),

    path("reports/create/", base_views.ReportCreateView.as_view()),
    path(
        "organizations/<int:org_id>/reports/",
        base_views.OrganizationReportsView.as_view(),
    ),

    path("stats/donor/", base_views.DonorStatsView.as_view()),
    path("stats/organization/", base_views.OrganizationStatsView.as_view()),

    path(
        "payments/<int:payment_id>/complete/",
        base_views.PaymentCompleteStubView.as_view(),
    ),

    path("notifications/", base_views.MyNotificationsView.as_view()),
    path(
        "notifications/<int:notification_id>/read/",
        base_views.NotificationReadView.as_view(),
    ),
]
