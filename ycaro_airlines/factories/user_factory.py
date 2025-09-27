from abc import ABC, abstractmethod
from ycaro_airlines.models.user import User
from ycaro_airlines.models.customer import Customer
from ycaro_airlines.models.customer_service import CustomerServiceWorker

class UserFactory(ABC):
    @abstractmethod
    def create_user(self, username: str, **kwargs) -> User:
        pass

class CustomerFactory(UserFactory):
    def create_user(self, username: str, **kwargs) -> Customer:
        return Customer(username=username, **kwargs)

class CustomerServiceFactory(UserFactory):
    def create_user(self, username: str, **kwargs) -> CustomerServiceWorker:
        return CustomerServiceWorker(username=username, **kwargs)

class UserFactoryProvider:
    _factories = {
        "customer": CustomerFactory(),
        "service": CustomerServiceFactory(),
    }
    
    @classmethod
    def get_factory(cls, user_type: str) -> UserFactory:
        factory = cls._factories.get(user_type)
        if not factory:
            raise ValueError(f"Unknown user type: {user_type}")
        return factory
    
    @classmethod
    def create_user(cls, user_type: str, username: str, **kwargs) -> User:
        factory = cls.get_factory(user_type)
        return factory.create_user(username, **kwargs)