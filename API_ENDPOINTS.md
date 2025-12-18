# Cinema Ticketing API - Endpoints Documentation

**Legend:**

- 🔐 = Admin authorization required
- ✅ = User authentication required
- ❌ = No authentication required

---

## Health Check

**GET** `/` - API health check and welcome message ❌

---

## Authentication

**POST** `/api/v1/auth/register` - Register User ❌  
**POST** `/api/v1/auth/login` - Login ❌  
**GET** `/api/v1/auth/me` - Read Users Me ✅  
**POST** `/api/v1/auth/logout` - Logout ✅  
**PUT** `/api/v1/auth/change-password` - Change Password ✅  
**POST** `/api/v1/auth/refresh-token` - Refresh Token ✅  
**POST** `/api/v1/auth/forgot-password` - Forgot Password ❌  
**POST** `/api/v1/auth/reset-password` - Reset Password ❌

---

## Favorites

**POST** `/api/v1/cinemas/{cinema_id}/favorite` - Add Cinema To Favorites ✅  
**DELETE** `/api/v1/cinemas/{cinema_id}/favorite` - Remove Cinema From Favorites ✅  
**GET** `/api/v1/cinemas/favorites` - Get User Favorite Cinemas ✅

---

## Cinemas

**POST** `/api/v1/cinemas/` - Create Cinema 🔐  
**GET** `/api/v1/cinemas/` - List Cinemas ❌  
**GET** `/api/v1/cinemas/search` - Search Cinemas ❌  
**GET** `/api/v1/cinemas/{cinema_id}` - Get Cinema ❌  
**PATCH** `/api/v1/cinemas/{cinema_id}` - Update Cinema 🔐  
**DELETE** `/api/v1/cinemas/{cinema_id}` - Delete Cinema 🔐  
**GET** `/api/v1/cinemas/{cinema_id}/amenities` - Get Cinema Amenities ❌  
**GET** `/api/v1/cinemas/{cinema_id}/movies` - Get Cinema Movies ❌  
**GET** `/api/v1/cinemas/{cinema_id}/showtimes` - Get Cinema Showtimes ❌

---

## Rooms

**POST** `/api/v1/cinemas/{cinema_id}/rooms/` - Create Room 🔐  
**GET** `/api/v1/cinemas/{cinema_id}/rooms/` - List Cinema Rooms ❌  
**GET** `/api/v1/rooms/{room_id}` - Get Room ❌

---

## Seats

**POST** `/api/v1/rooms/{room_id}/seats/bulk` - Create Seats Bulk 🔐  
**GET** `/api/v1/rooms/{room_id}/seats/` - List Room Seats ❌

---

## Movies

**GET** `/api/v1/movies/recommended` - Get Recommended Movies ✅  
**POST** `/api/v1/movies/` - Create Movie 🔐  
**GET** `/api/v1/movies/` - List Movies ❌  
**GET** `/api/v1/movies/search` - Search Movies ❌  
**GET** `/api/v1/movies/filter` - Filter Movies by Criteria ❌  
**GET** `/api/v1/movies/advanced-search` - Advanced Search Movies ❌  
**GET** `/api/v1/movies/{movie_id}` - Get Movie ❌  
**PATCH** `/api/v1/movies/{movie_id}` - Update Movie 🔐  
**DELETE** `/api/v1/movies/{movie_id}` - Delete Movie 🔐  
**GET** `/api/v1/movies/{movie_id}/cast` - Get Movie Cast (Detailed) ❌  
**GET** `/api/v1/movies/{movie_id}/showtimes` - Get Movie Showtimes ❌

---

## Cast

**POST** `/api/v1/casts/` - Create Cast Member 🔐  
**GET** `/api/v1/casts/` - List Cast Members ❌  
**GET** `/api/v1/casts/{cast_id}` - Get Cast Member ❌  
**PUT** `/api/v1/casts/{cast_id}` - Update Cast Member 🔐  
**DELETE** `/api/v1/casts/{cast_id}` - Delete Cast Member 🔐  
**GET** `/api/v1/casts/movie/{movie_id}` - Get Movie Cast Members ❌

---

## Screenings

