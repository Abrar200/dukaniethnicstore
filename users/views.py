from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from users.models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
import logging
import smtplib
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.views import View
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives

# Initialize the logger
logger = logging.getLogger(__name__)

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


def send_verification_email(user, request):
    """
    Send email verification email to user
    """
    # Generate verification token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Build verification URL
    verification_url = request.build_absolute_uri(
        reverse('email_verification', kwargs={'uidb64': uid, 'token': token})
    )

    # Email subject and content
    subject = 'Verify Your Email Address - Dukani'

    # Create plain text email content
    email_content = f"""
Hi {user.first_name or user.username},

Thank you for registering with Dukani!

Please click the link below to verify your email address and activate your account:
{verification_url}

If you didn't create this account, please ignore this email.

Best regards,
The Dukani Team
    """

    # Create HTML email content
    html_content = render_to_string('users/verification_email.html', {
        'user': user,
        'verification_url': verification_url,
    })

    try:
        # Send the email using EmailMultiAlternatives for both plain text and HTML
        email = EmailMultiAlternatives(
            subject=subject,
            body=email_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Error sending verification email to {user.email}: {str(e)}")
        return False


def user_register_view(request):
    # Initialize form data to preserve user input
    form_data = {
        'first_name': '',
        'last_name': '',
        'username': '',
        'email': '',
    }

    if request.method == 'POST':
        # Collect form data
        form_data['first_name'] = request.POST.get('first_name', '').strip()
        form_data['last_name'] = request.POST.get('last_name', '').strip()
        form_data['username'] = request.POST.get('username', '').strip()
        form_data['email'] = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        terms_accepted = request.POST.get('terms_accepted')

        # Validation flags
        has_errors = False

        # Basic field validation
        if not form_data['first_name']:
            messages.error(request, 'First name is required.')
            has_errors = True

        if not form_data['last_name']:
            messages.error(request, 'Last name is required.')
            has_errors = True

        if not form_data['username']:
            messages.error(request, 'Username is required.')
            has_errors = True

        if not form_data['email']:
            messages.error(request, 'Email is required.')
            has_errors = True

        if not password:
            messages.error(request, 'Password is required.')
            has_errors = True

        if not confirm_password:
            messages.error(request, 'Password confirmation is required.')
            has_errors = True

        if not terms_accepted:
            messages.error(request, 'You must agree to the Terms and Conditions.')
            has_errors = True

        # Password match validation
        if password and confirm_password and password != confirm_password:
            messages.error(request, 'Passwords do not match. Please try again.')
            has_errors = True

        # Password strength validation
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, f"Password error: {error}")
                has_errors = True

        # Username validation
        if form_data['username']:
            username_validator = RegexValidator(
                regex=r'^[a-zA-Z0-9_.]+$',
                message="Username can only contain letters, numbers, underscores, and periods."
            )

            try:
                username_validator(form_data['username'])
            except ValidationError as e:
                messages.error(request, f"Username error: {e.message}")
                has_errors = True

            # Check if username already exists
            if CustomUser.objects.filter(username=form_data['username']).exists():
                messages.error(request, 'This username is already taken. Please choose a different one.')
                has_errors = True

        # Email validation
        if form_data['email']:
            # Check if email already exists
            if CustomUser.objects.filter(email=form_data['email']).exists():
                messages.error(request, 'An account with this email already exists. Please use a different email or try logging in.')
                has_errors = True

        # If there are validation errors, return the form with preserved data
        if has_errors:
            return render(request, 'users/user_registration.html', {'form_data': form_data})

        # All validations passed - create the user
        try:
            # Create user with inactive account
            user = CustomUser.objects.create_user(
                username=form_data['username'],
                first_name=form_data['first_name'],
                last_name=form_data['last_name'],
                email=form_data['email'],
                password=password
            )
            user.is_active = False  # Set inactive until email is verified
            user.email_verified = False  # Email not verified yet
            user.save()

            # Send verification email
            if send_verification_email(user, request):
                messages.success(request,
                    f'Registration successful! We\'ve sent a verification email to {form_data["email"]}. '
                    'Please check your email (including spam folder) and click the verification link to activate your account.')
            else:
                messages.warning(request,
                    'Account created successfully, but there was an issue sending the verification email. '
                    'Please contact support for assistance.')

            # Clear form data on success
            form_data = {
                'first_name': '',
                'last_name': '',
                'username': '',
                'email': '',
            }

            return redirect('login')

        except Exception as e:
            logger.error(f"Error creating user account: {str(e)}")
            messages.error(request, 'An unexpected error occurred while creating your account. Please try again.')
            return render(request, 'users/user_registration.html', {'form_data': form_data})

    # GET request - show empty form
    return render(request, 'users/user_registration.html', {'form_data': form_data})


