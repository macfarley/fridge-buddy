from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from .models import Profile, Container, CatalogFood, ContainerFood
import json

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birthday']
    list_filter = ['birthday']

@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'container_type', 'owner', 'created_at']
    list_filter = ['container_type', 'created_at']
    search_fields = ['name', 'owner__username']

@admin.register(ContainerFood)
class ContainerFoodAdmin(admin.ModelAdmin):
    list_display = ['catalog_food', 'container', 'quantity', 'expiration_date', 'added_at']
    list_filter = ['expiration_date', 'added_at', 'container__container_type']
    search_fields = ['catalog_food__name', 'container__name']

@admin.register(CatalogFood)
class CatalogFoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'description']
    list_filter = ['category']
    search_fields = ['name', 'description']
    actions = ['populate_sample_foods']

    def populate_sample_foods(self, request, queryset):
        """Admin action to populate sample food items"""
        sample_foods = [
            {
                "name": "Chicken Breast",
                "category": "meat",
                "description": "Boneless, skinless chicken breast"
            },
            {
                "name": "Whole Milk",
                "category": "dairy",
                "description": "Fresh whole milk, 3.25% fat"
            },
            {
                "name": "Bananas",
                "category": "fruits",
                "description": "Fresh yellow bananas"
            },
            {
                "name": "Spinach",
                "category": "vegetables",
                "description": "Fresh baby spinach leaves"
            },
            {
                "name": "White Bread",
                "category": "grains",
                "description": "Sliced white bread loaf"
            },
            {
                "name": "Cheddar Cheese",
                "category": "dairy",
                "description": "Sharp cheddar cheese block"
            },
            {
                "name": "Ground Beef",
                "category": "meat",
                "description": "80/20 ground beef"
            },
            {
                "name": "Apples",
                "category": "fruits",
                "description": "Fresh red apples"
            },
            {
                "name": "Carrots",
                "category": "vegetables", 
                "description": "Fresh baby carrots"
            },
            {
                "name": "Brown Rice",
                "category": "grains",
                "description": "Long grain brown rice"
            },
            {
                "name": "Salmon",
                "category": "seafood",
                "description": "Fresh Atlantic salmon fillet"
            },
            {
                "name": "Eggs",
                "category": "dairy",
                "description": "Large grade A eggs"
            },
            {
                "name": "Olive Oil",
                "category": "condiments",
                "description": "Extra virgin olive oil"
            },
            {
                "name": "Black Pepper",
                "category": "other",
                "description": "Ground black pepper"
            },
            {
                "name": "Orange Juice",
                "category": "beverages",
                "description": "Fresh squeezed orange juice"
            }
        ]

        created_count = 0
        for food_data in sample_foods:
            food, created = CatalogFood.objects.get_or_create(
                name=food_data['name'],
                defaults={
                    'category': food_data['category'],
                    'description': food_data['description']
                }
            )
            if created:
                created_count += 1

        if created_count > 0:
            messages.success(request, f"Successfully created {created_count} new food items!")
        else:
            messages.info(request, "All sample foods already exist in the catalog.")

    populate_sample_foods.short_description = "Populate sample food items"
