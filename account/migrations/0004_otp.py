# Generated by Django 5.1.2 on 2024-10-23 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_user_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Otp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=11)),
                ('rand_code', models.CharField(max_length=10)),
                ('password', models.CharField(max_length=30)),
                ('full_name', models.CharField(max_length=100)),
                ('expiration_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
