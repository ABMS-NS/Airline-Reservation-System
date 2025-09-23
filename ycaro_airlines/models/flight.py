from datetime import datetime, timedelta
from enum import Enum, auto
from itertools import count
from math import inf
from random import randint, sample
from typing import Dict

from rich.table import Table
from rich.console import Console
from typing import (
    Any,
    Callable,
    List,
    NotRequired,
    Self,
    TypedDict,
    Optional,
    Unpack,
)

cities = ["Maceio", "Recife", "Aracaju", "Joao Pessoa"]


def stringify_date(date: datetime):
    return f"{str(date.hour).zfill(2)}:{str(date.minute).zfill(2)} {str(date.day).zfill(2)}/{str(date.month).zfill(2)}"


type booking_id = int

type filter = Callable[[List[Any]], List[Any]]


class SeatStatus(Enum):
    open = 0
    reserved = auto()
    checked_in = auto()


class Seat:
    def __init__(self, status: SeatStatus, id: int, booking: booking_id | None = None):
        self.status: SeatStatus = status
        self.booking: booking_id | None = booking
        self.id: int = id


class FlightQueryParams(TypedDict):
    date_arrival_gte: NotRequired[datetime]
    date_departure_gte: NotRequired[datetime]

    date_arrival_lte: NotRequired[datetime]
    date_departure_lte: NotRequired[datetime]

    price_lte: NotRequired[float]
    price_gte: NotRequired[float]

    city_from: NotRequired[str]
    city_to: NotRequired[str]

    flight_id: NotRequired[int]


