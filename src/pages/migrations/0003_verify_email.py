# Generated by Django 4.0.6 on 2022-08-13 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_fileupload'),
    ]

    operations = [
        migrations.CreateModel(
            name='verify_email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=200)),
                ('code', models.TextField()),
                ('verifiedBool', models.BooleanField()),
            ],
        ),
    ]