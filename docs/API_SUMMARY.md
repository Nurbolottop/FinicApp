# Finic API — Summary

## Auth
- POST /api/auth/register/donor/
- POST /api/auth/register/org/
- POST /api/auth/login/
- POST /api/auth/refresh/

## Donor
- GET /api/me/donor-profile/
- GET /api/donations/my/
- GET /api/stats/donor/

## Organization
- POST /api/campaigns/create/
- GET /api/campaigns/my/
- GET /api/stats/organization/
- GET /api/organizations/{id}/reports/

## Public
- GET /api/organizations/
- GET /api/campaigns/

## Donations & Payments
- POST /api/donations/
- POST /api/payments/{payment_id}/complete/

## Reports
- POST /api/reports/create/

## Notifications
- GET /api/notifications/
- POST /api/notifications/{id}/read/
