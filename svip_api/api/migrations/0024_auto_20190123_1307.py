# Generated by Django 2.1.3 on 2019-01-23 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20190123_1209'),
    ]

    operations = [
        migrations.RenameField(
            model_name='variant',
            old_name='myvariant_h19',
            new_name='myvariant_hg19',
        ),
    ]
