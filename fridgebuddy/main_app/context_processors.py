from .models import Container

def shopping_list_context(request):
    """
    Context processor to add shopping list data to all templates
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            # Get or create user's shopping list
            shopping_list, created = Container.objects.get_or_create(
                owner=request.user,
                container_type='SHOPPING',
                defaults={
                    'name': 'Shopping List',
                    'description': 'Your personal shopping list'
                }
            )
            
            # Get shopping list items count
            shopping_count = shopping_list.items.count()
            
            context['shopping_list_count'] = shopping_count
            context['has_shopping_items'] = shopping_count > 0
            
        except Exception:
            # If anything goes wrong, set safe defaults
            context['shopping_list_count'] = 0
            context['has_shopping_items'] = False
    else:
        context['shopping_list_count'] = 0
        context['has_shopping_items'] = False
    
    return context
