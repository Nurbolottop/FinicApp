# Generated manually for FCM device tokens

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FCMDeviceToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=255, unique=True)),
                ('device_type', models.CharField(choices=[('ios', 'iOS'), ('android', 'Android')], default='android', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fcm_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'FCM токен устройства',
                'verbose_name_plural': 'FCM токены устройств',
                'ordering': ('-created_at',),
            },
        ),
    ]
