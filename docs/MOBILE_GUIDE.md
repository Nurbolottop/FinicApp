# Finic API — Mobile Guide

## Base URL
- Production: `https://finic.webtm.ru`

All endpoints below are prefixed with `/api/`.

## Authentication (JWT)
### Donor (OTP)
#### 1) Register
- `POST /api/auth/donor/register/`

Body:
```json
{
  "phone": "+996700123456",
  "full_name": "Иванов Иван Иванович"
}
```

#### 2) Verify registration (OTP)
- `POST /api/auth/donor/verify/`

Body:
```json
{
  "phone": "+996700123456",
  "code": "482931"
}
```

#### 3) Login (request OTP)
- `POST /api/auth/donor/login/`

Body:
```json
{
  "phone": "+996700123456"
}
```

#### 4) Verify login (OTP)
- `POST /api/auth/donor/login/verify/`

Body:
```json
{
  "phone": "+996700123456",
  "code": "384920"
}
```

### Organization (phone + password)
#### Login
- `POST /api/auth/org/login/`

Body:
```json
{
  "phone": "+996555000111",
  "password": "OrgTempPass123"
}
```

Response contains:
- `access` (JWT access token)
- `refresh` (JWT refresh token)

### 3) Use access token in requests
Add header to all protected endpoints:

`Authorization: Bearer <access>`

### 4) Refresh access token
- `POST /api/auth/refresh/`

Body:
```json
{
  "refresh": "<refresh>"
}
```

## Common mobile flows

### Public: Organizations list
- `GET /api/organizations/`

### Public: Campaigns list
- `GET /api/campaigns/`

Query params:
- `status` (optional)
- `organization_id` (optional)

### Donor: Create donation
- `POST /api/donations/`
- Auth: Donor

Body example:
```json
{
  "amount": 500,
  "organization_id": 1,
  "campaign_id": 1,
  "category_id": 1
}
```

Notes:
- `campaign_id` and `category_id` can be omitted or set to `null`.
- After donation creation, a `Payment` is created automatically (stub provider).

### Donor: Complete payment (stub)
- `POST /api/payments/{payment_id}/complete/`
- Auth: Donor

Response example:
```json
{
  "status": "ok",
  "payment_id": 10,
  "donation_id": 15
}
```

### Donor: My donations
- `GET /api/donations/my/`
- Auth: Donor

### Notifications
#### List
- `GET /api/notifications/`
- Auth: Any authenticated user

#### Mark as read
- `POST /api/notifications/{id}/read/`
- Auth: Any authenticated user

Response:
```json
{
  "status": "ok"
}
```

## Status codes (typical)
- `200` OK
- `201` Created
- `400` Validation error
- `401` Unauthorized (missing/invalid token)
- `403` Forbidden (wrong role / no permission)
- `404` Not found
