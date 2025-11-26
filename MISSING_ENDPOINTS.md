# Missing Endpoints

## Existing & Required Endpoints

### **EXISTING ENDPOINTS** (29 total)

- ✅ Auth: `/register`, `/login`, `/me`
- ✅ User Profile: `/users/me`, `/users/me` (update), `/users/me/preferences`, `/users/me/profile-picture`, `/users/me` (delete), `/users/{id}`
- ✅ Cinemas: `/cinemas`, `/cinemas/{id}`, create rooms, rooms (3/5+)
- ✅ Movies: `/movies` CRUD + list (5/5)
- ✅ Screenings: Create, list, get, available seats (4/5)
- ✅ Seats: Bulk create, list (2/2)
- ✅ Tickets: Book, list, get, cancel (4/8)

---

## ❌ **MISSING ENDPOINTS**

### 🔐 \*\*1. Authentication

| `/auth/logout` | POST | ❌ MISSING | No logout/token revocation |
| `/auth/refresh-token` | POST | ❌ MISSING | Token refresh mechanism |
| `/auth/forgot-password` | POST | ❌ MISSING | Password reset request |
| `/auth/reset-password` | POST | ❌ MISSING | Complete password reset |
| `2FA/OTP` | POST | ❌ MISSING | Two-factor authentication |

---

### 👤 \*\*2. User Profile

| Endpoint                        | Method | Status         | Notes                              |
| ------------------------------- | ------ | -------------- | ---------------------------------- |
| `GET /users/me`                 | GET    | ✅ IMPLEMENTED | Get current user profile           |
| `PUT /users/me`                 | PUT    | ✅ IMPLEMENTED | Update profile (name, email)       |
| `PUT /users/me/profile-picture` | PUT    | ✅ IMPLEMENTED | Upload profile picture             |
| `PUT /users/me/preferences`     | PUT    | ✅ IMPLEMENTED | Dark mode, notifications |
| `DELETE /users/me`              | DELETE | ✅ IMPLEMENTED | Delete account (soft delete)       |
| `GET /users/:id`                | GET    | ✅ IMPLEMENTED | Public user profile                |

---

### 🎬 \*\*3. Movies

| Endpoint                  | Method | Status     | Notes            |
| ------------------------- | ------ | ---------- | ---------------- |
| `GET /movies/:id/cast`    | GET    | ❌ MISSING | Cast information |
| `GET /movies/:id/reviews` | GET    | ❌ MISSING | Movie reviews    |
| `GET /movies/search?q=`   | GET    | ❌ MISSING | Search endpoint  |

---

### ⭐ \*\*4. Reviews

| Endpoint                          | Method | Status     | Notes                   |
| --------------------------------- | ------ | ---------- | ----------------------- |
| `POST /movies/:id/reviews`        | POST   | ❌ MISSING | Add review              |
| `GET /movies/:id/reviews`         | GET    | ❌ MISSING | Get reviews (paginated) |
| `GET /movies/:id/reviews/summary` | GET    | ❌ MISSING | Rating breakdown        |
| `PUT /reviews/:id`                | PUT    | ❌ MISSING | Edit review             |
| `DELETE /reviews/:id`             | DELETE | ❌ MISSING | Delete review           |
| `POST /reviews/:id/react`         | POST   | ❌ MISSING | Like/dislike review     |
| `GET /reviews/:id`                | GET    | ❌ MISSING | Get single review       |

**Missing Features:**

- [ ] Review model/schema
- [ ] CRUD operations for reviews
- [ ] Rating system
- [ ] Review reactions (like/dislike)
- [ ] Review pagination & sorting

---

### 🏢 \*\*5. Cinemas & Amenities

| Endpoint                     | Method | Status     | Notes            |
| ---------------------------- | ------ | ---------- | ---------------- |
| `GET /cinemas`               | GET    | ✅ EXISTS  | List cinemas     |
| `GET /cinemas/:id`           | GET    | ✅ EXISTS  | Cinema details   |
| `POST /cinemas`              | POST   | ✅ EXISTS  | Create cinema    |
| `GET /cinemas/:id/amenities` | GET    | ❌ MISSING | Amenities list   |
| `GET /cinemas/search?q=`     | GET    | ❌ MISSING | Cinema search    |
| `GET /cinemas/:id/movies`    | GET    | ❌ MISSING | Movies at cinema |

**Missing Features:**

- [ ] Amenities model & endpoints
- [ ] Cinema search
- [ ] Movies by cinema listing
- [ ] Distance-based filtering
- [ ] Distance calculation (if needed)

---

### 🎥 \*\*6. Showtimes & Seat Maps

**Currently Have: 2/7 endpoints**

| Endpoint                             | Method | Status     | Notes                                  |
| ------------------------------------ | ------ | ---------- | -------------------------------------- |
| `GET /showtimes`                     | GET    | ❌ MISSING | List showtimes                         |
| `GET /movies/:id/showtimes?date=`    | GET    | ❌ MISSING | Showtimes by movie & date              |
| `GET /cinemas/:id/showtimes?date=`   | GET    | ❌ MISSING | Showtimes by cinema & date             |
| `GET /showtimes/:id`                 | GET    | ✅ PARTIAL | (as `/screenings/:id`)                 |
| `GET /showtimes/:id/seats`           | GET    | ✅ EXISTS  | (as `/screenings/:id/available-seats`) |
| `POST /showtimes/:id/lock-seats`     | POST   | ❌ MISSING | Temporary seat locking                 |
| `DELETE /showtimes/:id/unlock-seats` | DELETE | ❌ MISSING | Release locked seats                   |

