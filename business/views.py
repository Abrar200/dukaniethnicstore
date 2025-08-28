from django.shortcuts import render
from .models import Country, Product, Business, Service, OpeningHour, Cart, Message, State, Event, Variation, ProductVariation, VAR_CATEGORIES, CartItemVariation, ProductReview, Order, OrderItem, Refund, SavedEvent, ServiceImage, ServiceVideo, ServiceReview, ProductImage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
import logging
import json
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import itertools
from users.models import CustomUser
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from itertools import chain
from django.template import RequestContext
from django.template.context_processors import csrf
import stripe
from django.conf import settings
from collections import defaultdict
import string
import random
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from decimal import Decimal
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Subquery, OuterRef
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from .forms import ServiceReviewForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views import View
from users.views import send_verification_email
from .services.shippit_service import ShippitService


stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


def home(request):
    countries = Country.objects.all()
    products = Product.objects.all()
    context = {
        'countries': countries,
        'products': products,
    }
    return render(request, 'business/index.html', context)



def shop(request):
    return render(request, 'business/shop.html')

def privacy_policy(request):
    return render(request, 'business/privacy_policy.html')


def return_and_refund_policy(request):
    return render(request, 'business/return_and_refund_policy.html')


def terms_and_conditions(request):
    return render(request, 'business/terms_and_conditions.html')


def community(request):
    businesses = Business.objects.all().select_related('seller')

    countries = Country.objects.all()
    states = State.objects.all()

    country_filter = request.GET.getlist('country')
    state_filter = request.GET.getlist('state')

    if country_filter and state_filter:
        businesses = businesses.filter(
            countries__in=country_filter,
            states__in=state_filter
        ).distinct()
    elif country_filter:
        businesses = businesses.filter(countries__in=country_filter).distinct()
    elif state_filter:
        businesses = businesses.filter(states__in=state_filter).distinct()

    paginator = Paginator(businesses, 5)  # Show 10 businesses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.is_ajax():
        business_data = [
            {
                'business_name': business.business_name,
                'description': business.description,
                'business_slug': business.business_slug,
                'profile_picture': business.profile_picture.url,
                'seller_name': business.seller.get_full_name(),
                # Add more fields as needed
            }
            for business in page_obj
        ]
        return JsonResponse({'businesses': business_data})

    context = {
        'businesses': page_obj,
        'countries': countries,
        'states': states,
        'selected_countries': country_filter,
        'selected_states': state_filter,
    }
    return render(request, 'business/community.html', context)

import re

def validate_password(password):
    if len(password) < 12:
        raise ValidationError("Password must be at least 12 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r'[@$!%*#?&]', password):
        raise ValidationError("Password must contain at least one special character (@$!%*#?&).")


class BusinessRegistrationView(View):
    def get(self, request):
        countries = Country.objects.all()
        states = State.objects.all()
        day_choices = OpeningHour.DAY_CHOICES
        # Default empty context
        context = {
            'countries': countries,
            'states': states,
            'day_choices': day_choices,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'form_data': {},  # Will store previously entered data on validation errors
        }
        return render(request, 'users/business_registration.html', context)

    def post(self, request):
        try:
            # Collect form data to potentially return to the template
            form_data = {
                'first_name': request.POST.get('first_name', ''),
                'last_name': request.POST.get('last_name', ''),
                'username': request.POST.get('username', ''),
                'email': request.POST.get('email', ''),
                # Don't return passwords for security
                'business_name': request.POST.get('business_name', ''),
                'description': request.POST.get('description', ''),
                'business_type': request.POST.get('business_type', ''),
                'address': request.POST.get('address', ''),
                'postcode': request.POST.get('postcode', ''),
                'phone': request.POST.get('phone', ''),
                'website': request.POST.get('website', ''),
                'country_ids': request.POST.getlist('countries[]'),
                'state_ids': request.POST.getlist('states[]'),
            }

            # Collect opening hours data
            opening_hours_data = {}
            opening_hours_errors = []

            for day, day_display in OpeningHour.DAY_CHOICES:
                is_closed = request.POST.get(f'opening_hours-{day}-is_closed') == 'on'
                opening_time = request.POST.get(f'opening_hours-{day}-opening_time', '')
                closing_time = request.POST.get(f'opening_hours-{day}-closing_time', '')

                opening_hours_data[day] = {
                    'is_closed': is_closed,
                    'opening_time': opening_time,
                    'closing_time': closing_time
                }

                # Validate opening hours - either closed OR both times provided
                if not is_closed and (not opening_time or not closing_time):
                    opening_hours_errors.append(f"{day_display}: Please provide both opening and closing times or mark as closed.")

            form_data['opening_hours'] = opening_hours_data

            # Check for opening hours errors
            if opening_hours_errors:
                for error in opening_hours_errors:
                    messages.error(request, error)
                return self.render_form_with_errors(request, form_data)

            # User registration data extraction
            first_name = form_data['first_name']
            last_name = form_data['last_name']
            username = form_data['username']
            email = form_data['email']
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            business_type = form_data['business_type']
            postcode = form_data['postcode']

            # Validate postcode (Australian 4-digit postcode)
            if postcode and not postcode.isdigit():
                messages.error(request, 'Postcode must contain only numbers.')
                return self.render_form_with_errors(request, form_data)

            if postcode and len(postcode) != 4:
                messages.error(request, 'Postcode must be exactly 4 digits.')
                return self.render_form_with_errors(request, form_data)

            # Password validation
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return self.render_form_with_errors(request, form_data)

            # Validate password
            try:
                validate_password(password)
            except ValidationError as e:
                messages.error(request, e.messages[0])
                return self.render_form_with_errors(request, form_data)

            # Validate username
            username_validator = RegexValidator(
                regex=r'^[a-zA-Z0-9_.]+$',
                message="Username can only contain letters, numbers, underscores, and periods."
            )

            try:
                username_validator(username)
            except ValidationError as e:
                messages.error(request, e.message)
                return self.render_form_with_errors(request, form_data)

            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return self.render_form_with_errors(request, form_data)
            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                return self.render_form_with_errors(request, form_data)
            else:
                # Create temporary user account (inactive until subscription is complete)
                user = CustomUser.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password
                )
                user.is_seller = True
                user.is_active = False  # Set inactive until email is verified and subscription is complete
                user.save()

                # Store user info in session
                request.session['business_registration_user_id'] = user.id

                # Store business info in session (using email as business email)
                request.session['business_registration_data'] = {
                    'business_name': form_data['business_name'],
                    'description': form_data['description'],
                    'business_type': business_type,
                    'country_ids': form_data['country_ids'],
                    'state_ids': form_data['state_ids'],
                    'address': form_data['address'],
                    'phone': form_data['phone'],
                    'website': form_data['website'],
                    'email': email, # Use the same email for business
                    'postcode': postcode,
                }

                # Store opening hours data in session
                request.session['business_registration_opening_hours'] = opening_hours_data

                # Create Stripe customer
                customer = stripe.Customer.create(
                    email=email,
                    name=f"{first_name} {last_name}"
                )

                # Store customer ID in session
                request.session['business_registration_stripe_customer_id'] = customer.id

                # Get subscription price based on business type
                price_id = self._get_price_id_for_business_type(business_type)

                # Create checkout session for subscription
                checkout_session = stripe.checkout.Session.create(
                    customer=customer.id,
                    success_url=request.build_absolute_uri(reverse('business_subscription_success')),
                    cancel_url=request.build_absolute_uri(reverse('business_subscription_cancel')),
                    payment_method_types=['card'],
                    mode='subscription',
                    line_items=[{
                        'price': price_id,
                        'quantity': 1,
                    }],
                    metadata={
                        'user_id': user.id,
                        'business_type': business_type,
                    }
                )

                # Redirect to Stripe Checkout
                return redirect(checkout_session.url)

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            # Return form with previously entered data
            return self.render_form_with_errors(request, form_data if 'form_data' in locals() else {})

    def render_form_with_errors(self, request, form_data):
        """Helper method to render the form with validation errors and previously entered data"""
        countries = Country.objects.all()
        states = State.objects.all()
        day_choices = OpeningHour.DAY_CHOICES

        context = {
            'countries': countries,
            'states': states,
            'day_choices': day_choices,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'form_data': form_data,
        }
        return render(request, 'users/business_registration.html', context)

    def _get_price_id_for_business_type(self, business_type):
        """Get the Stripe price ID based on business type"""
        if business_type == 'product':
            return settings.STRIPE_PRODUCT_BUSINESS_PRICE_ID
        elif business_type == 'service':
            return settings.STRIPE_SERVICE_BUSINESS_PRICE_ID
        elif business_type == 'both':
            return settings.STRIPE_BOTH_BUSINESS_PRICE_ID
        else:
            raise ValueError(f"Invalid business type: {business_type}")


class BusinessSubscriptionSuccessView(View):
    def get(self, request):
        """Handle successful subscription"""
        # Get data from session
        user_id = request.session.get('business_registration_user_id')
        business_data = request.session.get('business_registration_data')
        opening_hours_data = request.session.get('business_registration_opening_hours')
        stripe_customer_id = request.session.get('business_registration_stripe_customer_id')

        if not all([user_id, business_data, opening_hours_data, stripe_customer_id]):
            messages.error(request, "Session data lost. Please start the registration process again.")
            return redirect('business_registration')

        try:
            # Get the user
            user = CustomUser.objects.get(id=user_id)

            # Retrieve customer's subscription from Stripe
            customer = stripe.Customer.retrieve(stripe_customer_id)
            subscriptions = stripe.Subscription.list(customer=stripe_customer_id, limit=1)

            if not subscriptions.data:
                messages.error(request, "No subscription found. Please contact support.")
                return redirect('home')

            subscription = subscriptions.data[0]

            # Show a form to upload files and complete registration
            return render(request, 'business/subscription_success.html', {
                'user': user,
                'business_data': business_data,
                'subscription_id': subscription.id,
            })

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('home')

    def post(self, request):
        """Complete business registration and create Stripe Connect account"""
        # Get data from session
        user_id = request.session.get('business_registration_user_id')
        business_data = request.session.get('business_registration_data')
        opening_hours_data = request.session.get('business_registration_opening_hours')
        stripe_customer_id = request.session.get('business_registration_stripe_customer_id')

        if not all([user_id, business_data, opening_hours_data, stripe_customer_id]):
            messages.error(request, "Session data lost. Please start the registration process again.")
            return redirect('business_registration')

        try:
            # Get the user
            user = CustomUser.objects.get(id=user_id)

            # Retrieve customer's subscription from Stripe
            subscriptions = stripe.Subscription.list(customer=stripe_customer_id, limit=1)

            if not subscriptions.data:
                messages.error(request, "No subscription found. Please contact support.")
                return redirect('home')

            subscription = subscriptions.data[0]

            # Get uploaded files (optional now)
            profile_picture = request.FILES.get('profile_picture')
            banner_image = request.FILES.get('banner_image')

            # Create the business with default images if none provided
            business = Business.objects.create(
                seller=user,
                business_name=business_data['business_name'],
                description=business_data['description'],
                business_type=business_data['business_type'],
                address=business_data['address'],
                postcode=business_data.get('postcode', '5000'),
                phone=business_data['phone'],
                website=business_data['website'],
                email=business_data['email'],
                profile_picture=profile_picture if profile_picture else 'business_profiles/DukaniEthnicStore.png',
                banner_image=banner_image if banner_image else 'business_profiles/DukaniEthnicStore.png',
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=subscription.id,
            )

            # Set M2M relationships
            business.countries.set(business_data['country_ids'])
            business.states.set(business_data['state_ids'])

            # Create opening hours
            for day, data in opening_hours_data.items():
                if data['is_closed']:
                    OpeningHour.objects.create(
                        business=business,
                        day=day,
                        is_closed=True
                    )
                elif data['opening_time'] and data['closing_time']:
                    OpeningHour.objects.create(
                        business=business,
                        day=day,
                        opening_time=data['opening_time'],
                        closing_time=data['closing_time'],
                        is_closed=False
                    )
                else:
                    messages.error(request, f"Please specify both opening and closing times or mark the day as closed for {day}.")
                    business.delete()
                    return redirect('business_registration')

            # Create Stripe Connect account
            try:
                account = stripe.Account.create(
                    type='express',
                    country='AU',
                    email=user.email,
                    business_type='individual',
                )

                business.stripe_account_id = account.id
                business.save()

                # Create account link for onboarding
                account_link = stripe.AccountLink.create(
                    account=account.id,
                    refresh_url=request.build_absolute_uri(reverse('business_connect_refresh')),
                    return_url=request.build_absolute_uri(reverse('business_connect_complete')),
                    type='account_onboarding',
                )

                # Store business slug in session for the Connect completion
                request.session['business_connect_business_slug'] = business.business_slug

                # Send verification email BEFORE activating the user
                try:
                    send_verification_email(user, request)
                    messages.success(request, "A verification email has been sent to your email address. Please verify your email to complete the registration.")
                except Exception as email_error:
                    messages.warning(request, f"Business created successfully, but there was an issue sending the verification email: {str(email_error)}")

                # Clear session data
                for key in ['business_registration_user_id', 'business_registration_data',
                           'business_registration_opening_hours', 'business_registration_stripe_customer_id']:
                    if key in request.session:
                        del request.session[key]

                # Redirect to Stripe Connect onboarding
                return redirect(account_link.url)

            except stripe.error.StripeError as e:
                business.delete()
                messages.error(request, f"Stripe error: {str(e)}")
                return redirect('business_registration')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('business_registration')

