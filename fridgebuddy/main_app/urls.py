from django.urls import path
# Import views to connect routes to view functions
from . import views 

urlpatterns = [
    # Define the landing page route
    path('', views.home, name='home'),
    # Define the about page route
    path('about/', views.about, name='about'),

    # User-specific routes for managing containers and food items
    # Index of containers
    path('my-foods/', views.container_index, name='container-index'),
    # Index of food in a specific container
    path('my-foods/<int:container_id>/', views.food_index, name='food-index'),
    # Create a new container
    path('my-foods/create/', views.ContainerCreate.as_view(), name='container-create'),
    # Update a container
    path('my-foods/<int:pk>/update/', views.ContainerUpdate.as_view(), name='container-update'),
    # Delete a container
    path('my-foods/<int:pk>/delete/', views.ContainerDelete.as_view(), name='container-delete'),

    # Global food catalog routes
    # Index of food items catalog
    path('food-catalog/', views.food_catalog, name='food-catalog'),
    # Detail view for a specific food item
    path('food/<int:food_id>/', views.food_detail, name='food-detail'),
    path('food/create/', views.FoodCreate.as_view(), name='food-create'),
    # change the name, description, etc. of a food item
    path('food/<int:pk>/update/', views.FoodUpdate.as_view(), name='food-update'),
    # Delete a food item from the catalog (not from a container) *Danger*
    path('food/<int:pk>/delete/', views.FoodDelete.as_view(), name='food-delete'),
   
]