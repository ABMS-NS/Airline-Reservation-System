# ycaro-airlines
Project made for Software Project class for the 2025.1 semester

## Project Functional Requirements
Airline Reservation System
- [x]  Flight Search: Users can search for flights based on various criteria;
- [x] Booking Management: Users can book, cancel, and modify flight bookings;
- [x] Online Check-in: Users can check in online for their flights;
- [x] Seat Selection: Users can select and change their seats;
- [x] Baggage Information: Information about baggage allowances and fees;
- [x] Loyalty Program Management: Management and redemption of frequent flyer points;
- [ ] Flight Status Updates: Real-time updates on flight status;
- [-] Special Requests: Handling of special requests like meals and accessibility needs;
- [x] Multi-City Booking: Booking flights with multiple stopovers;
- [-] Customer Support Interface: Assisting customers with their queries and issues

## Requirements in progress (date: 16/07/2025)
- Flight Search
- Flight Status Update

## Requirements done(date: 16/07/2025)
- Booking Management
- Online Check-in
- Seat Selection
- Baggage Information

## Project Structure
- Airplane: Airline airplane, can fly from a city to another during a flight
    - has:
        - Flights: Flights scheduled for this plane
    - can:
        - Fly from a city to another
        - Take off from a city
        - Land on a city

- Flight: Flight thats scheduled
    - has:
        - Flight Route: The route the flight is going to take
        - Flight Crew: Flight crew for this flight, will handle special requests
        - Departure time: time airplane is going to take off
        - check-in time: time limit on check-in
        - Estimated arrival time: time airplane is estimated to land on destination
    - can:
        - travel along route
        - show status in real time
        - reserve a seat to a booking
        - receive special request for the flight crew
        - Show baggage information and fees for current flight
        - declare flight crew

- Flight Route: The route a flight is going to take between take off and destination
    - has:
        - origin: city flight is going to start its route
        - current stop: current city flight airplane is in
        - stops: cities the flight is going to travel to
            - estimated departure time: estimated time to take off from 
    - can:
        - add stops before creating flight
        - remove stops before creating flight

- Booking: 
    - has: 
        - Flight: Flight associated with this booking
        - Customer: Customer that booked this booking
        - Price: Price to book a flight
        - Baggage: Baggage owner will bring to this bookings flight
    - can:
        - be booked
        - reserve a seat in this booking's flight before check-in(optional)
        - reserve a seat in this booking's flight during check-in(mandatory)
        - modify the selected seat on this booking's flight
        - be cancelled
        - be checked into a flight
        - create fee based on services requested by the Customer

- Price: Price of a booking calculated based on several criterea
    - has:
        - Flight price: Calculated based on distance travelled, amount of stops
        - Booking Fees: Fees the customer will pay if they request a service

- User: Users that can access the airline system
    - has:
        - username: username used to login
        - role: role user has in the system

    - can:
        - login in the system
        - logout of the system
        - modify account credentials

- Customer(User): Airline customer
    - has:
        - Loyalty Points: loyalty points accumulated from trips
        - Customer Support Issues: issues the user have/had with airline
        - Special Requests: Special requests made to a booking
        - Address: Customer address
        - Balance: Customer credits in the airline system
    - can:
        - redeem loyalty points for prizes
        - Book flights
        - Modify and/or cancel booking
        - check-in booking
        - Create special requests in a booking
        - start a chat with customer support to send questions and issues

- Loyalty Program: Loyalty program where customer can get points by travelling with airline
    - Rewards: Rewards user can claim based on trips made with airline

- Customer Support: 
    - has:
        - Customer Support Crew(User):
        - Customer Chat
    - can:
        - Chat with customer to answer his queries and try to solve his problems

- Cities:
    - has:
        - Airports
        - distance between other cities

- Airports: 
    - has:
        - city: city airport is located
        - fligths: flights that land and depart from this airport
        - airplanes: airplanes currently in this airport
    - can:
        - autorize landing
        - autorize takeoff

## Progresso
- [-] Logar como Cliente
    - [x] Ver voos
        - [x] Comprar Passagem 
            - [x] Selecionar assentos
            - [x] Visualizar informacoes de bagagens
            - [ ] Realizar pedidos especiais
        - [x] - Visualizar Voos
            - [-] filtrar voos
            - [x] Visualizar informacoes de bagagens
    - [x] Gerenciar Passagens
    - [x] Check-in Online
        - [x] Selecionar assentos
        - [ ] Realizar pedidos especiais
        - [x] Visualizar informacoes de bagagens
    - [ ] Gerenciar Milhas
        - [ ] Verificar historico
        - [ ] Resgatar pontos
            - [ ] Selecionar premio
        - [ ] Visualizar premios
    - [ ] SAC
        - [ ] chat?