class BusinessSubscriptionCancelView(View):
    def get(self, request):
        """Handle subscription cancellation"""
        user_id = request.session.get('business_registration_user_id')

        # Clean up the user if it was created
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
                user.delete()
            except CustomUser.DoesNotExist:
                pass

            # Clear session data
            for key in ['business_registration_user_id', 'business_registration_data',
                       'business_registration_opening_hours', 'business_registration_stripe_customer_id']:
                if key in request.session:
                    del request.session[key]

        messages.info(request, "Business registration cancelled. No charges were made.")
        return redirect('home')


class BusinessConnectRefreshView(View):
    def get(self, request):
        """Refresh Stripe Connect account link if it expires"""
        business_slug = request.session.get('business_connect_business_slug')

        if not business_slug:
            messages.error(request, "Session data lost. Please contact support.")
            return redirect('home')

        try:
            business = Business.objects.get(business_slug=business_slug)

            # Create a new account link
            account_link = stripe.AccountLink.create(
                account=business.stripe_account_id,
                refresh_url=request.build_absolute_uri(reverse('business_connect_refresh')),
                return_url=request.build_absolute_uri(reverse('business_connect_complete')),
                type='account_onboarding',
            )

            return redirect(account_link.url)

        except Business.DoesNotExist:
            messages.error(request, "Business not found. Please contact support.")
            return redirect('home')
        except stripe.error.StripeError as e:
            messages.error(request, f"Stripe error: {str(e)}")
            return redirect('home')

class BusinessConnectCompleteView(View):
    def get(self, request):
        """Handle completion of Stripe Connect onboarding"""
        business_slug = request.session.get('business_connect_business_slug')

        if not business_slug:
            messages.error(request, "Session data lost. Please contact support.")
            return redirect('home')

        try:
            business = Business.objects.get(business_slug=business_slug)
            user = business.seller

            # Business registration and Stripe Connect setup is complete
            # Now user just needs to verify their email to activate account
            if user.email_verified:
                # Email already verified, account should already be active
                messages.success(request, "Business registration complete! You can now log in.")
                return redirect('login')
            else:
                # Email not verified yet, remind user to check email
                messages.info(request, "Business registration is almost complete! Please check your email and click the verification link to activate your account.")
                return redirect('home')

            # Clear session data
            if 'business_connect_business_slug' in request.session:
                del request.session['business_connect_business_slug']

        except Business.DoesNotExist:
            messages.error(request, "Business not found. Please contact support.")
            return redirect('home')

class EmailVerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Mark email as verified and activate account
            user.email_verified = True
            user.is_active = True
            user.save()

            if user.is_seller:
                messages.success(request, 'Your email has been verified! Your business account is now active. You can now log in.')
            else:
                messages.success(request, 'Your email has been verified successfully! You can now log in.')

            return redirect('login')
        else:
            messages.error(request, 'The verification link is invalid or has expired.')
            return redirect('resend_verification')  # Redirect to resend verification page


@login_required
def edit_business(request, business_slug):
    business = get_object_or_404(Business, business_slug=business_slug)

    # Check if the user is the seller of the business
    if request.user != business.seller:
        return redirect('business_detail', business_slug=business.business_slug)

    countries = Country.objects.all()
    states = State.objects.all()

    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        description = request.POST.get('description')
        business_type = request.POST.get('business_type')
        country_ids = request.POST.getlist('countries')
        state_ids = request.POST.getlist('states')
        address = request.POST.get('address')
        postcode = request.POST.get('postcode')  # Added postcode
        phone = request.POST.get('phone')
        website = request.POST.get('website')
        email = request.POST.get('email')
        profile_picture = request.FILES.get('profile_picture')
        banner_image = request.FILES.get('banner_image')

        # Validate postcode (Australian 4-digit postcode)
        if postcode and not postcode.isdigit():
            messages.error(request, 'Postcode must contain only numbers.')
            return render(request, 'business/edit_business.html', {
                'business': business,
                'countries': countries,
                'states': states,
                'day_choices': OpeningHour.DAY_CHOICES,
            })

        if postcode and len(postcode) != 4:
            messages.error(request, 'Postcode must be exactly 4 digits.')
            return render(request, 'business/edit_business.html', {
                'business': business,
                'countries': countries,
                'states': states,
                'day_choices': OpeningHour.DAY_CHOICES,
            })

        if business_name and description and business_type and address and phone:
            business.business_name = business_name
            business.description = description
            business.business_type = business_type
            business.address = address
            business.postcode = postcode if postcode else '5000'  # Added postcode with default
            business.phone = phone
            business.website = website
            business.email = email
            if profile_picture:
                business.profile_picture = profile_picture
            if banner_image:
                business.banner_image = banner_image

            countries = Country.objects.filter(id__in=country_ids)
            business.countries.set(countries)

            states = State.objects.filter(id__in=state_ids)
            business.states.set(states)

            business.save()

            # Update or create OpeningHour instances
            for day, day_display in OpeningHour.DAY_CHOICES:
                is_closed_str = request.POST.get(f'opening_hours-{day}-is_closed', 'off')
                is_closed = is_closed_str == 'on'
                opening_time = request.POST.get(f'opening_hours-{day}-opening_time')
                closing_time = request.POST.get(f'opening_hours-{day}-closing_time')

                opening_hour, created = OpeningHour.objects.get_or_create(
                    business=business,
                    day=day,
                    defaults={
                        'is_closed': is_closed,
                        'opening_time': opening_time if not is_closed else None,
                        'closing_time': closing_time if not is_closed else None,
                    }
                )

                if not created:
                    opening_hour.is_closed = is_closed
                    opening_hour.opening_time = opening_time if not is_closed else None
                    opening_hour.closing_time = closing_time if not is_closed else None
                    opening_hour.save()

            messages.success(request, 'Business updated successfully!')
            return redirect('business_detail', business_slug=business.business_slug)

    context = {
        'business': business,
        'countries': countries,
        'states': states,
        'day_choices': OpeningHour.DAY_CHOICES,
    }
    return render(request, 'business/edit_business.html', context)


class BusinessDetailView(View):
    def get(self, request, business_slug):
        business = get_object_or_404(Business, business_slug=business_slug)
        products = business.products.all()
        services = business.services.all()
        opening_hours = business.opening_hours.all()
        return render(request, 'business/business_detail.html', {'business': business, 'products': products, 'opening_hours': opening_hours, 'services': services})


@method_decorator(login_required, name='dispatch')
class BusinessDeleteView(View):
    def post(self, request, business_slug):
        business = get_object_or_404(Business, business_slug=business_slug)

        if request.user != business.seller:
            messages.error(request, "You do not have permission to delete this business.")
            return redirect('business_detail', business_slug=business_slug)

        # Delete the business
        business.delete()

        # Set the user as not a seller
        request.user.is_seller = False
        request.user.save()

        messages.success(request, "Business has been successfully deleted.")
        return redirect('home')  # Redirect to the home page or any other page after deletion



