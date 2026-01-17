import os


_trusted = [
    "https://finic.webtm.ru",
]

_trusted_from_env = os.getenv("CSRF_TRUSTED_ORIGINS", "").strip()
if _trusted_from_env:
    _trusted.extend([v.strip() for v in _trusted_from_env.split(",") if v.strip()])

CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(_trusted))

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


_cors_allowed = [
    "https://finic.webtm.ru",
]

_cors_from_env = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
if _cors_from_env:
    _cors_allowed.extend([v.strip() for v in _cors_from_env.split(",") if v.strip()])

CORS_ALLOWED_ORIGINS = list(dict.fromkeys(_cors_allowed))

# If you really need allow-all (dev only): set CORS_ALLOW_ALL_ORIGINS=1
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "0").lower() in ("1", "true", "yes")

# Allow cookies/Authorization headers from frontend/mobile
CORS_ALLOW_CREDENTIALS = True

# Default headers are usually enough; keep it explicit for clarity
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Cache preflight results
CORS_PREFLIGHT_MAX_AGE = 86400