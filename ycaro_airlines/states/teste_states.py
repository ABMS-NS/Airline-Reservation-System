from ycaro_airlines.models.booking import Booking
from ycaro_airlines.models.customer import Customer
from ycaro_airlines.models.flight import Flight

# Criar voo e usuário
Flight.mock_flight()
user = Customer(username="teste_state")
flight = list(Flight.flights.values())[0]

# Criar booking
booking = Booking(
    owner_id=user.id,
    flight_id=flight.id,
    passenger_name="João Silva",
    passenger_cpf="123.456.789-12",
    price=200.0
)

print("=== Testando State Pattern ===\n")

# Estado inicial: BOOKED
print(f"1. Estado inicial: {booking.state.get_status_name()}")
print(f"   Pode cancelar? {booking.can_cancel()}")
print(f"   Pode check-in? {booking.can_check_in()}")
print(f"   Pode trocar assento? {booking.can_change_seat()}\n")

# Reservar assento
booking.reserve_seat(10)
print(f"2. Assento reservado: {booking.seat_id}\n")

# Fazer check-in
print("3. Tentando fazer check-in...")
booking.check_in()
print(f"   Novo estado: {booking.state.get_status_name()}")
print(f"   Pode cancelar? {booking.can_cancel()}")
print(f"   Pode trocar assento? {booking.can_change_seat()}\n")

# Tentar cancelar após check-in (não deve permitir)
print("4. Tentando cancelar após check-in...")
booking.cancel_booking()