**POST** `/api/v1/screenings/` - Create Screening 🔐  
**GET** `/api/v1/screenings/` - List Screenings ❌  
**GET** `/api/v1/screenings/{screening_id}` - Get Screening ❌  
**GET** `/api/v1/screenings/{screening_id}/available-seats` - Get Screening Available Seats ❌

---

## Showtimes

**GET** `/api/v1/showtimes/` - List Showtimes ❌  
**GET** `/api/v1/showtimes/{showtime_id}` - Get Showtime ❌  
**GET** `/api/v1/showtimes/{showtime_id}/seats` - Get Showtime Seats ❌

---

## Tickets

**POST** `/api/v1/tickets/book` - Book Tickets Endpoint ✅  
**GET** `/api/v1/tickets/my-tickets` - Get My Tickets ✅  
**GET** `/api/v1/tickets/{ticket_id}` - Get Ticket ✅  
**DELETE** `/api/v1/tickets/{ticket_id}` - Cancel Ticket Endpoint ✅  
**POST** `/api/v1/tickets/{ticket_id}/confirm-payment` - Confirm Payment ✅  
**GET** `/api/v1/tickets/` - List All Tickets 🔐  
**PUT** `/api/v1/tickets/{ticket_id}/status` - Update Ticket Status 🔐  
**POST** `/api/v1/tickets/{ticket_id}/resend` - Resend Ticket Confirmation ✅

---

## Users

**GET** `/api/v1/users/me` - Get Current User Profile ✅  
**PUT** `/api/v1/users/me` - Update User Profile ✅  
**DELETE** `/api/v1/users/me` - Delete User Account ✅  
**PUT** `/api/v1/users/me/preferences` - Update User Preferences ✅  
**PUT** `/api/v1/users/me/profile-picture` - Upload Profile Picture ✅  
**PUT** `/api/v1/users/me/profile-picture-url` - Update Profile Picture URL ✅  
**GET** `/api/v1/users/{user_id}` - Get User Profile ❌  
**GET** `/api/v1/users/me/search-history` - Get User Search History ✅  
**POST** `/api/v1/users/me/search-history` - Add Search Query ✅  
**DELETE** `/api/v1/users/me/search-history/{id}` - Delete Search Entry ✅  
**DELETE** `/api/v1/users/me/search-history` - Clear User Search History ✅

---

## Reviews

**POST** `/api/v1/movies/{movie_id}/reviews` - Create Review ✅  
**GET** `/api/v1/movies/{movie_id}/reviews` - Get Movie Reviews ❌  
**GET** `/api/v1/movies/{movie_id}/reviews/summary` - Get Movie Reviews Summary ❌  
**GET** `/api/v1/movies/reviews/{review_id}` - Get Review ❌  
**PUT** `/api/v1/movies/reviews/{review_id}` - Update Review ✅  
**DELETE** `/api/v1/movies/reviews/{review_id}` - Delete Review ✅  
**POST** `/api/v1/movies/reviews/{review_id}/react` - React To Review ✅

---

## Admin

**GET** `/api/v1/admin/stats/movies` - Get Movies Count 🔐
**GET** `/api/v1/admin/stats/cinemas` - Get Cinemas Count 🔐
**GET** `/api/v1/admin/stats/users` - Get Users Count 🔐
**GET** `/api/v1/admin/stats/bookings/recent` - Get Recent Bookings 🔐
**GET** `/api/v1/admin/stats/revenue` - Get Total Revenue 🔐
**GET** `/api/v1/admin/stats/revenue/period` - Get Revenue By Period 🔐
**GET** `/api/v1/admin/stats/tickets/total` - Get Total Tickets Sold 🔐
**GET** `/api/v1/admin/stats/movies/popular` - Get Popular Movies 🔐
**GET** `/api/v1/admin/stats/today` - Get Today's Statistics 🔐
**GET** `/api/v1/tickets/` - List All Tickets 🔐
**PUT** `/api/v1/tickets/{ticket_id}/status` - Update Ticket Status 🔐
**POST** `/api/v1/tickets/{ticket_id}/resend` - Resend Ticket Confirmation ✅

---
