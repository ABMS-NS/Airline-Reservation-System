from ycaro_airlines.factories.action_factory import ActionFactoryProvider
from ycaro_airlines.views.menu import MenuView, UIView
from ycaro_airlines.models.user import User

from ycaro_airlines.views.actions.booking.book_flight_action_v2 import BookFlightActionV2

class FlightsMenu(MenuView):
    title: str = "Search Flights Menu"

    def __init__(self, user: User, parent: "UIView | None" = None):
        self.children: list[UIView] = [
            BookFlightActionV2(user, self),  # Nova versão com decorators
            ActionFactoryProvider.create_booking_action("multi", user, self),
            ActionFactoryProvider.create_flight_action("search", user, self),
        ]
        super().__init__(user=user, children=self.children, parent=parent)