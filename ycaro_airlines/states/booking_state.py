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


# ===== ESTADO 1: BOOKED (Reservado) =====
class BookedState(BookingState):
    """Estado quando booking foi criado mas ainda não fez check-in"""
    
    def can_cancel(self) -> bool:
        return True  # Pode cancelar quando está reservado
    
    def can_check_in(self) -> bool:
        return True  # Pode fazer check-in
    
    def can_change_seat(self) -> bool:
        return True  # Pode mudar assento
    
    def cancel(self, booking: "Booking") -> bool:
        """Cancela a reserva"""
        from ycaro_airlines.states.booking_state import CancelledState
        
        # Libera o assento se houver
        if booking.seat_id is not None and booking.flight:
            booking.flight.open_seat(booking.seat_id)
        
        # Muda para estado cancelado
        booking.state = CancelledState()
        print("✅ Reserva cancelada com sucesso!")
        return True
    
    def check_in(self, booking: "Booking") -> bool:
        """Faz check-in"""
        from ycaro_airlines.states.booking_state import CheckedInState
        
        # Valida se tem assento
        if booking.seat_id is None:
            print("❌ Impossível fazer check-in: assento não selecionado")
            return False
        
        # Faz check-in no voo
        if booking.flight and booking.flight.check_in_seat(booking.id, booking.seat_id):
            # Muda para estado checked-in
            booking.state = CheckedInState()
            print("✅ Check-in realizado com sucesso!")
            return True
        
        print("❌ Falha ao fazer check-in")
        return False
    
    def get_status_name(self) -> str:
        return "booked"


# ===== ESTADO 2: CHECKED IN (Check-in feito) =====
class CheckedInState(BookingState):
    """Estado após check-in realizado"""
    
    def can_cancel(self) -> bool:
        return False  # Não pode cancelar após check-in
    
    def can_check_in(self) -> bool:
        return False  # Já fez check-in
    
    def can_change_seat(self) -> bool:
        return False  # Não pode mudar assento após check-in
    
    def cancel(self, booking: "Booking") -> bool:
        print("❌ Impossível cancelar: check-in já realizado")
        print("   Entre em contato com atendimento ao cliente")
        return False
    
    def check_in(self, booking: "Booking") -> bool:
        print("ℹ️  Check-in já foi realizado anteriormente")
        return False
    
    def get_status_name(self) -> str:
        return "checked_in"


# ===== ESTADO 3: CANCELLED (Cancelado) =====
class CancelledState(BookingState):
    """Estado quando booking foi cancelado"""
    
    def can_cancel(self) -> bool:
        return False  # Já está cancelado
    
    def can_check_in(self) -> bool:
        return False  # Não pode fazer check-in de reserva cancelada
    
    def can_change_seat(self) -> bool:
        return False  # Não pode mudar assento de reserva cancelada
    
    def cancel(self, booking: "Booking") -> bool:
        print("ℹ️  Esta reserva já está cancelada")
        return False
    
    def check_in(self, booking: "Booking") -> bool:
        print("❌ Impossível fazer check-in: reserva cancelada")
        return False
    
    def get_status_name(self) -> str:
        return "cancelled"