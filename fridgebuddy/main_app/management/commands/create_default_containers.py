"""
Django management command to create default containers for existing users.

This command is useful when:
1. The default container creation signal was added after users were already created
2. You need to retroactively add containers to existing users
3. Some users are missing their default containers for any reason

Usage: python manage.py create_default_containers
"""

# Import Django's base command class for creating custom management commands
from django.core.management.base import BaseCommand
# Import Django's built-in User model for accessing user accounts
from django.contrib.auth.models import User
# Import our custom Container model from the main app
from main_app.models import Container

class Command(BaseCommand):
    """
    Management command to create default containers for users who don't have them.
    
    This command iterates through all users and creates any missing default containers
    (Fridge, Freezer, Pantry, Shopping List) that they should have.
    """
    
    # Help text that appears when running: python manage.py help create_default_containers
    help = 'Create default containers for users who do not have them'

    def handle(self, *args, **options):
        """
        Main method that executes when the command is run.
        
        Args:
            *args: Positional arguments passed to the command (unused)
            **options: Keyword arguments passed to the command (unused)
        """
        # Inform the user that the command is starting
        self.stdout.write('Creating default containers for users...')
        
        # Define the standard containers that every user should have
        # Each container has a human-readable name and a type constant
        default_containers = [
            {'name': 'Fridge', 'container_type': 'FRIDGE'},
            {'name': 'Freezer', 'container_type': 'FREEZER'},
            {'name': 'Pantry', 'container_type': 'PANTRY'},
            {'name': 'Shopping List', 'container_type': 'SHOPPING'},
        ]
        
        # Initialize counters to track the command's progress and results
        users_updated = 0      # Number of users who received new containers
        containers_created = 0 # Total number of containers created
        
        # Iterate through every user in the system
        for user in User.objects.all():
            # Get all containers currently owned by this user
            user_containers = Container.objects.filter(owner=user)
            
            # Create a set of container types the user already has
            # This allows for fast lookup to avoid creating duplicates
            existing_types = set(user_containers.values_list('container_type', flat=True))
            
            # Track if any containers were created for this specific user
            user_got_new_containers = False
            
            # Check each default container type
            for container_data in default_containers:
                # Only create container if user doesn't already have this type
                if container_data['container_type'] not in existing_types:
                    # Create the missing container for this user
                    Container.objects.create(owner=user, **container_data)
                    
                    # Increment counters
                    containers_created += 1
                    user_got_new_containers = True
                    
                    # Log the creation for transparency
                    self.stdout.write(f'Created {container_data["name"]} for {user.username}')
            
            # If this user received any new containers, count them
            if user_got_new_containers:
                users_updated += 1
        
        # Display final summary of what was accomplished
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {containers_created} containers for {users_updated} users'
            )
        )
