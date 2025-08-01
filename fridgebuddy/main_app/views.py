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

# Define the landing page view function
def home(request):
    # Render the landing page template
    return render(request, 'home.html')
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
class ContainerIndexView(ListView):
    model = Container
    template_name = 'containers/index.html'
    context_object_name = 'container_list'
# Define the food index view function for a specific container
class FoodIndexView(ListView):
    model = ContainerFood
    template_name = 'food/index.html'
    context_object_name = 'food_list'
# create a new container
class ContainerCreate(CreateView):
    model = Container
    fields = ['name', 'container_type']
    template_name = 'containers/container_form.html'
    # if the container is created, redirect to the container detail page
    def get_success_url(self):
        return f'/my-foods/{self.object.pk}/'
# update a container This will allow users to change the name or type of container
class ContainerUpdate(UpdateView):
    model = Container
    fields = ['name', 'container_type']
    template_name = 'containers/container_form.html'
    # if the container is updated, redirect to the container detail page
    def get_success_url(self):
        return f'/my-foods/{self.object.pk}/'
# delete a container
class ContainerDelete(DeleteView):  
    model = Container
    template_name = 'containers/container_confirm_delete.html'
    # if the container is deleted, redirect to the container index
    def get_success_url(self):
        return '/my-foods/'