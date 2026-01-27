# 🎬 Cinema Seat Selection API - Frontend Developer Guide

## 🌐 Base URL

```
http://localhost:8000
```

## 🔑 Authentication

Most endpoints require JWT authentication. Include in header:

```javascript
headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN',
  'Content-Type': 'application/json'
}
```

---

## 📡 WebSocket Connection (Real-Time Updates)

### **Connect to Screening**

```javascript
// Connect to real-time seat updates for a specific screening
const ws = new WebSocket(
  `ws://localhost:8000/ws/screenings/${screeningId}?token=YOUR_JWT_TOKEN`,
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleRealtimeUpdate(data);
};
```

### **WebSocket Events Received:**

```javascript
// Connection confirmed
{
  "type": "connection_confirmed",
  "screening_id": 123,
  "message": "Connected to real-time seat updates"
}

// Single seat updated
{
  "type": "seat_update",
  "seat_id": 42,
  "status": "reserved",  // "available" | "reserved" | "booked"
  "reserved_by": 7,      // user_id (optional)
  "expires_at": "2026-01-26T18:30:00Z",  // ISO timestamp (optional)
  "timestamp": "2026-01-26T18:25:00Z"
}

// Multiple seats updated
{
  "type": "bulk_seat_update",
  "updates": [
    {"seat_id": 42, "status": "booked", "booked_by": 7},
    {"seat_id": 43, "status": "booked", "booked_by": 7}
  ],
  "timestamp": "2026-01-26T18:25:00Z"
}
```

---

## 🪑 Seat Availability & Management

### **1. Get Seat Availability**

```http
GET /api/v1/seat-reservations/screening/{screening_id}/availability
```

**Response:**

```javascript
[
  {
    seat: {
      id: 42,
      room_id: 1,
      row_label: "A",
      seat_number: 5,
      seat_type: "standard",
    },
    status: "available", // "available" | "reserved" | "booked"
    reserved_by: null, // user_id if reserved
    expires_at: null, // ISO timestamp if reserved
  },
  {
    seat: {
      id: 43,
      room_id: 1,
      row_label: "A",
      seat_number: 6,
      seat_type: "standard",
    },
    status: "reserved",
    reserved_by: 123,
    expires_at: "2026-01-26T18:30:00Z",
  },
];
```

**Frontend Usage:**

```javascript
async function loadSeatMap(screeningId) {
  const response = await fetch(
    `/api/v1/seat-reservations/screening/${screeningId}/availability`,
  );
  const seats = await response.json();

  seats.forEach((seatInfo) => {
    const seatElement = document.getElementById(`seat-${seatInfo.seat.id}`);

    // Update seat styling based on status
    seatElement.className = `seat ${seatInfo.status}`;
    seatElement.disabled = seatInfo.status !== "available";

    if (seatInfo.status === "reserved") {
      seatElement.title = `Reserved until ${new Date(seatInfo.expires_at).toLocaleTimeString()}`;
    }
  });
}
```

---

## 🔒 Seat Reservation (Step 1: Hold Seats)

### **2. Reserve Seats**

```http
POST /api/v1/seat-reservations/reserve
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**

```javascript
{
  "screening_id": 123,
  "seat_ids": [42, 43, 44]
}
```

**Success Response (201):**

```javascript
{
  "reservations": [
    {
      "id": 1001,
      "screening_id": 123,
      "seat_id": 42,
      "user_id": 7,
      "reserved_at": "2026-01-26T18:25:00Z",
      "expires_at": "2026-01-26T18:30:00Z", // 5 minutes from now
      "status": "active"
    }
    // ... more reservations
  ],
  "expires_in_minutes": 5,
  "message": "Reserved 3 seats for 5 minutes"
}
```

**Error Responses:**

```javascript
// 409 - Seats already taken
{
  "detail": "Seats [42, 43] are currently reserved by other users"
}

// 409 - Seats already booked
{
  "detail": "Seats [44] are already booked"
}

// 400 - Past screening
{
  "detail": "Cannot reserve seats for past screenings"
}
```

**Frontend Usage:**

