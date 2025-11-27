# Cinema Ticketing API - Endpoints Documentation

## 📋 Overview

**Base URL**: `http://localhost:8000/api/v1`  
**API Documentation**: `http://localhost:8000/docs`  
**Total Endpoints**: 39 implemented

### Endpoint Categories:

- 🔐 Authentication (3)
- 🎬 Cinemas (6)
- 🏠 Rooms (3)
- 💺 Seats (2)
- 🎥 Movies (5)
- 📽️ Screenings (4)
- ⭐ Reviews (7)
- 🎫 Tickets (4)
- 👤 User Profile (6)

---

## 🔐 Authentication Endpoints

### Base Path: `/api/v1/auth`

| Method | Endpoint    | Description                                    | Auth Required |
| ------ | ----------- | ---------------------------------------------- | ------------- |
| `POST` | `/register` | Register a new user account                    | ❌            |
| `POST` | `/login`    | Login with email + password, returns JWT token | ❌            |
| `GET`  | `/me`       | Get current authenticated user profile         | ✅            |

---

## 🎬 Cinema Endpoints

### Base Path: `/api/v1/cinemas`

| Method | Endpoint                 | Description                                  | Auth Required |
| ------ | ------------------------ | -------------------------------------------- | ------------- |
| `POST` | `/`                      | Create a new cinema                          | ❌            |
| `GET`  | `/`                      | List all cinemas (with pagination)           | ❌            |
| `GET`  | `/{cinema_id}`           | Get cinema details by ID                     | ❌            |
| `GET`  | `/search`                | Search cinemas by name, city, or address     | ❌            |
| `GET`  | `/{cinema_id}/amenities` | Get list of amenities for a cinema           | ❌            |
| `GET`  | `/{cinema_id}/movies`    | Get all movies currently showing at a cinema | ❌            |

---

## 🏠 Room Endpoints

### Base Path: `/api/v1`

| Method | Endpoint                      | Description                   | Auth Required |
| ------ | ----------------------------- | ----------------------------- | ------------- |
| `POST` | `/cinemas/{cinema_id}/rooms/` | Create a new room in a cinema | ❌            |
| `GET`  | `/cinemas/{cinema_id}/rooms/` | List all rooms in a cinema    | ❌            |
| `GET`  | `/rooms/{room_id}`            | Get room details by ID        | ❌            |

---

## 💺 Seat Endpoints

### Base Path: `/api/v1`

| Method | Endpoint                      | Description                                             | Auth Required |
| ------ | ----------------------------- | ------------------------------------------------------- | ------------- |
| `POST` | `/rooms/{room_id}/seats/bulk` | Bulk create seats for a room (e.g., 10 rows × 15 seats) | ❌            |
| `GET`  | `/rooms/{room_id}/seats/`     | List all seats in a room                                | ❌            |

---

## 🎥 Movie Endpoints

### Base Path: `/api/v1/movies`

| Method   | Endpoint      | Description                        | Auth Required |
| -------- | ------------- | ---------------------------------- | ------------- |
| `POST`   | `/`           | Create a new movie                 | ❌            |
| `GET`    | `/`           | List all movies (with pagination)  | ❌            |
| `GET`    | `/{movie_id}` | Get movie details by ID            | ❌            |
| `PATCH`  | `/{movie_id}` | Update movie information (partial) | ❌            |
| `DELETE` | `/{movie_id}` | Delete a movie                     | ❌            |

---

## 📽️ Screening Endpoints

### Base Path: `/api/v1/screenings`

| Method | Endpoint                          | Description                                                  | Auth Required |
| ------ | --------------------------------- | ------------------------------------------------------------ | ------------- |
| `POST` | `/`                               | Create a new screening (showtime)                            | ❌            |
| `GET`  | `/`                               | List screenings (with filters: movie_id, room_id, cinema_id) | ❌            |
| `GET`  | `/{screening_id}`                 | Get screening details by ID                                  | ❌            |
| `GET`  | `/{screening_id}/available-seats` | Get available seats for a screening                          | ❌            |

---

## ⭐ Review Endpoints

### Base Path: `/api/v1/movies`

| Method   | Endpoint                      | Description                                      | Auth Required |
| -------- | ----------------------------- | ------------------------------------------------ | ------------- |
| `POST`   | `/{movie_id}/reviews`         | Create a new review for a movie (1-5 stars)      | ✅            |
| `GET`    | `/{movie_id}/reviews`         | Get paginated reviews for a movie (with sorting) | ❌            |
| `GET`    | `/{movie_id}/reviews/summary` | Get review summary with rating breakdown         | ❌            |
| `GET`    | `/reviews/{review_id}`        | Get a single review by ID                        | ❌            |
| `PUT`    | `/reviews/{review_id}`        | Update a review (author only)                    | ✅            |
| `DELETE` | `/reviews/{review_id}`        | Delete a review (soft delete, author only)       | ✅            |
| `POST`   | `/reviews/{review_id}/react`  | Add like/dislike reaction to a review            | ✅            |

---

## 🎫 Ticket Endpoints

### Base Path: `/api/v1/tickets`

| Method   | Endpoint       | Description                               | Auth Required |
| -------- | -------------- | ----------------------------------------- | ------------- |
| `POST`   | `/book`        | Book tickets for a screening              | ✅            |
| `GET`    | `/my-tickets`  | Get current user's tickets                | ✅            |
| `GET`    | `/{ticket_id}` | Get ticket details by ID                  | ✅            |
| `DELETE` | `/{ticket_id}` | Cancel a ticket (if cancellation allowed) | ✅            |

---

## 👤 User Profile Endpoints

### Base Path: `/api/v1/users`

| Method   | Endpoint              | Description                                        | Auth Required |
| -------- | --------------------- | -------------------------------------------------- | ------------- |
| `GET`    | `/me`                 | Get current user profile                           | ✅            |
| `PUT`    | `/me`                 | Update user profile (name, email)                  | ✅            |
| `PUT`    | `/me/preferences`     | Update user preferences (dark mode, notifications) | ✅            |
| `PUT`    | `/me/profile-picture` | Upload/update profile picture                      | ✅            |
| `DELETE` | `/me`                 | Delete user account (soft delete)                  | ✅            |
| `GET`    | `/{user_id}`          | Get public user profile by ID                      | ❌            |

---

## 🏥 Health Check

| Method | Endpoint | Description                          | Auth Required |
| ------ | -------- | ------------------------------------ | ------------- |
| `GET`  | `/`      | API health check and welcome message | ❌            |

---
