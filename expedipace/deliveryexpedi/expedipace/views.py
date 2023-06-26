# Imports
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotFound
import requests
from django.views.generic import CreateView, UpdateView, DetailView, ListView, FormView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from math import radians, cos, sin, asin, sqrt
from django.urls import reverse_lazy, reverse
from django.contrib import messages
import googlemaps
from django.conf import settings
from googlemaps.exceptions import ApiError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from .models import Package, Location, LocationDistance, Shipment, Checkout, Packaging, Contact, Payment, Route
from .forms import PackageForm, LocationForm, QuoteForm, CheckoutForm, ShipmentForm, PackagingForm, ShipmentTrackingForm, ContactForm, EditShipmentForm, EditShippingForm, PaymentForm, ImageUploadForm
import django_countries
from django_countries import countries
from geopy import distance
from opencage.geocoder import OpenCageGeocode
import uuid
import stripe
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import send_mail


# Authentication Views 
def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')

    else:
        return render(request, 'login.html')

def register(request):


    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password==password2:       
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect(reverse('sign_up'))  # redirect to the sign up page using the reverse function
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect(reverse('sign_up'))  # redirect to the sign up page using the reverse function
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save();
                contact = Contact.objects.create(user=user, email=user.email)
                contact.save();
                print('User Created')
                # Send welcome email
                subject = 'Welcome to Global-Wis'
                message = f'Dear {user.username},\n\nThank you for registering on Global-Wis, your trusted delivery logistics company. We are excited to have you as a member!\n\nPlease login to your account to start a shipment: https://global-wis.com/accounts/login'
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = [user.email]
                send_mail(subject, message, from_email, to_email)

                return redirect('login')

        else:
            messages.info(request, 'Password Not Matching')
            return redirect(reverse('sign_up'))  # redirect to the sign up page using the reverse function
        return redirect('/')

    else:
        return render(request, 'signup.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

# ... after processing the form data ...


# Views Backends
class HomeView(FormView):
    template_name = 'home.html'
    form_class = ShipmentTrackingForm

    def form_valid(self, form):
        package_id = form.cleaned_data['package_id']
        try:
            package = Package.objects.get(package_id=package_id)
            context = {'username': self.request.user.username, 'package': package}
            return render(self.request, 'home.html', context)
        except Package.DoesNotExist:
            form.add_error('package_id', 'Invalid package ID')
            return self.form_invalid(form)


def get_geocode(address, api_key):
    url = "https://api.opencagedata.com/geocode/v1/json?q={}&key={}".format(address, api_key)
    response = requests.get(url).json()
    if response['total_results'] > 0:
        lat = response['results'][0]['geometry']['lat']
        lng = response['results'][0]['geometry']['lng']
        return lat, lng
    else:
        return None, None

def calculate_distance(pickup_country, pickup_lat, pickup_lng, delivery_country, delivery_lat, delivery_lng, api_key):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params_pickup = {"q": pickup_country, "key": api_key}
    print(f" Pickup country: {pickup_country}")
    params_delivery = {"q": delivery_country, "key": api_key}
    print(f" Delivery country: {delivery_country}")
    response_pickup = requests.get(url, params=params_pickup).json()
    response_delivery = requests.get(url, params=params_delivery).json()
    distance_km = distance.distance((pickup_lat, pickup_lng), (delivery_lat, delivery_lng)).km

    # Save distance to the database
    distance_obj, created = LocationDistance.objects.get_or_create(
        pickup_country=pickup_country,
        delivery_country=delivery_country,
        defaults={"distance_km": distance_km},
    )
    if not created:
        distance_obj.distance_km = distance_km
        distance_obj.save()

    return distance_km

class TrackQuoteView(TemplateView):
    template_name = 'trackquote.html'

class TrackingView(TemplateView):
    template_name = 'tracking.html'

class LocationView(TemplateView):
    template_name = 'location.html'

class SuccessHistoryView(TemplateView):
    template_name = 'success-history.html'

class AboutView(TemplateView):
    template_name = 'about.html'


class ServicesView(TemplateView):
    template_name = 'services.html'

class UserProfileView(TemplateView):
    template_name = 'user_profile.html'

class LoginView(TemplateView):
    template_name = 'login.html'

class PaymentSettingView(TemplateView):
    template_name = 'payment_settings.html'

    def get_object(self, queryset=None):
        try:
            return Contact.objects.get(user=self.request.user)
        except Contact.DoesNotExist:
            return Contact(email=self.request.user.email)

    def get_payments(self):
        shipments = Shipment.objects.filter(package__sender=self.request.user)
        payments = Payment.objects.filter(shipment__in=shipments)
        return payments

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.pk is not None:
            return super().get(request, *args, **kwargs)
        else:
            return redirect(reverse_lazy('user_information'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact'] = self.object
        context['payments'] = self.get_payments()
        return context


    

class SignupView(TemplateView):
    template_name = 'signup.html'
    
def support(request):
    if request.method == 'POST':
        # Retrieve data from the form
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        sub = request.POST['subject']
        message = request.POST['message']

        # Construct the email message
        email_message = f"Name: {full_name}\n\nEmail: {email}\n\nPhone Number: {phone_number}\n\nSubject: {sub}\n\nMessage: {message}"

         # Send email to support
        subject = f"{full_name}'s {sub}"
        message = email_message
        from_email = email
        to_email = [settings.SUPPORT_EMAIL]
        send_mail(subject, message, from_email, to_email)

        # Redirect to a thank you page after the email is sent
        return HttpResponseRedirect(reverse('thank_you'))

    return render(request, 'support.html')
    
def thank_you(request):
    return render(request, 'thank_you.html')

class QuotesCreateView(LoginRequiredMixin, CreateView):
    model = Package
    form_class = QuoteForm
    template_name = 'quote.html'
    
    def get_success_url(self):
        url = self.request.build_absolute_uri()
        if "create_shipment" in url:
            return "/checkout"
        elif "quote" in url:
            return "/show-price"

    # Define the constants for weight, volume and conversion rate
    WEIGHT_RATE = 10.0  # $10 per kg
    VOLUME_RATE = 0.2  # $0.2 per cubic meter
    VOLUMETRIC_WEIGHT_FACTOR = 5000  # Conversion rate for volumetric weight


    def form_valid(self, form):
        print(f"User: {self.request.user}")
        form.instance.sender = self.request.user
        pickup_country = form.cleaned_data["pickup_country"]
        delivery_country = form.cleaned_data["delivery_country"]
        weight = form.cleaned_data["weight"]
        length = form.cleaned_data.get("length")
        width = form.cleaned_data.get("width")
        height = form.cleaned_data.get("height")
        api_key = settings.MY_API_KEY
        print(f"api_key={api_key}")
        pickup_lat, pickup_lng = get_geocode(pickup_country, api_key)
        delivery_lat, delivery_lng = get_geocode(delivery_country, api_key)
        
        # Calculate the price based on weight and dimensions
        if pickup_country and delivery_country:
            pickup_country_name = countries.name(pickup_country)
            delivery_country_name = countries.name(delivery_country)
            print(f" Pickup country name: {pickup_country_name}")
            print(f" Delivery country name: {delivery_country_name}")
            # Calculate the price based on weight and dimensions
            base_price = weight * ((height * width * length) / 5000)
            # Calculate the distance between the pickup and delivery locations
            pickup_lat, pickup_lng = get_geocode(pickup_country, api_key)
            delivery_lat, delivery_lng = get_geocode(delivery_country, api_key)
            if pickup_lat and pickup_lng and delivery_lat and delivery_lng:
                distance = calculate_distance(pickup_country, pickup_lat, pickup_lng, delivery_country, delivery_lat, delivery_lng, api_key)
                # Calculate the Travel Duration
                speed_time = distance / 800 # Average flight speed for cargo planes is 800 km/hour
                form.instance.speed_time = speed_time
                # Calculate the distance-based cost
                rate_per_km = 0.1 # Replace with your own rate per kilometer
                distance_price = distance * rate_per_km

                # Add the distance-based cost to the base cost
                price = base_price + distance_price
                print(f"price{price}")
            else:
                # If geocoding fails, use the base cost as the price
                price = base_price

            # Save the calculated price and distance in the form instance
            # form.instance.price = price
            form.instance.distance = distance if 'distance' in locals() else None
        else:
            # If the pickup and delivery countries are not provided, use the base cost as the price
            price = weight * ((height * width * length) / 5000)
            form.instance.price = price

        # Save the form
        self.object = form.save()
        url = self.request.build_absolute_uri()
        package = None
        if "create_shipment" in url:
            # create a new package instance
            package = Package.objects.create(
                sender=self.request.user,
                pickup_country=pickup_country_name,
                delivery_country=delivery_country_name,
                weight=form.cleaned_data['weight'],
                height=form.cleaned_data['height'],
                width=form.cleaned_data['width'],
                length=form.cleaned_data['length']
            )

            # generate a unique package ID
            package_id = 'gbw' + uuid.uuid4().hex[:8]
            print(f"Package ID: {package_id}")

            # set the package_id field for the package instance
            package.package_id = package_id
            package.save()
            self.request.session['package_id'] = package.package_id

            checkout = Checkout.objects.create(
                sender_pickup_country=pickup_country_name,
                receiver_delivery_country=delivery_country_name,
                package=package,
            )
            checkout.save()

        # Redirect to the show_price view with the price and distance as parameters
        return HttpResponseRedirect(self.get_success_url() + f'?price={price}&distance={distance}&pickup_country={pickup_country_name}&delivery_country={delivery_country_name}&speed_time={speed_time}&package={package}')
    

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form_kwargs = self.get_form_kwargs()
        form_kwargs.pop('instance', None)  # Remove the instance argument
        return form_class(**form_kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            form = context['form']
            price = form.instance.price if form.instance.price else None
            distance = form.instance.distance if form.instance.distance else None
            speed_time = form.instance.speed_time if form.instance.speed_time else None
        else:
            price = None
            distance = None
            speed_time = None
        context["price"] = price
        context["distance"] = distance
        context["speed_time"] = speed_time
        print(f"Context Speed time: {speed_time} hrs")
        context["flag"] = "flag"
        return context

@login_required
def show_price(request):
    price = request.GET.get('price')
    distance = request.GET.get('distance')
    pickup_country = request.GET.get('pickup_country')
    delivery_country = request.GET.get('delivery_country')
    speed_time = request.GET.get('speed_time')
    package = request.GET.get('package')


    context = {
        'price': price,
        'distance': distance,
        'pickup_country': pickup_country,
        'pickup_zip': pickup_zip,
        'speed_time': speed_time,
        'delivery_country': delivery_country,
        'delivery_zip': delivery_zip,
        'package': package,
    }
    return render(request, 'show_price.html', context)


class CheckoutView(LoginRequiredMixin, FormView):
    form_class = CheckoutForm
    template_name = 'checkout.html'
    success_url = reverse_lazy('shipment_details')
    

    def get_initial(self):
        initial = super().get_initial()

        # Set initial values for form fields
        initial['pickup_country'] = self.request.GET.get('pickup_country')
        initial['delivery_country'] = self.request.GET.get('delivery_country')

        # Get the contact object for the current user
        try:
            contact = Contact.objects.get(user=self.request.user)
        except Contact.DoesNotExist:
            # No contact object exists, return empty initial dictionary
            return initial

        # Populate the checkout fields with the contact object data
        initial['sender_name'] = contact.name
        initial['sender_company'] = contact.company
        initial['sender_address'] = contact.address
        initial['sender_address2'] = contact.address2
        initial['sender_address3'] = contact.address3
        initial['sender_pickup_zip'] = contact.zip_code
        initial['sender_city'] = contact.city
        initial['sender_state'] = contact.state
        initial['sender_email'] = contact.email
        initial['sender_phone_type'] = contact.phone_type
        initial['sender_phone_code'] = contact.phone_country_code
        initial['sender_phone_number'] = contact.phone_number

        return initial


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pickup_country'] = self.request.GET.get('pickup_country')
        context['delivery_country'] = self.request.GET.get('delivery_country')
        return context

    def form_valid(self, form):
        # Get the package ID from the session
        package_id = self.request.session.get('package_id')
        pickup_country = self.request.GET.get('pickup_country')
        if package_id is None:
            return HttpResponseRedirect(reverse('create_shipment'))

        try:
            package = Package.objects.get(package_id=package_id)
        except Package.DoesNotExist:
            return HttpResponseRedirect(reverse('create_shipment'))

        # Get form data
        sender_name = form.cleaned_data['sender_name']
        sender_company = form.cleaned_data['sender_company']
        sender_address = form.cleaned_data['sender_address']
        sender_address2 = form.cleaned_data['sender_address2']
        sender_address3 = form.cleaned_data['sender_address3']
        sender_pickup_zip = form.cleaned_data['sender_pickup_zip']
        sender_city = form.cleaned_data['sender_city']
        sender_state = form.cleaned_data['sender_state']
        sender_email = form.cleaned_data['sender_email']
        sender_phone_type = form.cleaned_data['sender_phone_type']
        sender_phone_code = form.cleaned_data['sender_phone_code']
        sender_phone_number = form.cleaned_data['sender_phone_number']
        receiver_name = form.cleaned_data['receiver_name']
        receiver_company = form.cleaned_data['receiver_company']
        receiver_address = form.cleaned_data['receiver_address']
        receiver_address2 = form.cleaned_data['receiver_address2']
        receiver_address3 = form.cleaned_data['receiver_address3']
        receiver_delivery_zip = form.cleaned_data['receiver_delivery_zip']
        receiver_city = form.cleaned_data['receiver_city']
        receiver_state = form.cleaned_data['receiver_state']
        receiver_email = form.cleaned_data['receiver_email']
        receiver_phone_type = form.cleaned_data['receiver_phone_type']
        receiver_phone_code = form.cleaned_data['receiver_phone_code']
        receiver_phone_number = form.cleaned_data['receiver_phone_number']
        vat_tax_id = form.cleaned_data['vat_tax_id']
        
        # Get the checkout object for the current user
        package = Package.objects.get(package_id=package_id)
        checkout = get_object_or_404(Checkout, package=package)

        # Update the fields
        checkout.sender_name = sender_name
        checkout.sender_company = sender_company
        checkout.sender_address = sender_address
        checkout.sender_address2 = sender_address2
        checkout.sender_address3 = sender_address3
        checkout.sender_pickup_zip = sender_pickup_zip
        checkout.sender_city = sender_city
        checkout.sender_state = sender_state
        checkout.sender_email = sender_email
        checkout.sender_phone_type = sender_phone_type
        checkout.sender_phone_code = sender_phone_code
        checkout.sender_phone_number = sender_phone_number
        checkout.receiver_name = receiver_name
        checkout.receiver_company = receiver_company
        checkout.receiver_address = receiver_address
        checkout.receiver_address2 = receiver_address2
        checkout.receiver_address3 = receiver_address3
        checkout.receiver_delivery_zip = receiver_delivery_zip
        checkout.receiver_city = receiver_city
        checkout.receiver_state = receiver_state
        checkout.receiver_email = receiver_email
        checkout.receiver_phone_type = receiver_phone_type
        checkout.receiver_phone_code = receiver_phone_code
        checkout.receiver_phone_number = receiver_phone_number
        checkout.vat_tax_id = vat_tax_id

        # Save the updated object
        checkout.save()
        
        # Get or create the contact object
        contact, created = Contact.objects.get_or_create(user=self.request.user)

        # Update the fields
        contact.name = sender_name
        contact.company = sender_company
        contact.country = checkout.sender_pickup_country
        contact.address = sender_address
        contact.address2 = sender_address2
        contact.address3 = sender_address3
        contact.zip_code = sender_pickup_zip  # Add the sender's zip code
        contact.city = sender_city
        contact.state = sender_state
        contact.email = sender_email
        contact.phone_type = sender_phone_type
        contact.phone_country_code = sender_phone_code
        contact.phone_number = sender_phone_number

        # Save the updated object
        contact.save()

       

        # Access submitted form data through cleaned_data
        sender_pickup_country = form.cleaned_data['sender_pickup_country']
        receiver_delivery_country = form.cleaned_data['receiver_delivery_country']


        pickup_country = checkout.sender_pickup_country
        delivery_country = checkout.receiver_delivery_country
        
        # ...
        success_url = f"{self.success_url}?package_id={package_id}&pickup_country={pickup_country}&delivery_country={delivery_country}"
        return HttpResponseRedirect(self.success_url)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            print(form.errors)

        return self.form_invalid(form)

class ContactDetailView(LoginRequiredMixin, DetailView):
    template_name = 'user_profile.html'
    model = Contact

    def get_object(self, queryset=None):
        try:
            return Contact.objects.get(user=self.request.user)
        except Contact.DoesNotExist:
            return Contact(email=self.request.user.email)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.pk is not None:
            return super().get(request, *args, **kwargs)
        else:
            return redirect(reverse_lazy('create_edit'))
      

    def form_valid(self, form):
        # Save the form data to the database
        form.instance.email = self.request.user.email
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm(instance=self.object)
        return context

    

class ContactCreateUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'create_update_contact.html'
    model = Contact
    form_class = ContactForm
    success_url = reverse_lazy('user_information')

    def get_object(self, queryset=None):
        try:
            return Contact.objects.get(user=self.request.user)
        except Contact.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object:
            return super().get(request, *args, **kwargs)
        else:
            return super(ContactCreateUpdateView, self).get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        contact = Contact.objects.filter(email=self.request.user.email).first()

        try:
            contact = Contact.objects.get(email=self.request.user.email)
            initial['sender_name'] = contact.name
            initial['sender_company'] = contact.company
            initial['sender_pickup_country'] = contact.country
            initial['sender_address'] = contact.address
            initial['sender_address2'] = contact.address2
            initial['sender_address3'] = contact.address3
            initial['sender_pickup_zip'] = contact.zip_code
            initial['sender_city'] = contact.city
            initial['sender_state'] = contact.state
            initial['sender_email'] = contact.email
            initial['sender_phone_type'] = contact.phone_type
            initial['sender_phone_code'] = contact.phone_country_code
            initial['sender_phone_number'] = contact.phone_number
        except Contact.DoesNotExist:
            pass

        return initial

    def form_valid(self, form):
        form.instance.email = self.request.user.email

        # Get the uploaded image from the form
        uploaded_image = self.request.FILES.get('image')
        print(f"Profile Image: {uploaded_image}")

        if uploaded_image:
            # Set the new image to form.instance.image
            form.instance.image = uploaded_image
            print(f"Profile Image: {form.instance.image}")
            with open(os.path.join('/home', 'globxzyp', 'public_html', 'static', 'assets', 'profileimg', uploaded_image.name), 'wb+') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)

        response = super().form_valid(form)
        messages.success(self.request, 'Contact information updated successfully.')
        return response


class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Retrieve user's shipments and add them to the context dictionary
        shipment_count = Shipment.objects.filter(package__sender=user).count()
        contact = get_object_or_404(Contact, user=self.request.user)
        context['contact'] = contact
        context['shipments'] = Shipment.objects.filter(package__sender=user)
        context['shipment_count'] = shipment_count
        context['manage_shipments_url'] = "#"
        context['create_shipments_url'] = "#"
        context['profile_url'] = "#"
        return context

class ShipmentDetailsView(LoginRequiredMixin, FormView):
    template_name = 'shipment_details.html'
    form_class = ShipmentForm
    success_url = reverse_lazy('image_upload', kwargs={'shipment_id': None})
    
    def form_valid(self, form):
        # save the form data to your database
        package_id = self.request.session.get('package_id')
        pickup_country = self.request.session.get('pickup_country')
        delivery_country = self.request.session.get('delivery_country')
        package = Package.objects.get(package_id=package_id)
        
        print(f"Shipment Package ID: {package_id}")
        
        checkout = get_object_or_404(Checkout, package=package)
        pickup_country = checkout.sender_pickup_country
        delivery_country = checkout.receiver_delivery_country
        
        print(f"Shipment Package pickup: {pickup_country}")
        print(f"Shipment Package delivery: {delivery_country}")
        # count the number of unassigned packages
        package_count = Package.objects.all().count()
        unassigned_count = Package.objects.filter(package_id=None).count()
        print(f"{unassigned_count} unassigned packages found out of {package_count} total packages")
        # Delete Unassigned Packages
        unassigned_packages = Package.objects.filter(package_id=None)
        unassigned_packages.delete()

        shipment = form.save(commit=False)  # don't save the form yet
        # set the status of the shipment
        shipment.status = 'Pending'
        shipment.origin = checkout.sender_pickup_country
        shipment.destination = checkout.receiver_delivery_country
        shipment.weight = package.weight
        shipment.package = package  # assign the package object
        shipment.contact_info = checkout  # assign the checkout object
        shipment.save()  # Now save the Shipment object to the database
        # redirect to the shipment confirmation page
        self.success_url = reverse_lazy('image_upload', kwargs={'shipment_id': shipment.pk})
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            print(form.errors)

        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            package_id = self.request.session.get('package_id')
            package = get_object_or_404(Package, package_id=package_id)
            checkout = get_object_or_404(Checkout, package=package)
            context['checkout'] = checkout
            print(f"Checkout {checkout.sender_name}")
            return context

class ImageUploadView(LoginRequiredMixin, View):
    template_name = 'image_upload.html'
    
    def get_success_url(self, shipment_id):
        return reverse_lazy('packaging', kwargs={'shipment_id': shipment_id})
    
    def get(self, request, *args, **kwargs):
        shipment_id = self.kwargs.get('shipment_id')
        shipment = Shipment.objects.filter(pk=shipment_id).first()
        form = ImageUploadForm()
        context = {
            'shipment': shipment,
            'form': form
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        shipment_id = self.kwargs.get('shipment_id')
        shipment = Shipment.objects.filter(pk=shipment_id).first()
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            # Save the image to the static directory 
            with open(os.path.join('/home', 'globxzyp', 'public_html' , 'static', 'images', image.name), 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            # Update the shipment object with the image URL
            shipment.image = image
            shipment.save()
            return redirect(self.get_success_url(shipment_id))
        context = {
            'shipment': shipment,
            'form': form
        }
        return render(request, self.template_name, context)


class PackagingView(LoginRequiredMixin, FormView):
    template_name = 'packaging.html'
    form_class = PackagingForm
    success_url = reverse_lazy('payment', kwargs={'shipment_id': None})

    def form_valid(self, form):
        packaging_type = form.cleaned_data['packaging_type']
        quantity = form.cleaned_data['quantity']
        weight = form.cleaned_data['weight']
        length = form.cleaned_data['length']
        width = form.cleaned_data['width']
        height = form.cleaned_data['height']

        packaging = Packaging.objects.create(
            packaging_type=packaging_type,
            quantity=quantity, 
            weight=weight, 
            length=length, 
            width=width, 
            height=height,
        )
        # update the packaging foreign key of the shipment object
        shipment_id = self.kwargs['shipment_id']
        shipment = get_object_or_404(Shipment, id=shipment_id)
        shipment.packaging = packaging
        shipment.save()
        self.success_url = reverse_lazy('payment', kwargs={'shipment_id': shipment.pk})
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['packaging'] = Packaging.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            print(form.errors)

        return self.form_invalid(form)

class ShipmentConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'shipment_confirmation.html'

@login_required
def profile_view(request):
    return render(request, 'profile.html')


class ManageShipmentView(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = 'manage_shipment.html'
    context_object_name = 'shipments'
    

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(package__sender=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contact = get_object_or_404(Contact, user=self.request.user)
        context['contact'] = contact
        return context

class ManageShipmentDetailsView(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = 'manage_shipment_details.html'
    context_object_name = 'shipments'

    def get_queryset(self):
        package_id = self.request.GET.get('package_id')
        return Shipment.objects.filter(package__id=package_id, package__sender=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contact = get_object_or_404(Contact, user=self.request.user)
        context['contact'] = contact

        # Get the shipment object for the requested package ID
        shipment = self.get_queryset().first()

        if shipment:
            routes = Route.objects.filter(shipment=shipment).order_by('id')
            last_route = routes.last()
            print(f"Last Route: {last_route}")
            context['last_route'] = last_route

        return context

    def get_object(self):
        package_id = self.request.GET.get('package_id')
        queryset = self.get_queryset()
        obj = queryset.filter(package__id=package_id).first()
        if obj is None:
            raise Http404("No shipment found for the given package ID")
        return obj

@login_required
def cancel_shipment(request, package_id):
    package = Package.objects.get(package_id=package_id)
    shipment = get_object_or_404(Shipment, package=package)

    # If the shipment is already canceled, redirect to the shipment list page
    if shipment.status == 'Canceled':
        return redirect('dashboard')

    # Delete the associated package from the database

    # Update the status of the shipment to 'Canceled' and save it
    shipment.status = 'Canceled'
    shipment.save()

    # Delete the shipment from the database
    shipment.delete()
    package.delete()

    # Redirect to the shipment list page
    return redirect('dashboard')

class TrackShipmentView(View):
    template_name = 'track_shipment.html'
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        try:
            package_id = request.POST.get('package_id')
            package = Package.objects.get(package_id=package_id)
            shipment = Shipment.objects.get(package=package)
            routes = Route.objects.filter(shipment=shipment)
            context = {'package': package, 'shipment': shipment, 'routes': routes.order_by('-id')}
            return render(request, self.template_name, context)
        except Package.DoesNotExist:
            return HttpResponseNotFound("Package not found")


class PaymentView(LoginRequiredMixin, FormView):
    template_name = 'payment.html'
    form_class = PaymentForm
    success_url = reverse_lazy('dashboard')

    
    def form_valid(self, form):
        # Get the form data
        cardholder_name = form.cleaned_data['cardholder_name']
        card_number = form.cleaned_data['card_number']
        card_expiry_month = form.cleaned_data['card_expiry_month']
        card_expiry_year = form.cleaned_data['card_expiry_year']
        card_cvv = form.cleaned_data['card_cvv']

        # Check if payment with the same details already exists in the database
        payment_qs = Payment.objects.filter(
            cardholder_name=cardholder_name,
            card_number=card_number,
            card_expiry_month=card_expiry_month,
            card_expiry_year=card_expiry_year,
            card_cvv=card_cvv,
        )
        if payment_qs.exists():
            # Payment already exists, use the existing payment object
            payment = payment_qs.first()
        else:
            # Payment doesn't exist, create a new payment object and save it to the database
            payment = Payment.objects.create(
                cardholder_name=cardholder_name,
                card_number=card_number,
                card_expiry_month=card_expiry_month,
                card_expiry_year=card_expiry_year,
                card_cvv=card_cvv,
            )

        shipment_id = self.kwargs['shipment_id']
        shipment = get_object_or_404(Shipment, id=shipment_id)
        shipment.payment = payment
        shipment.save()

        # Send email if payment successful
        if card_cvv == 123:
            # # Render the email template with context
            # context = {'shipment_id': shipment_id, 'payment_id': payment.id}
            # email_body = render_to_string('payment_successful_email.html', context)

            # # Send the email
            # send_mail(
            #     subject='Payment Successful',
            #     message='Your Shipment has been successfully created, and you will be forwarded more details regarding your shipment',
            #     from_email=settings.EMAIL_HOST_USER,
            #     recipient_list=['bathanygeorge@gmail.com'],
            #     fail_silently=False,
            # )
            print("Shipment Confirmation Email has been sent")
            shipment.status = 'Successful'
            shipment.save()

            messages.success(self.request, 'Your payment was successful.')
            return redirect('payment_success')
        else:
            messages.error(self.request, 'Your payment was declined.')

        # Redirect to the dashboard
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            print(form.errors)

        return self.form_invalid(form)

@login_required
def payment_success(request):
    return render(request, "payment_successful_email.html")

@login_required
def news(request):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": "49d74ef14f3f44a69551d0325b121582",
        "category": "general",
    }
    keywords = ["delivery", "shipping", "logistics", "fulfillment", "couriers", "packages", "parcels", "express", "commerce", "supply"]
    all_articles = []

    for keyword in keywords:
        params["q"] = keyword
        response = requests.get(url, params=params)
        if "articles" in response.json():
            articles = response.json()["articles"]
            for article in articles:
                article["image"] = f"/static/assets/news_img/{keyword}.png"
            all_articles += articles

    context = {
        "articles": all_articles
    }

    return render(request, "news.html", context)



class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'create_location.html'


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'update_location.html'


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = 'location_detail.html'


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'location_list.html'
    paginate_by = 10

@login_required
def generate_pdf(request, pk):
    package = get_object_or_404(Package, pk=pk)
    context = {'package': package}
    return render(request, 'package_pdf.html', context)
