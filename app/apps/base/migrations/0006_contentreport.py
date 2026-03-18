# Generated manually for ContentReport model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0005_reportmedia'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_type', models.CharField(choices=[('campaign', 'Кампания'), ('organization', 'Организация')], max_length=20, verbose_name='Тип контента')),
                ('content_id', models.PositiveIntegerField(verbose_name='ID контента')),
                ('reason', models.TextField(verbose_name='Причина жалобы')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_reports', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Жалоба на контент',
                'verbose_name_plural': 'Жалобы на контент',
                'ordering': ['-created_at'],
            },
        ),
    ]