**Missing Features:**

- [ ] Seat locking mechanism (concurrency handling)
- [ ] Datetime filtering for showtimes
- [ ] Showtime format info (IMAX, 3D, etc.)
- [ ] Automatic seat unlock (expiration)

---

### 🎫 \*\*7. Bookings/Tickets

| Endpoint                             | Method | Status     | Notes                      |
| ------------------------------------ | ------ | ---------- | -------------------------- |
| `POST /bookings`                     | POST   | ✅ PARTIAL | (as `/tickets/book`)       |
| `GET /bookings/:id`                  | GET    | ✅ PARTIAL | (as `/tickets/:id`)        |
| `GET /users/me/bookings`             | GET    | ✅ EXISTS  | (as `/tickets/my-tickets`) |
| `PUT /bookings/:id/cancel`           | PUT    | ✅ PARTIAL | (as `DELETE /tickets/:id`) |
| `POST /bookings/:id/confirm-payment` | POST   | ❌ MISSING | After payment              |
| `GET /bookings`                      | GET    | ❌ MISSING | Admin: list all bookings   |
| `PUT /bookings/:id/status`           | PUT    | ❌ MISSING | Change booking status      |
| `POST /bookings/:id/resend-ticket`   | POST   | ❌ MISSING | Resend confirmation        |

**Missing Features:**

- [ ] Booking confirmation after payment
- [ ] QR code generation
- [ ] Email confirmation
- [ ] Ticket resend functionality
- [ ] Booking status tracking

---

### 💳 \*\*8. Optional: Payments

| Endpoint                       | Method | Status     | Notes                          |
| ------------------------------ | ------ | ---------- | ------------------------------ |
| `GET /payments/methods`        | GET    | ❌ MISSING | List saved payment methods     |
| `POST /payments/intent`        | POST   | ❌ MISSING | Create payment intent (Stripe) |
| `POST /payments/confirm`       | POST   | ❌ MISSING | Confirm payment                |
| `POST /payments/methods`       | POST   | ❌ MISSING | Add payment method             |
| `DELETE /payments/methods/:id` | DELETE | ❌ MISSING | Remove payment method          |

**Missing Features:**

- [ ] Payment provider integration (Stripe/PayPal)
- [ ] Payment methods management
- [ ] Payment intent creation
- [ ] Payment confirmation & settlement
- [ ] Transaction history

---

### 🔔 \*\*9. Notifications

| Endpoint                              | Method | Status     | Notes                           |
| ------------------------------------- | ------ | ---------- | ------------------------------- |
| `GET /notifications`                  | GET    | ❌ MISSING | Get notifications               |
| `PUT /notifications/preferences`      | PUT    | ❌ MISSING | Update preferences              |
| `POST /notifications/register-device` | POST   | ❌ MISSING | Register for push notifications |

**Missing Features:**

- [ ] Notification system
- [ ] Push notification registration
- [ ] Email notifications
- [ ] In-app notifications

---

### 💝 \*\*11. Optional: Favorites

| Endpoint                       | Method | Status     | Notes                   |
| ------------------------------ | ------ | ---------- | ----------------------- |
| `POST /cinemas/:id/favorite`   | POST   | ❌ MISSING | Add cinema to favorites |
| `DELETE /cinemas/:id/favorite` | DELETE | ❌ MISSING | Remove from favorites   |

---

### 🔍 **12. Optional: Recent Searches - PRIORITY: LOW** ❌❌

| Endpoint                    | Method | Status     | Notes           |
| --------------------------- | ------ | ---------- | --------------- |
| `GET /users/me/searches`    | GET    | ❌ MISSING | Recent searches |
| `DELETE /users/me/searches` | DELETE | ❌ MISSING | Clear searches  |

---

### 🎯 \*\*13. Optional: Recommendations

| Endpoint                  | Method | Status     | Notes              |
| ------------------------- | ------ | ---------- | ------------------ |
| `GET /movies/recommended` | GET    | ❌ MISSING | Recommended movies |

---

## 📈 Summary Statistics

| Category                   | Existing | Required | Missing | Coverage  |
| -------------------------- | -------- | -------- | ------- | --------- |
| Authentication             | 3        | 8        | 5       | 37.5%     |
| User Profile               | 6        | 6        | 0       | 100% ✅   |
| Movies                     | 5        | 7        | 2       | 71.4%     |
| Reviews                    | 0        | 7        | 7       | 0%        |
| Cinemas                    | 3        | 6        | 3       | 50%       |
| Showtimes                  | 2        | 7        | 5       | 28.6%     |
| Bookings/Tickets           | 4        | 8        | 4       | 50%       |
| Payments                   | 0        | 5        | 5       | 0%        |
| Notifications              | 0        | 3        | 3       | 0%        |
| Support & Legal            | 0        | 3        | 3       | 0%        |
| Favorites (Optional)       | 0        | 2        | 2       | 0%        |
| Searches (Optional)        | 0        | 2        | 2       | 0%        |
| Recommendations (Optional) | 0        | 1        | 1       | 0%        |
| **TOTALS**                 | **29**   | **75**   | **46**  | **38.7%** |
