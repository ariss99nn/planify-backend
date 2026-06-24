from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='passwordreset',
            name='code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True),
        ),
    ]
