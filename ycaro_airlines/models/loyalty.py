from ycaro_airlines.models.base_model import BaseModel
from enum import Enum

class RewardType(Enum):
    DISCOUNT = "discount"
    UPGRADE = "upgrade" 
    FREE_FLIGHT = "free_flight"
    BAGGAGE = "free_baggage"

class Reward(BaseModel):
    name: str
    description: str
    points_cost: int
    reward_type: RewardType
    value: float  #valor do desconto/benefício

    def __init__(self, name: str, description: str, points_cost: int, 
                 reward_type: RewardType, value: float, *args, **kwargs):
        super().__init__(
            name=name,
            description=description, 
            points_cost=points_cost,
            reward_type=reward_type,
            value=value,
            *args, **kwargs
        )

class LoyaltyProgram(BaseModel):
    available_rewards: list[Reward]
    
    def __init__(self, *args, **kwargs):
        # Criar rewards padrão
        rewards = [
            Reward("Discount 10%", "10% of any flight", 100, RewardType.DISCOUNT, 0.1),
            Reward("Discount 25%", "25% of any flight", 250, RewardType.DISCOUNT, 0.25),
            Reward("Free Baggage", "One extra baggage free", 150, RewardType.BAGGAGE, 149.99),
            Reward("Free National Flight", "One free national flight", 500, RewardType.FREE_FLIGHT, 400.0),
        ]
        super().__init__(available_rewards=rewards, *args, **kwargs)
    
    @classmethod
    def get_available_rewards(cls, user_points: int):
        program = cls()
        return [r for r in program.available_rewards if r.points_cost <= user_points]