# Generated by Django 3.0.12 on 2023-04-15 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('course_id', models.IntegerField(null=True)),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('desc', models.TextField()),
                ('offered_fall', models.BooleanField()),
                ('offered_winter', models.BooleanField()),
                ('offered_summer', models.BooleanField()),
                ('offered_spring', models.BooleanField()),
                ('units', models.PositiveSmallIntegerField()),
                ('department', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CourseList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('list_id', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(default=None, max_length=100)),
                ('courses', models.ManyToManyField(to='map_backend.Course')),
            ],
        ),
        migrations.CreateModel(
            name='RequirementGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connector', models.PositiveSmallIntegerField(choices=[(0, 'AND'), (1, 'OR')], default=0)),
                ('desc', models.TextField(blank=True, max_length=500, null=True)),
                ('order', models.IntegerField(help_text='Order at which requirement is checked - checks from low to high')),
            ],
        ),
        migrations.CreateModel(
            name='RequirementItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connector', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'AND'), (1, 'OR')], help_text='The first requirement item must have an empty connector', null=True)),
                ('desc', models.CharField(blank=True, max_length=255, null=True)),
                ('req_units', models.PositiveSmallIntegerField()),
                ('parent_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='map_backend.RequirementGroup')),
                ('req_list', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='map_backend.CourseList')),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('program_id', models.IntegerField(null=True)),
                ('name', models.TextField()),
                ('desc', models.TextField()),
                ('requirements', models.ManyToManyField(to='map_backend.RequirementGroup')),
            ],
        ),
        migrations.CreateModel(
            name='Calculator',
            fields=[
                ('calculator_id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.TextField(help_text='This will be the title of the webpage for that calculator')),
                ('courses', models.ManyToManyField(to='map_backend.Course')),
                ('programs', models.ManyToManyField(to='map_backend.Program')),
            ],
        ),
    ]