class BusinessOrdersView(LoginRequiredMixin, View):
    def get(self, request, business_slug):
        business = Business.objects.get(business_slug=business_slug)
        if request.user != business.seller:
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        # Fetch orders related to this business
        orders = Order.objects.filter(items__product__business=business).distinct().order_by('-created_at')
        order_data = []
        for order in orders:
            items = order.items.filter(product__business=business)
            order_data.append({
                'order': order,
                'items': items
            })

        return render(request, 'business/business_orders.html', {'business': business, 'orders': order_data})

    def post(self, request, business_slug):
        business = Business.objects.get(business_slug=business_slug)
        if request.user != business.seller:
            return JsonResponse({'error': 'Unauthorized access'}, status=403)

        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = Order.objects.get(id=order_id)

        # Update the order status
        order.order_status = new_status
        order.save()

        # Send email to the user based on the new status
        self.send_status_update_email(order, business, new_status)

        # Add a success message
        messages.success(request, f'Order status updated to {new_status} and email sent to the customer.')

        return redirect('business_orders', business_slug=business_slug)

    def send_status_update_email(self, order, business, status):
        user = order.user
        item_details = [
            f"{item.quantity} x {item.product.name} ({', '.join([f'{k}: {v}' for k, v in item.variations.items()]) if item.variations else ''})"
            for item in order.items.filter(product__business=business)
        ]

        if status == 'shipped':
            email_subject = f"Your order {order.ref_code} has been shipped"
            email_template = 'business/order_shipped_email.html'
        elif status == 'delivered':
            email_subject = f"Your order {order.ref_code} has been delivered"
            email_template = 'business/order_delivered_email.html'
        else:
            return

        email_body = render_to_string(email_template, {
            'user': user,
            'business': business,
            'order': order,
            'item_details': item_details
        })

        email = EmailMultiAlternatives(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(email_body, "text/html")
        email.send(fail_silently=False)


class ProductDetailView(View):
    def get(self, request, business_slug=None, product_slug=None):
        business = get_object_or_404(Business, business_slug=business_slug)
        product = get_object_or_404(Product, product_slug=product_slug, business=business)

        color_variations = Variation.objects.filter(product=product, name='color')
        size_variations = Variation.objects.filter(product=product, name='size')
        reviews = product.reviews.all()

        star_percentages = {
            5: product.star_rating_percentage(5),
            4: product.star_rating_percentage(4),
            3: product.star_rating_percentage(3),
            2: product.star_rating_percentage(2),
            1: product.star_rating_percentage(1),
        }

        context = {
            'product': product,
            'business': business,
            'color_variations': color_variations,
            'size_variations': size_variations,
            'reviews': reviews,
            'star_percentages': star_percentages,
            'overall_review': product.overall_review
        }

        return render(request, 'business/product_detail.html', context)

    @method_decorator(login_required)
    def post(self, request, business_slug=None, product_slug=None):
        business = get_object_or_404(Business, business_slug=business_slug)
        product = get_object_or_404(Product, product_slug=product_slug, business=business)

        review_text = request.POST.get('message')
        rating = request.POST.get('rating')

        if review_text and rating:
            rating = int(rating)
            ProductReview.objects.create(
                product=product,
                user=request.user,
                review_text=review_text,
                rating=rating
            )
            return redirect('product_detail', business_slug=business_slug, product_slug=product_slug)

        color_variations = Variation.objects.filter(product=product, name='color')
        size_variations = Variation.objects.filter(product=product, name='size')
        reviews = product.reviews.all()

        star_percentages = {
            5: product.star_rating_percentage(5),
            4: product.star_rating_percentage(4),
            3: product.star_rating_percentage(3),
            2: product.star_rating_percentage(2),
            1: product.star_rating_percentage(1),
        }

        context = {
            'product': product,
            'business': business,
            'color_variations': color_variations,
            'size_variations': size_variations,
            'reviews': reviews,
            'star_percentages': star_percentages,
        }

        return render(request, 'business/product_detail.html', context)



@method_decorator(login_required, name='dispatch')
class ProductDeleteView(View):
    def post(self, request, business_slug, product_slug):
        business = get_object_or_404(Business, business_slug=business_slug)
        product = get_object_or_404(Product, product_slug=product_slug, business=business)

        if request.user != business.seller:
            messages.error(request, "You do not have permission to delete this product.")
            return redirect('product_detail', business_slug=business_slug, product_slug=product_slug)

        product.delete()
        messages.success(request, "Product has been successfully deleted.")
        return redirect('business_detail', business_slug=business_slug)


class AjaxProductDetailView(View):
    def get(self, request, business_slug, product_slug):
        business = get_object_or_404(Business, business_slug=business_slug)
        product = get_object_or_404(Product, product_slug=product_slug, business=business)

        color_variations = Variation.objects.filter(product=product, name='color')
        size_variations = Variation.objects.filter(product=product, name='size')

        product_data = {
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'description': product.description,
            'images': [product.image.url, product.image2.url] if product.image and product.image2 else [],
            'color_variations': list(color_variations.values('id', 'values__id', 'values__value', 'values__image')),
            'size_variations': list(size_variations.values('id', 'values__id', 'values__value')),
            'sku': product.product_slug,
            'categories': [product.business.business_name],
            'tags': [tag.name for tag in product.tags.all()] if hasattr(product, 'tags') else []
        }
        return JsonResponse(product_data)



class ProductCreateView(LoginRequiredMixin, View):
    def get(self, request, business_slug):
        business = get_object_or_404(Business, business_slug=business_slug, seller=request.user)
        return render(request, 'business/product_create.html', {
            'business': business,
            'VAR_CATEGORIES': VAR_CATEGORIES,
            'Product': Product
        })

    def post(self, request, business_slug):
        business = get_object_or_404(Business, business_slug=business_slug, seller=request.user)
        if business.seller == request.user:
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            category = request.POST.get('category')
            image = request.FILES.get('image')
            image2 = request.FILES.get('image2')
            in_stock = request.POST.get('in_stock') == 'on'
            has_variations = request.POST.get('has_variations') == 'on'

            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                category=category,
                image=image,
                image2=image2,
                business=business,
                in_stock=in_stock,
                has_variations=has_variations
            )

            # Handle additional images
            additional_images = request.FILES.getlist('additional_images[]')
            for img in additional_images:
                ProductImage.objects.create(product=product, image=img)

            if has_variations:
                variation_names = request.POST.getlist('variation_names')
                for variation_name in variation_names:
                    variation = Variation.objects.create(
                        product=product,
                        name=variation_name
                    )
                    variation_values = request.POST.getlist(f'variation_values_{variation_name}')
                    variation_images = request.FILES.getlist(f'variation_images_{variation_name}')
                    for i, value in enumerate(variation_values):
                        variation_image = variation_images[i] if i < len(variation_images) else None
                        ProductVariation.objects.create(
                            variation=variation,
                            value=value,
                            image=variation_image
                        )

            return redirect('product_detail', business_slug=business.business_slug, product_slug=product.product_slug)
        else:
            return render(request, 'business/product_create.html', {
                'business': business,
                'error': 'You are not authorized to add products to this business.',
                'VAR_CATEGORIES': VAR_CATEGORIES,
                'Product': Product
            })



class ProductEditView(LoginRequiredMixin, View):
    def get(self, request, business_slug, product_slug):
        business = get_object_or_404(Business, business_slug=business_slug, seller=request.user)
        product = get_object_or_404(Product, product_slug=product_slug, business=business)
        variations = product.variations.all()
        variation_names = variations.values_list('name', flat=True)
        additional_images = product.additional_images.all()

        variations_with_values = {}
        for variation in variations:
            variation_values = ProductVariation.objects.filter(variation=variation, variation__product=product)
            variations_with_values[variation.name] = list(variation_values.values('id', 'value', 'image'))

        return render(request, 'business/product_edit.html', {
            'product': product,
            'business': business,
            'variations': variations,
            'variation_names': variation_names,
            'variations_with_values': variations_with_values,
            'additional_images': additional_images,
            'VAR_CATEGORIES': VAR_CATEGORIES
        })

    def post(self, request, business_slug, product_slug):
        business = get_object_or_404(Business, business_slug=business_slug, seller=request.user)
        product = get_object_or_404(Product, product_slug=product_slug, business=business)

        if request.user == business.seller:
            name = request.POST.get('name', product.name)
            description = request.POST.get('description', product.description)
            price = request.POST.get('price', product.price)
            image = request.FILES.get('image')
            image2 = request.FILES.get('image2')
            in_stock = request.POST.get('in_stock') == 'on'
            has_variations = request.POST.get('has_variations') == 'on'

            product.name = name
            product.description = description
            product.price = price
            if image:
                product.image = image
            if image2:
                product.image2 = image2
            product.in_stock = in_stock
            product.has_variations = has_variations
            product.save()

            # Handle deletion of additional images
            images_to_delete = request.POST.getlist('delete_images')
            ProductImage.objects.filter(id__in=images_to_delete).delete()

            # Handle new additional images
            additional_images = request.FILES.getlist('additional_images[]')
            for img in additional_images:
                ProductImage.objects.create(product=product, image=img)

            if has_variations:
                existing_variations = {v.name: v for v in product.variations.all()}

                variation_names = request.POST.getlist('variation_names')
                for variation_name in variation_names:
                    if variation_name in existing_variations:
                        variation = existing_variations[variation_name]
                    else:
                        variation = Variation.objects.create(
                            product=product,
                            name=variation_name
                        )

                    variation_values = request.POST.getlist(f'variation_values_{variation_name}')
                    variation_images = request.FILES.getlist(f'variation_images_{variation_name}')
                    variation_value_ids = request.POST.getlist(f'variation_value_ids_{variation_name}')

                    existing_values = {str(pv.id): pv for pv in variation.values.all()}

                    for i, value in enumerate(variation_values):
                        if value.strip() == "":
                            continue

                        variation_image = variation_images[i] if i < len(variation_images) else None
                        variation_value_id = variation_value_ids[i] if i < len(variation_value_ids) else None

                        if variation_value_id and variation_value_id in existing_values:
                            product_variation = existing_values[variation_value_id]
                            product_variation.value = value
                            if variation_image:
                                product_variation.image = variation_image
                            product_variation.save()
                        else:
                            existing_pv = ProductVariation.objects.filter(variation=variation, value=value).first()
                            if existing_pv:
                                if variation_image:
                                    existing_pv.image = variation_image
                                existing_pv.save()
                            else:
                                ProductVariation.objects.create(
                                    variation=variation,
                                    value=value,
                                    image=variation_image
                                )

                    for existing_value_id in existing_values.keys():
                        if existing_value_id not in variation_value_ids:
                            existing_values[existing_value_id].delete()

                for existing_variation_name in existing_variations.keys():
                    if existing_variation_name not in variation_names:
                        existing_variations[existing_variation_name].delete()
            else:
                product.variations.all().delete()

            return redirect('product_detail', business_slug=business.business_slug, product_slug=product.product_slug)
        else:
            return redirect('product_detail', business_slug=business.business_slug, product_slug=product.product_slug)


    @login_required
    @require_POST
    def delete_variation(request, variation_id):
        try:
            variation = ProductVariation.objects.get(id=variation_id)
            if variation.variation.product.business.seller == request.user:
                variation.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        except ProductVariation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Variation not found'}, status=404)


# Add this new view to handle deleting additional images via AJAX
@login_required
@require_POST
def delete_product_image(request, image_id):
    try:
        image = ProductImage.objects.get(id=image_id)
        if image.product.business.seller == request.user:
            image.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
    except ProductImage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

def services(request):
    services = Service.objects.all()

    countries = Country.objects.annotate(service_count=Count('business__services', distinct=True))
    states = State.objects.annotate(service_count=Count('business__services', distinct=True))

    selected_countries = request.GET.getlist('country')
    selected_states = request.GET.getlist('state')

    if selected_countries:
        services = services.filter(business__countries__id__in=selected_countries)
    if selected_states:
        services = services.filter(business__states__id__in=selected_states)

    paginator = Paginator(services, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "services": page_obj,
        "countries": countries,
        "states": states,
        "selected_countries": selected_countries,
        "selected_states": selected_states,
    }
    return render(request, "business/services.html", context)


import requests
import time
from urllib.parse import quote

