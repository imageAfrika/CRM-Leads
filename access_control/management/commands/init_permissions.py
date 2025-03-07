from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings

from access_control.models import AppPermission

class Command(BaseCommand):
    help = 'Initialize permissions for installed apps'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of permissions',
        )
    
    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # Get all installed apps
        installed_apps = [app for app in apps.get_app_configs() if app.name not in [
            'admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles'
        ]]
        
        # Define common features for apps
        common_features = {
            'dashboard': 'Dashboard',
            'reports': 'Reports',
            'settings': 'Settings',
        }
        
        # Define permission types
        permission_types = [
            ('view', 'View'),
            ('add', 'Add'),
            ('change', 'Change'),
            ('delete', 'Delete'),
            ('full', 'Full Access'),
        ]
        
        # Create permissions for each app
        for app in installed_apps:
            self.stdout.write(f"Processing app: {app.name}")
            
            # Create app-level permissions
            for perm_type, perm_name in permission_types:
                # Check if permission already exists
                perm_exists = AppPermission.objects.filter(
                    app_name=app.name,
                    feature=None,
                    permission_type=perm_type
                ).exists()
                
                if not perm_exists or force:
                    if perm_exists and force:
                        # Delete existing permission if force is True
                        AppPermission.objects.filter(
                            app_name=app.name,
                            feature=None,
                            permission_type=perm_type
                        ).delete()
                    
                    # Create permission
                    AppPermission.objects.create(
                        name=f"{app.verbose_name} - {perm_name}",
                        app_name=app.name,
                        feature=None,
                        permission_type=perm_type,
                        description=f"{perm_name} permission for {app.verbose_name} app"
                    )
                    self.stdout.write(f"  Created permission: {app.verbose_name} - {perm_name}")
            
            # Create feature-level permissions
            for feature_key, feature_name in common_features.items():
                for perm_type, perm_name in permission_types:
                    # Check if permission already exists
                    perm_exists = AppPermission.objects.filter(
                        app_name=app.name,
                        feature=feature_key,
                        permission_type=perm_type
                    ).exists()
                    
                    if not perm_exists or force:
                        if perm_exists and force:
                            # Delete existing permission if force is True
                            AppPermission.objects.filter(
                                app_name=app.name,
                                feature=feature_key,
                                permission_type=perm_type
                            ).delete()
                        
                        # Create permission
                        AppPermission.objects.create(
                            name=f"{app.verbose_name} - {feature_name} - {perm_name}",
                            app_name=app.name,
                            feature=feature_key,
                            permission_type=perm_type,
                            description=f"{perm_name} permission for {feature_name} in {app.verbose_name} app"
                        )
                        self.stdout.write(f"  Created permission: {app.verbose_name} - {feature_name} - {perm_name}")
        
        self.stdout.write(self.style.SUCCESS('Successfully initialized permissions for all apps')) 