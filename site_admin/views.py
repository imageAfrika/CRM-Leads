from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, NoReverseMatch
from django.apps import apps
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import router, models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.forms import modelform_factory, inlineformset_factory
from .models import AdminLog
import json


# Add login view for our site admin
def login_view(request):
    """
    Custom login view for the site admin.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next', reverse('site_admin:index'))
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password, or insufficient permissions.')
    
    return render(request, 'site_admin/login.html', {
        'title': 'Site Admin Login',
    })


def superuser_required(view_func=None):
    """
    Decorator for views that checks that the user is a superuser.
    """
    decorator = login_required(login_url='site_admin:login')
    if view_func:
        return decorator(view_func)
    return decorator


@login_required(login_url='site_admin:login')
def index(request):
    """
    Display admin dashboard with links to each registered app and model.
    """
    # Get all installed Django apps
    from django.apps import apps
    from django.contrib.auth.models import User
    
    # Prepare the app list
    app_list = []
    
    # Track total models for stats
    total_models_count = 0
    
    for app_config in apps.get_app_configs():
        # Skip some built-in apps
        if app_config.name in ['admin', 'contenttypes', 'sessions', 'messages', 'staticfiles']:
            continue
        
        # Get models for this app
        models = []
        for model in app_config.get_models():
            # Check if user has permission to view this model
            if has_model_permission(request.user, model, 'view'):
                models.append({
                    'name': model.__name__,
                    'verbose_name': model._meta.verbose_name,
                    'verbose_name_plural': model._meta.verbose_name_plural,
                    'add_url': reverse('site_admin:model_add', args=[app_config.label, model.__name__.lower()]),
                    'list_url': reverse('site_admin:model_list', args=[app_config.label, model.__name__.lower()])
                })
                total_models_count += 1
        
        if models:
            app_list.append({
                'name': app_config.name,
                'verbose_name': app_config.verbose_name,
                'models': models
            })
    
    # Get recent actions
    recent_actions = AdminLog.objects.all().order_by('-timestamp')[:10]
    
    # Get dashboard statistics
    total_users = User.objects.count()
    recent_actions_count = AdminLog.objects.count()
    total_apps = len(app_list)
    
    context = {
        'title': 'Site Admin',
        'app_list': app_list,
        'recent_actions': recent_actions,
        'total_users': total_users,
        'total_models': total_models_count,
        'recent_actions_count': recent_actions_count,
        'total_apps': total_apps
    }
    
    return render(request, 'site_admin/index.html', context)


def has_model_permission(user, model, action):
    """
    Check if user has permission for the given model and action.
    """
    if not user.is_active:
        return False
    
    if user.is_superuser:
        return True
    
    opts = model._meta
    codename = get_permission_codename(action, opts)
    return user.has_perm(f"{opts.app_label}.{codename}")


@login_required(login_url='site_admin:login')
def model_list(request, app_label, model_name):
    """
    View for listing objects of a specific model.
    """
    model = apps.get_model(app_label, model_name)
    
    # Check permissions
    if not has_model_permission(request.user, model, 'view'):
        raise Http404
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        # Get all text fields for searching
        search_fields = [f.name for f in model._meta.fields if isinstance(f, (models.CharField, models.TextField))]
        
        # Build dynamic Q objects for search
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f"{field}__icontains": search_query})
        
        queryset = model.objects.filter(q_objects)
    else:
        queryset = model.objects.all()
    
    # Order by primary key by default
    queryset = queryset.order_by('-pk')
    
    # Pagination
    paginator = Paginator(queryset, 20)  # Show 20 items per page
    page = request.GET.get('page')
    objects = paginator.get_page(page)
    
    # Determine display fields (first five fields by default)
    fields = [f.name for f in model._meta.fields[:5]]
    list_display = fields
    
    # Context
    context = {
        'app_label': app_label,
        'model_name': model_name,
        'model_verbose_name': model._meta.verbose_name,
        'model_verbose_name_plural': model._meta.verbose_name_plural,
        'objects': objects,
        'list_display': list_display,
        'search_query': search_query,
        'has_add_permission': has_model_permission(request.user, model, 'add'),
        'has_change_permission': has_model_permission(request.user, model, 'change'),
        'has_delete_permission': has_model_permission(request.user, model, 'delete'),
        'add_url': reverse('site_admin:model_add', kwargs={'app_label': app_label, 'model_name': model_name}),
    }
    
    return render(request, 'site_admin/model_list.html', context)


@login_required(login_url='site_admin:login')
def model_add(request, app_label, model_name):
    """
    View for adding a new object of a specific model.
    """
    model = apps.get_model(app_label, model_name)
    
    # Check permissions
    if not has_model_permission(request.user, model, 'add'):
        raise Http404
    
    # Create a ModelForm for the model
    ModelForm = modelform_factory(model, exclude=[])
    
    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save()
            
            # Log the addition
            AdminLog.objects.create(
                user=request.user,
                content_type=ContentType.objects.get_for_model(model),
                object_id=str(new_object.pk),
                object_repr=str(new_object),
                action_flag=1,  # Addition
                change_message=json.dumps([{'added': {}}]),
            )
            
            messages.success(request, f'The {model._meta.verbose_name} was added successfully.')
            return redirect('site_admin:model_list', app_label=app_label, model_name=model_name)
    else:
        form = ModelForm()
    
    context = {
        'form': form,
        'model': model,
        'app_label': app_label,
        'model_name': model_name,
        'model_verbose_name': model._meta.verbose_name,
        'title': f'Add {model._meta.verbose_name}',
        'is_add': True,
    }
    
    return render(request, 'site_admin/model_form.html', context)


@login_required(login_url='site_admin:login')
def model_change(request, app_label, model_name, object_id):
    """View for editing an existing model instance."""
    if not request.user.is_staff:
        messages.error(request, "You don't have access to the site admin.")
        return redirect('/')
    
    # Get model and object
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        raise Http404(f"Model {app_label}.{model_name} not found")
    
    obj = get_object_or_404(model, pk=object_id)
    
    # Check permissions
    if not has_model_permission(request.user, model, 'change'):
        messages.error(request, f"You don't have permission to change {model._meta.verbose_name}")
        return redirect('site_admin:model_list', app_label=app_label, model_name=model_name)
    
    # Create form
    ModelForm = modelform_factory(model, exclude=[])
    
    # Find related models for inline formsets
    inline_formsets = []
    for related_object in model._meta.related_objects:
        if related_object.related_model and related_object.field.name != 'content_type':
            related_model = related_object.related_model
            fk_name = related_object.field.name
            
            # Skip many-to-many relationships for simplicity
            if related_object.many_to_many:
                continue
                
            # Create inline formset factory
            FormSet = inlineformset_factory(
                model, related_model, 
                exclude=[], 
                extra=1, 
                can_delete=True
            )
            
            # Add the formset to the list
            inline_formsets.append({
                'model': related_model,
                'formset': FormSet(request.POST if request.method == 'POST' else None, 
                                  request.FILES if request.method == 'POST' else None,
                                  instance=obj),
                'prefix': related_model._meta.model_name
            })
    
    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES, instance=obj)
        
        # Check if the main form and all inline formsets are valid
        if form.is_valid() and all([formset_data['formset'].is_valid() for formset_data in inline_formsets]):
            # Save the main form
            form.save()
            
            # Save all inline formsets
            for formset_data in inline_formsets:
                formset_data['formset'].save()
                
            messages.success(request, f"{model._meta.verbose_name} was updated successfully.")
            return redirect('site_admin:model_list', app_label=app_label, model_name=model_name)
    else:
        form = ModelForm(instance=obj)
    
    context = {
        'app_label': app_label,
        'model_name': model_name,
        'model_verbose_name': model._meta.verbose_name,
        'object': obj,
        'form': form,
        'is_add': False,
        'title': f"Change {model._meta.verbose_name}",
        'has_delete_permission': has_model_permission(request.user, model, 'delete'),
        'delete_url': reverse('site_admin:model_delete', kwargs={'app_label': app_label, 'model_name': model_name, 'object_id': object_id}),
        'inline_formsets': [formset_data['formset'] for formset_data in inline_formsets]
    }
    
    # Use the model_change_form.html template if there are inline formsets
    template = 'site_admin/model_change_form.html' if inline_formsets else 'site_admin/model_form.html'
    return render(request, template, context)


@login_required(login_url='site_admin:login')
def model_delete(request, app_label, model_name, object_id):
    """
    View for deleting an object of a specific model.
    """
    model = apps.get_model(app_label, model_name)
    
    # Check permissions
    if not has_model_permission(request.user, model, 'delete'):
        raise Http404
    
    # Get the object
    obj = get_object_or_404(model, pk=object_id)
    
    # Get related objects that will be deleted
    using = router.db_for_write(model)
    collector = NestedObjects(using=using)
    collector.collect([obj])
    
    related_objects = []
    for related_model, related_objs in collector.model_objs.items():
        if related_model != model:
            related_objects.append({
                'related_model': related_model._meta.verbose_name,
                'count': len(related_objs)
            })
    
    # Get object data for display
    object_data = {}
    for field in model._meta.fields:
        value = getattr(obj, field.name)
        # Format the value for display
        if callable(value):
            value = value()
        object_data[field.verbose_name] = value
    
    if request.method == 'POST':
        obj.delete()
        
        # Log the deletion
        AdminLog.objects.create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(model),
            object_id=str(object_id),
            object_repr=str(obj),
            action_flag=3,  # Deletion
            change_message='',
        )
        
        messages.success(request, f'The {model._meta.verbose_name} was deleted successfully.')
        return redirect('site_admin:model_list', app_label=app_label, model_name=model_name)
    
    context = {
        'app_label': app_label,
        'model_name': model_name,
        'model_verbose_name': model._meta.verbose_name,
        'object': obj,
        'object_data': object_data,
        'related_objects': related_objects,
    }
    
    return render(request, 'site_admin/model_delete.html', context)


@superuser_required
def user_management(request):
    """
    View for managing users.
    """
    users = User.objects.all().order_by('username')
    
    context = {
        'users': users,
        'title': 'User management',
    }
    
    return render(request, 'site_admin/user_management.html', context)


@superuser_required
def group_management(request):
    """
    View for managing groups.
    """
    groups = Group.objects.all().annotate(user_count=Count('user')).order_by('name')
    
    context = {
        'groups': groups,
        'title': 'Group management',
    }
    
    return render(request, 'site_admin/group_management.html', context)


def dark_mode_test(request):
    """
    View for testing dark mode implementation across UI components.
    """
    return render(request, 'site_admin/dark_mode_test.html')
