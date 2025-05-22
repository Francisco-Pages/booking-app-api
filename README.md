# Booking Manager API

A backend API built with Django for managing residential property bookings. This project is designed to serve as the core of a property rental platform, handling property listings, availability, and booking operations. The application is containerized using Docker for ease of deployment and scalability.

## Features

- Django-based REST API
- Dockerized for easy deployment
- Dev/Prod dependency separation
- Manage properties and bookings (WIP)
- Ready for testing and future expansion

## Project Structure

booking-app-api/
├── booking_app/          # Django project directory
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose config
├── requirements.txt      # Production dependencies
├── requirements.dev.txt  # Development dependencies
└── README.md             # You’re reading it!

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Francisco-Pages/booking-app-api.git
cd booking-app-api
```
2. Run with Docker

Make sure you have Docker and Docker Compose installed.
```bash
docker-compose up --build
```
3. Access the application

Once the containers are running, you can access the Django development server at:

http://localhost:8000/

Development

To install dependencies for development:
```bash
pip install -r requirements.dev.txt
```
Use the Django CLI to run the server locally:
```bash
python manage.py runserver
```

TODO
	•	Implement user authentication
	•	Add property listing and booking models
	•	Create REST API endpoints
	•	Add automated tests
	•	Improve API documentation

Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

License

This project is licensed under the MIT License.
