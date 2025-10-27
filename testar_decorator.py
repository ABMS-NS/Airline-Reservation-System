"""
Arquivo de teste para decorators (funcionalidade feita)

"""


from ycaro_airlines.models import Flight
from ycaro_airlines.decorators import *

Flight.mock_flight()
flight = list(Flight.flights.values())[0]

pricing = BasicFlightPricing(flight)
pricing = SeatSelectionDecorator(pricing)
pricing = BaggageDecorator(pricing, 2)

print(f'Preço: R${pricing.get_price():.2f}')
print('Features:', pricing.get_features())
