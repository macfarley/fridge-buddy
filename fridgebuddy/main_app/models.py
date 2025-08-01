from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta

# User model is provided by Django's auth system, with new fields for tracking food preferences and restrictions

# Global catalog of all available food items
class CatalogFood(models.Model):
    CATEGORY_CHOICES = [
        ('dairy', 'Dairy'),
        ('meat', 'Meat & Poultry'),
        ('seafood', 'Seafood'),
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('grains', 'Grains & Bread'),
        ('condiments', 'Condiments & Sauces'),
        ('beverages', 'Beverages'),
        ('leftovers', 'Leftovers'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = 'Catalog items'
    
    def __str__(self):
        return self.name

# User owns many containers
class Container(models.Model):
    CONTAINER_TYPES = [
        ('FRIDGE',   'Fridge'),
        ('FREEZER',  'Freezer'),
        ('PANTRY',   'Pantry'),
        ('SHOPPING', 'Shopping List'),
    ]
    name = models.CharField(max_length=100)
    container_type = models.CharField(max_length=10, choices=CONTAINER_TYPES, default='FRIDGE')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='containers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ContainerFood model represents food items in user containers
class ContainerFood(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE, related_name='items')
    catalog_food = models.ForeignKey(CatalogFood, on_delete=models.CASCADE, related_name='container_entries')
    quantity = models.PositiveIntegerField(default=1, help_text="Number of this food item in the container")
    added_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True, help_text="Expiration date for this food item in the container")
    checked_off = models.BooleanField(default=False, help_text="Whether item is checked off (e.g., in shopping list)")
    is_frozen = models.BooleanField(default=False, help_text="Check if the item is frozen")

    class Meta:
        unique_together = ('container', 'catalog_food')
        ordering = ['expiration_date', 'catalog_food__name']
        verbose_name_plural = 'Container Food Items'

    def __str__(self):
        return f"{self.catalog_food.name} in {self.container.name}"

    def save(self, *args, **kwargs):
        if not self.expiration_date:  # Only set if not already provided
            # Use added_at.date() since we need a date, not datetime
            base_date = self.added_at.date() if self.added_at else date.today()
            
            if self.catalog_food.category == 'dairy':
                self.expiration_date = base_date + timedelta(weeks=2)
            elif self.catalog_food.category == 'seafood':
                self.expiration_date = base_date + timedelta(days=4)
            elif self.catalog_food.category == 'meat':
                self.expiration_date = base_date + timedelta(weeks=1)
                if self.is_frozen:
                    self.expiration_date = base_date + timedelta(weeks=26)  # Frozen meat lasts 6 months
            elif self.catalog_food.category in ['vegetables', 'fruits']:
                self.expiration_date = base_date + timedelta(weeks=1)
            elif self.catalog_food.category == 'grains':
                self.expiration_date = base_date + timedelta(weeks=4)
            elif self.catalog_food.category == 'condiments':
                self.expiration_date = base_date + timedelta(weeks=12)
            elif self.catalog_food.category == 'beverages':
                self.expiration_date = base_date + timedelta(weeks=8)
            elif self.catalog_food.category == 'leftovers':
                self.expiration_date = base_date + timedelta(days=3)
            else:
                self.expiration_date = base_date + timedelta(weeks=4)  # Default for 'other'
        super().save(*args, **kwargs)

    @property
    def days_until_expiration(self):
        """Calculate days until expiration (negative if expired)"""
        if not self.expiration_date:
            return None
        return (self.expiration_date - date.today()).days
    
    @property
    def is_expired(self):
        """Check if food has expired"""
        if not self.expiration_date:
            return False
        return self.days_until_expiration < 0
    
    @property
    def expires_soon(self):
        """Check if food expires within 3 days"""
        if not self.expiration_date:
            return False
        return 0 <= self.days_until_expiration <= 3
    
    @property
    def status_class(self):
        """Return CSS class for status styling"""
        if self.is_expired:
            return 'expired'
        elif self.expires_soon:
            return 'warning'
        return 'fresh'