```javascript
async function reserveSeats(screeningId, seatIds) {
  try {
    const response = await fetch("/api/v1/seat-reservations/reserve", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        screening_id: screeningId,
        seat_ids: seatIds,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      showError(error.detail);
      return null;
    }

    const result = await response.json();

    // Show success message with countdown
    showSuccess(
      `Seats reserved! You have ${result.expires_in_minutes} minutes to complete payment.`,
    );
    startReservationCountdown(result.reservations[0].expires_at);

    return result.reservations;
  } catch (error) {
    showError("Failed to reserve seats. Please try again.");
    return null;
  }
}
```

---

## ⏰ Reservation Management

### **3. Extend Reservation**

```http
POST /api/v1/seat-reservations/extend
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**

```javascript
{
  "screening_id": 123,
  "seat_ids": [42, 43, 44]
}
```

**Query Parameters:**

- `additional_minutes=5` (optional, default: 5)

**Success Response (200):**

```javascript
{
  "reservations": [
    {
      "id": 1001,
      "expires_at": "2026-01-26T18:35:00Z", // Extended by 5 minutes
      "status": "active"
    }
  ],
  "expires_in_minutes": 5,
  "message": "Extended reservation for 3 seats by 5 minutes"
}
```

### **4. Cancel Reservations**

```http
DELETE /api/v1/seat-reservations/cancel/{screening_id}
Authorization: Bearer YOUR_JWT_TOKEN
```

**Query Parameters (Optional):**

- `seat_ids=42,43,44` - Cancel specific seats only

**Success Response (204):**

```
No content - reservations cancelled
```

### **5. My Active Reservations**

```http
GET /api/v1/seat-reservations/my-reservations
Authorization: Bearer YOUR_JWT_TOKEN
```

**Query Parameters:**

- `include_expired=false` (optional)

**Response:**

```javascript
[
  {
    id: 1001,
    screening_id: 123,
    seat_id: 42,
    reserved_at: "2026-01-26T18:25:00Z",
    expires_at: "2026-01-26T18:30:00Z",
    status: "active",
  },
];
```

---

## 🎟️ Ticket Booking (Step 2: Confirm Purchase)

### **6. Quick Book (Reserve + Confirm)**

```http
POST /api/v1/tickets/book
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**

```javascript
{
  "screening_id": 123,
  "seat_ids": [42, 43, 44],
  "payment_id": "stripe_pi_1234567890" // Optional for idempotency
}
```

**Success Response (201):**

```javascript
[
  {
    id: 2001,
    user_id: 7,
    screening_id: 123,
    seat_id: 42,
    price: 15.99,
    status: "confirmed",
    booked_at: "2026-01-26T18:25:00Z",
    confirmed_at: "2026-01-26T18:25:30Z",
    payment_id: "stripe_pi_1234567890",
  },
  // ... more tickets
];
```

### **7. Book From Existing Reservations (Payment Webhook)**

```http
POST /api/v1/tickets/book-from-reservation
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**

```javascript
{
  "screening_id": 123,
  "seat_ids": [42, 43, 44],
  "payment_id": "stripe_pi_1234567890" // REQUIRED for idempotency
}
```

**Success Response (201):**

```javascript
// Same as above - returns confirmed tickets
[
  {
    id: 2001,
    status: "confirmed",
    confirmed_at: "2026-01-26T18:25:30Z",
    // ... other fields
  },
];
```

**⚠️ IMPORTANT**: This endpoint is **idempotent**. If called multiple times with same `payment_id`, it returns existing tickets (not an error). Perfect for payment provider webhooks!

**Frontend Usage (Payment Success):**

```javascript
async function confirmPayment(paymentId, screeningId, seatIds) {
  try {
    const response = await fetch("/api/v1/tickets/book-from-reservation", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        screening_id: screeningId,
        seat_ids: seatIds,
        payment_id: paymentId, // Critical for preventing double-booking
      }),
    });

    const tickets = await response.json();

    // Show success and redirect to tickets
    showSuccess("Booking confirmed! Check your email for tickets.");
    redirectToMyTickets();

    return tickets;
  } catch (error) {
    showError("Payment succeeded but booking failed. Contact support.");
  }
}
```

---

## 🎫 Ticket Management

### **8. My Tickets**

```http
GET /api/v1/tickets/my-tickets
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response:**

