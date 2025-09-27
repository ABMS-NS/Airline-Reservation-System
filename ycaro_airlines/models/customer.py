from typing import ClassVar
from ycaro_airlines.models.base_model import BaseModel

import ycaro_airlines.models.customer_service as customer_service
from ycaro_airlines.models.user import Roles, User

from pydantic import BaseModel as PydanticBaseModel  # Renomear import

class LoyaltyManager(PydanticBaseModel):
    points: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(points=0, *args, **kwargs)

    def gain_points(self, amount: int):
        if amount < 0:
            raise ValueError("Loyalty points gained amount must not be negative")
        self.points += amount

    def spend_points(self, amount: int):
        if amount < 0:
            raise ValueError("Amount must be positive")
        if amount > self.points:
            raise ValueError("Insufficient loyalty points")
        self.points -= amount


class Customer(User):
    loyalty_points: LoyaltyManager

    def __init__(self, username: str, *args, **kwargs) -> None:
        role = Roles.Customer
        loyalty_points = LoyaltyManager()

        super().__init__(
            loyalty_points=loyalty_points,
            username=username,
            role=role,
            *args,
            **kwargs,
        )

    @property
    def issues(self):
        return filter(
            lambda x: True if x.customer_id == self.id else False,
            customer_service.Issue.list(),
        )

    def gain_loyalty_points(self, amount: int):
        self.loyalty_points.gain_points(amount)

    def spend_loyalty_points(self, amount: int):
        self.loyalty_points.spend_points(amount)
