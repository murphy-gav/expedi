# Generated by Django 4.2 on 2023-06-21 15:13

import datetime
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_name', models.CharField(blank=True, max_length=100, null=True)),
                ('sender_company', models.CharField(blank=True, default=False, max_length=100, null=True)),
                ('sender_pickup_country', models.CharField(blank=True, default=False, max_length=200, null=True)),
                ('sender_address', models.CharField(blank=True, max_length=200, null=True)),
                ('sender_address2', models.CharField(blank=True, default=False, max_length=200, null=True)),
                ('sender_address3', models.CharField(blank=True, default=False, max_length=200, null=True)),
                ('sender_pickup_zip', models.IntegerField(blank=True, null=True)),
                ('sender_city', models.CharField(blank=True, max_length=100, null=True)),
                ('sender_state', models.CharField(blank=True, max_length=100, null=True)),
                ('sender_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('sender_phone_type', models.CharField(blank=True, max_length=100, null=True)),
                ('sender_phone_code', models.CharField(blank=True, max_length=10, null=True)),
                ('sender_phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('receiver_name', models.CharField(blank=True, max_length=100, null=True)),
                ('receiver_company', models.CharField(blank=True, default=False, max_length=100, null=True)),
                ('receiver_delivery_country', models.CharField(blank=True, default=False, max_length=200, null=True)),
                ('receiver_address', models.CharField(blank=True, max_length=200, null=True)),
                ('receiver_address2', models.CharField(blank=True, default=False, max_length=200, null=True)),
                ('receiver_address3', models.CharField(blank=True, default=False, max_length=200, null=True)),
                ('receiver_delivery_zip', models.IntegerField(blank=True, null=True)),
                ('receiver_city', models.CharField(blank=True, max_length=100, null=True)),
                ('receiver_state', models.CharField(blank=True, max_length=100, null=True)),
                ('receiver_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('receiver_phone_type', models.CharField(blank=True, max_length=100, null=True)),
                ('receiver_phone_code', models.CharField(blank=True, max_length=10, null=True)),
                ('receiver_phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('vat_tax_id', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('zip_code', models.IntegerField(blank=True, default=False, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, default=False, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, default=False, null=True, upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='LocationDistance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_country', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_country', models.CharField(blank=True, max_length=100, null=True)),
                ('distance_km', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_country', models.CharField(blank=True, default=False, max_length=255, null=True)),
                ('delivery_country', models.CharField(blank=True, default=False, max_length=255, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, default=False, max_digits=5, null=True)),
                ('width', models.DecimalField(blank=True, decimal_places=2, default=False, max_digits=5, null=True)),
                ('length', models.DecimalField(blank=True, decimal_places=2, default=False, max_digits=5, null=True)),
                ('package_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(blank=True, default=datetime.datetime(2023, 6, 21, 8, 13, 50, 876075, tzinfo=datetime.timezone.utc), null=True)),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Packaging',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('packaging_type', models.CharField(blank=True, default=False, max_length=500, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('length', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('width', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cardholder_name', models.CharField(blank=True, max_length=100, null=True)),
                ('card_number', models.CharField(blank=True, max_length=100, null=True)),
                ('card_expiry_month', models.IntegerField(blank=True, null=True)),
                ('card_expiry_year', models.IntegerField(blank=True, null=True)),
                ('card_cvv', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('zip_code', models.IntegerField(blank=True, default=False, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, default=False, max_length=100, null=True)),
                ('agent_name', models.CharField(blank=True, max_length=255, null=True)),
                ('agent_contact', models.CharField(blank=True, max_length=255, null=True)),
                ('open_time', models.DateTimeField(blank=True, default=datetime.datetime(2023, 6, 21, 8, 13, 50, 876979, tzinfo=datetime.timezone.utc), null=True)),
                ('close_time', models.DateTimeField(blank=True, default=datetime.datetime(2023, 6, 21, 13, 13, 50, 876987, tzinfo=datetime.timezone.utc), null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(blank=True, null=True, upload_to='')),
                ('status', models.CharField(blank=True, choices=[('Pending', 'pending'), ('Successful', 'successful')], default=False, max_length=10, null=True)),
                ('origin', models.CharField(blank=True, default=False, max_length=255, null=True)),
                ('destination', models.CharField(blank=True, default=False, max_length=255, null=True)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('shipping_type', models.CharField(blank=True, choices=[('documents', 'Documents'), ('packages', 'Packages')], max_length=10, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('item_description', models.CharField(blank=True, max_length=255, null=True)),
                ('manufacturer_id', models.CharField(blank=True, max_length=255, null=True)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('units', models.CharField(blank=True, max_length=10, null=True)),
                ('item_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('country_of_origin', models.CharField(blank=True, max_length=255, null=True)),
                ('schedule_b', models.CharField(blank=True, max_length=255, null=True)),
                ('reference', models.CharField(blank=True, max_length=255, null=True)),
                ('invoice_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('contact_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expedipace.checkout')),
                ('drop_off_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='drop_off_shipments', to='expedipace.stations')),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expedipace.package')),
                ('packaging', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expedipace.packaging')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expedipace.payment')),
                ('pick_up_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pick_up_shipments', to='expedipace.stations')),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zip_code', models.IntegerField(blank=True, default=False, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, default=False, max_length=100, null=True)),
                ('time', models.DateTimeField(blank=True, default=datetime.datetime(2023, 6, 21, 8, 13, 50, 878172, tzinfo=datetime.timezone.utc), null=True)),
                ('delivery_status', models.CharField(blank=True, choices=[('On-Transit', 'on-transit'), ('Delivered', 'delivered')], default=False, max_length=10, null=True)),
                ('shipment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expedipace.shipment')),
            ],
        ),
        migrations.CreateModel(
            name='PackageCountByLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField()),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expedipace.location')),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('company', models.CharField(blank=True, default=False, max_length=100)),
                ('country', models.CharField(blank=True, default=False, max_length=200)),
                ('address', models.CharField(max_length=200)),
                ('address2', models.CharField(blank=True, default=False, max_length=200)),
                ('address3', models.CharField(blank=True, default=False, max_length=200)),
                ('zip_code', models.IntegerField(blank=True, null=True)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone_type', models.CharField(max_length=100)),
                ('phone_country_code', models.CharField(max_length=10)),
                ('phone_number', models.CharField(max_length=20)),
                ('user', models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='checkout',
            name='package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='expedipace.package'),
        ),
    ]