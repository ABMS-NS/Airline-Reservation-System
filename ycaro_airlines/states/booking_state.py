from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# Evita importação circular
if TYPE_CHECKING:
    from ycaro_airlines.models.booking import Booking

class BookingState(ABC):
    """
    Interface para estados de Booking.
    Cada estado concreto define comportamento específico.
    """
    
    @abstractmethod
    def can_cancel(self) -> bool:
        """Verifica se booking pode ser cancelado neste estado"""
        pass
    
    @abstractmethod
    def can_check_in(self) -> bool:
        """Verifica se pode fazer check-in neste estado"""
        pass
    
    @abstractmethod
    def can_change_seat(self) -> bool:
        """Verifica se pode trocar assento neste estado"""
        pass
    
    @abstractmethod
    def cancel(self, booking: "Booking") -> bool:
        """Tenta cancelar o booking"""
        pass
    
    @abstractmethod
    def check_in(self, booking: "Booking") -> bool:
        """Tenta fazer check-in"""
        pass
    
    @abstractmethod
    def get_status_name(self) -> str:
        """Retorna nome do estado"""
        pass


# ===== ESTADO 1: BOOKED =====
class BookedState(BookingState):
    def can_cancel(self) -> bool: return True
    def can_check_in(self) -> bool: return True
    def can_change_seat(self) -> bool: return True

    def cancel(self, booking: "Booking") -> bool:
        from ycaro_airlines.states.booking_state import CancelledState
        if booking.seat_id is not None and booking.flight:
            booking.flight.open_seat(booking.seat_id)
        booking.state = CancelledState()
        print("✅ Reserva cancelada com sucesso!")
        return True

    def check_in(self, booking: "Booking") -> bool:
        from ycaro_airlines.states.booking_state import CheckedInState
        if booking.seat_id is None:
            print("❌ Impossível fazer check-in: assento não selecionado")
            return False
        if booking.flight and booking.flight.check_in_seat(booking.id, booking.seat_id):
            booking.state = CheckedInState()
            print("✅ Check-in realizado com sucesso!")
            return True
        print("❌ Falha ao fazer check-in")
        return False

    def get_status_name(self) -> str:
        return "booked"


# ===== ESTADO 2: CHECKED IN =====
class CheckedInState(BookingState):
    def can_cancel(self) -> bool: return False
    def can_check_in(self) -> bool: return False
    def can_change_seat(self) -> bool: return False

    def cancel(self, booking: "Booking") -> bool:
        print("❌ Impossível cancelar: check-in já realizado")
        print("   Entre em contato com atendimento ao cliente")
        return False

    def check_in(self, booking: "Booking") -> bool:
        print("ℹ️  Check-in já foi realizado anteriormente")
        return False

    def get_status_name(self) -> str:
        return "checked_in"


# ===== ESTADO 3: CANCELLED =====
class CancelledState(BookingState):
    def can_cancel(self) -> bool: return False
    def can_check_in(self) -> bool: return False
    def can_change_seat(self) -> bool: return False

    def cancel(self, booking: "Booking") -> bool:
        print("ℹ️  Esta reserva já está cancelada")
        return False

    def check_in(self, booking: "Booking") -> bool:
        print("❌ Impossível fazer check-in: reserva cancelada")
        return False

    def get_status_name(self) -> str:
        return "cancelled"