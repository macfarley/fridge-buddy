# This file contains the core models for the FridgeBuddy application.
# It defines the data structure for users, food items, containers, and their relationships.

# This import makes use of Django's ORM to define models and relationships.
from django.db import models
# This import is used for URL resolution in case we need to link to specific model instances.
from django.urls import reverse
# Importing User model from Django's built-in authentication system.
from django.contrib.auth.models import User
# Importing date and timedelta for handling expiration dates.
from datetime import date, timedelta

# User model is provided by Django's auth system
# out of the box User contains username, email, password, first_name, last_name
# We will extend it via ForeignKey relationships in other models.

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
    # Charfield is used for single line text, TextField for longer descriptions
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    #this is optional, can be blank.  We'll use it for extra info like "organic", "gluten-free", "vegan", etc.
    description = models.TextField(blank=True)
    # Might wire up to an unsplash or other image service later
    image_url = models.URLField(blank=True)
    # automatically set when the item is created, in case we want to track when items were added to the catalog
    created_at = models.DateTimeField(auto_now_add=True)
    contributor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contributed_foods')
    #Meta options for ordering and plural name
    class Meta:
        ordering = ['category', 'name']
        verbose_name_plural = 'Catalog items'
    # String representation for admin and debugging
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
    # User who owns this container
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='containers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ContainerFood model represents food items in user containers
class ContainerFood(models.Model):
    # ForeignKey to the container this food item belongs to
    container = models.ForeignKey(Container, on_delete=models.CASCADE, related_name='items')
    # ForeignKey to the catalog food item
    catalog_food = models.ForeignKey(CatalogFood, on_delete=models.CASCADE, related_name='container_entries')
    # Quantity of this food item in the container
    quantity = models.PositiveIntegerField(default=1, help_text="Number of this food item in the container")
    # This is the purchase date or the date it was moved to the container
    added_at = models.DateTimeField(auto_now_add=True)
    # this will either be explicit or set automatically based on category rules
    expiration_date = models.DateField(null=True, blank=True, help_text="Expiration date for this food item in the container")
    # Whether the item is checked off (e.g., in shopping list)
    checked_off = models.BooleanField(default=False, help_text="Whether item is checked off (e.g., in shopping list)")
    # Whether the item is frozen (affects expiration rules)
    is_frozen = models.BooleanField(default=False, help_text="Check if the item is frozen")

    class Meta:
        # unique_together ensures that the same food item cannot be added multiple times to the same container, it should just add to quantity
        unique_together = ('container', 'catalog_food')
        # ensures items closest to expiration appear first
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
