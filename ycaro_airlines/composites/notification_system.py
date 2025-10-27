"""
ycaro_airlines/composites/notification_system.py

Composite Pattern para Sistema de Notificações
Permite enviar notificações individuais ou em grupo
"""
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime


# ===== COMPONENT =====
class NotificationComponent(ABC):
    """Interface base para componentes de notificação"""
    
    @abstractmethod
    def send(self, message: str) -> bool:
        """Envia notificação"""
        pass
    
    @abstractmethod
    def get_recipients_count(self) -> int:
        """Retorna número de destinatários"""
        pass


# ===== LEAF (Notificações individuais) =====

class EmailNotification(NotificationComponent):
    """Notificação por e-mail (leaf)"""
    
    def __init__(self, email: str):
        self.email = email
    
    def send(self, message: str) -> bool:
        print(f"📧 [EMAIL] Enviando para {self.email}")
        print(f"   Mensagem: {message}")
        return True
    
    def get_recipients_count(self) -> int:
        return 1


class SMSNotification(NotificationComponent):
    """Notificação por SMS (leaf)"""
    
    def __init__(self, phone: str):
        self.phone = phone
    
    def send(self, message: str) -> bool:
        print(f"📱 [SMS] Enviando para {self.phone}")
        print(f"   Mensagem: {message[:100]}...")  # SMS limitado
        return True
    
    def get_recipients_count(self) -> int:
        return 1


class PushNotification(NotificationComponent):
    """Notificação push no app (leaf)"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
    
    def send(self, message: str) -> bool:
        print(f"🔔 [PUSH] Enviando para usuário #{self.user_id}")
        print(f"   Mensagem: {message}")
        return True
    
    def get_recipients_count(self) -> int:
        return 1


class WhatsAppNotification(NotificationComponent):
    """Notificação via WhatsApp (leaf)"""
    
    def __init__(self, phone: str):
        self.phone = phone
    
    def send(self, message: str) -> bool:
        print(f"💬 [WhatsApp] Enviando para {self.phone}")
        print(f"   Mensagem: {message}")
        return True
    
    def get_recipients_count(self) -> int:
        return 1


# ===== COMPOSITE (Grupos de notificações) =====

class NotificationGroup(NotificationComponent):
    """Grupo de notificações (composite)"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.notifications: List[NotificationComponent] = []
    
    def add(self, notification: NotificationComponent):
        """Adiciona notificação ao grupo"""
        self.notifications.append(notification)
        return self
    
    def remove(self, notification: NotificationComponent):
        """Remove notificação do grupo"""
        self.notifications.remove(notification)
        return self
    
    def send(self, message: str) -> bool:
        """Envia para todos os componentes do grupo"""
        if self.name:
            print(f"\n📢 Enviando notificação em grupo: '{self.name}'")
        
        success = True
        for notification in self.notifications:
            if not notification.send(message):
                success = False
        
        return success
    
    def get_recipients_count(self) -> int:
        """Conta total de destinatários (recursivo)"""
        return sum(n.get_recipients_count() for n in self.notifications)


# ===== TEMPLATES DE NOTIFICAÇÃO =====

class NotificationTemplate:
    """Templates de mensagens para diferentes eventos"""
    
    @staticmethod
    def booking_confirmation(booking_id: int, flight_info: str) -> str:
        return f"""
✅ RESERVA CONFIRMADA

Booking ID: {booking_id}
Voo: {flight_info}
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Bom voo! ✈️
        """.strip()
    
    @staticmethod
    def check_in_reminder(flight_info: str, departure_time: str) -> str:
        return f"""
⏰ LEMBRETE DE CHECK-IN

Seu voo está próximo!
{flight_info}
Partida: {departure_time}

Faça o check-in online agora! 
        """.strip()
    
    @staticmethod
    def flight_delay(flight_info: str, new_time: str, reason: str) -> str:
        return f"""
⚠️ ATRASO NO VOO

{flight_info}
Novo horário: {new_time}
Motivo: {reason}

Pedimos desculpas pelo inconveniente.
        """.strip()
    
    @staticmethod
    def boarding_call(gate: str, seat: str) -> str:
        return f"""
🚪 CHAMADA PARA EMBARQUE

Portão: {gate}
Assento: {seat}

Dirija-se ao portão de embarque agora!
        """.strip()
    
    @staticmethod
    def cancellation(booking_id: int, refund_info: str) -> str:
        return f"""
❌ RESERVA CANCELADA

Booking ID: {booking_id}
{refund_info}

Reembolso será processado em até 7 dias úteis.
        """.strip()


# ===== BUILDER PARA NOTIFICAÇÕES =====

class NotificationBuilder:
    """Builder para criar grupos de notificação facilmente"""
    
    def __init__(self):
        self.group = NotificationGroup()
    
    def add_email(self, email: str):
        self.group.add(EmailNotification(email))
        return self
    
    def add_sms(self, phone: str):
        self.group.add(SMSNotification(phone))
        return self
    
    def add_push(self, user_id: int):
        self.group.add(PushNotification(user_id))
        return self
    
    def add_whatsapp(self, phone: str):
        self.group.add(WhatsAppNotification(phone))
        return self
    
    def set_name(self, name: str):
        self.group.name = name
        return self
    
    def build(self) -> NotificationGroup:
        return self.group


# ===== SERVIÇO DE NOTIFICAÇÃO =====

class NotificationService:
    """Serviço centralizado para gerenciar notificações"""
    
    @staticmethod
    def notify_booking_confirmation(user, booking):
        """Notifica confirmação de reserva"""
        
        # Criar grupo de notificações para o usuário
        notifications = NotificationBuilder() \
            .set_name("Confirmação de Reserva") \
            .add_email(f"{user.username}@example.com") \
            .add_push(user.id) \
            .add_sms("+55 82 99999-9999") \
            .build()
        
        # Criar mensagem usando template
        message = NotificationTemplate.booking_confirmation(
            booking.id,
            f"{booking.flight.From} → {booking.flight.To}"
        )
        
        # Enviar
        notifications.send(message)
        print(f"\n📊 Total de notificações enviadas: {notifications.get_recipients_count()}")
    
    @staticmethod
    def notify_check_in_reminder(user, booking):
        """Lembra usuário de fazer check-in"""
        
        notifications = NotificationBuilder() \
            .set_name("Lembrete de Check-in") \
            .add_email(f"{user.username}@example.com") \
            .add_whatsapp("+55 82 99999-9999") \
            .add_push(user.id) \
            .build()
        
        message = NotificationTemplate.check_in_reminder(
            f"{booking.flight.From} → {booking.flight.To}",
            booking.flight.departure.strftime('%d/%m/%Y %H:%M')
        )
        
        notifications.send(message)
    
    @staticmethod
    def notify_flight_delay(affected_bookings: List, new_time: str, reason: str):
        """Notifica múltiplos passageiros sobre atraso"""
        
        # Criar grupo composto com subgrupos
        main_group = NotificationGroup("Atraso de Voo - Notificação em Massa")
        
        for booking in affected_bookings:
            # Criar subgrupo para cada passageiro
            passenger_group = NotificationBuilder() \
                .add_email(f"{booking.passenger_name}@example.com") \
                .add_sms("+55 82 99999-9999") \
                .build()
            
            main_group.add(passenger_group)
        
        # Enviar para todos de uma vez
        message = NotificationTemplate.flight_delay(
            "Voo YC-123",
            new_time,
            reason
        )
        
        main_group.send(message)
        print(f"\n📊 Total de passageiros notificados: {len(affected_bookings)}")
        print(f"📊 Total de notificações enviadas: {main_group.get_recipients_count()}")