from django.urls import path
from . import views
from .views import BusinessRegistrationView, BusinessSubscriptionSuccessView, BusinessSubscriptionCancelView, BusinessConnectRefreshView, BusinessConnectCompleteView

urlpatterns = [
    path('', views.home, name="home"),
    path('shop/', views.shop, name="shop"),
    path('products/', views.products, name="products"),
    path('services/', views.services, name="services"),
    path('search/', views.search, name='search'),
    path('community/', views.community, name="community"),
    path('community/?country=<int:country_id>', views.community, name='community'),
    path('events/', views.events, name='events'),
    path('create-event/', views.create_event, name='create_event'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),

    # Business registration and subscription routes (MOVED UP)
    path('business/registration/', views.BusinessRegistrationView.as_view(), name='business_registration'),
    path('business/subscription/success/', BusinessSubscriptionSuccessView.as_view(), name='business_subscription_success'),
    path('business/subscription/cancel/', BusinessSubscriptionCancelView.as_view(), name='business_subscription_cancel'),
    path('business/connect/refresh/', BusinessConnectRefreshView.as_view(), name='business_connect_refresh'),
    path('business/connect/complete/', BusinessConnectCompleteView.as_view(), name='business_connect_complete'),

    # User registration business route
    path('user/register-business', BusinessRegistrationView.as_view(), name="business_registration"),

    # Business specific routes with slugs (MOVED DOWN)
    path('business/<slug:business_slug>/', views.BusinessDetailView.as_view(), name='business_detail'),
    path('business/<slug:business_slug>/orders/', views.BusinessOrdersView.as_view(), name='business_orders'),
    path('business/<slug:business_slug>/delete/', views.BusinessDeleteView.as_view(), name='delete_business'),
    path('quick-shop/<slug:product_slug>/', views.quick_shop_view, name='quick_shop'),
    path('business/<slug:business_slug>/edit/', views.edit_business, name='edit_business'),
    path('business/<slug:business_slug>/product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('business/<slug:business_slug>/product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('business/<slug:business_slug>/product/<slug:product_slug>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('ajax/product/<slug:business_slug>/<slug:product_slug>/', views.AjaxProductDetailView.as_view(), name='ajax_product_detail'),
    path('business/<slug:business_slug>/product/<slug:product_slug>/edit/', views.ProductEditView.as_view(), name='product_edit'),
    path('business/<slug:business_slug>/service/create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('business/<slug:business_slug>/service/<slug:service_slug>/edit/', views.ServiceEditView.as_view(), name='service_edit'),
    path('business/<slug:business_slug>/service/<slug:service_slug>/', views.service_detail, name='service_detail'),
    path('business/<str:business_slug>/service/<str:service_slug>/review/', views.ServiceReviewView.as_view(), name='service_review'),
    path('delete-product-image/<int:image_id>/', views.delete_product_image, name='delete_product_image'),

    # Other routes
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/delete/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('cart/update_quantity/', views.CartView.as_view(), name='update_quantity'),
    path('cart/data/', views.CartView.as_view(), name='cart_data'),
    path('cart/add/', views.CartView.as_view(), name='add'),
    path('checkout/', views.CreateCheckoutSessionView.as_view(), name='checkout'),
    path('create-checkout-session/', views.CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    path('cancel/', views.PaymentSuccessView.as_view(), name='cancel'),
    path('orders/', views.UserOrdersView.as_view(), name='user_orders'),
    path('request-refund/<int:order_id>/', views.RequestRefundView.as_view(), name='request_refund'),
    path('message/<slug:business_slug>/', views.message_seller, name='message_seller'),
    path('message/buyer/<str:username>/', views.message_buyer, name='message_buyer'),
    path('messages/', views.user_messages_view, name='user_messages'),
    path('messages/<slug:business_slug>/', views.user_messages_view, name='user_messages_with_slug'),
    path('delete-variation/<int:variation_id>/', views.ProductEditView.delete_variation, name='delete_variation'),
    path('privacy-policy/', views.privacy_policy, name="privacy"),
    path('return-and-refund-policy/', views.return_and_refund_policy, name="return-policy"),
    path('terms-and-conditions/', views.terms_and_conditions, name="terms-and-conditions"),
    path('save_event/<int:event_id>/', views.save_event, name='save_event'),
    path('remove_saved_event/<int:event_id>/', views.remove_saved_event, name='remove_saved_event'),
    path('saved_events/', views.saved_events, name='saved_events'),
    path('verify-email/<uidb64>/<token>/', views.EmailVerificationView.as_view(), name='email_verification'),


    path('validate-address/', views.validate_address_free, name='validate_address'),
    path('delivery-tracking/<str:delivery_id>/', views.delivery_tracking, name='delivery_tracking'),
    path('test-doordash/', views.test_doordash_credentials, name='test_doordash'),
    path('get-delivery-quote/', views.DeliveryQuoteView.as_view(), name='get_delivery_quote'),
    path('debug-business-addresses/', views.debug_business_addresses, name='debug_business_addresses'),
    path('test-shippit/', views.test_shippit_directly, name='test_shippit'),
]