class Flight:
    flights: dict[int, Self] = {}
    flight_counter = count()

    def __init__(
        self,
        From: str,
        To: str,
        capacity: int = 255,
        departure_date: datetime = datetime.now() + timedelta(hours=1),
        arrival_date: datetime = datetime.now() + timedelta(hours=3),
        price: float = 200.00,
    ) -> None:
        self.From = From

        self.To = To

        self.id = next(self.flight_counter)

        self.capacity = capacity
        if capacity < 0:
            raise ValueError("Capacity must be a positive number")

        if departure_date < datetime.today():
            raise ValueError("Departure date must be a future date")

        if arrival_date < datetime.today():
            raise ValueError("Arrival date must be a future date")

        if arrival_date < departure_date:
            raise ValueError("Flight must depart before arrival")

        self.departure = departure_date
        self.arrival = arrival_date

        if price < 0:
            raise ValueError("Flight price must be positive")

        self.price = price

        self.seats: Dict[int, Seat] = {
            id: Seat(status=SeatStatus.open, id=id, booking=None)
            for id in range(0, self.capacity)
        }

    def __str__(self):
        return f"{self.id} - {self.From} -> {self.To}\n{stringify_date(self.departure)} -> {stringify_date(self.arrival)} | R${self.price} "

    @classmethod
    def mock_flight(cls):
        """Creates mocked flights to fill flights global dictionary"""
        timedelta_arrival = timedelta(days=randint(1, 6), hours=randint(1, 5))
        city1, city2 = sample(cities, k=2)
        price = randint(100, 400)
        mock: Flight = Flight(
            From=city1,
            To=city2,
            departure_date=datetime.now() + timedelta_arrival,
            arrival_date=datetime.now()
            + timedelta_arrival
            + timedelta(hours=randint(1, 5)),
            price=price,
        )

        Flight.flights[mock.id] = mock
        return mock

    def check_in_seat(self, booking_id: booking_id, seat_id: int):
        seat = self.seats.get(seat_id)

        if seat is None or seat.booking != booking_id:
            return False

        seat.status = SeatStatus.checked_in
        return True

    def occupy_seat(self, booking_id: booking_id, seat_id: int) -> Seat | None:
        if (seat := self.seats.get(seat_id)) is None:
            return None

        if seat.status is not SeatStatus.open:
            return None

        seat.status = SeatStatus.reserved
        seat.booking = booking_id

        return seat

    def open_seat(self, seat_id: int):
        if self.seats.get(seat_id) is None:
            return False

        self.seats[seat_id].booking = None
        self.seats[seat_id].status = SeatStatus.open

        return True

    @classmethod
    def get_flight(cls, fligth_id: int):
        return cls.flights.get(fligth_id)

    @classmethod
    def list_flights(cls, **query: Unpack[FlightQueryParams]) -> List["Flight"]:
        filtered_list: List[Flight] = list(cls.flights.values())

        if flight_id := query.get("flight_id"):
            return [i for i in filtered_list if i.id == flight_id]

        if query.get("date_arrival_gte") or query.get("date_arrival_lte"):
            filtered_list = filter_by_date(
                filtered_list,
                date_lte=query.get("date_arrival_lte"),
                date_gte=query.get("date_arrival_gte"),
            )

        if query.get("date_departure_gte") or query.get("date_departure_lte"):
            filtered_list = filter_by_date(
                filtered_list,
                date_lte=query.get("date_departure_lte"),
                date_gte=query.get("date_departure_gte"),
                departure=True,
            )

        if query.get("price_lte") or query.get("price_lte"):
            filtered_list = filter_by_price(
                filtered_list,
                price_lte=query.get("price_lte"),
                price_gte=query.get("price_gte"),
            )

        if query.get("city_from") or query.get("city_to"):
            filtered_list = filter_by_city(
                filtered_list, From=query.get("city_from"), To=query.get("city_to")
            )

        return list(filtered_list)

    @classmethod
    def print_flights_table(
        cls, console: Console, **query_params: Unpack[FlightQueryParams]
    ):
        # filtered_flights = cls.list_flights()
        # for filter in filters:
        #     filtered_flights = filter(filtered_flights)
        table = Table(title="Flights")
        table.add_column("Flight")
        table.add_column("From", justify="right", no_wrap=True)
        table.add_column("Departure", justify="right", no_wrap=True)
        table.add_column("Destination")
        table.add_column("Arrival", justify="right", no_wrap=True)
        table.add_column("Price", justify="right", no_wrap=True)

        for i in cls.list_flights(**query_params):
            table.add_row(
                f"{i.id}",
                f"{i.From}",
                f"{stringify_date(i.departure)}",
                f"{i.To}",
                f"{stringify_date(i.arrival)}",
                "${:,.2f}".format(i.price),
            )

        console.print(table)

    def print_flight_table(self, console: Console):
        table = Table(title="Flights")
        table.add_column("Flight")
        table.add_column("From", justify="right", no_wrap=True)
        table.add_column("Departure", justify="right", no_wrap=True)
        table.add_column("Destination")
        table.add_column("Arrival", justify="right", no_wrap=True)
        table.add_column("Price", justify="right", no_wrap=True)

        table.add_row(
            f"{self.id}",
            f"{self.From}",
            f"{stringify_date(self.departure)}",
            f"{self.To}",
            f"{stringify_date(self.arrival)}",
            "${:,.2f}".format(self.price),
        )

        console.print(table)


def filter_by_city(
    flights: List[Flight], From: Optional[str] = None, To: Optional[str] = None
):
    filtered_list = flights

    if From is not None:
        filtered_list = [x for x in filtered_list if x.From == From]

    if To is not None:
        filtered_list = [x for x in filtered_list if x.To == To]

    return filtered_list


def filter_by_date(
    flights: list[Flight],
    date_lte: Optional[datetime] = None,
    date_gte: Optional[datetime] = None,
    departure: bool = False,
):
    filtered_list = flights
    if not date_lte:
        date_lte = datetime.max
    if not date_gte:
        date_gte = datetime.min

    if departure:
        filtered_list = [
            x for x in filtered_list if date_gte <= x.departure <= date_lte
        ]
    else:
        filtered_list = [x for x in filtered_list if date_gte <= x.arrival <= date_lte]

    return filtered_list


def filter_by_price(
    flights: list[Flight],
    price_lte: Optional[float] = None,
    price_gte: Optional[float] = None,
):
    if not price_lte:
        price_lte = inf

    if not price_gte:
        price_gte = 0

    filtered_list = [x for x in flights if price_lte >= x.price >= price_gte]

    return filtered_list
