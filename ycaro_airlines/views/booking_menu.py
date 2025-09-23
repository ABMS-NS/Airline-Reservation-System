from functools import partial
from typing import Callable, Tuple
import questionary
from ycaro_airlines.views.actions.booking_actions import (
    cancel_booking_action,
    check_in_action,
    select_seat_action,
)
from ycaro_airlines.views import console, menu_factory
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models.booking import Booking, BookingStatus


class BookingMenu(ActionView):
    title: str = "See Bookings"

    def operation(self) -> UIView | None:
        if self.user is None:
            raise ValueError("User must be logged")

        Booking.print_bookings_table(self.user.id, console)

        if len(Booking.list_customer_bookings(self.user.id)) == 0:
            print("There are no bookings to manage!")
            return self.parent

        booking_id = questionary.autocomplete(
            "Type the id of the booking you wish to manage:(type 'q' to go back)",
            choices=[str(i.id) for i in Booking.list_customer_bookings(self.user.id)],
            validate=lambda x: (
                True
                if x
                in {str(i.id) for i in Booking.list_customer_bookings(self.user.id)}
                or x == "q"
                else False
            ),
        ).ask()

        if booking_id == "q" or not booking_id:
            return self.parent

        booking = Booking.get(int(booking_id))

        if booking is None:
            raise ValueError("Booking Id must be valid")

        booking.print_booking_table(console)

        options: list[Tuple[str, Callable]] = [
            (
                "Cancel Booking",
                partial(cancel_booking_action, user=self.user, booking=booking),
            ),
            ("Change Seat", partial(select_seat_action, booking=booking)),
            (
                "Online Check-in",
                partial(check_in_action, user=self.user, booking=booking),
            ),
        ]

        if booking.status != BookingStatus.booked:
            options = [
                (
                    "Ver passagem",
                    partial(booking.print_booking_table, console=console),
                )
            ]

        menu_factory("Booking management", options)()

        return self.parent
