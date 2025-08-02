# main_app/views.py
# This is where we define the view functions for our application
# Import render to render templates
from django.shortcuts import render, redirect
# Import HttpResponse to send text-based responses
from django.http import HttpResponse

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
        return Container.objects.filter(owner=self.request.user)
    
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
class FoodCreate(CreateView):
    model = CatalogFood
    fields = ['name', 'category', 'description', 'image_url']
    template_name = 'main_app/food_form.html'
    
    def get_success_url(self):
        return f'/food/{self.object.pk}/'

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
    context_object_name = 'food_list'

class FoodDetailView(DetailView):
    model = CatalogFood
    template_name = 'catalog_food/details.html'
    context_object_name = 'food'