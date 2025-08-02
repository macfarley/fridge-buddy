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
    list_display = ['food', 'container', 'quantity', 'expiration_date', 'date_added']
    list_filter = ['expiration_date', 'date_added', 'container__container_type']
    search_fields = ['food__name', 'container__name']

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
                "category": "MEAT",
                "description": "Boneless, skinless chicken breast"
            },
            {
                "name": "Whole Milk",
                "category": "DAIRY",
                "description": "Fresh whole milk, 3.25% fat"
            },
            {
                "name": "Bananas",
                "category": "FRUIT",
                "description": "Fresh yellow bananas"
            },
            {
                "name": "Spinach",
                "category": "VEGETABLE",
                "description": "Fresh baby spinach leaves"
            },
            {
                "name": "White Bread",
                "category": "GRAIN",
                "description": "Sliced white bread loaf"
            },
            {
                "name": "Cheddar Cheese",
                "category": "DAIRY",
                "description": "Sharp cheddar cheese block"
            },
            {
                "name": "Ground Beef",
                "category": "MEAT",
                "description": "80/20 ground beef"
            },
            {
                "name": "Apples",
                "category": "FRUIT",
                "description": "Fresh red apples"
            },
            {
                "name": "Carrots",
                "category": "VEGETABLE", 
                "description": "Fresh baby carrots"
            },
            {
                "name": "Brown Rice",
                "category": "GRAIN",
                "description": "Long grain brown rice"
            },
            {
                "name": "Salmon",
                "category": "SEAFOOD",
                "description": "Fresh Atlantic salmon fillet"
            },
            {
                "name": "Eggs",
                "category": "DAIRY",
                "description": "Large grade A eggs"
            },
            {
                "name": "Olive Oil",
                "category": "OTHER",
                "description": "Extra virgin olive oil"
            },
            {
                "name": "Black Pepper",
                "category": "SPICE",
                "description": "Ground black pepper"
            },
            {
                "name": "Orange Juice",
                "category": "BEVERAGE",
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
