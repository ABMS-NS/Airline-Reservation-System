from ycaro_airlines.factories.action_factory import ActionFactoryProvider
from ycaro_airlines.views.menu import MenuView, UIView
from ycaro_airlines.models.user import User

class FlightsMenu(MenuView):
    title: str = "Search Flights Menu"

    def __init__(self, user: User, parent: "UIView | None" = None):
        # Usando as factories para criar actions
        self.children: list[UIView] = [
            ActionFactoryProvider.create_booking_action("single", user, self),
            ActionFactoryProvider.create_booking_action("multi", user, self),
            ActionFactoryProvider.create_flight_action("search", user, self),
        ]
        super().__init__(user=user, children=self.children, parent=parent)