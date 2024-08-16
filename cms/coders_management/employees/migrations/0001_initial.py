# Generated by Django 5.1 on 2024-08-16 08:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(max_length=100)),
                ('employee_id', models.CharField(max_length=10, unique=True)),
                ('extension_number', models.CharField(blank=True, max_length=5)),
                ('tl_name', models.CharField(blank=True, max_length=100)),
                ('photo', models.ImageField(blank=True, upload_to='photos/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
