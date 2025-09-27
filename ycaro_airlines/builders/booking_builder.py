from ycaro_airlines.models.booking import Booking
from ycaro_airlines.models.user import User

class BookingBuilder:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._flight_id: int = None
        self._owner_id: int = None
        self._passenger_name: str = None
        self._passenger_cpf: str = None
        self._price: float = None
        self._seat_id: int = None
        return self
    
    def for_flight(self, flight_id: int):
        self._flight_id = flight_id
        return self
    
    def for_user(self, user: User):
        self._owner_id = user.id
        return self
    
    def with_passenger(self, name: str, cpf: str):
        self._passenger_name = name
        self._passenger_cpf = cpf
        return self
    
    def with_price(self, price: float):
        self._price = price
        return self
    
    def with_seat(self, seat_id: int):
        self._seat_id = seat_id
        return self
    
    def build(self) -> Booking:
        if not all([self._flight_id, self._owner_id, self._passenger_name, 
                   self._passenger_cpf, self._price is not None]):
            raise ValueError("Missing required booking information")
        
        return Booking(
            flight_id=self._flight_id,
            owner_id=self._owner_id,
            passenger_name=self._passenger_name,
            passenger_cpf=self._passenger_cpf,
            price=self._price,
            seat_id=self._seat_id
        )