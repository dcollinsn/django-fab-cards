from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fab_cards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='printing',
            name='language',
            field=models.CharField(default='en', max_length=2),
        ),
    ]
