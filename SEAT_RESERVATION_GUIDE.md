# Seat Reservation API Guide

## Overview
Real-time seat reservations with WebSocket updates. Reservations expire after 5 minutes.

## Key Endpoints

### Toggle Reservation (Primary)
**POST** `/api/v1/seat-reservations/toggle`
- Reserves available seats, unreserves user's own reservations
- Body: `{"screening_id": 123, "seat_id": 456}` or `{"screening_id": 123, "seat_ids": [456, 457]}`

### Get Availability (User-Aware)
**GET** `/api/v1/seat-reservations/screening/{screening_id}/availability/me`
- Returns seats with `status`: `available`, `reserved`, `reserved_by_me`, `booked`
- `is_mine`: true for user's reservations

### Cancel All Reservations
**DELETE** `/api/v1/seat-reservations/cancel/{screening_id}`
- Cancel user's reservations for a screening

## WebSocket Real-time Updates

**URL:** `ws://localhost:8000/ws/screenings/{screening_id}?token={jwt_token}`

**Messages:**
- `connection_confirmed`: Connected successfully
- `bulk_seat_update`: Real-time seat changes with `is_mine` per user

## Status Values
- `available`: Free to reserve
- `reserved_by_me`: User's reservation
- `reserved`: Another user's reservation  
- `booked`: Sold ticket

## Best Practices
1. Use `/availability/me` for user-aware status
2. Use `/toggle` for seat clicking
3. Cancel reservations in `ngOnDestroy()`
4. Handle WebSocket `bulk_seat_update` messages
5. Check `previously_reserved_by` for expired reservations

## Frontend Implementation

```typescript
// Key interfaces
export interface SeatAvailability {
  seat: Seat;
  status: 'available' | 'reserved' | 'reserved_by_me' | 'booked';
  is_mine: boolean;
  expires_at: string | null;
}

// Service methods
getAvailability(screeningId: number): Observable<SeatAvailability[]> {
  return this.http.get(`${this.apiUrl}/screening/${screeningId}/availability/me`);
}

toggleSeat(screeningId: number, seatId: number): Observable<any> {
  return this.http.post(`${this.apiUrl}/toggle`, { screening_id: screeningId, seat_id: seatId });
}

cancelAll(screeningId: number): Observable<void> {
  return this.http.delete(`${this.apiUrl}/cancel/${screeningId}`);
}

// WebSocket connection
const ws = new WebSocket(`ws://localhost:8000/ws/screenings/${screeningId}?token=${token}`);
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'bulk_seat_update') {
    data.updates.forEach(update => updateSeatStatus(update));
  }
};

// Seat click handler
onSeatClick(seat: SeatAvailability) {
  if (seat.status === 'booked' || (seat.status === 'reserved' && !seat.is_mine)) return;
  this.seatService.toggleSeat(this.screeningId, seat.seat.id).subscribe();
}
```

## Status Values
- `available`: Free to reserve (Green)
- `reserved_by_me`: User's reservation (Blue)  
- `reserved`: Another user's reservation (Grey)
- `booked`: Sold ticket (Red)

## Best Practices
1. Use `/availability/me` for user-aware status
2. Use `/toggle` for seat clicking
3. Cancel reservations in component `ngOnDestroy()`
4. Handle WebSocket `bulk_seat_update` messages
5. Check `previously_reserved_by` for expired reservations

## Error Handling
- **409**: Seat taken by another user - refresh availability
- **404**: Screening/seat not found
- **422**: Invalid request format
