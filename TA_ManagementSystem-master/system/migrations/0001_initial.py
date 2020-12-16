# Generated by Django 3.0.2 on 2020-02-01 17:33

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
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CRN', models.CharField(max_length=5)),
                ('semester', models.CharField(max_length=10)),
                ('title', models.CharField(max_length=50)),
                ('subject', models.CharField(max_length=4)),
                ('courseName', models.CharField(max_length=30)),
                ('capacity', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TADuty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('labNumber', models.IntegerField(default=0)),
                ('preparationHour', models.FloatField(default=0)),
                ('labHour', models.FloatField(default=0)),
                ('labWorkingHour', models.FloatField(default=0)),
                ('assignmentNumber', models.IntegerField(default=0)),
                ('assignmentWorkingHour', models.FloatField(default=0)),
                ('contactHour', models.FloatField(default=0)),
                ('otherDutiesHour', models.FloatField(default=0)),
                ('totalHour', models.FloatField(default=0)),
                ('curriculum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.Course')),
            ],
        ),
        migrations.CreateModel(
            name='TA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cv', models.FileField(upload_to=None, max_length=254, blank=True)),
                ('availableHours', models.FloatField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DepartmentHead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='system.Teacher'),
        ),
    ]