from datetime import datetime
from typing import Optional, List
from math import inf
from ycaro_airlines.strategies.flight_filter_strategy import FlightFilterStrategy
from ycaro_airlines.models.flight import Flight

# ===== ESTRATÉGIA 1: Filtro por Cidade =====
class CityFilterStrategy(FlightFilterStrategy):
    """
    Estratégia para filtrar voos por cidade de origem e/ou destino.
    """
    
    def __init__(self, from_city: Optional[str] = None, to_city: Optional[str] = None):
        """
        Args:
            from_city: Cidade de origem (opcional)
            to_city: Cidade de destino (opcional)
        """
        self.from_city = from_city  #armazena o critério de filtro
        self.to_city = to_city
    
    def filter(self, flights: List[Flight]) -> List[Flight]:
        """
        Aplica o filtro de cidade nos voos.
        Se from_city estiver definido, filtra por origem.
        Se to_city estiver definido, filtra por destino.
        """
        result = flights  #começa com todos os voos
        
        #aplica filtro de origem
        if self.from_city is not None:
            result = [flight for flight in result if flight.From == self.from_city]
        
        #aplica filtro de destino
        if self.to_city is not None:
            result = [flight for flight in result if flight.To == self.to_city]
        
        return result
    
    def description(self) -> str:
        parts = []
        if self.from_city:
            parts.append(f"Origem: {self.from_city}")
        if self.to_city:
            parts.append(f"Destino: {self.to_city}")
        return " | ".join(parts) if parts else "Sem filtro de cidade"


# ===== ESTRATÉGIA 2: Filtro por Preço =====
class PriceFilterStrategy(FlightFilterStrategy):
    """
    Estratégia para filtrar voos por faixa de preço.
    """
    
    def __init__(self, min_price: float = 0, max_price: float = inf):
        """
        Args:
            min_price: Preço mínimo (padrão: 0)
            max_price: Preço máximo (padrão: infinito)
        """
        self.min_price = min_price
        self.max_price = max_price
    
    def filter(self, flights: List[Flight]) -> List[Flight]:
        return [
            flight for flight in flights 
            if self.min_price <= flight.price <= self.max_price
        ]
    
    def description(self) -> str:
        return f"Preço: R${self.min_price:.2f} - R${self.max_price:.2f}"


# ===== ESTRATÉGIA 3: Filtro por Data de Partida =====
class DepartureDateFilterStrategy(FlightFilterStrategy):
    """
    Estratégia concreta para filtrar voos por data de partida.
    """
    
    def __init__(self, start_date: Optional[datetime] = None, 
                 end_date: Optional[datetime] = None):
        """
        Args:
            start_date: Data de partida mínima (opcional)
            end_date: Data de partida máxima (opcional)
        """
        #define valores padrão se não especificados
        self.start_date = start_date if start_date else datetime.min
        self.end_date = end_date if end_date else datetime.max
    
    def filter(self, flights: List[Flight]) -> List[Flight]:
        """
        Retorna voos cuja data de partida está no intervalo especificado.
        """
        return [
            flight for flight in flights
            if self.start_date <= flight.departure <= self.end_date
        ]
    
    def description(self) -> str:
        start = self.start_date.strftime("%d/%m/%Y") if self.start_date != datetime.min else "Qualquer"
        end = self.end_date.strftime("%d/%m/%Y") if self.end_date != datetime.max else "Qualquer"
        return f"Partida: {start} - {end}"


# ===== ESTRATÉGIA 4: Filtro por Data de Chegada =====
class ArrivalDateFilterStrategy(FlightFilterStrategy):
    """
    Estratégia para filtrar voos por data de chegada.
    """
    
    def __init__(self, start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None):
        self.start_date = start_date if start_date else datetime.min
        self.end_date = end_date if end_date else datetime.max
    
    def filter(self, flights: List[Flight]) -> List[Flight]:
        """
        Retorna voos cuja data de chegada está no intervalo especificado.
        """
        return [
            flight for flight in flights
            if self.start_date <= flight.arrival <= self.end_date
        ]
    
    def description(self) -> str:
        start = self.start_date.strftime("%d/%m/%Y") if self.start_date != datetime.min else "Qualquer"
        end = self.end_date.strftime("%d/%m/%Y") if self.end_date != datetime.max else "Qualquer"
        return f"Chegada: {start} - {end}"


# ===== ESTRATÉGIA 5: Filtro por ID =====
class FlightIdFilterStrategy(FlightFilterStrategy):
    """
    Estratégia concreta para filtrar voo específico por ID.
    """
    
    def __init__(self, flight_id: int):
        """
        Args:
            flight_id: ID do voo a ser encontrado
        """
        self.flight_id = flight_id
    
    def filter(self, flights: List[Flight]) -> List[Flight]:
        """
        Retorna lista com apenas o voo que tem o ID especificado.
        """
        return [flight for flight in flights if flight.id == self.flight_id]
    
    def description(self) -> str:
        return f"ID do Voo: {self.flight_id}"


# ===== ESTRATÉGIA COMPOSTA: Múltiplos Filtros =====
class CompositeFilterStrategy(FlightFilterStrategy):
    """
    Estratégia que permite combinar múltiplas estratégias.
    """
    
    def __init__(self):
        """Inicializa com lista vazia de estratégias"""
        self.strategies: List[FlightFilterStrategy] = []
    
    def add_strategy(self, strategy: FlightFilterStrategy):
        """
        Adiciona uma nova estratégia à composição.
        
        Args:
            strategy: Estratégia de filtro a ser adicionada
        """
        self.strategies.append(strategy)
        return self  #é pra permitir encadeamentos: composite.add().add()
    
    def filter(self, flights: List[Flight]) -> List[Flight]:
        """
        Aplica todas as estratégias em sequência.
        Cada estratégia filtra o resultado da anterior.
        """
        result = flights  #começa com todos os voos
        
        #aplica cada estratégia sequencialmente
        for strategy in self.strategies:
            result = strategy.filter(result)
            
            #otimização: se lista ficar vazia, não precisa continuar
            if not result:
                break
        
        return result
    
    def description(self) -> str:
        """Combina descrições de todas as estratégias"""
        if not self.strategies:
            return "Sem filtros aplicados"
        
        descriptions = [s.description() for s in self.strategies]
        return " + ".join(descriptions)