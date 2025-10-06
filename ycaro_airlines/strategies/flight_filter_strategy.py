from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

# TYPE_CHECKING é True apenas durante verificação de tipos, não em runtime
if TYPE_CHECKING:
    from ycaro_airlines.models.flight import Flight

class FlightFilterStrategy(ABC):
    """
    Interface abstrata para estratégias de filtro.
    """
    
    @abstractmethod
    def filter(self, flights: List["Flight"]) -> List["Flight"]:  #usando string para type hint
        """
        Método abstrato que todas as estratégias devem implementar.
        
        Args:
            flights: Lista de voos a serem filtrados
            
        Returns:
            Lista filtrada de voos
        """
        pass
    
    @abstractmethod
    def description(self) -> str:
        """
        Retorna descrição do filtro aplicado.
        """
        pass