from ycaro_airlines.views.actions.customer_actions import create_issue_action
from ycaro_airlines.views import menu_factory, console
from ycaro_airlines.views.actions.booking_actions import (
    select_seat_action,
    check_in_action,
    cancel_booking_action,
    book_flight_action,
)

from ycaro_airlines.views.actions.flight_actions import search_flight_action
import questionary
from ycaro_airlines.models import Customer, Booking, Flight, BookingStatus
from typing import Callable, Tuple
from functools import partial

from ycaro_airlines.models.user import User

# TODO: Change Customer to user and check


def customer_menu(user: User):
    options: list[Tuple[str, Callable]] = [
        ("Browse Flights", partial(flights_menu, user=user)),
        ("My Bookings", partial(bookings_menu, user=user)),
        ("Customer Service", partial(customer_service_menu, user=user)),
    ]

    menu_factory("Customer Menu", options)()


def customer_service_menu(user: User):
    options: list[Tuple[str, Callable]] = [
        ("See issues", partial(issues_menu, user=user)),
        ("Create issue", partial(create_issue_action, user=user)),
    ]
    menu_factory("Customer Service", options)()


# TODO: implement
def issues_menu(user: User):
    pass


def bookings_menu(user: User):
    Booking.print_bookings_table(user.id, console)

    if len(Booking.list_customer_bookings(user.id)) == 0:
        print("There are no bookings to manage!")
        return

    booking_id = questionary.autocomplete(
        "Type the id of the booking you wish to manage:(type 'q' to go back)",
        choices=[str(i.id) for i in Booking.list_customer_bookings(user.id)],
        validate=lambda x: (
            True
            if x in {str(i.id) for i in Booking.list_customer_bookings(user.id)}
            or x == "q"
            else False
        ),
    ).ask()

    if booking_id == "q" or not booking_id:
        return

    booking = Booking.get(int(booking_id))

    if booking is None:
        raise ValueError("Booking Id must be valid")

    booking.print_booking_table(console)

    options: list[Tuple[str, Callable]] = [
        (
            "Cancel Booking",
            partial(cancel_booking_action, user=user, booking=booking),
        ),
        ("Change Seat", partial(select_seat_action, booking=booking)),
        ("Online Check-in", partial(check_in_action, user=user, booking=booking)),
    ]

    if booking.status != BookingStatus.booked:
        options = [
            (
                "Ver passagem",
                partial(booking.print_booking_table, console=console),
            )
        ]

    menu_factory("Booking management", options)()


def flights_menu(user: Customer):
    options: list[Tuple[str, Callable]] = [
        ("Book flight", partial(book_flight_action, user=user)),
        ("Search flights", search_flight_action),
    ]

    Flight.print_flights_table(console)

    menu_factory("Flights", options)()
