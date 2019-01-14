# Generated by Django 2.1.3 on 2019-01-07 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LMS',
            fields=[
                ('uuid', models.CharField(max_length=2048, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'lms',
            },
        ),
        migrations.CreateModel(
            name='WIMS',
            fields=[
                ('url', models.CharField(max_length=2048, primary_key=True, serialize=False)),
                ('ident', models.CharField(max_length=2048)),
                ('password', models.CharField(max_length=2048)),
            ],
            options={
                'verbose_name_plural': 'wims',
            },
        ),
        migrations.CreateModel(
            name='WimsClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wims_uuid', models.CharField(max_length=16)),
                ('lms_uuid', models.CharField(max_length=16)),
                ('lms', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lti_app.LMS')),
                ('wims', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lti_app.WIMS')),
            ],
            options={
                'verbose_name_plural': 'wimsclasses',
            },
        ),
        migrations.CreateModel(
            name='WimsUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lms_uuid', models.CharField(max_length=16)),
                ('quser', models.CharField(max_length=256)),
                ('lms', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lti_app.LMS')),
                ('wclass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lti_app.WimsClass')),
            ],
        ),
        migrations.AddIndex(
            model_name='wimsuser',
            index=models.Index(fields=['lms', 'lms_uuid', 'wclass'], name='lti_app_wim_lms_id_1b3653_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='wimsuser',
            unique_together={('lms', 'lms_uuid'), ('quser', 'wclass')},
        ),
        migrations.AddIndex(
            model_name='wimsclass',
            index=models.Index(fields=['lms', 'lms_uuid', 'wims'], name='lti_app_wim_lms_id_a7be4e_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='wimsclass',
            unique_together={('lms', 'lms_uuid'), ('wims', 'wims_uuid')},
        ),
    ]