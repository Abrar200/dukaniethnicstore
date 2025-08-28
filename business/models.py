from django.db import models
from users.models import CustomUser
from django.utils.text import slugify
from django.core.serializers import serialize
import json
from django.utils import timezone
from django.db.models import Avg, Count
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

class Country(models.Model):
    name = models.CharField(max_length=300)
    image = models.ImageField(upload_to="country_images/")
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3)

    def __str__(self):
        return self.name



class Business(models.Model):
    BUSINESS_TYPE_CHOICES = [
        ('product', 'Product Business'),
        ('service', 'Service Business'),
        ('both', 'Product & Service Business'),
    ]
    seller = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='business')
    business_name = models.CharField(max_length=100)
    description = models.TextField()
    business_slug = models.SlugField(unique=True, blank=True)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES)
    countries = models.ManyToManyField(Country)
    states = models.ManyToManyField(State)
    address = models.CharField(max_length=200)
    postcode = models.CharField(max_length=4, help_text="4-digit Australian postcode", default='5000')
    phone = models.CharField(max_length=20)
    website = models.URLField(default='www.website.com')
    email = models.EmailField(default='name@email.com')
    # Updated to make images optional with default values
    profile_picture = models.ImageField(
        upload_to='business_profiles/',
        default='business_profiles/DukaniEthnicStore.png',
        blank=True,
        null=True
    )
    banner_image = models.ImageField(
        upload_to='business_banners/',
        default='business_profiles/DukaniEthnicStore.png',
        blank=True,
        null=True
    )
    is_featured = models.BooleanField(default=False)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    # Stripe subscription fields
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)


    def get_pickup_address(self):
        """Get formatted pickup address for delivery services"""
        return f"{self.address}, {self.postcode}" if self.postcode else self.address

    def get_postcode(self):
        """Get business postcode, extract from address if not in separate field"""
        if self.postcode:
            return self.postcode

        # Try to extract from address field
        import re
        postcode_pattern = r'\b(\d{4})\b'
        matches = re.findall(postcode_pattern, self.address)
        return matches[-1] if matches else None

    def __str__(self):
        return self.business_name

    def save(self, *args, **kwargs):
        if not self.business_slug:
            self.business_slug = slugify(self.business_name)
        super().save(*args, **kwargs)

class OpeningHour(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('public_holiday', 'Public Holiday'),
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='opening_hours')
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    is_closed = models.BooleanField(default=False)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        if self.is_closed:
            return f"{self.business.business_name} - {self.get_day_display()} (Closed)"
        else:
            return f"{self.business.business_name} - {self.get_day_display()} ({self.opening_time} - {self.closing_time})"

    def clean(self):
        if not self.is_closed and (not self.opening_time or not self.closing_time):
            raise ValidationError("You must either select both opening and closing hours or mark the day as closed.")


class Product(models.Model):
    class Category(models.TextChoices):
        ELECTRONICS = 'EL', _('Electronics')
        CLOTHING = 'CL', _('Clothing, Shoes & Jewelry')
        BOOKS = 'BK', _('Books')
        HOME = 'HM', _('Home & Kitchen')
        BEAUTY = 'BE', _('Beauty & Personal Care')
        TOYS = 'TY', _('Toys & Games')
        SPORTS = 'SP', _('Sports & Outdoors')
        AUTOMOTIVE = 'AU', _('Automotive')
        HEALTH = 'HE', _('Health & Household')
        GROCERY = 'GR', _('Grocery & Gourmet Food')
        PET_SUPPLIES = 'PT', _('Pet Supplies')
        OFFICE = 'OF', _('Office Products')
        TOOLS = 'TL', _('Tools & Home Improvement')
        MOVIES = 'MV', _('Movies & TV')
        GARDEN = 'GD', _('Garden & Outdoor')
        HANDMADE = 'HN', _('Handmade')
        BABY = 'BA', _('Baby')
        INDUSTRIAL = 'IN', _('Industrial & Scientific')
        ARTS = 'AR', _('Arts, Crafts & Sewing')
        MUSIC = 'MU', _('Musical Instruments')
        OTHER = 'OT', _('Other')

    category = models.CharField(
        max_length=2,
        choices=Category.choices,
        default=Category.OTHER,
    )
    name = models.CharField(max_length=100)
    product_slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    image2 = models.ImageField(upload_to='products/', null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    in_stock = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)
    new_releases = models.BooleanField(default=False)
    has_variations = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.business.business_name}, {self.name}'

    def get_json_data(self):
        # Get all images including main image, second image, and additional images
        images = []
        if self.image:
            images.append(self.image.url)
        if self.image2:
            images.append(self.image2.url)

        # Add additional images
        additional_images = self.additional_images.all()
        for img in additional_images:
            images.append(img.image.url)

        data = {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'description': self.description,
            'images': images,
            'min_delivery_time': self.min_delivery_time,
            'max_delivery_time': self.max_delivery_time,
        }
        return json.dumps(data)

    def save(self, *args, **kwargs):
        if not self.product_slug:
            self.product_slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def overall_review(self):
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0

    def star_rating_percentage(self, star):
        total_reviews = self.reviews.count()
        if total_reviews == 0:
            return 0
        star_count = self.reviews.filter(rating=star).count()
        return round((star_count / total_reviews) * 100)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/additional_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.product.name} - Additional Image {self.id}"

