from django.contrib import admin
from django.urls import path

from expedipace import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', views.logout, name='logout'),
    path('accounts/signup/', views.register, name='sign_up'),
    # Swiftdrop App urls
    path('', views.HomeView.as_view(), name='home'),
    path('location/', views.LocationView.as_view(), name='location'),
    path('user_profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('trackquote/', views.TrackQuoteView.as_view(), name='trackquote'),
    path('tracking/', views.TrackingView.as_view(), name='tracking'),
    path('success-history/', views.SuccessHistoryView.as_view(), name='successHistory'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('support/', views.support, name='support'),
    path('thank_you/', views.thank_you, name='thank_you'),
    path('quote/', views.QuotesCreateView.as_view(), {'action': 'quote'}, name='quote'),
    path('create_shipment/', views.QuotesCreateView.as_view(), {'action': 'create'}, name='create_shipment'),
    path('show-price/', views.show_price, name='show_price'),
    path('news/', views.news, name="news"),
    path('payment/<int:shipment_id>/', views.PaymentView.as_view(), name="payment"),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('profile/', views.profile_view, name="profile"),
    path('manage_shipments/', views.ManageShipmentView.as_view(), name="manage_shipments"),
    path('manage_shipment_details/', views.ManageShipmentDetailsView.as_view(), name="manage_shipment_details"),
    path('track_shipment/', views.TrackShipmentView.as_view(), name='track_shipment'),
    path('user_information/', views.ContactDetailView.as_view(), name='user_information'),
    path('payment_settings/', views.PaymentSettingView.as_view(), name='payment_settings'),
    path('user_information_update/', views.ContactCreateUpdateView.as_view(), name='user_information_update'),
    path('create_edit/', views.ContactCreateUpdateView.as_view(), name='create_edit'),
    path('cancel_shipment/<str:package_id>/', views.cancel_shipment, name='cancel_shipment'),
    path('payment_success', views.payment_success, name='payment_success'), 
 

    # Shipment detials
    path('shipment-details/', views.ShipmentDetailsView.as_view(), name='shipment_details'),
    path('image_upload/<int:shipment_id>', views.ImageUploadView.as_view(), name='image_upload'),
    path('packaging/<int:shipment_id>/', views.PackagingView.as_view(), name='packaging'),
    path('shipment-confirmation/', views.ShipmentConfirmationView.as_view(), name='shipment_confirmation'),

    # Location URLs
    path('locations/', views.LocationListView.as_view(), name='location_list'),
    path('locations/create/', views.LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/', views.LocationDetailView.as_view(), name='location_detail'),
    path('locations/<int:pk>/update/', views.LocationUpdateView.as_view(), name='location_update'),
]

