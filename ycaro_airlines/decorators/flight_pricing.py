"""
Decorator Pattern para Sistema de Pricing Dinâmico
Adiciona funcionalidades aos voos sem modificar a classe Flight
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycaro_airlines.models.flight import Flight

# ===== COMPONENT (Interface) =====
class FlightPricing(ABC):
    """Interface base para pricing de voos"""
    
    @abstractmethod
    def get_price(self) -> float:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    def get_features(self) -> list[str]:
        """Retorna lista de features incluídas"""
        pass


# ===== CONCRETE COMPONENT =====
class BasicFlightPricing(FlightPricing):
    """Implementação básica - apenas o preço do voo"""
    
    def __init__(self, flight: "Flight", base_price: float = None):
        self.flight = flight
        self._base_price = base_price if base_price else flight.price
    
    def get_price(self) -> float:
        return self._base_price
    
    def get_description(self) -> str:
        return f"Voo {self.flight.id}: {self.flight.From} → {self.flight.To}"
    
    def get_features(self) -> list[str]:
        return ["Passagem aérea"]


# ===== BASE DECORATOR =====
class FlightPricingDecorator(FlightPricing):
    """Decorator base que encapsula outro FlightPricing"""
    
    def __init__(self, pricing: FlightPricing):
        self._pricing = pricing
    
    def get_price(self) -> float:
        return self._pricing.get_price()
    
    def get_description(self) -> str:
        return self._pricing.get_description()
    
    def get_features(self) -> list[str]:
        return self._pricing.get_features()


# ===== CONCRETE DECORATORS =====

class LoyaltyDiscountDecorator(FlightPricingDecorator):
    """Aplica desconto de fidelidade"""
    
    def __init__(self, pricing: FlightPricing, discount_percent: float):
        super().__init__(pricing)
        self.discount_percent = discount_percent
    
    def get_price(self) -> float:
        base_price = self._pricing.get_price()
        discount = base_price * (self.discount_percent / 100)
        return base_price - discount
    
    def get_description(self) -> str:
        return f"{self._pricing.get_description()} + Desconto Fidelidade {self.discount_percent}%"
    
    def get_features(self) -> list[str]:
        features = self._pricing.get_features()
        features.append(f"Desconto de {self.discount_percent}% (Fidelidade)")
        return features


class SeatSelectionDecorator(FlightPricingDecorator):
    """Adiciona taxa de seleção de assento"""
    
    SEAT_FEE = 40.0
    
    def get_price(self) -> float:
        return self._pricing.get_price() + self.SEAT_FEE
    
    def get_description(self) -> str:
        return f"{self._pricing.get_description()} + Seleção de Assento"
    
    def get_features(self) -> list[str]:
        features = self._pricing.get_features()
        features.append(f"Seleção de Assento (+R${self.SEAT_FEE})")
        return features


class BaggageDecorator(FlightPricingDecorator):
    """Adiciona taxa de bagagem extra"""
    
    BAG_FEE = 149.99
    
    def __init__(self, pricing: FlightPricing, num_bags: int = 1):
        super().__init__(pricing)
        self.num_bags = num_bags
    
    def get_price(self) -> float:
        return self._pricing.get_price() + (self.BAG_FEE * self.num_bags)
    
    def get_description(self) -> str:
        return f"{self._pricing.get_description()} + {self.num_bags} Bagagem Extra"
    
    def get_features(self) -> list[str]:
        features = self._pricing.get_features()
        total = self.BAG_FEE * self.num_bags
        features.append(f"{self.num_bags}x Bagagem Extra (+R${total:.2f})")
        return features


class PriorityBoardingDecorator(FlightPricingDecorator):
    """Adiciona embarque prioritário"""
    
    PRIORITY_FEE = 59.90
    
    def get_price(self) -> float:
        return self._pricing.get_price() + self.PRIORITY_FEE
    
    def get_description(self) -> str:
        return f"{self._pricing.get_description()} + Embarque Prioritário"
    
    def get_features(self) -> list[str]:
        features = self._pricing.get_features()
        features.append(f"Embarque Prioritário (+R${self.PRIORITY_FEE})")
        return features


class InsuranceDecorator(FlightPricingDecorator):
    """Adiciona seguro viagem"""
    
    FEES = {"basic": 29.90, "premium": 79.90}
    
    def __init__(self, pricing: FlightPricing, insurance_type: str = "basic"):
        super().__init__(pricing)
        self.insurance_type = insurance_type
    
    def get_price(self) -> float:
        return self._pricing.get_price() + self.FEES[self.insurance_type]
    
    def get_description(self) -> str:
        return f"{self._pricing.get_description()} + Seguro {self.insurance_type.title()}"
    
    def get_features(self) -> list[str]:
        features = self._pricing.get_features()
        fee = self.FEES[self.insurance_type]
        features.append(f"Seguro {self.insurance_type.title()} (+R${fee})")
        return features