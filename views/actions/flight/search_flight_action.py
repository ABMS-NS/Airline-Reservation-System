import questionary
from ycaro_airlines.views.actions.flight_actions import (
    str_can_be_date,
    str_can_be_float,
)
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models import Flight, FlightQueryParams, cities
from math import inf
from datetime import datetime
from ycaro_airlines.views import console


class SearchFlightAction(ActionView):
    title: str = "Search Flights"

    def operation(self) -> UIView | None:
        Flight.print_flights_table(console)

        options: list[str] = [
            "price",
            "city",
            "departure date",
            "arrival date",
            "flight id",
        ]

        selected = questionary.checkbox(
            "How do you want to filter flights?", choices=options
        ).ask()
        if not selected:
            return self.parent

        flight_query_params: FlightQueryParams = {}

        if "flight id" in selected:
            flight_id = questionary.autocomplete(
                "Type the id of the flight:",
                choices=[str(k) for k, _ in Flight.flights.items()],
                validate=lambda x: (
                    True if x in {str(k) for k, _ in Flight.flights.items()} else False
                ),
            ).ask()
            if flight_id:
                flight_query_params["flight_id"] = int(flight_id)

        if "price" in selected:
            price_lte = questionary.text(
                "Price <= (default: infinity):", default="", validate=str_can_be_float
            ).ask()

            if price_lte == "" or not price_lte:
                price_lte = inf

            price_gte = questionary.text(
                "Price >= (default: 0):",
                default="",
                validate=str_can_be_float,
            ).ask()

            if price_gte == "" or not price_gte:
                price_gte = 0

            flight_query_params["price_lte"] = float(price_lte)
            flight_query_params["price_gte"] = float(price_gte)

        if "city" in selected:
            city_from: str = questionary.autocomplete(
                "From:", choices=cities, validate=lambda x: x in cities
            ).ask()
            city_to: str = questionary.autocomplete(
                "To:", choices=cities, validate=lambda x: x in cities
            ).ask()

            if city_from != "" and city_from:
                flight_query_params["city_from"] = city_from

            if city_to != "" and city_to:
                flight_query_params["city_to"] = city_to

        if "arrival date" in selected:
            arrival_lte = questionary.text(
                "Arrival <=:(dd-mm-yyyy)", "", validate=str_can_be_date
            ).ask()

            arrival_gte = questionary.text(
                "Arrival >=:(dd-mm-yyyy)", "", validate=str_can_be_date
            ).ask()
            if arrival_lte != "" and arrival_lte:
                arrival_lte = list(map(lambda x: int(x), arrival_lte.split("/")))

                flight_query_params["date_arrival_lte"] = datetime(
                    day=arrival_lte[0], month=arrival_lte[1], year=arrival_lte[2]
                )

            if arrival_gte != "" and arrival_gte:
                arrival_gte = list(map(lambda x: int(x), arrival_gte.split("/")))

                flight_query_params["date_arrival_gte"] = datetime(
                    day=arrival_gte[0], month=arrival_gte[1], year=arrival_gte[2]
                )

        if "departure date" in selected:
            departure_lte = questionary.text(
                "Departure <=:(dd-mm-yyyy)", "", validate=str_can_be_date
            ).ask()

            departure_gte = questionary.text(
                "Departure >=:(dd-mm-yyyy)", "", validate=str_can_be_date
            ).ask()

            if departure_lte != "" and departure_lte:
                departure_lte = list(map(lambda x: int(x), departure_lte.split("/")))
                flight_query_params["date_departure_lte"] = datetime(
                    day=departure_lte[0],
                    month=departure_lte[1],
                    year=departure_lte[2],
                    hour=23,
                    minute=59,
                )

            if departure_gte != "" and departure_gte:
                departure_gte = list(map(lambda x: int(x), departure_gte.split("/")))
                flight_query_params["date_departure_gte"] = datetime(
                    day=departure_gte[0],
                    month=departure_gte[1],
                    year=departure_gte[2],
                    hour=0,
                    minute=0,
                )

        Flight.print_flights_table(console=console, **flight_query_params)

        return self.parent
