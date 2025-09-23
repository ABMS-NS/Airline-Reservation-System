from ycaro_airlines.views.booking_menu import BookingMenu
from ycaro_airlines.views.flight_menu import FlightsMenu
from ycaro_airlines.views.menu import MenuView, UIView
from ycaro_airlines.models.user import User


class CustomerMenu(MenuView):
    title: str = "Customer Menu"

    def __init__(self, user: User, parent) -> None:
        self.children: list[UIView] = [
            FlightsMenu(user, self),
            BookingMenu(user, self),
        ]
        super().__init__(user, parent, self.children)