@login_required
def validate_address_free(request):
    """Validate address using free Nominatim service (OpenStreetMap)"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)

    address = request.GET.get('address')
    if not address:
        return JsonResponse({'error': 'Address parameter required'}, status=400)

    try:
        # Use Nominatim (free OpenStreetMap geocoding service)
        # Be respectful with rate limiting - max 1 request per second
        time.sleep(1)

        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'addressdetails': '1',
            'limit': '1',
            'countrycodes': 'au',  # Restrict to Australia
            'extratags': '1'
        }

        headers = {
            'User-Agent': 'DukaniEthnicStore/1.0 (contact@dukani.com)'  # Replace with your email
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()

        if data and len(data) > 0:
            result = data[0]

            # Extract address components
            address_parts = result.get('address', {})

            return JsonResponse({
                'success': True,
                'formatted_address': result.get('display_name', ''),
                'latitude': float(result.get('lat', 0)),
                'longitude': float(result.get('lon', 0)),
                'components': {
                    'house_number': address_parts.get('house_number', ''),
                    'road': address_parts.get('road', ''),
                    'suburb': address_parts.get('suburb', ''),
                    'city': address_parts.get('city', address_parts.get('town', '')),
                    'state': address_parts.get('state', ''),
                    'postcode': address_parts.get('postcode', ''),
                    'country': address_parts.get('country', '')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Address not found or invalid'
            })

    except Exception as e:
        logger.error(f"Address validation error: {str(e)}")
        return JsonResponse({'error': f'Address validation failed: {str(e)}'}, status=500)

from django.db.models import Avg

def service_detail(request, business_slug, service_slug):
    service = get_object_or_404(Service, service_slug=service_slug, business__business_slug=business_slug)
    reviews = service.reviews.all()
    overall_review = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    opening_hours = service.business.opening_hours.all()

    context = {
        'service': service,
        'reviews': reviews,
        'overall_review': overall_review,
        'opening_hours': opening_hours,
    }
    return render(request, 'business/service_detail.html', context)


class ServiceCreateView(LoginRequiredMixin, View):
    def get(self, request, business_slug):
        business = get_object_or_404(Business, business_slug=business_slug, seller=request.user)
        return render(request, 'business/service_create.html', {'business': business})

    def post(self, request, business_slug):
        business = get_object_or_404(Business, business_slug=business_slug, seller=request.user)
        if business.seller == request.user:
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            image = request.FILES.get('image')

            service = Service.objects.create(
                name=name,
                description=description,
                price=price,
                image=image,
                business=business
            )

            for img in request.FILES.getlist('additional_images[]'):
                ServiceImage.objects.create(service=service, image=img)

            for vid in request.FILES.getlist('additional_videos[]'):
                ServiceVideo.objects.create(service=service, video=vid)

            messages.success(request, 'Service created successfully.')
            return redirect('service_detail', business_slug=business.business_slug, service_slug=service.service_slug)
        else:
            messages.error(request, 'You do not have permission to create a service for this business.')
            return redirect('business_detail', business_slug=business_slug)

class ServiceReviewView(LoginRequiredMixin, View):
    def post(self, request, business_slug, service_slug):
        service = get_object_or_404(Service, service_slug=service_slug, business__business_slug=business_slug)
        review_text = request.POST.get('message')
        rating = request.POST.get('rating')
        user = request.user

        if review_text and rating:
            ServiceReview.objects.create(
                service=service,
                user=user,
                review_text=review_text,
                rating=int(rating)
            )
            messages.success(request, 'Your review has been submitted successfully.')
        else:
            messages.error(request, 'Please provide both a review text and a rating.')

        return redirect('service_detail', business_slug=service.business.business_slug, service_slug=service.service_slug)

class ServiceEditView(LoginRequiredMixin, View):
    def get(self, request, business_slug, service_slug):
        service = get_object_or_404(Service, service_slug=service_slug, business__business_slug=business_slug)
        business = service.business

        if request.user != business.seller:
            return redirect('service_detail', business_slug=business.business_slug, service_slug=service.service_slug)

        return render(request, 'business/service_edit.html', {'service': service, 'business': business})

    def post(self, request, business_slug, service_slug):
        service = get_object_or_404(Service, service_slug=service_slug, business__business_slug=business_slug)
        business = service.business

        if request.user == business.seller:
            service.name = request.POST.get('name')
            service.description = request.POST.get('description')
            service.price = request.POST.get('price')

            if 'delete_main_image' in request.POST:
                service.image.delete()
                service.image = None

            if 'image' in request.FILES:
                service.image = request.FILES['image']

            service.save()

            # Handle deletion of additional images
            images_to_delete = request.POST.getlist('delete_images')
            ServiceImage.objects.filter(id__in=images_to_delete).delete()

            # Handle deletion of videos
            videos_to_delete = request.POST.getlist('delete_videos')
            ServiceVideo.objects.filter(id__in=videos_to_delete).delete()

            # Handle new additional images
            for img in request.FILES.getlist('additional_images[]'):
                ServiceImage.objects.create(service=service, image=img)

            # Handle new videos
            for vid in request.FILES.getlist('additional_videos[]'):
                ServiceVideo.objects.create(service=service, video=vid)

            messages.success(request, 'Service updated successfully.')
            return redirect('service_detail', business_slug=business.business_slug, service_slug=service.service_slug)
        else:
            messages.error(request, 'You do not have permission to edit this service.')
            return redirect('service_detail', business_slug=business.business_slug, service_slug=service.service_slug)


class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'business/cart.html', {'cart_items': cart_items, 'total_price': total_price})

    @method_decorator(login_required)
    def post(self, request):
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            selected_variations = data.get('selected_variations', [])
            quantity = data.get('quantity', 1)  # Get the quantity from the request
            logger.debug(f'Received product_id: {product_id} with variations: {selected_variations} with quantity {quantity}')
        except json.JSONDecodeError:
            logger.error("Invalid JSON data in the request body")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if not product_id:
            logger.error("No product_id provided in the request")
            return JsonResponse({'error': 'No product_id provided'}, status=400)

        product = get_object_or_404(Product, id=product_id)

        variation_categories = product.variations.count()

        if product.has_variations and len(selected_variations) != variation_categories:
            messages.error(request, f"Please select all {variation_categories} variations.")
            return JsonResponse({'error': f'Please select all {variation_categories} variations.'}, status=400)

        variation_key = "-".join(sorted(str(v_id) for v_id in selected_variations))

        cart_item = Cart.objects.filter(user=request.user, product=product, variation_key=variation_key).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,  # Set the quantity
                variation_key=variation_key
            )
            for variation_id in selected_variations:
                product_variation = get_object_or_404(ProductVariation, id=variation_id)
                CartItemVariation.objects.create(cart=cart_item, product_variation=product_variation)

        cart_item.save()

        cart_items = Cart.objects.filter(user=request.user)
        cart_data = []
        for item in cart_items:
            item_variations = [v.product_variation.value for v in item.variations.all()]
            cart_data.append({
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': float(item.product.price),
                    'image': item.product.image.url if item.product.image else None,
                },
                'variations': item_variations,
                'quantity': item.quantity,
            })
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        logger.debug("Returning updated cart data as JSON response")
        return JsonResponse({'success': True, 'items': cart_data, 'subtotal': total_price})

    def get_cart_data(self, request):
        logger.debug("Received request to fetch cart data")
        cart_items = Cart.objects.filter(user=request.user)
        cart_data = []
        for item in cart_items:
            item_variations = [v.product_variation.value for v in item.variations.all()]
            cart_data.append({
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': float(item.product.price),
                    'image': str(item.product.image.url) if item.product.image else None,
                },
                'variations': item_variations,
                'quantity': item.quantity,
            })
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        logger.debug(f"Returning cart data: {cart_data}")
        return JsonResponse({'items': cart_data, 'subtotal': total_price})

    def update_quantity(self, request):
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            action = data.get('action')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        cart_item = get_object_or_404(Cart, id=item_id)

        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1

        cart_item.save()

        cart_items = Cart.objects.filter(user=request.user)
        cart_data = [
            {
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': float(item.product.price),
                    'image': item.product.image.url if item.product.image else None,
                },
                'variations': [v.product_variation.value for v in item.variations.all()],
                'quantity': item.quantity,
            }
            for item in cart_items
        ]
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        return JsonResponse({'success': True, 'items': cart_data, 'subtotal': total_price})

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.path == '/cart/update_quantity/':
                return self.update_quantity(request, *args, **kwargs)
            else:
                # Handle other POST requests here
                pass
        elif request.method == 'GET':
            if request.path == '/cart/data/':
                logger.debug(f"Request Path: {request.path}")
                return self.get_cart_data(request)
            else:
                # Handle other GET requests here
                pass

        return super().dispatch(request, *args, **kwargs)

@csrf_exempt
@login_required
def debug_business_addresses(request):
    """Debug view to check business addresses and postcode extraction"""

    # Get user's cart items
    cart_items = Cart.objects.filter(user=request.user).select_related('product__business')

    debug_info = []

    for cart_item in cart_items:
        business = cart_item.product.business

        # Test postcode extraction
        def extract_postcode_debug(address):
            """Extract 4-digit Australian postcode from address string with debugging"""
            print(f"DEBUG: Trying to extract postcode from: '{address}'")

            # Look for 4-digit number that could be a postcode
            postcode_pattern = r'\b(\d{4})\b'
            matches = re.findall(postcode_pattern, address)
            print(f"DEBUG: Pattern \\b(\\d{{4}})\\b found matches: {matches}")

            if matches:
                result = matches[-1]
                print(f"DEBUG: Returning postcode: {result}")
                return result

            # If no postcode found, try to extract from common formats
            state_postcode_pattern = r'\b[A-Z]{2,3}\s+(\d{4})\b'
            matches = re.findall(state_postcode_pattern, address.upper())
            print(f"DEBUG: State pattern found matches: {matches}")

            if matches:
                result = matches[-1]
                print(f"DEBUG: Returning state postcode: {result}")
                return result

            print("DEBUG: No postcode found")
            return None

        extracted_postcode = extract_postcode_debug(business.address)

        business_info = {
            'business_id': business.id,
            'business_name': business.business_name,
            'address': business.address,
            'extracted_postcode': extracted_postcode,
            'postcode_field': getattr(business, 'postcode', 'Field not exists'),
        }

        debug_info.append(business_info)

    return JsonResponse({
        'debug_info': debug_info,
        'total_businesses': len(debug_info)
    })

logger = logging.getLogger(__name__)

# Replace your existing DeliveryQuoteView with this updated version

@method_decorator(csrf_exempt, name='dispatch')
class DeliveryQuoteView(View):
    def post(self, request):
        """Get delivery quotes for cart items from all businesses"""

        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        try:
            # Parse request data
            data = json.loads(request.body)
            dropoff_address = data.get('dropoff_address')

            if not dropoff_address:
                return JsonResponse({'error': 'Dropoff address is required'}, status=400)

            logger.info(f"=== DELIVERY QUOTE REQUEST ===")
            logger.info(f"User: {request.user.username}")
            logger.info(f"Dropoff address: {dropoff_address}")

            # Get user's cart items
            cart_items = Cart.objects.filter(user=request.user).select_related('product__business')

            if not cart_items.exists():
                logger.warning("No cart items found for user")
                return JsonResponse({'error': 'No items in cart'}, status=400)

            # Group cart items by business
            businesses_data = {}
            for cart_item in cart_items:
                business = cart_item.product.business
                business_id = business.id

                if business_id not in businesses_data:
                    businesses_data[business_id] = {
                        'business': business,
                        'items': [],
                        'total_weight': 0
                    }

                # Add item to business group
                item_weight = 0.5  # Default weight per item in kg
                businesses_data[business_id]['items'].append({
                    'product': cart_item.product,
                    'quantity': cart_item.quantity,
                    'weight': item_weight * cart_item.quantity
                })
                businesses_data[business_id]['total_weight'] += item_weight * cart_item.quantity

            logger.info(f"Found {len(businesses_data)} businesses in cart")

            # Initialize Shippit service
            shippit_service = ShippitService()

            # Get quotes for each business
            business_quotes = {}
            total_delivery_fee = 0

            for business_id, business_data in businesses_data.items():
                business = business_data['business']
                logger.info(f"Processing business: {business.business_name}")

                # Get business postcode
                business_postcode = self.get_business_postcode(business)
                if not business_postcode:
                    logger.warning(f"Could not get postcode for business: {business.business_name}")
                    business_quotes[business_id] = {
                        'business_name': business.business_name,
                        'error': 'Business postcode not available'
                    }
                    continue

                # Extract postcode from delivery address
                delivery_postcode = self.extract_postcode(dropoff_address)
                if not delivery_postcode:
                    logger.warning(f"Could not extract postcode from delivery address: {dropoff_address}")
                    business_quotes[business_id] = {
                        'business_name': business.business_name,
                        'error': 'Invalid delivery address format'
                    }
                    continue

                # Prepare package details
                package_details = {
                    'weight': max(business_data['total_weight'], 0.1),  # Minimum 100g
                    'length': 20,  # Default package dimensions in cm
                    'width': 15,
                    'height': 10
                }

                logger.info(f"Requesting quote from {business_postcode} to {delivery_postcode}")
                logger.info(f"Package details: {package_details}")

                # Get quote from Shippit
                quote_response = shippit_service.quote_delivery(
                    pickup_postcode=business_postcode,
                    delivery_postcode=delivery_postcode,
                    package_details=package_details
                )

                logger.info(f"Shippit response for {business.business_name}: {quote_response}")

                if quote_response['success']:
                    quotes = quote_response.get('quotes', [])
                    logger.info(f"Received {len(quotes)} quotes for {business.business_name}")

                    if quotes:
                        # Find the cheapest standard delivery option
                        # Filter out same-day/priority options for regular checkout
                        standard_quotes = [q for q in quotes if q.get('courier_name', '').lower() not in ['priority', 'ondemand']]

                        if not standard_quotes:
                            # If no standard quotes, use the cheapest available
                            standard_quotes = quotes

                        # Get the cheapest quote
                        cheapest_quote = min(standard_quotes, key=lambda x: x.get('price', float('inf')))
                        delivery_fee = float(cheapest_quote.get('price', 0))

                        logger.info(f"Selected quote: {cheapest_quote}")

                        business_quotes[business_id] = {
                            'business_name': business.business_name,
                            'delivery_fee': delivery_fee,
                            'courier': cheapest_quote.get('courier_name', 'Standard'),
                            'service_type': cheapest_quote.get('service_type', 'Standard'),
                            'eta_info': {
                                'eta_date_from': cheapest_quote.get('eta_date_from'),
                                'eta_date_to': cheapest_quote.get('eta_date_to')
                            },
                            'quote_data': cheapest_quote
                        }

                        total_delivery_fee += delivery_fee
                        logger.info(f"Quote successful for {business.business_name}: ${delivery_fee}")

                    else:
                        logger.warning(f"No quotes returned for {business.business_name}")
                        business_quotes[business_id] = {
                            'business_name': business.business_name,
                            'error': 'No quotes available'
                        }

                else:
                    error_info = quote_response.get('error', {})
                    error_msg = error_info.get('message', 'Quote request failed')
                    logger.error(f"Quote failed for {business.business_name}: {error_msg}")
                    business_quotes[business_id] = {
                        'business_name': business.business_name,
                        'error': f'Quote failed: {error_msg}'
                    }

            # Check if we have any successful quotes
            successful_quotes = {k: v for k, v in business_quotes.items() if 'delivery_fee' in v}

            logger.info(f"Final results: {len(successful_quotes)} successful, {len(business_quotes) - len(successful_quotes)} failed")

            if not successful_quotes:
                logger.error("No successful quotes obtained")
                return JsonResponse({
                    'error': 'No delivery quotes available',
                    'business_quotes': business_quotes,
                    'debug': 'Check console for detailed logs'
                }, status=400)

            # Return successful response
            response_data = {
                'success': True,
                'total_delivery_fee': round(total_delivery_fee, 2),
                'business_quotes': business_quotes,
                'dropoff_address': dropoff_address
            }

            logger.info(f"Quote request successful. Total fee: ${total_delivery_fee}")
            return JsonResponse(response_data)

        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        except Exception as e:
            logger.error(f"Unexpected error in delivery quote: {str(e)}")
            logger.exception("Full exception details:")
            return JsonResponse({
                'error': 'Internal server error',
                'debug_info': str(e) if settings.DEBUG else None
            }, status=500)

    def get_business_postcode(self, business):
        """Get business postcode from postcode field or extract from address"""
        logger.info(f"Getting postcode for business: {business.business_name}")

        # Method 1: Check if business has a separate postcode field
        if hasattr(business, 'postcode') and business.postcode:
            postcode = str(business.postcode).strip()
            logger.info(f"Found postcode field: '{postcode}'")

            # Validate it's a 4-digit Australian postcode
            if postcode.isdigit() and len(postcode) == 4:
                logger.info(f"Valid postcode from field: {postcode}")
                return postcode
            else:
                logger.warning(f"Invalid postcode format: '{postcode}'")

        # Method 2: Try to extract from address field
        logger.info(f"Trying to extract from address: '{business.address}'")
        extracted = self.extract_postcode(business.address)
        if extracted:
            logger.info(f"Extracted from address: {extracted}")
            return extracted

        logger.warning(f"No valid postcode found for {business.business_name}")
        return None

    def extract_postcode(self, address):
        """Extract 4-digit Australian postcode from address string"""
        logger.info(f"Extracting postcode from: '{address}'")

        if not address:
            logger.warning("Address is empty")
            return None

        # Clean the address
        address = address.strip()

        # Method 1: Look for 4-digit number that could be a postcode
        postcode_pattern = r'\b(\d{4})\b'
        matches = re.findall(postcode_pattern, address)

        if matches:
            # Filter out common non-postcode 4-digit numbers
            valid_postcodes = []
            for match in matches:
                # Australian postcodes are typically 1000-9999
                if 1000 <= int(match) <= 9999:
                    valid_postcodes.append(match)

            if valid_postcodes:
                result = valid_postcodes[-1]  # Take the last one
                logger.info(f"Extracted postcode: {result}")
                return result

        # Method 2: Look for state + postcode pattern
        state_postcode_pattern = r'\b(?:NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\s+(\d{4})\b'
        matches = re.findall(state_postcode_pattern, address.upper())

        if matches:
            result = matches[-1]
            logger.info(f"Extracted state postcode: {result}")
            return result

        # Method 3: Look for common address formats
        # "Address, City State Postcode"
        end_pattern = r'(\d{4})\s*$'
        matches = re.findall(end_pattern, address)

        if matches:
            result = matches[-1]
            logger.info(f"Extracted end postcode: {result}")
            return result

        logger.warning(f"No postcode found in '{address}'")
        return None


@login_required
def test_shippit_directly(request):
    """Test Shippit API directly with hardcoded values"""

    print("\n" + "="*60)
    print("🧪 DIRECT SHIPPIT API TEST")
    print("="*60)

    try:
        # Initialize service
        shippit_service = ShippitService()
        print(f"✅ Shippit service initialized")
        print(f"   API Key: {shippit_service.api_key[:10]}..." if shippit_service.api_key else "❌ No API key")
        print(f"   Base URL: {shippit_service.base_url}")
        print(f"   Environment: {shippit_service.environment}")

        # Test with hardcoded postcodes
        pickup_postcode = "5000"  # Adelaide
        delivery_postcode = "5000"  # Same as pickup for testing

        package_details = {
            'weight': 1.0,  # 1kg
            'length': 20,
            'width': 15,
            'height': 10
        }

        print(f"\n📦 Test Parameters:")
        print(f"   Pickup postcode: {pickup_postcode}")
        print(f"   Delivery postcode: {delivery_postcode}")
        print(f"   Package: {package_details}")

        # Make the API call
        print(f"\n🌐 Making API call...")
        result = shippit_service.quote_delivery(
            pickup_postcode=pickup_postcode,
            delivery_postcode=delivery_postcode,
            package_details=package_details
        )

        print(f"\n📨 Raw API Response:")
        print(f"   Success: {result.get('success')}")
        print(f"   Full result: {result}")

        if result.get('success'):
            quotes = result.get('quotes', [])
            print(f"\n✅ SUCCESS! Found {len(quotes)} quotes")
            for i, quote in enumerate(quotes):
                print(f"   Quote {i+1}: ${quote.get('price', 'N/A')} via {quote.get('courier_name', 'Unknown')}")
        else:
            error = result.get('error', {})
            print(f"\n❌ FAILED!")
            print(f"   Error: {error}")

        return JsonResponse({
            'test': 'direct_shippit',
            'result': result,
            'debug': 'Check console for detailed output'
        })

    except Exception as e:
        print(f"\n💥 EXCEPTION: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

        return JsonResponse({
            'test': 'direct_shippit',
            'error': str(e),
            'debug': 'Check console for detailed output'
        })

# Replace your get_delivery_quote view with this heavily debugged version

import logging
import json
import traceback
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@login_required
@csrf_exempt
def get_delivery_quote(request):
    """Get delivery quote using Shippit"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        delivery_address = data.get('dropoff_address')

        if not delivery_address:
            return JsonResponse({'error': 'Dropoff address is required'}, status=400)

        # Extract postcode from address (simplified - in production use proper parsing)
        try:
            delivery_postcode = delivery_address.split(',')[-1].strip().split(' ')[-1]
            if not delivery_postcode.isdigit() or len(delivery_postcode) != 4:
                raise ValueError("Invalid postcode format")
        except:
            return JsonResponse({
                'error': 'Could not extract valid postcode from address',
                'suggestion': 'Please format address as "Street, City, State POSTCODE"'
            }, status=400)

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)

        # Group items by business
        business_quotes = {}
        total_delivery_fee = 0
        shippit = ShippitService()

        for business in Business.objects.filter(products__cart__user=request.user).distinct():
            business_items = cart_items.filter(product__business=business)
            if not business_items.exists():
                continue

            # Get pickup postcode from business address
            try:
                pickup_postcode = business.address.split(',')[-1].strip().split(' ')[-1]
                if not pickup_postcode.isdigit() or len(pickup_postcode) != 4:
                    raise ValueError("Business has invalid postcode format")
            except:
                logger.error(f"Business {business.id} has invalid address format for postcode extraction")
                continue

            # Calculate package weight/dimensions (simplified - should use real product data)
            package_weight = min(max(len(business_items) * 0.5, 1), 30)  # 0.5kg per item, min 1kg, max 30kg
            package_details = {
                'weight': package_weight,
                'length': 30,
                'width': 30,
                'height': 30
            }

            # Get quote
            quote_result = shippit.quote_delivery(
                pickup_postcode=pickup_postcode,
                delivery_postcode=delivery_postcode,
                package_details=package_details
            )

            if quote_result['success']:
                # Select the cheapest quote
                quotes = quote_result.get('quotes', [])
                if quotes:
                    cheapest_quote = min(quotes, key=lambda x: x['price']['amount'])
                    business_quotes[business.id] = {
                        'business_name': business.business_name,
                        'delivery_fee': cheapest_quote['price']['amount'],
                        'courier': cheapest_quote['courier']['name'],
                        'estimated_delivery_date': cheapest_quote['estimated_delivery_date'],
                        'pickup_postcode': pickup_postcode,
                        'delivery_postcode': delivery_postcode
                    }
                    total_delivery_fee += cheapest_quote['price']['amount']
                else:
                    business_quotes[business.id] = {
                        'error': 'No available couriers for this route'
                    }
            else:
                business_quotes[business.id] = {
                    'error': quote_result.get('error', {}).get('message', 'Failed to get quote')
                }

        if not business_quotes:
            return JsonResponse({'error': 'No valid businesses found for delivery'}, status=400)

        return JsonResponse({
            'success': True,
            'total_delivery_fee': total_delivery_fee,
            'business_quotes': business_quotes,
            'currency': 'AUD'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in get_delivery_quote: {str(e)}")
        return JsonResponse({
            'error': f'An unexpected error occurred: {str(e)}'
        }, status=500)

@login_required
def validate_address(request):
    """Validate address using Google Maps Geocoding API"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)

    address = request.GET.get('address')
    if not address:
        return JsonResponse({'error': 'Address parameter required'}, status=400)

    try:
        # Use Google Maps Geocoding API to validate address
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        if not api_key:
            return JsonResponse({'error': 'Address validation unavailable'}, status=503)

        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': api_key,
            'region': 'au'  # Bias results to Australia
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data['status'] == 'OK' and data['results']:
            result = data['results'][0]
            formatted_address = result['formatted_address']
            location = result['geometry']['location']

            return JsonResponse({
                'success': True,
                'formatted_address': formatted_address,
                'latitude': location['lat'],
                'longitude': location['lng']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Address not found or invalid'
            })

    except Exception as e:
        logger.error(f"Address validation error: {str(e)}")
        return JsonResponse({'error': f'Address validation failed: {str(e)}'}, status=500)

def create_delivery_from_quotes(order, tip_amount=0):
    """Create DoorDash deliveries for an order based on saved quotes"""
    if not DOORDASH_AVAILABLE or not DELIVERY_MODELS_AVAILABLE:
        logger.warning("Delivery service not available")
        return []

    try:
        # Get order items grouped by business
        cart_items = order.items.all()
        business_deliveries = {}

        for item in cart_items:
            business = item.product.business
            if business.id not in business_deliveries:
                business_deliveries[business.id] = {
                    'business': business,
                    'items': [],
                    'total_value': 0
                }
            business_deliveries[business.id]['items'].append(item)
            business_deliveries[business.id]['total_value'] += item.price * item.quantity

        doordash_service = DoorDashService()
        created_deliveries = []

        for business_id, delivery_info in business_deliveries.items():
            business = delivery_info['business']

            # Try to find recent quote for this business and user
            recent_quote = DeliveryQuote.objects.filter(
                user=order.user,
                pickup_address__icontains=business.address,
                is_accepted=False,
                created_at__gte=timezone.now() - timedelta(minutes=10)
            ).order_by('-created_at').first()

            if not recent_quote:
                logger.error(f"No recent quote found for business {business.business_name}")
                continue

            # Prepare pickup and dropoff details
            pickup_details = {
                'business_name': business.business_name,
                'phone': business.phone,
                'instructions': f"Order items: {', '.join([f'{item.quantity}x {item.product.name}' for item in delivery_info['items']])}",
                'order_value': int(delivery_info['total_value'] * 100)  # Convert to cents
            }

            dropoff_details = {
                'name': order.user.get_full_name(),
                'phone': getattr(order.user, 'phone', '+61400000000'),
                'instructions': order.note or 'Please deliver to door'
            }

            # Accept the quote and create delivery
            result = doordash_service.accept_delivery_quote(
                external_delivery_id=recent_quote.quote_id,
                pickup_details=pickup_details,
                dropoff_details=dropoff_details,
                tip=int(tip_amount * 100)  # Convert to cents
            )

            if result['success']:
                # Create delivery record
                delivery = Delivery.objects.create(
                    order=order,
                    delivery_quote=recent_quote,
                    external_delivery_id=recent_quote.quote_id,
                    doordash_delivery_id=result.get('delivery_id'),
                    delivery_status='created',
                    tracking_url=result.get('tracking_url'),
                    delivery_fee=recent_quote.delivery_fee,
                    tip_amount=tip_amount,
                    pickup_address=recent_quote.pickup_address,
                    dropoff_address=recent_quote.dropoff_address,
                    pickup_time_estimated=recent_quote.pickup_time_estimated,
                    dropoff_time_estimated=recent_quote.dropoff_time_estimated,
                    delivery_data=result['data']
                )

                # Mark quote as accepted
                recent_quote.is_accepted = True
                recent_quote.save()

                created_deliveries.append(delivery)
                logger.info(f"Delivery created for business {business.business_name}: {delivery.external_delivery_id}")
            else:
                logger.error(f"Failed to create delivery for business {business.business_name}: {result.get('error', 'Unknown error')}")

        return created_deliveries

    except Exception as e:
        logger.error(f"Error creating deliveries: {str(e)}")
        return []

@login_required
def delivery_tracking(request, delivery_id):
    """View delivery tracking information"""
    try:
        delivery = Delivery.objects.get(
            external_delivery_id=delivery_id,
            order__user=request.user
        )

        # Get latest status from DoorDash
        doordash_service = DoorDashService()
        status_result = doordash_service.get_delivery_status(delivery.external_delivery_id)

        if status_result['success']:
            # Update delivery status
            delivery_data = status_result['data']
            delivery.delivery_status = delivery_data.get('delivery_status', delivery.delivery_status)
            delivery.delivery_data = delivery_data
            delivery.save()

        context = {
            'delivery': delivery,
            'order': delivery.order,
            'tracking_url': delivery.tracking_url
        }

        return render(request, 'business/delivery_tracking.html', context)

    except Delivery.DoesNotExist:
        messages.error(request, "Delivery not found.")
        return redirect('user_orders')
    except Exception as e:
        logger.error(f"Delivery tracking error: {str(e)}")
        messages.error(request, "Error loading delivery information.")
        return redirect('user_orders')


from collections import defaultdict


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'business/checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
        })

    def post(self, request, *args, **kwargs):
        try:
            cart_items = Cart.objects.filter(user=request.user)

            if not cart_items.exists():
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            YOUR_DOMAIN = "https://dukani.pythonanywhere.com"

            # Parse request data
            try:
                request_data = json.loads(request.body)
                logger.info(f"🔍 Received checkout data: {request_data}")
            except json.JSONDecodeError:
                logger.error("❌ Invalid JSON in request body")
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)

            # Extract form data
            delivery_method = request_data.get('delivery_method', 'pickup')
            address = request_data.get('address', '')
            city = request_data.get('city', '')
            state = request_data.get('state', '')
            postal_code = request_data.get('postal_code', '')
            note = request_data.get('note', '')
            tip_amount = float(request_data.get('tip_amount', 0))
            delivery_fee = float(request_data.get('delivery_fee', 0))

            logger.info(f"💰 Delivery method: {delivery_method}")
            logger.info(f"💰 Delivery fee: ${delivery_fee}")
            logger.info(f"💰 Tip amount: ${tip_amount}")

            # Prepare line items for Stripe
            line_items = []

            # Add product items
            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'aud',
                        'product_data': {
                            'name': item.product.name,
                        },
                        'unit_amount': int(float(item.product.price) * 100),
                    },
                    'quantity': item.quantity,
                })

            # Add delivery fee if applicable
            if delivery_method == 'delivery' and delivery_fee > 0:
                logger.info(f"💰 Adding delivery fee line item: ${delivery_fee}")
                line_items.append({
                    'price_data': {
                        'currency': 'aud',
                        'product_data': {
                            'name': 'Delivery Fee',
                        },
                        'unit_amount': int(delivery_fee * 100),
                    },
                    'quantity': 1,
                })

            # Add tip if provided
            if tip_amount > 0:
                logger.info(f"💰 Adding tip line item: ${tip_amount}")
                line_items.append({
                    'price_data': {
                        'currency': 'aud',
                        'product_data': {
                            'name': 'Driver Tip',
                        },
                        'unit_amount': int(tip_amount * 100),
                    },
                    'quantity': 1,
                })

            logger.info(f"💰 Total line items: {len(line_items)}")
            for i, item in enumerate(line_items):
                logger.info(f"💰 Line item {i+1}: {item['price_data']['product_data']['name']} - ${item['price_data']['unit_amount']/100}")

            # Create a Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=YOUR_DOMAIN + '/success/',
                cancel_url=YOUR_DOMAIN + '/cancel/',
            )

            logger.info(f"✅ Created Stripe session: {checkout_session.id}")

            # Save necessary data to session for post-payment processing
            request.session['checkout_session_id'] = checkout_session.id
            request.session['delivery_method'] = delivery_method
            request.session['delivery_fee'] = delivery_fee
            request.session['tip_amount'] = tip_amount
            request.session['address'] = address
            request.session['city'] = city
            request.session['state'] = state
            request.session['postal_code'] = postal_code
            request.session['note'] = note

            # Store cart items for order creation
            request.session['cart_items'] = [
                {
                    'product_id': item.product.id,
                    'quantity': item.quantity,
                    'variations': [
                        {
                            'variation_name': cv.product_variation.variation.name,
                            'variation_value': cv.product_variation.value
                        }
                        for cv in item.variations.all()
                    ]
                }
                for item in cart_items
            ]

            # Store business items for transfers
            business_items = self.group_items_by_business(cart_items)
            request.session['business_items'] = {
                str(business.id): [
                    {
                        'amount': int(float(item.product.price) * 100 * item.quantity),
                        'business': business.stripe_account_id,
                        'product_id': item.product.id,
                        'quantity': item.quantity,
                        'variations': [
                            {
                                'variation_name': cv.product_variation.variation.name,
                                'variation_value': cv.product_variation.value
                            }
                            for cv in item.variations.all()
                        ]
                    }
                    for item in items
                ]
                for business, items in business_items.items()
            }

            return JsonResponse({'id': checkout_session.id})

        except Exception as e:
            logger.error(f"❌ Stripe checkout session creation error: {str(e)}")
            logger.exception("Full traceback:")
            return JsonResponse({'error': str(e)}, status=500)

    def group_items_by_business(self, cart_items):
        business_items = defaultdict(list)
        for item in cart_items:
            business_items[item.product.business].append(item)
        return business_items

    def create_shippit_deliveries(self, order, tip_amount=0):
        """Create Shippit deliveries for an order"""
        deliveries = []
        shippit = ShippitService()

        # Group order items by business
        business_items = defaultdict(list)
        for item in order.items.all():
            business_items[item.product.business].append(item)

        for business, items in business_items.items():
            try:
                # Prepare order data
                order_data = {
                    'order_reference': f"{order.ref_code}-{business.id}",
                    'customer': {
                        'name': order.user.get_full_name(),
                        'email': order.user.email,
                        'phone': getattr(order.user, 'phone', '+61400000000')
                    },
                    'delivery_address': {
                        'street': order.address,
                        'suburb': order.city,
                        'state': order.state,
                        'postcode': order.postal_code,
                        'country': 'AU'
                    },
                    'pickup_address': {
                        'name': business.business_name,
                        'street': business.address,
                        'suburb': business.city if hasattr(business, 'city') else '',
                        'state': business.states.first().name if business.states.exists() else '',
                        'postcode': business.address.split(',')[-1].strip().split(' ')[-1],
                        'country': 'AU',
                        'phone': business.phone
                    },
                    'packages': [{
                        'items': [{
                            'description': item.product.name,
                            'quantity': item.quantity,
                            'weight': 0.5  # Default 0.5kg per item
                        } for item in items],
                        'weight': len(items) * 0.5  # Total weight
                    }],
                    'delivery_instructions': order.note or '',
                    'courier': {
                        'allocation_preference': 'auto'
                    }
                }

                # Add tip if provided (Shippit supports tips through special instructions)
                if tip_amount > 0:
                    order_data['delivery_instructions'] += f"\nDriver tip: ${tip_amount:.2f}"

                # Create order in Shippit
                result = shippit.create_order(order_data)

                if result['success']:
                    delivery = Delivery.objects.create(
                        order=order,
                        external_delivery_id=result['tracking_number'],
                        delivery_status='created',
                        tracking_url=result['tracking_url'],
                        delivery_fee=next((q['delivery_fee'] for q in business_quotes.values()
                                         if q.get('business_id') == business.id), 0),
                        tip_amount=tip_amount,
                        pickup_address=business.address,
                        dropoff_address=f"{order.address}, {order.city}, {order.state} {order.postal_code}",
                        delivery_data=result['data']
                    )
                    deliveries.append(delivery)
                else:
                    logger.error(f"Failed to create Shippit delivery for business {business.id}: {result.get('error')}")

            except Exception as e:
                logger.error(f"Error creating Shippit delivery for business {business.id}: {str(e)}")

        return deliveries

# Update PaymentSuccessView to handle delivery creation
class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        checkout_session_id = request.session.get('checkout_session_id')
        business_items = request.session.get('business_items')
        cart_items = request.session.get('cart_items')
        delivery_method = request.session.get('delivery_method', 'pickup')
        delivery_fee = request.session.get('delivery_fee', 0)
        tip_amount = request.session.get('tip_amount', 0)
        address = request.session.get('address')
        city = request.session.get('city')
        state = request.session.get('state')
        postal_code = request.session.get('postal_code')
        note = request.session.get('note')

        if not checkout_session_id or not business_items or not cart_items:
            return JsonResponse({'error': 'Session data not found'}, status=400)

        try:
            # Retrieve the checkout session
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            payment_intent_id = session.payment_intent

            # Create transfers for each business (85% of product value, excluding delivery fees)
            for business_id, items in business_items.items():
                total_amount = sum(item['amount'] for item in items)
                stripe.Transfer.create(
                    amount=int(total_amount * 0.85),  # 85% of the total amount (excluding delivery)
                    currency='aud',
                    destination=items[0]['business'],
                    transfer_group=payment_intent_id,
                )

            # Generate a unique reference code
            characters = string.ascii_letters + string.digits
            ref_code = ''.join(random.choice(characters) for _ in range(10))

            # Calculate total price including delivery and tip
            product_total = sum(item['quantity'] * Product.objects.get(id=item['product_id']).price for item in cart_items)
            total_with_delivery = product_total + delivery_fee + tip_amount

            # Create order
            order = Order.objects.create(
                user=request.user,
                ref_code=ref_code,
                total_amount=product_total,
                delivery_method=delivery_method,
                delivery_fee=delivery_fee,
                tip_amount=tip_amount,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                note=note
            )

            # Create order items
            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                variations = {
                    v['variation_name']: v['variation_value']
                    for v in item['variations']
                }
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price,
                    variations=variations
                )

            # Create DoorDash deliveries if delivery method is selected
            if delivery_method == 'delivery':
                try:
                    deliveries = create_delivery_from_quotes(order, tip_amount)
                    if deliveries:
                        logger.info(f"Created {len(deliveries)} deliveries for order {order.ref_code}")
                        # Send delivery confirmation emails
                        self.send_delivery_emails(order, deliveries)
                    else:
                        logger.warning(f"No deliveries created for order {order.ref_code}")
                        messages.warning(request, "Order created but delivery setup encountered issues. We'll contact you shortly.")
                except Exception as e:
                    logger.error(f"Delivery creation failed for order {order.ref_code}: {str(e)}")
                    messages.warning(request, "Order created but delivery setup encountered issues. We'll contact you shortly.")

            # Clear the cart
            Cart.objects.filter(user=request.user).delete()

            # Send order emails to businesses
            self.send_order_emails(order, business_items)

            # Clear the session data
            session_keys = [
                'checkout_session_id', 'business_items', 'cart_items',
                'delivery_method', 'delivery_fee', 'tip_amount',
                'address', 'city', 'state', 'postal_code', 'note'
            ]
            for key in session_keys:
                if key in request.session:
                    del request.session[key]

            return render(request, 'business/success.html', {
                'order': order,
                'delivery_method': delivery_method,
                'total_with_delivery': total_with_delivery
            })
        except Exception as e:
            logger.error(f"Payment success processing error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    def send_order_emails(self, order, business_items):
        """Send order confirmation emails to businesses"""
        for business_id, items in business_items.items():
            business = Business.objects.get(id=business_id)
            business_total = sum(item['amount'] for item in items) / 100  # Convert cents to dollars

            item_details = []
            for item in items:
                variations_str = ', '.join([f'{v["variation_name"]}: {v["variation_value"]}' for v in item["variations"]])
                item_detail = (
                    f"{item['quantity']} x {Product.objects.get(id=item['product_id']).name} "
                    f"({variations_str}) - "
                    f"${item['amount'] / 100}"
                )
                item_details.append(item_detail)

            email_subject = f"New Order Received - {order.ref_code}"

            # Include delivery information in email
            delivery_info = ""
            if order.delivery_method == 'delivery':
                delivery_info = f"""
                <p><strong>Delivery Required:</strong> Yes</p>
                <p><strong>Delivery Address:</strong> {order.address}, {order.city}, {order.state} {order.postal_code}</p>
                <p><strong>Delivery Fee:</strong> ${order.delivery_fee}</p>
                """
            else:
                delivery_info = "<p><strong>Delivery Required:</strong> No (Customer Pickup)</p>"

            email_body = render_to_string('business/new_order.html', {
                'business': business,
                'order': order,
                'business_total': business_total,
                'item_details': item_details,
                'delivery_info': delivery_info
            })

            email = EmailMultiAlternatives(
                subject=email_subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[business.email],
            )
            email.attach_alternative(email_body, "text/html")
            email.send(fail_silently=False)

    def send_delivery_emails(self, order, deliveries):
        """Send delivery information to customer and businesses"""
        # Email to customer
        tracking_links = [delivery.tracking_url for delivery in deliveries if delivery.tracking_url]

        customer_email_body = render_to_string('business/delivery_confirmation.html', {
            'order': order,
            'deliveries': deliveries,
            'tracking_links': tracking_links
        })

        customer_email = EmailMultiAlternatives(
            subject=f"Delivery Confirmation - Order {order.ref_code}",
            body=customer_email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email],
        )
        customer_email.attach_alternative(customer_email_body, "text/html")
        customer_email.send(fail_silently=False)



class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        checkout_session_id = request.session.get('checkout_session_id')
        business_items = request.session.get('business_items')
        cart_items = request.session.get('cart_items')
        address = request.session.get('address')
        city = request.session.get('city')
        state = request.session.get('state')
        postal_code = request.session.get('postal_code')
        note = request.session.get('note')

        if not checkout_session_id or not business_items or not cart_items:
            return JsonResponse({'error': 'Session data not found'}, status=400)

        try:
            # Retrieve the checkout session
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            payment_intent_id = session.payment_intent

            # Create transfers for each business
            for business_id, items in business_items.items():
                total_amount = sum(item['amount'] for item in items)
                stripe.Transfer.create(
                    amount=int(total_amount * 0.85),  # 85% of the total amount
                    currency='aud',
                    destination=items[0]['business'],
                    transfer_group=payment_intent_id,
                )

            # Generate a unique reference code with strings and digits
            characters = string.ascii_letters + string.digits
            ref_code = ''.join(random.choice(characters) for _ in range(10))

            total_price = sum(item['quantity'] * Product.objects.get(id=item['product_id']).price for item in cart_items)
            order = Order.objects.create(
                user=request.user,
                ref_code=ref_code,
                total_amount=total_price,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                note=note
            )

            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                variations = {
                    v['variation_name']: v['variation_value']
                    for v in item['variations']
                }
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price,
                    variations=variations
                )

            # Clear the cart
            Cart.objects.filter(user=request.user).delete()

            # Send email to businesses
            self.send_order_emails(order, business_items)

            # Clear the session data
            del request.session['checkout_session_id']
            del request.session['business_items']
            del request.session['cart_items']
            del request.session['address']
            del request.session['city']
            del request.session['state']
            del request.session['postal_code']
            del request.session['note']

            return render(request, 'business/success.html')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def send_order_emails(self, order, business_items):
        for business_id, items in business_items.items():
            business = Business.objects.get(id=business_id)
            business_total = sum(item['amount'] for item in items) / 100  # Convert cents to dollars

            item_details = []
            for item in items:
                # Build the variations string for each item
                variations_str = ', '.join([f'{v["variation_name"]}: {v["variation_value"]}' for v in item["variations"]])
                item_detail = (
                    f"{item['quantity']} x {Product.objects.get(id=item['product_id']).name} "
                    f"({variations_str}) - "
                    f"${item['amount'] / 100}"  # Convert cents to dollars
                )
                item_details.append(item_detail)

            email_subject = f"New Order Received - {order.ref_code}"
            email_body = render_to_string('business/new_order.html', {
                'business': business,
                'order': order,
                'business_total': business_total,
                'item_details': item_details
            })

            # Send email using EmailMultiAlternatives to include the HTML message
            email = EmailMultiAlternatives(
                subject=email_subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[business.email],
            )
            email.attach_alternative(email_body, "text/html")
            email.send(fail_silently=False)


class UserOrdersView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'business/user_orders.html', {'orders': orders})



class RequestRefundView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return render(request, 'business/request_refund.html', {'order': order})

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.refund_requested:
            return redirect('user_orders')

        email = request.POST.get('email')
        reason = request.POST.get('reason')

        refund = Refund.objects.create(
            order=order,
            reason=reason,
            email=email
        )

        order.refund_requested = True
        order.save()

        # Get unique business emails associated with this order
        business_emails = OrderItem.objects.filter(order=order).select_related('product__business').values_list('product__business__email', flat=True).distinct()

        # Send email to each business
        for business_email in business_emails:
            # Get items for this specific business in this order
            business_items = OrderItem.objects.filter(
                order=order,
                product__business__email=business_email
            ).select_related('product')

            items_details = "\n".join([
                f"- {item.quantity} x {item.product.name} - ${item.price}"
                for item in business_items
            ])

            message = f"""
A refund has been requested for Order #{order.ref_code}.

Items from your business in this order:
{items_details}

Reason: {reason}

Customer Email: {email}
            """

            send_mail(
                f'Refund Request for Order #{order.ref_code}',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [business_email],
                fail_silently=False,
            )

        return redirect('user_orders')


@login_required
def message_seller(request, business_slug):
    business = get_object_or_404(Business, business_slug=business_slug)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=business.seller,
                business=business,
                content=content
            )
            return redirect('message_seller', business_slug=business.business_slug)

    # Mark messages as read for the current user and business
    Message.objects.filter(recipient=request.user, business=business).update(is_read=True)

    messages = Message.objects.filter(
        Q(sender=request.user, recipient=business.seller) |
        Q(sender=business.seller, recipient=request.user)
    ).filter(business=business).order_by('timestamp')

    individual_business_message_counter = Message.objects.filter(recipient=request.user, business=business, is_read=False).count()
    context = {
        'business': business,
        'messages': messages,
        'individual_business_message_counter': individual_business_message_counter,
    }
    return render(request, 'business/message.html', context)


@login_required
def message_buyer(request, username):
    user = get_object_or_404(CustomUser, username=username)
    business = Business.objects.filter(seller=request.user).first()

    if not business:
        return redirect('user_messages')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=user,
                business=business,
                content=content
            )
            return redirect('message_buyer', username=user.username)

    # Mark messages as read for the current user and buyer
    Message.objects.filter(recipient=request.user, sender=user).update(is_read=True)

    messages = Message.objects.filter(
        Q(sender=request.user, recipient=user) |
        Q(sender=user, recipient=request.user)
    ).filter(business=business).order_by('timestamp')

    context = {
        'user': user,
        'messages': messages,
    }
    return render(request, 'business/message_buyer.html', context)

@login_required
def user_messages_view(request):
    businesses = Business.objects.filter(
        Q(messages__sender=request.user) | Q(messages__recipient=request.user)
    ).distinct()

    user_messages = []
    latest_messages = []

    for business in businesses:
        if request.user == business.seller:
            # Query messages for business with other users
            messages = Message.objects.filter(
                Q(sender=business.seller) | Q(recipient=business.seller)
            ).filter(business=business).order_by('-timestamp')
            for user, chat in itertools.groupby(messages, lambda m: m.recipient if m.sender == request.user else m.sender):
                last_message = next(chat)
                unread_count = Message.objects.filter(recipient=business.seller, sender=user, business=business, is_read=False).count()
                user_messages.append({
                    'business': business,
                    'last_message': last_message,
                    'user': user,
                    'unread_count': unread_count,
                })
                latest_messages.append(last_message)
        else:
            last_message = Message.objects.filter(
                Q(sender=request.user, recipient=business.seller) |
                Q(sender=business.seller, recipient=request.user)
            ).filter(business=business).order_by('-timestamp').first()
            unread_count = Message.objects.filter(recipient=request.user, sender=business.seller, is_read=False).count()
            user_messages.append({
                'business': business,
                'last_message': last_message,
                'unread_count': unread_count,
            })
            latest_messages.append(last_message)

    # Sort user_messages by the latest message timestamp
    user_messages = sorted(user_messages, key=lambda um: um['last_message'].timestamp, reverse=True)

    unread_message_counter = sum(msg['unread_count'] for msg in user_messages)

    if request.method == 'POST':
        business_slug = request.POST.get('business_slug')
        business = get_object_or_404(Business, business_slug=business_slug)
        content = request.POST.get('content')
        if content:
            if request.user == business.seller:
                # Business sending message to user
                username = request.POST.get('username')
                if username:
                    recipient = get_object_or_404(CustomUser, username=username)
                    Message.objects.create(
                        sender=request.user,
                        recipient=recipient,
                        business=business,
                        content=content
                    )
                    return redirect(f'{request.path}?business_slug={business.business_slug}&username={recipient.username}')
            else:
                # User sending message to business
                Message.objects.create(
                    sender=request.user,
                    recipient=business.seller,
                    business=business,
                    content=content
                )
                return redirect(f'{request.path}?business_slug={business.business_slug}')

    selected_business = None
    selected_user = None
    messages = []
    if 'business_slug' in request.GET:
        business_slug = request.GET.get('business_slug')
        selected_business = get_object_or_404(Business, business_slug=business_slug)
        if request.user == selected_business.seller and 'username' in request.GET:
            # Query messages for selected_business with selected_user
            username = request.GET.get('username')
            if username:
                selected_user = get_object_or_404(CustomUser, username=username)
                messages = Message.objects.filter(
                    Q(sender=selected_user, recipient=selected_business.seller) |
                    Q(sender=selected_business.seller, recipient=selected_user)
                ).filter(business=selected_business).order_by('timestamp')
        else:
            messages = Message.objects.filter(
                Q(sender=request.user, recipient=selected_business.seller) |
                Q(sender=selected_business.seller, recipient=request.user)
            ).filter(business=selected_business).order_by('timestamp')

        Message.objects.filter(recipient=request.user, business=selected_business).update(is_read=True)

    context = {
        'user_messages': user_messages,
        'selected_business': selected_business,
        'selected_user': selected_user,
        'messages': messages,
        'unread_message_counter': unread_message_counter,
    }
    return render(request, 'business/user_messages.html', context)


from django.utils import timezone

def events(request):
    events = Event.objects.all().select_related('organizer', 'country', 'state')

    # Date filters
    date_filter = request.GET.get('date_filter')
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            events = events.filter(start_time__date=today)
        elif date_filter == 'next_week':
            next_week = today + timezone.timedelta(days=7)
            events = events.filter(start_time__date__range=[today, next_week])
        elif date_filter == 'next_month':
            next_month = today + timezone.timedelta(days=30)
            events = events.filter(start_time__date__range=[today, next_month])

    # Top events filter
    if request.GET.get('top_events'):
        events = events.filter(top_event=True)

    # Event type filter
    event_type = request.GET.get('event_type')
    if event_type:
        events = events.filter(event_type=event_type)

    # Location filters
    country_filter = request.GET.getlist('country')
    state_filter = request.GET.getlist('state')

    if country_filter:
        events = events.filter(country__in=country_filter)
    if state_filter:
        events = events.filter(state__in=state_filter)

    # Get filter options for template
    countries = Country.objects.all()
    states = State.objects.all()
    event_types = Event.EVENT_TYPE_CHOICES

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        events_data = [{
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'event_type': event.get_event_type_display(),
            'country': event.country.name,
            'state': event.state.name,
            'start_time': event.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'location': event.location,
            'banner_image': event.banner_image.url if event.banner_image else None,
            'organizer_name': event.organizer.get_full_name(),
            'is_saved': event.saved_by.filter(user=request.user).exists() if request.user.is_authenticated else False,
        } for event in events]
        return JsonResponse({'events': events_data})

    context = {
        'events': events,
        'countries': countries,
        'states': states,
        'event_types': event_types,
        'selected_countries': country_filter,
        'selected_states': state_filter,
        'selected_event_type': event_type,
        'selected_date_filter': date_filter,
        'show_top_events': request.GET.get('top_events') == 'true',
    }
    return render(request, 'business/events.html', context)

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    is_organizer = request.user == event.organizer

    # Use the correct related_name to access the reverse relationship
    is_saved = event.saved_by.filter(user=request.user).exists()

    # Debugging print statements
    print(f"Event ID: {event_id}")
    print(f"User: {request.user.username}")
    print(f"Is Organizer: {is_organizer}")
    print(f"Is Saved: {is_saved}")

    context = {
        'event': event,
        'is_organizer': is_organizer,
        'is_saved': is_saved,
        'events': Event.objects.all()  # Assuming you want to show all events in the "Other Events" section
    }

    return render(request, 'business/event_detail.html', context)


@login_required
def save_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    saved_event, created = SavedEvent.objects.get_or_create(user=request.user, event=event)

    if created:
        messages.success(request, 'Event saved successfully.')
        return JsonResponse({'status': 'saved'})
    else:
        saved_event.delete()
        messages.success(request, 'Event removed successfully.')
        return JsonResponse({'status': 'removed'})

@login_required
def saved_events(request):
    saved_events = request.user.saved_events.select_related('event')
    context = {
        'saved_events': saved_events,
    }
    return render(request, 'business/saved_events.html', context)

@login_required
def remove_saved_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    saved_event = get_object_or_404(SavedEvent, user=request.user, event=event)
    saved_event.delete()
    return JsonResponse({'status': 'removed'}, status=200)


@login_required
def create_event(request):
    countries = Country.objects.all()
    states = State.objects.all()
    event_types = Event.EVENT_TYPE_CHOICES

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_type = request.POST.get('event_type')
        country_id = request.POST.get('country')
        state_id = request.POST.get('state')
        start_time = request.POST.get('start_time')
        location = request.POST.get('location')
        banner_image = request.FILES.get('banner_image')
        top_event = request.POST.get('top_event') == 'on' and request.user.is_staff

        if all([title, description, event_type, country_id, state_id, start_time, location, banner_image]):
            try:
                country = Country.objects.get(id=country_id)
                state = State.objects.get(id=state_id)

                event = Event.objects.create(
                    organizer=request.user,
                    title=title,
                    description=description,
                    event_type=event_type,
                    country=country,
                    state=state,
                    start_time=start_time,
                    location=location,
                    banner_image=banner_image,
                    top_event=top_event
                )
                messages.success(request, 'Event created successfully!')
                return redirect('event_detail', event.id)
            except (Country.DoesNotExist, State.DoesNotExist):
                messages.error(request, 'Invalid country or state selected.')
            except Exception as e:
                messages.error(request, f'Error creating event: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')

    context = {
        'countries': countries,
        'states': states,
        'event_types': event_types,
        'is_staff': request.user.is_staff,
    }
    return render(request, 'business/create_event.html', context)

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if the user is the organizer of the event
    if request.user != event.organizer:
        messages.error(request, "You don't have permission to edit this event.")
        return redirect('event_detail', event_id=event.id)

    countries = Country.objects.all()
    states = State.objects.all()

    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_type = request.POST.get('event_type')
        country_id = request.POST.get('country')
        state_id = request.POST.get('state')
        start_time = request.POST.get('start_time')
        location = request.POST.get('location')
        banner_image = request.FILES.get('banner_image')
        top_event = request.POST.get('top_event') == 'on'

        if title and description and event_type and country_id and state_id and start_time and location:
            # Update event fields
            event.title = title
            event.description = description
            event.event_type = event_type
            event.country_id = country_id
            event.state_id = state_id
            event.start_time = start_time
            event.location = location

            # Only update banner_image if a new one was uploaded
            if banner_image:
                event.banner_image = banner_image

            # Only staff can set top_event status
            if request.user.is_staff:
                event.top_event = top_event

            event.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', event_id=event.id)
        else:
            messages.error(request, 'Please fill in all required fields.')

    context = {
        'event': event,
        'countries': countries,
        'states': states,
    }
    return render(request, 'business/edit_event.html', context)

def products(request):
    products = Product.objects.all()

    # Category filter
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)

    # Country and State filters
    selected_countries = request.GET.getlist('country')
    selected_states = request.GET.getlist('state')

    if selected_countries:
        products = products.filter(business__countries__id__in=selected_countries).distinct()
    if selected_states:
        products = products.filter(business__states__id__in=selected_states).distinct()

    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_high_low':
        products = products.order_by('-price')
    elif sort == 'price_low_high':
        products = products.order_by('price')
    elif sort == 'best_selling':
        products = products.filter(is_best_seller=True)
    elif sort == 'popular':
        products = products.filter(is_popular=True)
    elif sort == 'trending':
        products = products.filter(trending=True)
    elif sort == 'new_releases':
        products = products.filter(new_releases=True)

    # Pagination
    paginator = Paginator(products, 9)  # Show 9 products per page
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # Get all categories for the filter
    categories = Product.Category.choices

    # Get countries and states with their product counts
    countries = Country.objects.annotate(
        product_count=Count('business__products', distinct=True)
    )
    states = State.objects.annotate(
        product_count=Count('business__products', distinct=True)
    )

    context = {
        "products": products,
        "categories": categories,
        "countries": countries,
        "states": states,
        "selected_countries": selected_countries,
        "selected_states": selected_states,
    }

    return render(request, "business/products.html", context)


def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query)
    services = Service.objects.filter(name__icontains=query)
    businesses = Business.objects.filter(business_name__icontains=query)

    context = {
        'query': query,
        'products': products,
        'services': services,
        'businesses': businesses,
    }
    return render(request, 'business/search.html', context)

@login_required
def quick_shop_view(request, product_slug):
    # Get the product based on the slug
    product = get_object_or_404(Product, product_slug=product_slug)

    # Check if the product has variations
    if product.has_variations:
        # Redirect to the product detail page
        product_detail_url = reverse('product_detail', args=[product.business.business_slug, product.product_slug])
        messages.info(request, f"Please select your variations.")
        return redirect(product_detail_url)
    else:
        # Get the current user
        user = request.user

        # Create a new cart item
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': 1, 'variation_key': None}
        )

        # If the cart item already exists, increment the quantity
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        # Display a success message
        messages.success(request, f"{product.name} has been added to your cart.")

        # Redirect to the checkout page
        return redirect('checkout')


@login_required
def delete_cart_item(request, cart_item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        cart_item.delete()
        messages.success(request, "Item successfully removed from the cart.")
    return redirect('cart')  # Replace 'cart' with your cart URL name

# Add this test view to your business/views.py for debugging

@login_required
def test_doordash_credentials(request):
    """Test view to check DoorDash credentials and service"""

    response_data = {
        'timestamp': timezone.now().isoformat(),
        'user': str(request.user),
        'tests': {}
    }

    # Test 1: Check if settings are configured
    response_data['tests']['settings'] = {
        'DOORDASH_DEVELOPER_ID': bool(getattr(settings, 'DOORDASH_DEVELOPER_ID', None)),
        'DOORDASH_KEY_ID': bool(getattr(settings, 'DOORDASH_KEY_ID', None)),
        'DOORDASH_SIGNING_SECRET': bool(getattr(settings, 'DOORDASH_SIGNING_SECRET', None)),
        'DOORDASH_BASE_URL': getattr(settings, 'DOORDASH_BASE_URL', 'Not set'),
    }

    # Test 2: Try to import DoorDash service
    try:
        from business.services.doordash_service import DoorDashService
        response_data['tests']['service_import'] = {'success': True}

        # Test 3: Try to initialize service
        try:
            service = DoorDashService()
            response_data['tests']['service_init'] = {'success': True}

            # Test 4: Try to generate JWT
            try:
                headers = service.get_headers()
                response_data['tests']['jwt_generation'] = {
                    'success': True,
                    'has_authorization': 'Authorization' in headers,
                    'headers_count': len(headers)
                }

                # Test 5: Try a simple API call to test authentication
                try:
                    # Use a minimal quote request to test auth
                    test_result = service.get_delivery_quote(
                        pickup_address="123 Test St, Adelaide SA 5000",
                        dropoff_address="456 Test Ave, Adelaide SA 5001",
                        order_value=1000  # $10 test order
                    )
                    response_data['tests']['api_call'] = {
                        'success': test_result['success'],
                        'error': test_result.get('error', None),
                        'status_code': test_result.get('status_code', None)
                    }
                except Exception as api_error:
                    response_data['tests']['api_call'] = {
                        'success': False,
                        'error': str(api_error),
                        'error_type': type(api_error).__name__
                    }

            except Exception as jwt_error:
                response_data['tests']['jwt_generation'] = {
                    'success': False,
                    'error': str(jwt_error),
                    'error_type': type(jwt_error).__name__
                }

        except Exception as init_error:
            response_data['tests']['service_init'] = {
                'success': False,
                'error': str(init_error),
                'error_type': type(init_error).__name__
            }

    except ImportError as import_error:
        response_data['tests']['service_import'] = {
            'success': False,
            'error': str(import_error)
        }

    # Test 6: Check if models are available
    try:
        from business.models import DeliveryQuote, Delivery
        response_data['tests']['models'] = {'success': True}
    except ImportError as model_error:
        response_data['tests']['models'] = {
            'success': False,
            'error': str(model_error)
        }

    # Test 7: Check cart status
    try:
        cart_items = Cart.objects.filter(user=request.user)
        cart_data = []
        for item in cart_items:
            cart_data.append({
                'product': item.product.name,
                'business': item.product.business.business_name,
                'business_address': item.product.business.address,
                'quantity': item.quantity,
                'price': float(item.product.price)
            })

        response_data['tests']['cart'] = {
            'success': True,
            'item_count': cart_items.count(),
            'items': cart_data
        }
    except Exception as cart_error:
        response_data['tests']['cart'] = {
            'success': False,
            'error': str(cart_error)
        }

    return JsonResponse(response_data, json_dumps_params={'indent': 2})