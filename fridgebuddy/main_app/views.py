# main_app/views.py
# This is where we define the view functions for our application
# Import render to render templates
from django.shortcuts import render, redirect
# Import HttpResponse to send text-based responses
from django.http import HttpResponse, JsonResponse

# Django class-based views and mixins
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

# Django authentication and forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Forms and models
from django import forms
from .models import Profile, Container, CatalogFood, ContainerFood

# Define the landing page view function
def home(request):
    # Render the landing page template with user authentication context
    context = {
        'user_authenticated': request.user.is_authenticated
    }
    return render(request, 'home.html', context)
# Define the about page
def about(request):
    return render(request, 'about.html')


# Profile update view for authenticated users
@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        
        # Get or create profile if it doesn't exist
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)

        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        profile.birthday = request.POST.get('birthday', profile.birthday)

        # if 'profile_image' in request.FILES:
        #     profile.profile_image = request.FILES['profile_image']

        user.save()
        profile.save()

        return redirect('dashboard')

    return redirect('dashboard')

# Custom signup form combining User and Profile fields
class CustomSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text="Optional.")
    last_name = forms.CharField(max_length=30, required=False, help_text="Optional.")
    email = forms.EmailField(max_length=254, help_text="Required. Enter a valid email address.")
    birthday = forms.DateField(required=False, help_text="Optional. Enter your birthday.")
    # profile_image = forms.ImageField(required=False, help_text="Optional. Upload a profile image (JPG, max 15MB).")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                birthday=self.cleaned_data['birthday'],
                # profile_image=self.cleaned_data['profile_image']
            )
        return user

# Signup view for user registration
def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CustomSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

# Dashboard view for authenticated users
@login_required
def dashboard(request):
    from datetime import date
    
    # Get user's containers for the dashboard display
    container_list = Container.objects.filter(owner=request.user)
    
    # Get or create profile if it doesn't exist
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    context = {
        'user': request.user,
        'container_list': container_list,
        'today': date.today()
    }
    return render(request, 'dashboard.html', context)