```javascript
[
  {
    id: 2001,
    user_id: 7,
    screening_id: 123,
    seat_id: 42,
    price: 15.99,
    status: "confirmed",
    booked_at: "2026-01-26T18:25:00Z",
    confirmed_at: "2026-01-26T18:25:30Z",
  },
];
```

### **9. Get Specific Ticket**

```http
GET /api/v1/tickets/{ticket_id}
Authorization: Bearer YOUR_JWT_TOKEN
```

### **10. Cancel Ticket**

```http
DELETE /api/v1/tickets/{ticket_id}
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 🧹 Admin/Maintenance

### **11. Manual Cleanup (Testing)**

```http
POST /api/v1/seat-reservations/cleanup
```

**Response:**

```javascript
{
  "message": "Cleaned up 5 expired reservations",
  "timestamp": "2026-01-26T18:30:00Z",
  "duration_seconds": 0.125
}
```

### **12. WebSocket Statistics**

```http
GET /ws/stats
```

**Response:**

```javascript
{
  "total_connections": 42,
  "active_screenings": [123, 124, 125],
  "screening_details": {
    "123": 15,  // 15 users watching screening 123
    "124": 8,
    "125": 19
  }
}
```

---

## 🧪 Testing Correctness

### **Test Scenario 1: Basic Reservation Flow**

```javascript
// 1. Get initial availability
const availability = await fetch(
  "/api/v1/seat-reservations/screening/123/availability",
);

// 2. Reserve seats
const reservation = await fetch("/api/v1/seat-reservations/reserve", {
  method: "POST",
  body: JSON.stringify({ screening_id: 123, seat_ids: [42, 43] }),
});

// 3. Verify WebSocket update received (seat status = "reserved")
// 4. Book tickets
const tickets = await fetch("/api/v1/tickets/book-from-reservation", {
  method: "POST",
  body: JSON.stringify({
    screening_id: 123,
    seat_ids: [42, 43],
    payment_id: "test_payment_123",
  }),
});

// 5. Verify WebSocket update received (seat status = "booked")
```

### **Test Scenario 2: Concurrency**

Open two browser tabs and simultaneously try to reserve the same seat. Only one should succeed.

### **Test Scenario 3: Idempotency**

```javascript
// Call booking endpoint twice with same payment_id
const result1 = await bookFromReservation(paymentId, screeningId, seatIds);
const result2 = await bookFromReservation(paymentId, screeningId, seatIds);

// Both should return same tickets, no error
assert(result1[0].id === result2[0].id);
```

### **Test Scenario 4: Expiration**

```javascript
// 1. Reserve seats
// 2. Wait 5+ minutes (or use cleanup endpoint)
// 3. Verify seats become available again via WebSocket
// 4. Try to book expired reservation - should fail
```

---

## 🎯 Recommended Frontend Flow

### **1. Seat Map Page**

```javascript
// On page load
1. Connect WebSocket
2. Load seat availability
3. Render seat map with real-time updates
4. Handle seat selection (reserve on click)

// WebSocket handlers
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'seat_update':
      updateSeatUI(data.seat_id, data.status);
      break;
    case 'bulk_seat_update':
      data.updates.forEach(update =>
        updateSeatUI(update.seat_id, update.status)
      );
      break;
  }
};
```

### **2. Payment Page**

```javascript
// Show reservation countdown
// Handle payment via Stripe/PayPal
// On payment success: call book-from-reservation
// Handle payment failures: cancel reservations
```

### **3. Error Handling**

```javascript
// Always handle these status codes:
// 409: Conflict (seats taken)
// 400: Bad request (validation)
// 404: Not found
// 401: Unauthorized
// 500: Server error
```

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
**GET** `/api/v1/movies/coming-soon` - Get Coming Soon Movies ❌  
**GET** `/api/v1/movies/trending` - Get Trending Movies ❌  
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
**PUT** `/api/v1/screenings/{screening_id}` - Update Screening 🔐  
**DELETE** `/api/v1/screenings/{screening_id}` - Delete Screening 🔐

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
