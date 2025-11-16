# Game Product Model Start #
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import User


class Game(models.Model):
    """Game catalog (Free Fire, PUBG, Mobile Legends, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='games/', blank=True, null=True)
    platform = models.CharField(
        max_length=50,
        choices=[
            ('mobile', 'Mobile'),
            ('pc', 'PC'),
            ('webgame', 'Webgame'),
            ('console', 'Console'),
        ],
        default='mobile'
    )
    language = models.CharField(max_length=50, default='English')
    region = models.CharField(max_length=50, default='Global')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return self.name


class GameProductDiamond(models.Model):
    """Diamond products - completely separate, can be used by any game product"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diamond_quantity = models.PositiveIntegerField(
        unique=True,
        help_text="Number of diamonds (e.g., 100, 210, 310)"
    )
    name = models.CharField(
        max_length=255,
        help_text="Display name (e.g., '100 Diamonds')"
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='diamonds/', blank=True, null=True)
    
    original_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Original price before discount"
    )
    
    currency = models.CharField(max_length=10, default='BDT', help_text="Currency code (e.g., BDT, USD)")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    stock_quantity = models.PositiveIntegerField(default=9999)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['diamond_quantity']

    def __str__(self):
        return f"{self.name} - {self.currency} {self.original_price}"


class GameProduct(models.Model):
    """Base product model for games - can select multiple diamond products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='products')
    
    name = models.CharField(max_length=255, help_text="Product name")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Many-to-many relationship - can select any combination of diamond products
    available_diamonds = models.ManyToManyField(
        GameProductDiamond,
        related_name='game_products',
        blank=True,
        help_text="Select which diamond products are available for this game product"
    )
    
    currency = models.CharField(max_length=10, default='BDT', help_text="Currency code (e.g., BDT, USD)")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return f"{self.game.name} - {self.name}"


class GameProductDiscount(models.Model):
    """Discount model - can apply to any GameProductDiamond"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_product_diamond = models.ForeignKey(
        GameProductDiamond,
        on_delete=models.CASCADE,
        related_name='discounts'
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount percentage (0-100)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = [['game_product_diamond', 'discount_percentage']]

    def __str__(self):
        if self.game_product_diamond:
            return f"{self.game_product_diamond.name} - {self.discount_percentage}%"
        return f"Discount - {self.discount_percentage}%"
    
    @property
    def discounted_price(self):
        """Calculate price after discount"""
        if not self.game_product_diamond or not self.game_product_diamond.original_price:
            return 0
        if self.discount_percentage and self.discount_percentage > 0:
            discount_amount = (self.game_product_diamond.original_price * self.discount_percentage) / 100
            return self.game_product_diamond.original_price - discount_amount
        return self.game_product_diamond.original_price


class GameProductTransaction(models.Model):
    """Transaction model for game product purchases"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bkash', 'Bkash'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=100, unique=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    game_product = models.ForeignKey(
        GameProduct,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    game_product_diamond = models.ForeignKey(
        GameProductDiamond,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    
    # In-game player ID (required for game products)
    in_game_player_id = models.CharField(
        max_length=255,
        help_text="Player ID / Account ID for the game"
    )
    
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    game_server = models.CharField(max_length=100, blank=True)
    game_region = models.CharField(max_length=100, blank=True)
    
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='bkash')
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=255, blank=True)
    
    game_product_discount = models.ForeignKey(
        GameProductDiscount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    save_for_future = models.BooleanField(
        default=False,
        help_text="Save player ID for future purchases"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['in_game_player_id']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            date_str = timezone.now().strftime('%Y%m%d')
            self.transaction_id = f"TXN-{date_str}-{str(self.id)[:8].upper()}"
        
        if self.discount_percentage > 0:
            self.discount_amount = (self.original_price * self.discount_percentage) / 100
            self.final_price = self.original_price - self.discount_amount
        else:
            self.final_price = self.original_price
        
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.user.email} - {self.game_product_diamond.name}"
# Game Product Model End #