# Container Management Views with Inline Form Functionality
class ContainerIndexView(LoginRequiredMixin, ListView):
    """
    Main container listing view with inline creation functionality.
    
    This view handles both:
    1. GET requests: Display all user's containers + inline creation form
    2. POST requests: Process new container creation without page navigation
    
    Features:
    - Shows all containers owned by the user
    - Inline form for quick container creation
    - No separate page needed for adding containers
    - Immediate feedback on form submission
    """
    model = Container
    template_name = 'containers/index.html'
    context_object_name = 'container_list'

    def get_queryset(self):
        # Security: Only show containers owned by the current user
        # Annotate with total quantity of items in each container
        from django.db.models import Sum, Count
        return Container.objects.filter(owner=self.request.user).annotate(
            total_quantity=Sum('items__quantity'),
            item_count=Count('items')
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add the container creation form to every GET request
        # This enables the inline form functionality
        from django import forms
        
        class ContainerForm(forms.ModelForm):
            """Inline form for creating new containers without page navigation"""
            class Meta:
                model = Container
                fields = ['name', 'container_type']
                widgets = {
                    'name': forms.TextInput(attrs={
                        'placeholder': 'Enter container name',
                        'class': 'form-input'
                    }),
                    'container_type': forms.Select(attrs={
                        'class': 'form-select'
                    })
                }
        
        context['form'] = ContainerForm()
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Handle inline container creation via POST request.
        
        This method processes the inline form submission and either:
        - Redirects to success page if form is valid
        - Re-renders the page with form errors if invalid
        
        This provides immediate feedback without losing user context.
        """
        from django import forms
        
        class ContainerForm(forms.ModelForm):
            class Meta:
                model = Container
                fields = ['name', 'container_type']
        
        form = ContainerForm(request.POST)
        if form.is_valid():
            # Create the container and assign to current user
            container = form.save(commit=False)
            container.owner = request.user
            container.save()
            
            # Redirect back to the same page to show the new container
            return redirect('my-lists')
        else:
            # If form is invalid, re-render with errors
            # This maintains the page context while showing validation errors
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            context['form'] = form  # Include form with errors
            return self.render_to_response(context)
# Container Detail View - Shows all food items in a specific container with interactive features
class FoodIndexView(LoginRequiredMixin, DetailView):
    """
    Display detailed view of a container and all its food items.
    
    This view provides:
    - Container information (name, type)
    - List of all food items in the container
    - Interactive batch operations (select, move, delete)
    - Quantity adjustment controls for each item
    - Expiration status indicators
    
    The template includes JavaScript for:
    - Checkbox selection with "Select All" functionality
    - Live counters for selected items and pending changes
    - Quantity adjustment with +/- buttons
    - Batch operations bar that appears when items are selected
    """
    model = Container
    template_name = 'containers/details.html'
    context_object_name = 'container'
    pk_url_kwarg = 'container_id'  # URL parameter name for container ID

    def get_queryset(self):
        # Security: Only allow access to containers owned by the current user
        return Container.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all food items in this container, ordered by expiration date
        # This ensures expired items appear first for better user awareness
        context['food_items'] = ContainerFood.objects.filter(
            container=self.object,
            container__owner=self.request.user  # Double-check security
        ).order_by('expiration_date')
        
        return context
# create a new container
class ContainerCreate(LoginRequiredMixin, CreateView):
    model = Container
    fields = ['name', 'container_type']
    template_name = 'main_app/container_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return f'/my-lists/{self.object.pk}/'
# update a container This will allow users to change the name or type of container
class ContainerUpdate(LoginRequiredMixin, UpdateView):
    model = Container
    fields = ['name', 'container_type']
    template_name = 'main_app/container_form.html'

    def get_queryset(self):
        return Container.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return f'/my-lists/{self.object.pk}/'
# delete a container
class ContainerDelete(LoginRequiredMixin, DeleteView):  
    model = Container
    template_name = 'containers/container_confirm_delete.html'

    def get_queryset(self):
        return Container.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return '/my-lists/'

# Food CRUD views
class FoodCreate(LoginRequiredMixin, CreateView):
    model = CatalogFood
    fields = ['name', 'category', 'description', 'image_url']
    template_name = 'main_app/food_form.html'
    
    def form_valid(self, form):
        # Set the contributor to the current user
        form.instance.contributor = self.request.user
        
        # Save the catalog food item
        response = super().form_valid(form)
        
        # Check if user wants to add to shopping list
        if self.request.POST.get('add_to_shopping_list'):
            # Get or create a shopping list for the user
            shopping_list, created = Container.objects.get_or_create(
                owner=self.request.user,
                container_type='SHOPPING',
                defaults={'name': 'Shopping List'}
            )
            
            # Add the food item to the shopping list
            ContainerFood.objects.get_or_create(
                container=shopping_list,
                catalog_food=self.object,
                defaults={
                    'quantity': 1,
                    'checked_off': False
                }
            )
        
        return response
    
    def get_success_url(self):
        return f'/food-catalog/{self.object.pk}/'

class FoodUpdate(UpdateView):
    model = CatalogFood
    fields = ['name', 'category', 'description', 'image_url']
    template_name = 'main_app/food_form.html'
    
    def get_success_url(self):
        return f'/food/{self.object.pk}/'

class FoodDelete(DeleteView):
    model = CatalogFood
    template_name = 'main_app/confirm_delete.html'
    
    def get_success_url(self):
        return '/food-catalog/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_catalog_food'] = True
        return context

class FoodCatalogListView(ListView):
    model = CatalogFood
    template_name = 'catalog_food/index.html'
    context_object_name = 'foods'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get or create user's shopping list (container with type 'SHOPPING')
            shopping_list, created = Container.objects.get_or_create(
                owner=self.request.user,
                container_type='SHOPPING',
                defaults={
                    'name': 'Shopping List',
                    'description': 'Your personal shopping list'
                }
            )
            context['shopping_list'] = shopping_list
            context['shopping_items'] = shopping_list.items.all()
        return context

class FoodDetailView(DetailView):
    model = CatalogFood
    template_name = 'catalog_food/details.html'
    context_object_name = 'food'

class ShoppingListView(LoginRequiredMixin, DetailView):
    """
    Display the user's shopping list as a dedicated page with batch operations.
    Enhanced to handle form submissions and reduce JavaScript dependency.
    """
    model = Container
    template_name = 'shopping_list/index.html'
    context_object_name = 'shopping_list'
    
    def get_object(self):
        # Get or create user's shopping list
        shopping_list, created = Container.objects.get_or_create(
            owner=self.request.user,
            container_type='SHOPPING',
            defaults={
                'name': 'Shopping List',
                'description': 'Your personal shopping list'
            }
        )
        return shopping_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add user's containers for the dropdown (excluding shopping list)
        context['user_containers'] = Container.objects.filter(
            owner=self.request.user
        ).exclude(container_type='SHOPPING').order_by('name')
        
        # Add forms for server-side processing
        from .forms import BatchMoveShoppingItemsForm, ContainerSelectionForm
        
        context['batch_move_form'] = BatchMoveShoppingItemsForm(user=self.request.user)
        context['container_selection_form'] = ContainerSelectionForm(user=self.request.user)
        
        # Handle container selection if submitted
        if self.request.GET.get('selected_container'):
            try:
                selected_container_id = int(self.request.GET.get('selected_container'))
                selected_container = Container.objects.get(
                    pk=selected_container_id,
                    owner=self.request.user
                )
                context['selected_container'] = selected_container
                context['selected_container_items'] = selected_container.items.all().order_by('expiration_date')
            except (ValueError, Container.DoesNotExist):
                pass
        
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Handle form submissions for batch operations
        """
        from .forms import BatchMoveShoppingItemsForm, ClearCheckedItemsForm
        from django.contrib import messages
        from django.shortcuts import redirect
        
        # Handle batch move operation
        if 'batch_move' in request.POST:
            form = BatchMoveShoppingItemsForm(user=request.user, data=request.POST)
            if form.is_valid():
                return self._handle_batch_move(form, request)
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        
        # Handle clear checked items operation
        elif 'clear_checked' in request.POST:
            form = ClearCheckedItemsForm(data=request.POST)
            if form.is_valid():
                return self._handle_clear_checked(form, request)
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        
        return redirect('shopping-list')
    
    def _handle_batch_move(self, form, request):
        """
        Process batch move operation server-side
        """
        from django.contrib import messages
        from django.shortcuts import redirect
        
        item_ids = form.cleaned_data['selected_items']
        target_container = form.cleaned_data['target_container']
        
        # Get shopping items to move
        shopping_items = ContainerFood.objects.filter(
            pk__in=item_ids,
            container__owner=request.user,
            container__container_type='SHOPPING'
        )
        
        moved_count = 0
        for shopping_item in shopping_items:
            # Check if item already exists in target container
            existing_item, created = ContainerFood.objects.get_or_create(
                container=target_container,
                catalog_food=shopping_item.catalog_food,
                defaults={
                    'quantity': shopping_item.quantity,
                    'is_frozen': target_container.container_type == 'FREEZER'
                }
            )
            
            if not created:
                # Item already exists, increase quantity
                existing_item.quantity += shopping_item.quantity
                existing_item.save()
            else:
                # New item, let model calculate default expiration
                existing_item.is_frozen = target_container.container_type == 'FREEZER'
                existing_item.save()
            
            # Remove from shopping list
            shopping_item.delete()
            moved_count += 1
        
        messages.success(
            request, 
            f'Successfully moved {moved_count} items to {target_container.name}'
        )
        return redirect('shopping-list')
    
    def _handle_clear_checked(self, form, request):
        """
        Process clear checked items operation server-side
        """
        from django.contrib import messages
        from django.shortcuts import redirect
        
        item_ids = form.cleaned_data['checked_items']
        
        # Remove checked items from shopping list
        removed_items = ContainerFood.objects.filter(
            pk__in=item_ids,
            container__owner=request.user,
            container__container_type='SHOPPING'
        )
        
        removed_count = removed_items.count()
        removed_items.delete()
        
        messages.success(request, f'Removed {removed_count} items from shopping list')
        return redirect('shopping-list')

# AJAX endpoint for adding food to containers
@login_required
def add_food_to_container(request):
    """
    AJAX endpoint to add a catalog food item to a user's container
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            food_id = data.get('food_id')
            container_id = data.get('container_id')
            quantity = data.get('quantity', 1)
            
            # Validate inputs
            if not food_id or not container_id:
                return JsonResponse({'error': 'Missing food_id or container_id'}, status=400)
            
            # Get the catalog food and container
            try:
                catalog_food = CatalogFood.objects.get(pk=food_id)
                container = Container.objects.get(pk=container_id, owner=request.user)
            except CatalogFood.DoesNotExist:
                return JsonResponse({'error': 'Food item not found'}, status=404)
            except Container.DoesNotExist:
                return JsonResponse({'error': 'Container not found or access denied'}, status=404)
            
            # Add or update the food in container
            container_food, created = ContainerFood.objects.get_or_create(
                container=container,
                catalog_food=catalog_food,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # If item already exists, increase quantity
                container_food.quantity += quantity
                container_food.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Added {catalog_food.name} to {container.name}',
                'created': created,
                'new_quantity': container_food.quantity
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

# AJAX endpoint for batch adding foods to shopping list
@login_required
def batch_add_to_shopping_list(request):
    """
    AJAX endpoint to add multiple catalog food items to user's shopping list
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            food_ids = data.get('food_ids', [])
            
            if not food_ids:
                return JsonResponse({'error': 'No food items provided'}, status=400)
            
            # Get or create user's shopping list
            shopping_list, created = Container.objects.get_or_create(
                owner=request.user,
                container_type='SHOPPING',
                defaults={
                    'name': 'Shopping List',
                    'description': 'Your personal shopping list'
                }
            )
            
            added_items = []
            updated_items = []
            
            # Add each food item to shopping list
            for food_id in food_ids:
                try:
                    catalog_food = CatalogFood.objects.get(pk=food_id)
                    container_food, created = ContainerFood.objects.get_or_create(
                        container=shopping_list,
                        catalog_food=catalog_food,
                        defaults={'quantity': 1}
                    )
                    
                    if created:
                        added_items.append({
                            'id': catalog_food.pk,
                            'name': catalog_food.name,
                            'category': catalog_food.category,
                            'quantity': container_food.quantity
                        })
                    else:
                        # Item already exists, increase quantity
                        container_food.quantity += 1
                        container_food.save()
                        updated_items.append({
                            'id': catalog_food.pk,
                            'name': catalog_food.name,
                            'category': catalog_food.category,
                            'quantity': container_food.quantity
                        })
                        
                except CatalogFood.DoesNotExist:
                    continue  # Skip invalid food IDs
            
            # Get updated shopping list count
            shopping_count = shopping_list.items.count()
            
            return JsonResponse({
                'success': True,
                'added_items': added_items,
                'updated_items': updated_items,
                'shopping_count': shopping_count,
                'message': f'Added {len(added_items)} new items and updated {len(updated_items)} existing items to your shopping list'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)


@login_required
def move_shopping_item_to_container(request):
    """
    AJAX endpoint to move an item from shopping list to a selected container
    """
    if request.method == 'POST':
        try:
            import json
            from datetime import datetime, date
            data = json.loads(request.body)
            item_id = data.get('item_id')
            container_id = data.get('container_id')
            expiration_date = data.get('expiration_date')  # Optional explicit date
            quantity = data.get('quantity', 1)
            
            # Get the shopping list item
            try:
                shopping_item = ContainerFood.objects.get(
                    pk=item_id,
                    container__owner=request.user,
                    container__container_type='SHOPPING'
                )
            except ContainerFood.DoesNotExist:
                return JsonResponse({'error': 'Shopping item not found'}, status=404)
            
            # Get the target container
            try:
                target_container = Container.objects.get(
                    pk=container_id,
                    owner=request.user
                )
            except Container.DoesNotExist:
                return JsonResponse({'error': 'Container not found'}, status=404)
            
            # Parse expiration date if provided
            parsed_expiration = None
            if expiration_date:
                try:
                    parsed_expiration = datetime.strptime(expiration_date, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({'error': 'Invalid expiration date format'}, status=400)
            
            # Check if item already exists in target container
            existing_item, created = ContainerFood.objects.get_or_create(
                container=target_container,
                catalog_food=shopping_item.catalog_food,
                defaults={
                    'quantity': quantity,
                    'expiration_date': parsed_expiration,
                    'is_frozen': target_container.container_type == 'FREEZER'
                }
            )
            
            if not created:
                # Item already exists, increase quantity
                existing_item.quantity += quantity
                if parsed_expiration:
                    existing_item.expiration_date = parsed_expiration
                existing_item.save()
            
            # If no explicit expiration date was provided, let the model's save method calculate it
            if created and not parsed_expiration:
                existing_item.is_frozen = target_container.container_type == 'FREEZER'
                existing_item.save()  # This will trigger default expiration calculation
            
            # Remove or reduce quantity from shopping list
            if shopping_item.quantity > quantity:
                shopping_item.quantity -= quantity
                shopping_item.save()
            else:
                shopping_item.delete()
            
            # Get updated shopping list count
            shopping_count = Container.objects.get(
                owner=request.user,
                container_type='SHOPPING'
            ).items.count()
            
            return JsonResponse({
                'success': True,
                'message': f'Moved {shopping_item.catalog_food.name} to {target_container.name}',
                'shopping_count': shopping_count,
                'expiration_date': existing_item.expiration_date.strftime('%Y-%m-%d') if existing_item.expiration_date else None
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)


@login_required
def batch_move_shopping_items(request):
    """
    AJAX endpoint to move multiple shopping list items to a selected container
    """
    if request.method == 'POST':
        try:
            import json
            from datetime import datetime
            data = json.loads(request.body)
            item_ids = data.get('item_ids', [])
            container_id = data.get('container_id')
            
            if not item_ids:
                return JsonResponse({'error': 'No items selected'}, status=400)
            
            if not container_id:
                return JsonResponse({'error': 'No target container selected'}, status=400)
            
            # Get the target container
            try:
                target_container = Container.objects.get(
                    pk=container_id,
                    owner=request.user
                )
            except Container.DoesNotExist:
                return JsonResponse({'error': 'Container not found'}, status=404)
            
            # Get all shopping items to be moved
            shopping_items = ContainerFood.objects.filter(
                pk__in=item_ids,
                container__owner=request.user,
                container__container_type='SHOPPING'
            )
            
            if not shopping_items.exists():
                return JsonResponse({'error': 'No valid shopping items found'}, status=404)
            
            moved_items = []
            
            # Process each shopping item
            for shopping_item in shopping_items:
                # Check if item already exists in target container
                existing_item, created = ContainerFood.objects.get_or_create(
                    container=target_container,
                    catalog_food=shopping_item.catalog_food,
                    defaults={
                        'quantity': shopping_item.quantity,
                        'is_frozen': target_container.container_type == 'FREEZER'
                    }
                )
                
                if not created:
                    # Item already exists, increase quantity
                    existing_item.quantity += shopping_item.quantity
                    existing_item.save()
                else:
                    # New item, let model calculate default expiration
                    existing_item.is_frozen = target_container.container_type == 'FREEZER'
                    existing_item.save()
                
                moved_items.append({
                    'name': shopping_item.catalog_food.name,
                    'quantity': shopping_item.quantity
                })
                
                # Remove from shopping list
                shopping_item.delete()
            
            # Get updated shopping list count
            shopping_count = Container.objects.get(
                owner=request.user,
                container_type='SHOPPING'
            ).items.count()
            
            return JsonResponse({
                'success': True,
                'message': f'Moved {len(moved_items)} items to {target_container.name}',
                'moved_items': moved_items,
                'shopping_count': shopping_count
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)


@login_required
def update_food_item(request):
    """
    AJAX endpoint to update a food item's properties (expiration date, quantity, etc.)
    """
    if request.method == 'POST':
        try:
            import json
            from datetime import datetime
            data = json.loads(request.body)
            item_id = data.get('item_id')
            expiration_date = data.get('expiration_date')
            quantity = data.get('quantity')
            
            # Get the food item
            try:
                food_item = ContainerFood.objects.get(
                    pk=item_id,
                    container__owner=request.user
                )
            except ContainerFood.DoesNotExist:
                return JsonResponse({'error': 'Food item not found'}, status=404)
            
            # Update expiration date if provided
            if expiration_date:
                try:
                    parsed_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
                    food_item.expiration_date = parsed_date
                except ValueError:
                    return JsonResponse({'error': 'Invalid expiration date format'}, status=400)
            
            # Update quantity if provided
            if quantity is not None:
                if quantity < 0:
                    return JsonResponse({'error': 'Quantity cannot be negative'}, status=400)
                food_item.quantity = quantity
            
            food_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Updated {food_item.catalog_food.name}',
                'expiration_date': food_item.expiration_date.strftime('%Y-%m-%d') if food_item.expiration_date else None,
                'quantity': food_item.quantity,
                'days_until_expiration': food_item.days_until_expiration,
                'status_class': food_item.status_class
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)


@login_required
def delete_food_item(request):
    """
    AJAX endpoint to delete a food item with option to add to shopping list
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            item_id = data.get('item_id')
            add_to_shopping = data.get('add_to_shopping', False)
            
            # Get the food item
            try:
                food_item = ContainerFood.objects.get(
                    pk=item_id,
                    container__owner=request.user
                )
            except ContainerFood.DoesNotExist:
                return JsonResponse({'error': 'Food item not found'}, status=404)
            
            catalog_food = food_item.catalog_food
            quantity = food_item.quantity
            
            # Add to shopping list if requested
            shopping_count = 0
            if add_to_shopping:
                shopping_list, created = Container.objects.get_or_create(
                    owner=request.user,
                    container_type='SHOPPING',
                    defaults={
                        'name': 'Shopping List',
                        'description': 'Your personal shopping list'
                    }
                )
                
                # Add or update quantity in shopping list
                shopping_item, created = ContainerFood.objects.get_or_create(
                    container=shopping_list,
                    catalog_food=catalog_food,
                    defaults={'quantity': quantity}
                )
                
                if not created:
                    shopping_item.quantity += quantity
                    shopping_item.save()
                
                shopping_count = shopping_list.items.count()
            
            # Delete the food item
            food_item.delete()
            
            message = f'Removed {catalog_food.name}'
            if add_to_shopping:
                message += f' and added to shopping list'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'shopping_count': shopping_count
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)