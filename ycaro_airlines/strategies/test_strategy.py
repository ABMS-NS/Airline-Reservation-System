from ycaro_airlines.models.flight import Flight
from ycaro_airlines.strategies.concrete_filters import (
    CityFilterStrategy,
    PriceFilterStrategy,
    DepartureDateFilterStrategy,
    ArrivalDateFilterStrategy,
    FlightIdFilterStrategy,
    CompositeFilterStrategy
)
from ycaro_airlines.strategies.flight_filter_context import FlightFilterContext

# Criar voos de teste
print("Criando voos de teste...")
for _ in range(10):
    Flight.mock_flight()

print(f"Total de voos criados: {len(Flight.flights)}\n")

# Exemplo 1: Usar estratégia única
print("=== Exemplo 1: Filtro por Cidade ===")
city_strategy = CityFilterStrategy(from_city="Maceio")
context = FlightFilterContext(city_strategy)
result = context.apply_filter(list(Flight.flights.values()))
print(f"Filtro: {context.get_description()}")
print(f"Voos de Maceió: {len(result)}\n")

# Exemplo 2: Trocar estratégia em tempo de execução
print("=== Exemplo 2: Trocar Estratégia ===")
context.set_strategy(PriceFilterStrategy(min_price=100, max_price=300))
result = context.apply_filter(list(Flight.flights.values()))
print(f"Filtro: {context.get_description()}")
print(f"Voos entre R$100-300: {len(result)}\n")

# Exemplo 3: Estratégia composta
print("=== Exemplo 3: Múltiplos Filtros ===")
composite = CompositeFilterStrategy()
composite.add_strategy(CityFilterStrategy(from_city="Maceio"))
composite.add_strategy(PriceFilterStrategy(max_price=250))

context.set_strategy(composite)
result = context.apply_filter(list(Flight.flights.values()))
print(f"Filtro: {context.get_description()}")
print(f"Voos encontrados: {len(result)}")

# Mostrar detalhes dos voos encontrados
if result:
    print("\nDetalhes dos voos encontrados:")
    for flight in result:
        print(f"  ID: {flight.id} | {flight.From} -> {flight.To} | R${flight.price:.2f}")