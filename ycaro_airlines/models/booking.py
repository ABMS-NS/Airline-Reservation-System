from enum import Enum, auto
from typing import TypeAlias
from pydantic import Field
from ycaro_airlines.models.base_model import BaseModel
from ycaro_airlines.models.flight import Flight, stringify_date
from rich.table import Table
from rich.console import Console

# importar estados
from ycaro_airlines.states.booking_state import (
    BookingState,
    BookedState,
    CheckedInState,
    CancelledState
)


# Manter enum por compatibilidade (mas não usar mais) (MUDAR DEPOIS)
class BookingStatus(Enum):
    booked = 1
    checked_in = auto()
    cancelled = auto()


CustomerID: TypeAlias = int


class Booking(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True  #permite armazenar BookingState
    }

    flight_id: int
    owner_id: int
    price: float
    seat_id: int | None
    passenger_name: str
    passenger_cpf: str

    #ADICIONADO PARA O STATE OBJECT
    state: BookingState = Field(default_factory=BookedState, exclude=True)

    #mannter status para compatibilidade com código antigo
    status: BookingStatus

    def __init__(
        self,
        owner_id: int,
        flight_id: int,
        passenger_name: str,
        passenger_cpf: str,
        price: float,
        seat_id: int | None = None,
        *args,
        **kwargs,
    ):
        initial_state = BookedState()
        super().__init__(
            owner_id=owner_id,
            flight_id=flight_id,
            passenger_name=passenger_name,
            passenger_cpf=passenger_cpf,
            price=price,
            seat_id=seat_id,
            status=BookingStatus.booked,
            state=initial_state,
            *args,
            **kwargs,
        )

    def cancel_booking(self) -> bool:
        """Usa State Pattern para cancelar."""
        success = self.state.cancel(self)
        if success:
            self.status = BookingStatus.cancelled
        return success

    def check_in(self) -> bool:
        """Usa State Pattern para check-in."""
        success = self.state.check_in(self)
        if success:
            self.status = BookingStatus.checked_in
        return success

    def can_cancel(self) -> bool:
        return self.state.can_cancel()

    def can_check_in(self) -> bool:
        return self.state.can_check_in()

    def can_change_seat(self) -> bool:
        return self.state.can_change_seat()

    def reserve_seat(self, seat_id: int) -> bool:
        if not self.state.can_change_seat():
            print(f"❌ Não é possível mudar assento no estado atual: {self.state.get_status_name()}")
            return False

        reserved_seat = self.flight.occupy_seat(booking_id=self.id, seat_id=seat_id)

        if reserved_seat is None:
            return False

        if self.seat_id:
            self.flight.open_seat(self.seat_id)

        self.seat_id = reserved_seat.id
        return True

    @property
    def seat(self):
        if self.flight is not None:
            return self.flight.seats[self.seat_id] if self.seat_id else None
        return None

    @property
    def flight(self):
        if (flight := Flight.get_flight(self.flight_id)) is None:
            raise ValueError("Booking must have a flight")
        return flight

    @classmethod
    def list_customer_bookings(cls, customer_id: CustomerID):
        return [x for x in cls.list() if x.owner_id == customer_id]

    @classmethod
    def print_bookings_table(cls, customer_id: CustomerID, console: Console):
        table = Table(title="Bookings")
        table.add_column("Booking")
        table.add_column("Flight")
        table.add_column("From", justify="right", no_wrap=True)
        table.add_column("Departure", justify="right", no_wrap=True)
        table.add_column("Destination")
        table.add_column("Arrival", justify="right", no_wrap=True)
        table.add_column("Status", justify="right", no_wrap=True)
        table.add_column("Seat", justify="right", no_wrap=True)

        for i in cls.list_customer_bookings(customer_id):
            status_display = i.state.get_status_name()
            table.add_row(
                f"{i.id}",
                f"{i.flight.id}",
                f"{i.flight.From}",
                f"{stringify_date(i.flight.departure)}",
                f"{i.flight.To}",
                f"{stringify_date(i.flight.arrival)}",
                f"{status_display}",
                f"{i.seat_id}" if i.seat_id else "N/A",
            )
        console.print(table)

    def print_booking_table(self, console: Console):
        table = Table(title="Bookings")
        table.add_column("Booking")
        table.add_column("Flight")
        table.add_column("From", justify="right", no_wrap=True)
        table.add_column("Departure", justify="right", no_wrap=True)
        table.add_column("Destination")
        table.add_column("Arrival", justify="right", no_wrap=True)
        table.add_column("Status", justify="right", no_wrap=True)
        table.add_column("Seat", justify="right", no_wrap=True)

        status_display = self.state.get_status_name()
        table.add_row(
            f"{self.id}",
            f"{self.flight.id}",
            f"{self.flight.From}",
            f"{stringify_date(self.flight.departure)}",
            f"{self.flight.To}",
            f"{stringify_date(self.flight.arrival)}",
            f"{status_display}",
            f"{self.seat_id}" if self.seat_id else "N/A",
        )
        console.print(table)
