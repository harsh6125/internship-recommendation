
# Internship Recommender System

An intelligent web application that helps students discover and apply for internships tailored to their skills, preferences, and goals. Built with FastAPI, MongoDB, and a modern HTML/CSS/JavaScript frontend.

---

## 🚀 Features

- Secure user registration and login (JWT authentication)
- Create, update, and manage student profiles
- Personalized internship recommendations based on your profile
- Browse random internships on the home page
- Clean, modern, and responsive UI
- Robust error handling and user feedback

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/harsh6125/internship-recommendation.git
   cd internship-recommendation
   ```
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start MongoDB:**
   - Make sure MongoDB is running locally (default: `mongodb://localhost:27017`).
4. **Run the FastAPI backend:**
   ```bash
   uvicorn main:app --reload
   ```
5. **Open the frontend:**
   - Open `index.html` in your browser.

---

## 💡 Usage Guide

1. **Register:** Create a new account with a unique username and password.
2. **Login:** Log in to receive a secure access token.
3. **Create Profile:** Fill out your student profile with skills, preferences, and expectations.
4. **Get Recommendations:** Click "Get Recommendations" to view internships matched to your profile.
5. **Browse Internships:** See random internships on the home page, even before logging in.

---

## 📚 API Overview

| Endpoint                       | Method | Description                                 |
|--------------------------------|--------|---------------------------------------------|
| `/users/register`              | POST   | Register a new user                         |
| `/token`                       | POST   | Login and receive JWT token                 |
| `/profile`                     | POST   | Create student profile (auth required)      |
| `/profile`                     | GET    | Get your profile (auth required)            |
| `/profile`                     | PUT    | Update your profile (auth required)         |
| `/profile/{student_id}`        | GET    | Get a student profile by ID                 |
| `/profile/{student_id}`        | PUT    | Update a student profile by ID              |
| `/profile/{student_id}`        | DELETE | Delete a student profile by ID              |
| `/internships/random`          | GET    | Get random internships                      |
| `/recommendations/{student_id}`| GET    | Get recommendations for a student           |

---

## 🧰 Technologies Used

- **FastAPI** — Backend API framework (Python)
- **MongoDB** — NoSQL database for storing users, profiles, internships
- **Pydantic** — Data validation and serialization
- **Uvicorn** — ASGI server for running FastAPI
- **HTML, CSS, JavaScript** — Frontend UI

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions, bug reports, or want to add features, please open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
