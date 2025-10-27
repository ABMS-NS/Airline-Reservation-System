from ycaro_airlines.views.actions.booking_actions import select_seat_action
from ycaro_airlines.views.menu import ActionView, UIView
import re
import questionary
from ycaro_airlines.models import Flight, Booking, Customer
from ycaro_airlines.views import console


class BookMultiFlightAction(ActionView):
    title: str = "Book Multiple Flights"

    def operation(self) -> UIView | None:
        if self.user is None:
            raise ValueError("User must be logged")
        if not isinstance(self.user, Customer):
            raise ValueError("User must be customer")

        flight_id = questionary.autocomplete(
            "Type the id of the flight you want to book:(type q to go back)",
            choices=[str(k) for k, _ in Flight.flights.items()],
            validate=lambda x: True
            if x in {str(k) for k, _ in Flight.flights.items()} or x == "q"
            else False,
        ).ask()

        if flight_id == "q" or not flight_id:
            return self.parent

        flight_1 = Flight.flights[int(flight_id)]
        flight_1.print_flight_table(console)

        flight_id = questionary.autocomplete(
            "Type the id of the second flight you want to book:(type q to go back)",
            choices=[
                str(k)
                for k, _ in filter(
                    lambda x: True if x[1].From == flight_1.To else False,
                    Flight.flights.items(),
                )
            ],
            validate=lambda x: True
            if x
            in {
                str(k)
                for k, _ in filter(
                    lambda x: True if x[1].From == flight_1.To else False,
                    Flight.flights.items(),
                )
            }
            or x == "q"
            else False,
        ).ask()

        if flight_id == "q" or not flight_id:
            return self.parent

        flight_2 = Flight.flights[int(flight_id)]

        flight_1.print_flight_table(console)
        flight_2.print_flight_table(console)

        wants_to_book = questionary.confirm(
            "Are you sure you want to book those flights?"
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

        booking_1 = Booking(
            flight_id=flight_1.id,
            owner_id=self.user.id,
            passenger_name=passenger_name,
            passenger_cpf=passenger_cpf,
            price=flight_1.price,
        )
        booking_2 = Booking(
            flight_id=flight_2.id,
            owner_id=self.user.id,
            passenger_name=passenger_name,
            passenger_cpf=passenger_cpf,
            price=flight_1.price,
        )

        wants_to_spend_loyalty_points = questionary.confirm(
            f"Do you wish to spend loyalty points to get a discount?(you have: {self.user.loyalty_points} loyalty points)"
        ).ask()

        if wants_to_spend_loyalty_points:
            loyalty_points_spent_booking_1 = int(
                questionary.text(
                    "how many loyalty points do you wish to spend on the booking for the first flight?(1 Loyalty Point = R$1.00)",
                    validate=lambda x: True
                    if re.fullmatch("[0-9]+", x)
                    and int(x) <= self.user.loyalty_points.points
                    else False,
                ).ask()
            )

            if loyalty_points_spent_booking_1 > booking_1.price:
                loyalty_points_spent_booking_1 = int(booking_1.price)

            self.user.spend_loyalty_points(int(loyalty_points_spent_booking_1))

            booking_1.price -= loyalty_points_spent_booking_1

            loyalty_points_spent_booking_2 = int(
                questionary.text(
                    "how many loyalty points do you wish to spend on the booking for the second flight?(1 Loyalty Point = R$1.00)",
                    validate=lambda x: True
                    if re.fullmatch("[0-9]+", x)
                    and int(x) <= self.user.loyalty_points.points
                    else False,
                ).ask()
            )

            if loyalty_points_spent_booking_2 > booking_2.price:
                loyalty_points_spent_booking_2 = int(booking_2.price)

            self.user.spend_loyalty_points(int(loyalty_points_spent_booking_2))
            booking_2.price -= loyalty_points_spent_booking_2

        wants_to_select_seat_flight_1 = questionary.confirm(
            "Do you want to choose a seat in flight 1 for R$40.00?"
        ).ask()

        if wants_to_select_seat_flight_1:
            booking_1.price += 40
            select_seat_action(booking_1)

        wants_to_select_seat_flight_2 = questionary.confirm(
            "Do you want to choose a seat in flight 2 for R$40.00?"
        ).ask()

        if wants_to_select_seat_flight_2:
            booking_2.price += 40
            select_seat_action(booking_2)

        print("Flight booked!")

        return self.parent
