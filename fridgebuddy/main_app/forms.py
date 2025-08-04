"""
Django Forms for FridgeBuddy Application

This file contains form definitions for handling user input and data validation.
Forms are used to replace JavaScript functionality where possible, providing
better security, validation, and server-side processing.
"""

from django import forms
from django.contrib.auth.models import User
from .models import Container, ContainerFood, CatalogFood


class BatchMoveShoppingItemsForm(forms.Form):
    """
    Form for handling batch move operations from shopping list to containers.
    Replaces JavaScript-heavy batch operations with server-side processing.
    """
    
    selected_items = forms.CharField(
        widget=forms.HiddenInput(),
        help_text="Comma-separated list of item IDs to move"
    )
    
    target_container = forms.ModelChoiceField(
        queryset=Container.objects.none(),  # Will be set in __init__
        empty_label="Select a container...",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        help_text="Choose the container to move items to"
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Only show containers owned by the user, excluding shopping list
            self.fields['target_container'].queryset = Container.objects.filter(
                owner=user
            ).exclude(container_type='SHOPPING').order_by('name')
    
    def clean_selected_items(self):
        """
        Validate and parse the selected items string into a list of IDs
        """
        items_str = self.cleaned_data.get('selected_items', '')
        if not items_str:
            raise forms.ValidationError("No items selected for moving")
        
        try:
            # Parse comma-separated string into list of integers
            item_ids = [int(id.strip()) for id in items_str.split(',') if id.strip()]
            if not item_ids:
                raise forms.ValidationError("No valid items selected")
            return item_ids
        except ValueError:
            raise forms.ValidationError("Invalid item IDs provided")
    
    def clean(self):
        """
        Cross-field validation to ensure user owns the selected items
        """
        cleaned_data = super().clean()
        item_ids = cleaned_data.get('selected_items', [])
        target_container = cleaned_data.get('target_container')
        
        if item_ids and target_container:
            # Verify all items exist and belong to the user's shopping list
            valid_items = ContainerFood.objects.filter(
                pk__in=item_ids,
                container__owner=target_container.owner,
                container__container_type='SHOPPING'
            )
            
            if len(valid_items) != len(item_ids):
                raise forms.ValidationError("Some selected items are invalid or don't belong to you")
        
        return cleaned_data


class MoveShoppingItemForm(forms.Form):
    """
    Form for moving a single shopping item to a container with optional expiration date.
    Handles the individual item move functionality with proper validation.
    """
    
    item_id = forms.IntegerField(widget=forms.HiddenInput())
    
    target_container = forms.ModelChoiceField(
        queryset=Container.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        }),
        help_text="Quantity to move (remaining will stay in shopping list)"
    )
    
    expiration_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text="Leave blank to use automatic expiration calculation"
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['target_container'].queryset = Container.objects.filter(
                owner=user
            ).exclude(container_type='SHOPPING').order_by('name')
    
    def clean_item_id(self):
        """
        Validate that the item exists and belongs to the user's shopping list
        """
        item_id = self.cleaned_data.get('item_id')
        try:
            item = ContainerFood.objects.get(
                pk=item_id,
                container__container_type='SHOPPING'
            )
            return item_id
        except ContainerFood.DoesNotExist:
            raise forms.ValidationError("Shopping item not found")
    
    def clean_quantity(self):
        """
        Validate quantity doesn't exceed available amount in shopping list
        """
        quantity = self.cleaned_data.get('quantity')
        item_id = self.cleaned_data.get('item_id')
        
        if item_id and quantity:
            try:
                item = ContainerFood.objects.get(pk=item_id)
                if quantity > item.quantity:
                    raise forms.ValidationError(
                        f"Cannot move {quantity} items. Only {item.quantity} available."
                    )
            except ContainerFood.DoesNotExist:
                pass  # Will be caught by item_id validation
        
        return quantity


class ClearCheckedItemsForm(forms.Form):
    """
    Form for clearing checked items from the shopping list.
    Provides server-side handling for the clear functionality.
    """
    
    checked_items = forms.CharField(
        widget=forms.HiddenInput(),
        help_text="Comma-separated list of checked item IDs to remove"
    )
    
    def clean_checked_items(self):
        """
        Validate and parse the checked items string
        """
        items_str = self.cleaned_data.get('checked_items', '')
        if not items_str:
            raise forms.ValidationError("No items selected for removal")
        
        try:
            item_ids = [int(id.strip()) for id in items_str.split(',') if id.strip()]
            if not item_ids:
                raise forms.ValidationError("No valid items selected")
            return item_ids
        except ValueError:
            raise forms.ValidationError("Invalid item IDs provided")


class UpdateShoppingItemForm(forms.ModelForm):
    """
    Form for updating shopping list items (quantity, checked status, etc.).
    Provides server-side validation and processing for item updates.
    """
    
    class Meta:
        model = ContainerFood
        fields = ['quantity', 'checked_off']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'checked_off': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_quantity(self):
        """
        Ensure quantity is positive
        """
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1")
        return quantity


class ContainerSelectionForm(forms.Form):
    """
    Simple form for container selection in the shopping list interface.
    Used for the container dropdown functionality.
    """
    
    selected_container = forms.ModelChoiceField(
        queryset=Container.objects.none(),
        required=False,
        empty_label="-- Select Container --",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit();'  # Auto-submit on selection
        })
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['selected_container'].queryset = Container.objects.filter(
                owner=user
            ).exclude(container_type='SHOPPING').order_by('name')
