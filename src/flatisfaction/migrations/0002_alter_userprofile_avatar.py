# Generated by Django 5.2.3 on 2025-06-17 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flatisfaction', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(upload_to='user_avatars/'),
        ),
    ]
