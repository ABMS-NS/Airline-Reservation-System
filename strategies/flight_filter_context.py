from typing import List, TYPE_CHECKING
from ycaro_airlines.strategies.flight_filter_strategy import FlightFilterStrategy

if TYPE_CHECKING:
    from ycaro_airlines.models.flight import Flight

class FlightFilterContext:
    """
    Mantém referência para uma estratégia e delega o trabalho de filtro para ela.
    """
    
    def __init__(self, strategy: FlightFilterStrategy = None):
        self._strategy = strategy
    
    def set_strategy(self, strategy: FlightFilterStrategy):
        self._strategy = strategy
    
    def apply_filter(self, flights: List["Flight"]) -> List["Flight"]:
        if self._strategy is None:
            raise ValueError("Nenhuma estratégia de filtro definida")
        
        return self._strategy.filter(flights)
    
    def get_description(self) -> str:
        if self._strategy is None:
            return "Nenhum filtro aplicado"
        return self._strategy.description()