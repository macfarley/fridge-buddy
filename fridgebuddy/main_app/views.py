# main_app/views.py
# This is where we define the view functions for our application
# Import render to render templates
from django.shortcuts import render
# Import HttpResponse to send text-based responses
from django.http import HttpResponse
# Class-based views for creating, updating, and deleting containers and food items
from django.views.generic import ListView, DetailView,CreateView, UpdateView, DeleteView
# Import models to interact with the database
from .models import Container, CatalogFood, ContainerFood
from django.contrib.auth.mixins import LoginRequiredMixin

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


# Food-related view functions
# Class-based views for food items
# Define the food catalog view function
class FoodCatalogListView(ListView):
    model = CatalogFood
    template_name = 'catalog_food/index.html'
    context_object_name = 'food_list'
# Define the food detail view function
class FoodDetailView(DetailView):
    model = CatalogFood
    template_name = 'catalog_food/detail.html'
    context_object_name = 'food'


# Container-related view functions
# Define the container index view function
class ContainerIndexView(LoginRequiredMixin, ListView):
    model = Container
    template_name = 'containers/index.html'
    context_object_name = 'container_list'

    def get_queryset(self):
        return Container.objects.filter(owner=self.request.user)
# Define the food index view function for a specific container
class FoodIndexView(LoginRequiredMixin, ListView):
    model = ContainerFood
    template_name = 'food/index.html'
    context_object_name = 'food_list'

    def get_queryset(self):
        return ContainerFood.objects.filter(container__owner=self.request.user)
# create a new container
class ContainerCreate(LoginRequiredMixin, CreateView):
    model = Container
    fields = ['name', 'container_type']
    template_name = 'containers/container_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return f'/my-lists/{self.object.pk}/'
# update a container This will allow users to change the name or type of container
class ContainerUpdate(LoginRequiredMixin, UpdateView):
    model = Container
    fields = ['name', 'container_type']
    template_name = 'containers/container_form.html'

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