def user_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if email is verified
            if not user.email_verified:
                messages.error(request, 'Please verify your email address before logging in. Check your email for the verification link.')
                return render(request, 'users/user_login.html')

            # Check if account is active
            if not user.is_active:
                messages.error(request, 'Your account is not active. Please contact support.')
                return render(request, 'users/user_login.html')

            # Login successful
            login(request, user)
            messages.success(request, 'Login successful.')

            # Redirect to appropriate page based on user type
            if user.is_seller and hasattr(user, 'business'):
                return redirect('business_detail', business_slug=user.business.business_slug)
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/user_login.html')


class EmailVerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            # Verify the email
            user.verify_email()

            if user.is_seller:
                messages.success(request, 'Your email has been verified successfully! Your business account is now active. You can now log in.')
            else:
                messages.success(request, 'Your email has been verified successfully! You can now log in.')

            return redirect('login')
        else:
            messages.error(request, 'The verification link is invalid or has expired. Please request a new verification email.')
            return redirect('resend_verification')


def resend_verification_view(request):
    """Allow users to request a new verification email"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.email_verified:
                messages.info(request, 'Your email is already verified. You can log in.')
                return redirect('login')

            if send_verification_email(user, request):
                messages.success(request, 'A new verification email has been sent to your email address.')
            else:
                messages.error(request, 'There was an error sending the verification email. Please try again.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with this email address.')

    return render(request, 'users/resend_verification.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful.')
    return redirect('login')


@login_required
def profile(request, username):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')

        # Update the user's information
        user = request.user

        # If email is being changed, require re-verification
        if user.email != email:
            user.email_verified = False
            user.is_active = False
            send_verification_email(user, request)
            messages.warning(request, 'Email changed. Please check your new email address for verification before your next login.')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        user.save()

        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('profile', username=user.username)

    # Retrieve the user's current information
    user = request.user
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'username': user.username,
    }

    return render(request, 'users/profile.html', context)


def password_reset_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                subject = "Password Reset Requested"
                email_template_name = "users/password_reset_email.html"
                c = {
                    "email": user.email,
                    "domain": request.get_host(),
                    "site_name": "Dukani",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    "token": default_token_generator.make_token(user),
                    "protocol": 'https' if request.is_secure() else 'http',
                }
                email_content = render_to_string(email_template_name, c)

                logger.debug(f"Sending password reset email to {user.email}")

                send_mail(
                    subject,
                    email_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
                logger.debug("Password reset email sent successfully")
                return redirect('password_reset_done')

            except CustomUser.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
                logger.error("No account found with this email address")
                return redirect('reset_password')

    return render(request, 'users/password_reset.html')


def password_reset_done_view(request):
    return render(request, 'users/password_reset_done.html')


def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            if new_password1 == new_password2:
                try:
                    validate_password(new_password1)
                    user.set_password(new_password1)
                    user.save()
                    messages.success(request, 'Password has been reset successfully.')
                    return redirect('password_reset_complete')
                except ValidationError as e:
                    messages.error(request, str(e))
            else:
                messages.error(request, 'Passwords do not match.')
        return render(request, 'users/password_reset_confirm.html')
    else:
        messages.error(request, 'The reset link is no longer valid.')
        return redirect('reset_password')


def password_reset_complete_view(request):
    return render(request, 'users/password_reset_complete.html')