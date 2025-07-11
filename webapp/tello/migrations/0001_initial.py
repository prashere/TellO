# Generated by Django 4.2.3 on 2025-03-18 01:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('teacherid', models.AutoField(primary_key=True, serialize=False)),
                ('teachername', models.CharField(max_length=100)),
                ('teachergrade', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('studentid', models.AutoField(primary_key=True, serialize=False)),
                ('studentname', models.CharField(max_length=100)),
                ('studentgrade', models.CharField(max_length=50)),
                ('studentage', models.IntegerField()),
                ('additional_notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assignedteacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tello.teacher')),
            ],
        ),
    ]
