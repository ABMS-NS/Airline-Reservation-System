import re
import questionary
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models import Flight, Booking, Customer
from ycaro_airlines.views import console
from ycaro_airlines.models.flight import SeatStatus


def select_seat_action(booking: Booking):
    seat = questionary.autocomplete(
        "Which seat do you want?",
        choices=[
            str(k)
            for k, v in booking.flight.seats.items()
            if v.status is SeatStatus.open
        ],
        validate=lambda x: True
        if x
        in {
            str(k)
            for k, v in booking.flight.seats.items()
            if v.status is SeatStatus.open
        }
        else False,
    ).ask()

    if not seat:
        return False

    seat = int(seat)

    booking.reserve_seat(seat)


class BookFlightAction(ActionView):
    title: str = "Book Flight"

    def operation(self) -> UIView | None:
        if self.user is None:
            return self.parent

        if not isinstance(self.user, Customer):
            return self.parent

        flight_id = questionary.autocomplete(
            "Type the id of the flight you want to book:(type q to go back)",
            choices=[str(k) for k, _ in Flight.flights.items()],
            validate=lambda x: True
            if x in {str(k) for k, _ in Flight.flights.items()} or x == "q"
            else False,
        ).ask()

        if flight_id == "q" or not flight_id:
            return self.parent

        flight = Flight.flights[int(flight_id)]
        flight.print_flight_table(console)

        wants_to_book = questionary.confirm(
            "Are you sure you want to book this flight?"
        ).ask()

        if not wants_to_book:
            return self.parent

        passenger_name = questionary.text("Type passenger name:").ask()
        passenger_cpf = questionary.text(
            "Type passenger cpf",
            validate=lambda x: True
            if re.fullmatch(r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$", x)
            else False,
        ).ask()
        if not passenger_name or not passenger_cpf:
            print("Operation Cancelled")
            return self.parent

        # voce quer comprar essa passagem
        booking = Booking(
            flight_id=flight.id,
            owner_id=self.user.id,
            passenger_name=passenger_name,
            passenger_cpf=passenger_cpf,
            price=flight.price,
        )

        wants_to_spend_loyalty_points = questionary.confirm(
            f"Do you wish to spend loyalty points to get a discount?(you have: {self.user.loyalty_points} loyalty points)"
        ).ask()

        if wants_to_spend_loyalty_points:
            loyalty_points_spent = int(
                questionary.text(
                    "how many loyalty points do you wish to spend?(1 Loyalty Point = R$1.00)",
                    validate=lambda x: True
                    if re.fullmatch("[0-9]+", x)
                    and int(x) <= self.user.loyalty_points.points
                    else False,
                ).ask()
            )

            if loyalty_points_spent > booking.price:
                loyalty_points_spent = int(booking.price)

            self.user.spend_loyalty_points(int(loyalty_points_spent))
            booking.price -= loyalty_points_spent

        wants_to_select_seat = questionary.confirm(
            "Do you want to choose this seat for R$40.00?"
        ).ask()

        if wants_to_select_seat:
            booking.price += 40
            select_seat_action(booking)

        print("Flight booked!")

        return self.parent
