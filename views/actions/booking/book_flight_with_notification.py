"""
ycaro_airlines/views/actions/booking/book_flight_with_notification.py

BookFlightAction integrado com Sistema de Notificações (Composite Pattern)
"""
import re
import questionary
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models import Flight, Booking, Customer
from ycaro_airlines.views import console
from ycaro_airlines.composites.notification_system import (
    NotificationService,
    NotificationBuilder,
    NotificationTemplate
)


class BookFlightWithNotificationAction(ActionView):
    title: str = "Book Flight (with Notifications)"

    def operation(self) -> UIView | None:
        if self.user is None or not isinstance(self.user, Customer):
            return self.parent

        # Selecionar voo
        flight_id = questionary.autocomplete(
            "Digite o ID do voo (q para voltar):",
            choices=[str(k) for k in Flight.flights.keys()],
            validate=lambda x: x in {str(k) for k in Flight.flights.keys()} or x == "q"
        ).ask()

        if flight_id == "q" or not flight_id:
            return self.parent

        flight = Flight.flights[int(flight_id)]
        flight.print_flight_table(console)

        if not questionary.confirm("Deseja reservar este voo?").ask():
            return self.parent

        # Dados do passageiro
        passenger_name = questionary.text("Nome do passageiro:").ask()
        passenger_cpf = questionary.text(
            "CPF do passageiro:",
            validate=lambda x: bool(re.fullmatch(r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$", x))
        ).ask()

        if not passenger_name or not passenger_cpf:
            print("❌ Operação cancelada")
            return self.parent

        # Criar booking
        booking = Booking(
            flight_id=flight.id,
            owner_id=self.user.id,
            passenger_name=passenger_name,
            passenger_cpf=passenger_cpf,
            price=flight.price,
        )

        print(f"\n✅ Voo reservado com sucesso! Booking ID: {booking.id}")

        # ===== COMPOSITE PATTERN EM AÇÃO =====
        # Perguntar preferências de notificação
        print("\n📢 Configure suas notificações:")
        
        notification_prefs = questionary.checkbox(
            "Como deseja receber notificações sobre esta reserva?",
            choices=[
                questionary.Choice("📧 E-mail", "email"),
                questionary.Choice("📱 SMS", "sms"),
                questionary.Choice("🔔 Notificação Push", "push"),
                questionary.Choice("💬 WhatsApp", "whatsapp"),
            ]
        ).ask()

        if notification_prefs:
            # Construir grupo de notificações baseado nas preferências
            builder = NotificationBuilder().set_name(f"Notificações - Booking {booking.id}")
            
            if "email" in notification_prefs:
                email = questionary.text(
                    "E-mail:",
                    default=f"{self.user.username}@example.com"
                ).ask()
                builder.add_email(email)
            
            if "sms" in notification_prefs:
                phone = questionary.text(
                    "Telefone (com DDD):",
                    default="+55 82 99999-9999"
                ).ask()
                builder.add_sms(phone)
            
            if "push" in notification_prefs:
                builder.add_push(self.user.id)
            
            if "whatsapp" in notification_prefs:
                phone = questionary.text(
                    "WhatsApp (com DDD):",
                    default="+55 82 99999-9999"
                ).ask()
                builder.add_whatsapp(phone)
            
            # Enviar notificação de confirmação
            notifications = builder.build()
            message = NotificationTemplate.booking_confirmation(
                booking.id,
                f"{flight.From} → {flight.To}"
            )
            
            print("\n📤 Enviando notificações...")
            notifications.send(message)
            print(f"✅ {notifications.get_recipients_count()} notificações enviadas com sucesso!")
        
        questionary.press_any_key_to_continue().ask()
        return self.parent


# ===== EXEMPLO DE USO EM CHECK-IN =====

def check_in_with_notification(user: Customer, booking: Booking):
    """Faz check-in e envia notificações"""
    
    print("⏳ Processando check-in...")
    
    if booking.check_in():
        print("✅ Check-in realizado com sucesso!")
        
        # Ganhar pontos
        points = int(booking.price // 10)
        user.gain_loyalty_points(points)
        print(f"🎁 Você ganhou {points} pontos de fidelidade!")
        
        # Enviar notificações de confirmação de check-in
        notifications = NotificationBuilder() \
            .add_email(f"{user.username}@example.com") \
            .add_push(user.id) \
            .build()
        
        # Template customizado para check-in
        message = f"""
✅ CHECK-IN CONFIRMADO

Booking ID: {booking.id}
Voo: {booking.flight.From} → {booking.flight.To}
Assento: {booking.seat_id if booking.seat_id else 'Não selecionado'}
Portão: A{booking.flight.id % 10 + 1}

🎁 Você ganhou {points} pontos de fidelidade!

Apresente-se no portão 30 minutos antes da partida.
Bom voo! ✈️
        """.strip()
        
        print("\n📤 Enviando confirmação...")
        notifications.send(message)
    else:
        print("❌ Falha no check-in")


# ===== EXEMPLO: NOTIFICAÇÃO EM MASSA =====

def notify_flight_delay_example():
    """Exemplo de notificação em massa para atraso de voo"""
    
    from ycaro_airlines.models.booking import Booking
    from ycaro_airlines.composites.notification_system import (
        NotificationGroup,
        EmailNotification,
        SMSNotification,
        PushNotification
    )
    
    print("=== EXEMPLO: NOTIFICAÇÃO DE ATRASO EM MASSA ===\n")
    
    # Simular vários passageiros afetados
    affected_passengers = [
        {"name": "João Silva", "email": "joao@example.com", "phone": "+55 82 91111-1111", "user_id": 1},
        {"name": "Maria Santos", "email": "maria@example.com", "phone": "+55 82 92222-2222", "user_id": 2},
        {"name": "Pedro Costa", "email": "pedro@example.com", "phone": "+55 82 93333-3333", "user_id": 3},
    ]
    
    # Criar grupo principal
    main_group = NotificationGroup("Atraso Voo YC-456")
    
    # Para cada passageiro, criar subgrupo
    for passenger in affected_passengers:
        passenger_group = NotificationGroup(passenger["name"])
        passenger_group.add(EmailNotification(passenger["email"]))
        passenger_group.add(SMSNotification(passenger["phone"]))
        passenger_group.add(PushNotification(passenger["user_id"]))
        
        main_group.add(passenger_group)
    
    # Enviar para todos de uma vez
    message = NotificationTemplate.flight_delay(
        "Maceió → Recife",
        "16:30 (atraso de 2h)",
        "Condições meteorológicas adversas"
    )
    
    print("📤 Enviando notificações...")
    main_group.send(message)
    
    print(f"\n📊 Resumo:")
    print(f"   Passageiros afetados: {len(affected_passengers)}")
    print(f"   Total de notificações: {main_group.get_recipients_count()}")