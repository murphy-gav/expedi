from django.db import models
import requests
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django_countries.fields import CountryField
from django.utils import timezone



# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    zip_code =  models.IntegerField(default=False, blank=True, null=True)
    country =  models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, default=False, blank=True, null=True)
    image = models.ImageField(default=False, null=True, blank=True)

    def __str__(self):
        return self.name

    # add other fields as needed

class LocationDistance(models.Model):
    pickup_country = models.CharField(max_length=100, blank=True, null=True)
    delivery_country = models.CharField(max_length=100, blank=True, null=True)
    distance_km = models.FloatField(blank=True, null=True)


class Package(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    pickup_country = models.CharField(max_length=255, default=False, blank=True, null=True)
    delivery_country = models.CharField(max_length=255, default=False, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, default=False, blank=True, null=True)
    width = models.DecimalField(max_digits=5, decimal_places=2, default=False, blank=True, null=True)
    length = models.DecimalField(max_digits=5, decimal_places=2, default=False, blank=True, null=True)
    package_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now() - timezone.timedelta(hours=7), blank=True, null=True)

    def __str__(self):
        return self.package_id

class Checkout(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    sender_name = models.CharField(max_length=100, null=True, blank=True)
    sender_company = models.CharField(max_length=100, default=False, blank=True, null=True)
    sender_pickup_country = models.CharField(max_length=200, default=False, null=True, blank=True)
    sender_address = models.CharField(max_length=200, blank=True, null=True)
    sender_address2 = models.CharField(max_length=200, blank=True, null=True ,default=False)
    sender_address3 = models.CharField(max_length=200, blank=True, null=True ,default=False)
    sender_pickup_zip = models.IntegerField(blank=True, null=True)
    sender_city = models.CharField(max_length=100, null=True, blank=True)
    sender_state = models.CharField(max_length=100, null=True, blank=True)
    sender_email = models.EmailField(blank=True, null=True)
    sender_phone_type = models.CharField(max_length=100, null=True, blank=True)
    sender_phone_code = models.CharField(max_length=10, null=True, blank=True)
    sender_phone_number = models.CharField(max_length=20, null=True, blank=True)
    receiver_name = models.CharField(max_length=100, null=True, blank=True)
    receiver_company = models.CharField(max_length=100, default=False, blank=True, null=True)
    receiver_delivery_country = models.CharField(max_length=200, blank=True, default=False, null=True)
    receiver_address = models.CharField(max_length=200, blank=True, null=True)
    receiver_address2 = models.CharField(max_length=200, blank=True, default=False, null=True)
    receiver_address3 = models.CharField(max_length=200, blank=True, default=False, null=True)
    receiver_delivery_zip = models.IntegerField(blank=True, null=True)
    receiver_city = models.CharField(max_length=100, null=True, blank=True)
    receiver_state = models.CharField(max_length=100, null=True, blank=True)
    receiver_email = models.EmailField(blank=True, null=True)
    receiver_phone_type = models.CharField(max_length=100, null=True, blank=True)
    receiver_phone_code = models.CharField(max_length=10, null=True, blank=True)
    receiver_phone_number = models.CharField(max_length=20, null=True, blank=True)
    vat_tax_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.sender_name} to {self.receiver_name}"
    
class Packaging(models.Model):
    packaging_type = models.CharField(max_length=500, default=False, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    length = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.packaging_type

class Payment(models.Model):
    cardholder_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=100, blank=True, null=True)
    card_expiry_month = models.IntegerField(blank=True, null=True)
    card_expiry_year = models.IntegerField(blank=True, null=True)
    card_cvv = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.cardholder_name}'s Card Details"

class Stations(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    zip_code =  models.IntegerField(default=False, blank=True, null=True)
    country =  models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, default=False, blank=True, null=True)
    agent_name = models.CharField(max_length=255, blank=True, null=True)
    agent_contact = models.CharField(max_length=255, blank=True, null=True)
    open_time = models.DateTimeField(default=timezone.now ()- timezone.timedelta(hours=7), blank=True, null=True)
    close_time = models.DateTimeField(default=timezone.now()- timezone.timedelta(hours=2), blank=True, null=True)

    def __str__(self):
        return self.name
    


class Shipment(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    image = models.FileField(null=True, blank=True)
    STATUS_CHOICES = (
        ('Pending', 'pending'),
        ('Successful', 'successful'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
    default=False, null=True, blank=True)
    origin = models.CharField(max_length=255, default=False, null=True, blank=True)
    destination = models.CharField(max_length=255, default=False, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    shipping_type = models.CharField(max_length=10, choices=[('documents', 'Documents'), ('packages', 'Packages')], null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    contact_info = models.ForeignKey(Checkout, on_delete=models.CASCADE, null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    item_description = models.CharField(max_length=255, blank=True, null=True)
    manufacturer_id = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    units = models.CharField(max_length=10, blank=True, null=True)
    item_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    country_of_origin = models.CharField(max_length=255, blank=True, null=True)
    schedule_b = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    invoice_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    drop_off_location = models.ForeignKey(Stations, on_delete=models.CASCADE, null=True, blank=True, related_name='drop_off_shipments')
    pick_up_location = models.ForeignKey(Stations, on_delete=models.CASCADE, null=True, blank=True, related_name='pick_up_shipments')
    packaging = models.ForeignKey(Packaging, on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)

    

    def __str__(self):
        return f"{self.package.sender}'s Shipment"


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=False)
    name = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True)
    company = models.CharField(max_length=100, blank=True, default=False)
    country = models.CharField(max_length=200, blank=True, default=False)
    address = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200, blank=True, default=False)
    address3 = models.CharField(max_length=200, blank=True, default=False)
    zip_code = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    email = models.EmailField()
    phone_type = models.CharField(max_length=100)
    phone_country_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user}'s Contact Information"

class Route(models.Model):
    zip_code =  models.IntegerField(default=False, blank=True, null=True)
    country =  models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, default=False, blank=True, null=True)
    time = models.DateTimeField(default=timezone.now ()- timezone.timedelta(hours=7), blank=True, null=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    DELIVERY_CHOICES = (
        ('On-Transit', 'on-transit'),
        ('Delivered', 'delivered'),
    )
    delivery_status = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default=False, null=True, blank=True)

    def __str__(self):
        return self.country

class PackageCountByLocation(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True,null=True)
    count = models.IntegerField()

class PackageCountByLocationView(LoginRequiredMixin, ListView):
    model = PackageCountByLocation
    template_name = 'package_count_by_location.html'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(count=Count('pickup_location'))
        return qs


