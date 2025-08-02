# This file defines URL patterns for the main application of the FridgeBuddy project.
# Import path to define URL routes
from django.urls import path
# Import views to connect routes to view functions
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Define the landing page route
    path('', views.home, name='home'),
    # Define the about page route
    path('about/', views.about, name='about'),

    # User-specific routes for managing containers and food items
    # Index of containers
    path('my-lists/', views.ContainerIndexView.as_view(), name='my-lists'),
    # Index of food in a specific container
    path('my-lists/<int:container_id>/', views.FoodIndexView.as_view(), name='food-index'),
    # Create a new container
    path('my-lists/create/', views.ContainerCreate.as_view(), name='container-create'),
    # Update a container
    path('my-lists/<int:pk>/update/', views.ContainerUpdate.as_view(), name='container-update'),
    # Delete a container
    path('my-lists/<int:pk>/delete/', views.ContainerDelete.as_view(), name='container-delete'),

    # Global food catalog routes
    # Index of food items catalog
    path('food-catalog/', views.FoodCatalogListView.as_view(), name='food-catalog'),
    # Detail view for a specific food item
    path('food-catalog/<int:pk>/', views.FoodDetailView.as_view(), name='food-detail'),
    path('food-catalog/create/', views.FoodCreate.as_view(), name='food-create'),
    # change the name, description, etc. of a food item
    path('food-catalog/<int:pk>/update/', views.FoodUpdate.as_view(), name='food-update'),
    # Delete a food item from the catalog (not from a container) *Danger*
    path('food-catalog/<int:pk>/delete/', views.FoodDelete.as_view(), name='food-delete'),

    # Path to user's dashboard (if implemented)
    # path('dashboard/', views.dashboard, name='dashboard'),  # Optional
    # Path to User's Container Index
    # path('my-lists/', views.user_container_index, name='user-container-index'),
    # Path to single User's Container Detail
    # path('my-lists/<int:container_id>/', views.user_container_detail, name='user-container-detail'),
    # Path to create a new container
    # path('my-lists/create/', views.user_container_create, name='user-container-create'),
    # Path to change a container's name or type
    # path('my-lists/<int:container_id>/update/', views.user_container_update, name='user-container-update'),
    # Path to delete a container
    # path('my-lists/<int:container_id>/delete/', views.user_container_delete, name='user-container-delete'),

    # Authentication routes
    # Login route
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Logout route
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Sign-up route (if using a custom view, replace with your view)
    path('accounts/signup/', views.signup, name='signup'),
]