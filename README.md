# CRM-Leads

A multi-tenant CRM system for managing leads built with Django and django-tenants.

## Features

- 🏢 **Multi-tenant architecture**: Isolated data for each client using PostgreSQL schemas
- 📊 **Lead management**: Track leads through various stages of your sales pipeline
- 📝 **Activity tracking**: Log all interactions with leads
- 👥 **User assignments**: Assign leads to specific team members
- 📱 **Responsive design**: Works on desktop and mobile devices

## Requirements

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Django 5.0 or higher

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/CRM-Leads.git
cd CRM-Leads
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Make sure PostgreSQL is installed and running on your system. You can download it from [https://www.postgresql.org/download/](https://www.postgresql.org/download/).

### 5. Run the setup script

We've created a setup script that will guide you through the entire setup process:

```bash
python setup.py
```

This script will:
- Check PostgreSQL installation
- Configure the database
- Set up the Django apps
- Run migrations
- Create a superuser
- Start the development server

### Manual Setup (if setup.py fails)

If the setup script doesn't work, you can follow these steps manually:

1. Verify PostgreSQL connection:
```bash
python check_postgres.py
```

2. Configure the database:
```bash
python setup_postgres.py
```

3. Create the tenants app:
```bash
python create_tenants_app.py
```

4. Create the leads app:
```bash
python create_leads_app.py
```

5. Run migrations:
```bash
python manage.py makemigrations tenants
python manage.py makemigrations leads
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

## Usage

### Creating Tenants

1. Access the admin interface at `http://localhost:8000/admin/`
2. Log in with the superuser credentials you created during setup
3. Go to "Clients" and click "Add Client"
4. Fill in the client details and save
5. Add a domain for the client (e.g., `client1.localhost`)

### Accessing Tenant Sites

To access a tenant's site, you need to use the domain you registered for the tenant. For local development, you can:

1. Add entries to your hosts file:
   - Windows: `C:\Windows\System32\drivers\etc\hosts`
   - Linux/Mac: `/etc/hosts`

   Add lines like:
   ```
   127.0.0.1 client1.localhost
   127.0.0.1 client2.localhost
   ```

2. Access the tenant site at `http://client1.localhost:8000/`

### Managing Leads

1. Log in to a tenant site
2. Navigate to the Leads section
3. Create, view, and update leads
4. Track activities for each lead

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'django_tenants'**
   - Make sure `django-tenants` is installed: `pip install django-tenants`
   - Check that 'django_tenants' is in INSTALLED_APPS in settings.py

2. **PostgreSQL connection issues**
   - Verify PostgreSQL is running
   - Check the connection settings in settings.py
   - Ensure the user has appropriate permissions

3. **Tenant creation issues**
   - Make sure the PostgreSQL user has CREATE DATABASE privileges
   - Verify that the database engine is set to 'django_tenants.postgresql_backend'

4. **DLL load failed while importing _psycopg**
   - This is often due to missing PostgreSQL client libraries
   - Try installing `psycopg2-binary` instead: `pip install psycopg2-binary`
   - On Windows, make sure the PostgreSQL bin directory is in your PATH
   - Alternatively, copy the PostgreSQL DLLs to your Python DLLs directory:
     ```
     # Find where your PostgreSQL is installed
     # Copy libpq.dll and other required DLLs from PostgreSQL\bin to Python\DLLs
     ```
   - Using the binary version with the `--no-deps` flag can also help:
     ```
     pip uninstall -y psycopg2 psycopg2-binary
     pip install --no-deps psycopg2-binary
     ```

5. **Path environment conflicts**
   - If you have multiple Python environments, make sure you're using the correct one
   - Use the full path to your Python executable in the correct environment:
     ```
     C:\path\to\your\venv\Scripts\python.exe -m pip install psycopg2-binary
     ```

### Using Pre-compiled Wheels

If you continue to have issues with psycopg2, try using pre-compiled wheels:

1. Download the appropriate wheel for your Python version from [Christoph Gohlke's website](https://www.lfd.uci.edu/~gohlke/pythonlibs/#psycopg)
2. Install the wheel directly:
```bash
pip install C:\path\to\downloaded\psycopg2-2.9.10-cp310-cp310-win_amd64.whl
```

### Getting Help

If you encounter any issues not covered here, please open an issue on GitHub.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [django-tenants](https://django-tenants.readthedocs.io/)
- [Bootstrap](https://getbootstrap.com/)