VAR_CATEGORIES = (
    ('size', 'Size'),
    ('color', 'Color'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    name = models.CharField(max_length=50, choices=VAR_CATEGORIES, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.get_name_display()}"

class ProductVariation(models.Model):
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, related_name='values', null=True)
    value = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='product_variations/', null=True, blank=True)

    class Meta:
        unique_together = (('variation', 'value'),)

    def __str__(self):
        return f"{self.variation.product.name} - {self.variation.get_name_display()} - {self.value}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    review_text = models.TextField()
    rating = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'

    @property
    def date(self):
        return (timezone.now() - self.created_at).days


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    variation_key = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class CartItemVariation(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='variations')
    product_variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cart} - {self.product_variation}"

class Service(models.Model):
    name = models.CharField(max_length=100)
    service_slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='services/', null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return f'{self.business.business_name}, {self.name}'

    def save(self, *args, **kwargs):
        if not self.service_slug:
            self.service_slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def overall_review(self):
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0

    def star_rating_percentage(self, star):
        total_reviews = self.reviews.count()
        if total_reviews == 0:
            return 0
        star_count = self.reviews.filter(rating=star).count()
        return round((star_count / total_reviews) * 100)

class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='additional_images', default="1")
    image = models.ImageField(upload_to='services/additional_images/')

class ServiceVideo(models.Model):
    service = models.ForeignKey(Service, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='services/videos/')

class ServiceReview(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    review_text = models.TextField()
    rating = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} on {self.service.name}'

    @property
    def date(self):
        return (timezone.now() - self.created_at).days

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('ordered', 'ordered'),
        ('shipped', 'shipped'),
        ('delivered', 'delivered'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    ref_code = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    postal_code = models.CharField(max_length=20, null=True)
    note = models.TextField(null=True, blank=True)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default="ordered")
    delivery_method = models.CharField(
        max_length=20,
        choices=[
            ('pickup', 'Pickup'),
            ('delivery', 'Delivery')
        ],
        default='pickup'
    )
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    @property
    def total_with_delivery(self):
        return self.total_amount + self.delivery_fee + self.tip_amount

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    variations = JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} ({', '.join([f'{k}: {v}' for k, v in self.variations.items()]) if self.variations else ''})"


class DeliveryQuote(models.Model):
    """Store DoorDash delivery quotes"""
    quote_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pickup_address = models.TextField()
    dropoff_address = models.TextField()
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='AUD')
    pickup_time_estimated = models.DateTimeField(null=True, blank=True)
    dropoff_time_estimated = models.DateTimeField(null=True, blank=True)
    quote_data = models.JSONField()
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Quote {self.quote_id} - ${self.delivery_fee}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

class Delivery(models.Model):
    """Store DoorDash delivery information"""
    DELIVERY_STATUS_CHOICES = [
        ('quote', 'Quote'),
        ('created', 'Created'),
        ('dasher_confirmed', 'Dasher Confirmed'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_quote = models.ForeignKey(DeliveryQuote, on_delete=models.CASCADE, null=True, blank=True)
    external_delivery_id = models.CharField(max_length=100)
    doordash_delivery_id = models.CharField(max_length=100, null=True, blank=True)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='created')
    tracking_url = models.URLField(null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pickup_address = models.TextField()
    dropoff_address = models.TextField()
    pickup_time_estimated = models.DateTimeField(null=True, blank=True)
    dropoff_time_estimated = models.DateTimeField(null=True, blank=True)
    pickup_time_actual = models.DateTimeField(null=True, blank=True)
    dropoff_time_actual = models.DateTimeField(null=True, blank=True)
    delivery_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery {self.external_delivery_id} for Order {self.order.ref_code}"


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    email = models.EmailField()
    accepted = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.pk}"


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    business = models.ForeignKey(Business, related_name='messages', on_delete=models.CASCADE, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f''

    @property
    def sender_is_business(self):
        return self.sender.business.exists()

    @property
    def recipient_is_business(self):
        return self.recipient.business.exists()



class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('employment', 'Employment'),
        ('food', 'Food & Dining'),
        ('business', 'Business'),
        ('festival', 'Festival'),
        ('art', 'Art & Culture'),
        ('sport', 'Sport'),
        ('music', 'Music'),
        ('education', 'Education'),
        ('technology', 'Technology'),
        ('health', 'Health & Wellness'),
        ('other', 'Other')
    ]

    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='organized_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='other')
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='events')
    state = models.ForeignKey('State', on_delete=models.CASCADE, related_name='events')
    start_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    banner_image = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    top_event = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        return self.start_time > timezone.now()

    @property
    def is_today(self):
        return self.start_time.date() == timezone.now().date()


class SavedEvent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_events')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} saved {self.event.title}"

