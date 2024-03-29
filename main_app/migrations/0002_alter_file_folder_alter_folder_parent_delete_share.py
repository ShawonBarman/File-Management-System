# Generated by Django 4.1.7 on 2024-03-02 17:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="folder",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="main_app.folder",
            ),
        ),
        migrations.AlterField(
            model_name="folder",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="main_app.folder",
            ),
        ),
        migrations.DeleteModel(
            name="Share",
        ),
    ]
