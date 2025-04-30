# Player Stats Explorer

A Django application for exploring basketball player statistics.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```
   python manage.py makemigrations player_stats
   python manage.py migrate
   ```
6. Create a superuser (for admin access):
   ```
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```
8. Access the application at http://127.0.0.1:8000/

## Features

- Search for basketball players
- View predicted stats for the upcoming season
- View historical performance data

## Admin Interface

Access the admin interface at http://127.0.0.1:8000/admin/ to add, edit, or delete player data.
