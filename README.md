### INF601 - Advanced Programming in Python
### Htet Aung Hlaing
### Mini Project 4

# Project Title
Mini Project 4: Event Management and Booking Web Application

## Description
- This project is a full-stack event management and booking system built using **Django**.
- It allows users to register, log in, view events, and book available seats.
- Admins can add, edit, and delete events through the Django Admin panel.
- Users can also submit feedback and manage their bookings.

The app uses **Bootstrap 5** for a clean and responsive interface, including modals for confirmation dialogs, styled forms, and a mobile-friendly navigation bar.

## Getting Started

### Dependencies
* Install the required packages using:
```
pip install -r requirements.txt
```
* Set settings file location in the Django configuration. By default, it is `mysite\settings.py`

### Go to the Project Directory
* Move to the project directory by:
```commandline
cd EventBoard
```

### Database Setup
* Create and apply database migrations using:
```
python manage.py makemigrations
```
```
python manage.py migrate
```

### Create a Superuser (for Admin Access)
* Run the following command and follow the prompts:
```
python manage.py createsuperuser
```
* Then set up admin account by entering name, email, and password.

### Running the Server
* Start the Django development server with:
```
python manage.py runserver
```
* Then open your browser and visit:
http://127.0.0.1:8000/
* To access admin panel, open:
http://127.0.0.1:8000/admin and login using the created name and password.


## Features
* User registration, login, and logout
* Event listing with filtering and details page
* Seat booking system with seat availability tracking
* Booking history with cancellation confirmation modal
* Previous event filtering by time period
* Feedback form with interactive star rating system
* Django admin panel for event and user management
* Flash message system for user feedback (success/error)
* Responsive Bootstrap 5 design

## Authors
* Htet Aung Hlaing

## Version History
* 1.0
    * Complete Django event booking system
    * Styled pages for events, feedback, and bookings
    * Bootstrap 5 responsive layout integrated

## Acknowledgments
* [Django Documentation](https://docs.djangoproject.com/en/5.2/)
* [Bootstrap 5](https://getbootstrap.com/)
* [SQLite](https://www.sqlite.org/)
* [Django Tutorial](https://docs.djangoproject.com/en/5.2/intro/tutorial01/)
