# Missing Endpoints

## 🔐 Authentication

| Endpoint  | Method | Status     | Notes                     |
| --------- | ------ | ---------- | ------------------------- |
| `2FA/OTP` | POST   | ❌ MISSING | Two-factor authentication |

---

## 🎥 Showtimes & Seat Maps

| Endpoint                             | Method | Status     | Notes                  |
| ------------------------------------ | ------ | ---------- | ---------------------- |
| `POST /showtimes/:id/lock-seats`     | POST   | ❌ MISSING | Temporary seat locking |
| `DELETE /showtimes/:id/unlock-seats` | DELETE | ❌ MISSING | Release locked seats   |

**Missing Features:**

- [ ] Seat locking mechanism (concurrency handling)
- [ ] Showtime format info (IMAX, 3D, etc.)
- [ ] Automatic seat unlock (expiration)

---

## 🎫 Bookings/Tickets

| Endpoint                             | Method | Status     | Notes                    |
| ------------------------------------ | ------ | ---------- | ------------------------ |
| `POST /bookings/:id/confirm-payment` | POST   | ❌ MISSING | After payment            |
| `GET /bookings`                      | GET    | ❌ MISSING | Admin: list all bookings |
| `PUT /bookings/:id/status`           | PUT    | ❌ MISSING | Change booking status    |
| `POST /bookings/:id/resend-ticket`   | POST   | ❌ MISSING | Resend confirmation      |

**Missing Features:**

- [ ] Booking confirmation after payment
- [ ] QR code generation
- [ ] Email confirmation
- [ ] Ticket resend functionality
- [ ] Booking status tracking

---

## 💳 Payments

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

## 🔔 Notifications

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
