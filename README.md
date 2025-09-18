# Internship Recommender System

A web application that helps students find suitable internships based on their skills, preferences, and profile. Built with FastAPI, MongoDB, and a modern HTML/CSS/JS frontend.

## Features
- User registration and login (JWT authentication)
- Create, update, and manage student profiles
- Get personalized internship recommendations
- Browse random internships on the front page
- Modern, aesthetic UI with robust error handling

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/harsh6125/internship-recommendation.git
   cd internship-recommendation
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start MongoDB and ensure it is running locally.
4. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
5. Open `index.html` in your browser for the frontend.

## Usage
- Register a new user and log in.
- Create your student profile.
- Click "Get Recommendations" to see internships tailored to you.
- Browse random internships on the home page.

## API Endpoints
- `POST /users/register` — Register a new user
- `POST /token` — Login and get JWT token
- `POST /profile` — Create student profile (auth required)
- `GET /profile` — Get your profile (auth required)
- `PUT /profile` — Update your profile (auth required)
- `GET /internships/random` — Get random internships
- `GET /recommendations/{student_id}` — Get recommendations for a student

## Technologies Used
- FastAPI (Python)
- MongoDB
- HTML, CSS, JavaScript

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.
