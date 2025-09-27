from datetime import datetime
from math import inf
from ycaro_airlines.models.flight import FlightQueryParams

class FlightQueryBuilder:
    def __init__(self):
        self._params: FlightQueryParams = {}
    
    def with_price_range(self, min_price: float = 0, max_price: float = inf):
        if min_price >= 0:
            self._params["price_gte"] = min_price
        if max_price < inf:
            self._params["price_lte"] = max_price
        return self
    
    def with_cities(self, from_city: str = None, to_city: str = None):
        if from_city:
            self._params["city_from"] = from_city
        if to_city:
            self._params["city_to"] = to_city
        return self
    
    def with_departure_date_range(self, start_date: datetime = None, end_date: datetime = None):
        if start_date:
            self._params["date_departure_gte"] = start_date
        if end_date:
            self._params["date_departure_lte"] = end_date
        return self
    
    def with_arrival_date_range(self, start_date: datetime = None, end_date: datetime = None):
        if start_date:
            self._params["date_arrival_gte"] = start_date
        if end_date:
            self._params["date_arrival_lte"] = end_date
        return self
    
    def with_flight_id(self, flight_id: int):
        self._params["flight_id"] = flight_id
        return self
    
    def build(self) -> FlightQueryParams:
        return self._params.copy()
    
    def reset(self):
        self._params = {}
        return self