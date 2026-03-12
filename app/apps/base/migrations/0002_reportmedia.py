# Generated manually for ReportMedia model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='reports/media/')),
                ('media_type', models.CharField(choices=[('image', 'Фото'), ('video', 'Видео')], default='image', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_files', to='base.report')),
            ],
            options={
                'verbose_name': 'Медиа файл отчёта',
                'verbose_name_plural': 'Медиа файлы отчётов',
            },
        ),
    ]
