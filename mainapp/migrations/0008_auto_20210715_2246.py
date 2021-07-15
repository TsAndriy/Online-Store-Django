# Generated by Django 3.2.4 on 2021-07-15 19:46

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0007_auto_20210715_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='related_cart', to='mainapp.CartProduct'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, verbose_name='Name')),
                ('last_name', models.CharField(max_length=255, verbose_name='Surname')),
                ('phone', models.CharField(max_length=20, verbose_name='Phone')),
                ('address', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Address')),
                ('status', models.CharField(choices=[('new', 'New order'), ('in_progress', 'Order in processing'), ('ready', 'Order ready'), ('completed', 'Order complete')], default='new', max_length=100, verbose_name='Product status')),
                ('bying_type', models.CharField(choices=[('self', 'You take away'), ('delivery', 'Delivery')], default='self', max_length=100, verbose_name='Product type')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Order creation date')),
                ('order_date', models.DateField(default=django.utils.timezone.now, verbose_name='Date of receipt of the order')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_orders', to='mainapp.customer', verbose_name='Customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='orders',
            field=models.ManyToManyField(related_name='related_customer', to='mainapp.Order', verbose_name='Buyers order'),
        ),
    ]
