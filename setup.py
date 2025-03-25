#!/usr/bin/env python

"""
Setup script for CRM-Leads project with django-tenants
"""

import os
import sys
import subprocess
import importlib.util

def run_command(command):
    """Run a command and return its output"""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    returncode = process.returncode
    return returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

def check_import(module_name):
    """Check if a module can be imported"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def install_requirements():
    """Install required packages"""
    print("\n=== Installing requirements ===")
    
    if not os.path.exists('requirements.txt'):
        print("Error: requirements.txt not found!")
        return False
    
    print("Installing required packages from requirements.txt...")
    returncode, stdout, stderr = run_command('pip install -r requirements.txt')
    
    if returncode != 0:
        print(f"Error installing requirements: {stderr}")
        return False
    
    print("Requirements installed successfully!")
    return True

def check_postgres():
    """Check PostgreSQL setup"""
    print("\n=== Checking PostgreSQL setup ===")
    
    # Check if psycopg2 is installed
    if not check_import('psycopg2'):
        print("psycopg2 is not installed. Installing...")
        returncode, stdout, stderr = run_command('pip install psycopg2')
        if returncode != 0:
            print(f"Error installing psycopg2: {stderr}")
            print("Please install PostgreSQL and try again.")
            return False
    
    # Run the check_postgres.py script
    if os.path.exists('check_postgres.py'):
        print("Running PostgreSQL check script...")
        returncode, stdout, stderr = run_command('python check_postgres.py')
        if returncode != 0:
            print(f"PostgreSQL check failed: {stderr}")
            return False
        print(stdout)
    else:
        print("Warning: check_postgres.py not found!")
        # Try basic PostgreSQL connection test
        try:
            import psycopg2
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            )
            conn.close()
            print("Successfully connected to PostgreSQL!")
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {str(e)}")
            return False
    
    return True

def setup_database():
    """Setup database for django-tenants"""
    print("\n=== Setting up database ===")
    
    if os.path.exists('setup_postgres.py'):
        print("Running PostgreSQL setup script...")
        returncode, stdout, stderr = run_command('python setup_postgres.py')
        if returncode != 0:
            print(f"PostgreSQL setup failed: {stderr}")
            return False
        print(stdout)
    else:
        print("Warning: setup_postgres.py not found!")
        proceed = input("Do you want to proceed without running the setup_postgres.py script? (y/n): ")
        if proceed.lower() != 'y':
            return False
    
    return True

def create_apps():
    """Create and set up the tenants and leads apps"""
    print("\n=== Setting up Django apps ===")
    
    # Create tenants app
    if os.path.exists('create_tenants_app.py'):
        print("Running tenants app setup script...")
        returncode, stdout, stderr = run_command('python create_tenants_app.py')
        if returncode != 0:
            print(f"Tenants app setup failed: {stderr}")
            return False
        print(stdout)
    else:
        print("Warning: create_tenants_app.py not found!")
    
    # Create leads app
    if os.path.exists('create_leads_app.py'):
        print("Running leads app setup script...")
        returncode, stdout, stderr = run_command('python create_leads_app.py')
        if returncode != 0:
            print(f"Leads app setup failed: {stderr}")
            return False
        print(stdout)
    else:
        print("Warning: create_leads_app.py not found!")
    
    return True

def run_migrations():
    """Run Django migrations"""
    print("\n=== Running migrations ===")
    
    # Make migrations for tenants app
    print("Creating migrations for tenants app...")
    returncode, stdout, stderr = run_command('python manage.py makemigrations tenants')
    if returncode != 0:
        print(f"Error creating migrations for tenants app: {stderr}")
        return False
    print(stdout)
    
    # Make migrations for leads app
    print("Creating migrations for leads app...")
    returncode, stdout, stderr = run_command('python manage.py makemigrations leads')
    if returncode != 0:
        print(f"Error creating migrations for leads app: {stderr}")
        return False
    print(stdout)
    
    # Apply shared migrations
    print("Applying shared migrations...")
    returncode, stdout, stderr = run_command('python manage.py migrate_schemas --shared')
    if returncode != 0:
        print(f"Error applying shared migrations: {stderr}")
        # Let's try without the custom command
        print("Trying standard migrate command...")
        returncode, stdout, stderr = run_command('python manage.py migrate')
        if returncode != 0:
            print(f"Error applying migrations: {stderr}")
            return False
    print(stdout)
    
    # Apply all migrations
    print("Applying all migrations...")
    returncode, stdout, stderr = run_command('python manage.py migrate_schemas')
    if returncode != 0:
        print(f"Error applying all migrations: {stderr}")
        # Let's try without the custom command
        print("Trying standard migrate command...")
        returncode, stdout, stderr = run_command('python manage.py migrate')
        if returncode != 0:
            print(f"Error applying migrations: {stderr}")
            return False
    print(stdout)
    
    return True

def create_superuser():
    """Create a superuser for Django admin"""
    print("\n=== Creating superuser ===")
    
    create_user = input("Do you want to create a superuser? (y/n): ")
    if create_user.lower() == 'y':
        print("Creating superuser...")
        returncode, stdout, stderr = run_command('python manage.py createsuperuser')
        if returncode != 0:
            print(f"Error creating superuser: {stderr}")
            return False
        print(stdout)
    
    return True

def start_server():
    """Start the Django development server"""
    print("\n=== Starting development server ===")
    
    start = input("Do you want to start the development server? (y/n): ")
    if start.lower() == 'y':
        print("Starting development server...")
        # This will block until the server is stopped
        os.system('python manage.py runserver')
    else:
        print("\nTo start the server later, run: python manage.py runserver")
    
    return True

def main():
    """Main setup function"""
    print("=== CRM-Leads Setup ===")
    print("This script will set up your CRM-Leads project with django-tenants.")
    
    # Ask confirmation before proceeding
    proceed = input("Do you want to proceed with the setup? (y/n): ")
    if proceed.lower() != 'y':
        print("Setup cancelled.")
        return
    
    # Step 1: Install requirements
    if not install_requirements():
        print("Failed to install requirements. Please fix the issues and try again.")
        return
    
    # Step 2: Check PostgreSQL
    if not check_postgres():
        print("PostgreSQL setup check failed. Please fix the issues and try again.")
        return
    
    # Step 3: Set up the database
    if not setup_database():
        print("Database setup failed. Please fix the issues and try again.")
        return
    
    # Step 4: Create and set up the apps
    if not create_apps():
        print("App setup failed. Please fix the issues and try again.")
        return
    
    # Step 5: Run migrations
    if not run_migrations():
        print("Migrations failed. Please fix the issues and try again.")
        return
    
    # Step 6: Create superuser
    if not create_superuser():
        print("Superuser creation failed. You can create one later with: python manage.py createsuperuser")
    
    # Step 7: Start server
    if not start_server():
        print("Server start failed. You can start it later with: python manage.py runserver")
    
    print("\n=== Setup Complete ===")
    print("Your CRM-Leads project is now set up and ready to use!")
    print("\nNext steps:")
    print("1. Access the admin interface at: http://localhost:8000/admin/")
    print("2. Create a tenant and domain in the admin interface")
    print("3. Access the tenant site at the domain you created")
    print("4. Start managing leads for your clients!")

if __name__ == "__main__":
    main() 