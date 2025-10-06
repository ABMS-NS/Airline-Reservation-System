from abc import ABC, abstractmethod
from typing import List
from ycaro_airlines.models.flight import Flight

# interface Strategy - define o contrato que todas as estratégias devem seguir
class FlightFilterStrategy(ABC):
    """
    Interface abstrata para estratégias de filtro de voos.
    Cada estratégia concreta implementa um critério diferente de filtro.
    """
    
    @abstractmethod
    def filter(self, flights: List[Flight]) -> List[Flight]:
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