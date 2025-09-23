from ycaro_airlines.views.actions.booking.book_flight_action import BookFlightAction
from ycaro_airlines.views.actions.booking.book_multi_flight_action import (
    BookMultiFlightAction,
)
from ycaro_airlines.views.actions.flight_actions import SearchFlightAction
from ycaro_airlines.views.menu import MenuView, UIView
from ycaro_airlines.models.user import User


class FlightsMenu(MenuView):
    title: str = "Search Flights Menu"

    def __init__(self, user: User, parent: "UIView | None" = None):
        self.children: list[UIView] = [
            BookFlightAction(user, self),
            BookMultiFlightAction(user, self),
            SearchFlightAction(user, self),
        ]
        super().__init__(user=user, children=self.children, parent=parent)
