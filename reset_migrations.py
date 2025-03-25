import os
import shutil
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

def reset_migrations():
    # Remove database
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("Removed db.sqlite3")

    # Remove migration files for each app
    apps_to_reset = [
        'access_control', 'admin', 'auth', 'authentication', 'banking', 
        'clients', 'communication', 'contenttypes', 'documents', 'expenses', 
        'leads', 'people', 'products', 'project_management', 'projects', 
        'purchases', 'registration', 'reports', 'sales', 'sessions', 'site_admin'
    ]

    for app in apps_to_reset:
        migration_dir = os.path.join(settings.BASE_DIR, app, 'migrations')
        if os.path.exists(migration_dir):
            for filename in os.listdir(migration_dir):
                if filename != '__init__.py' and filename.endswith('.py'):
                    file_path = os.path.join(migration_dir, filename)
                    os.remove(file_path)
                    print(f"Removed {file_path}")

    print("Migration reset complete. Run 'python manage.py makemigrations' and then 'python manage.py migrate'.")

if __name__ == '__main__':
    reset_migrations()
