from abc import ABC, abstractmethod
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models.user import User

class ActionFactory(ABC):
    @abstractmethod
    def create_action(self, user: User, parent: UIView = None) -> ActionView:
        pass

class BookingActionFactory(ActionFactory):
    def __init__(self, action_type: str):
        self.action_type = action_type
    
    def create_action(self, user: User, parent: UIView = None) -> ActionView:
        from ycaro_airlines.views.actions.booking.book_flight_action import BookFlightAction
        from ycaro_airlines.views.actions.booking.book_multi_flight_action import BookMultiFlightAction
        
        match self.action_type:
            case "single":
                return BookFlightAction(user, parent)
            case "multi":
                return BookMultiFlightAction(user, parent)
            case _:
                raise ValueError(f"Unknown booking action type: {self.action_type}")

class FlightActionFactory(ActionFactory):
    def __init__(self, action_type: str):
        self.action_type = action_type
    
    def create_action(self, user: User, parent: UIView = None) -> ActionView:
        from ycaro_airlines.views.actions.flight_actions import SearchFlightAction
        
        match self.action_type:
            case "search":
                return SearchFlightAction(user, parent)
            case _:
                raise ValueError(f"Unknown flight action type: {self.action_type}")

class ActionFactoryProvider:
    @staticmethod
    def create_booking_action(action_type: str, user: User, parent: UIView = None) -> ActionView:
        factory = BookingActionFactory(action_type)
        return factory.create_action(user, parent)
    
    @staticmethod
    def create_flight_action(action_type: str, user: User, parent: UIView = None) -> ActionView:
        factory = FlightActionFactory(action_type)
        return factory.create_action(user, parent)