"""
ycaro_airlines/views/booking_menu.py

SUBSTITUIR O ARQUIVO EXISTENTE
Agora integrado com os 3 padrões estruturais
"""
from functools import partial
from typing import Callable, Tuple
import questionary
from ycaro_airlines.views.actions.booking_actions import (
    cancel_booking_action,
    check_in_action,
    select_seat_action,
)
from ycaro_airlines.views import console, menu_factory
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models.booking import Booking, BookingStatus

# ADAPTER para pagamentos
from ycaro_airlines.adapters import PaymentGatewayFactory

# COMPOSITE para notificações
from ycaro_airlines.composites import (
    NotificationBuilder,
    NotificationTemplate
)


class BookingMenu(ActionView):
    title: str = "See Bookings"

    def operation(self) -> UIView | None:
        if self.user is None:
            raise ValueError("User must be logged")

        Booking.print_bookings_table(self.user.id, console)

        if len(Booking.list_customer_bookings(self.user.id)) == 0:
            print("There are no bookings to manage!")
            return self.parent

        booking_id = questionary.autocomplete(
            "Type the id of the booking you wish to manage:(type 'q' to go back)",
            choices=[str(i.id) for i in Booking.list_customer_bookings(self.user.id)],
            validate=lambda x: (
                True
                if x
                in {str(i.id) for i in Booking.list_customer_bookings(self.user.id)}
                or x == "q"
                else False
            ),
        ).ask()

        if booking_id == "q" or not booking_id:
            return self.parent

        booking = Booking.get(int(booking_id))

        if booking is None:
            raise ValueError("Booking Id must be valid")

        booking.print_booking_table(console)

        # Menu de opções com integração dos padrões
        options: list[Tuple[str, Callable]] = [
            (
                "Cancel Booking",
                partial(self._cancel_with_refund, booking=booking),
            ),
            ("Change Seat", partial(select_seat_action, booking=booking)),
            (
                "Online Check-in",
                partial(self._checkin_with_notification, booking=booking),
            ),
        ]

        # Se já fez check-in, mostrar apenas visualização
        if booking.status != BookingStatus.booked:
            options = [
                (
                    "View Ticket",
                    partial(booking.print_booking_table, console=console),
                )
            ]
        else:
            # Adicionar opção de pagar se ainda não pagou
            options.append(
                ("💳 Process Payment", partial(self._process_payment, booking=booking))
            )

        menu_factory("Booking management", options)()

        return self.parent

    def _process_payment(self, booking: Booking):
        """
        Processa pagamento usando ADAPTER PATTERN
        """
        print("\n" + "="*50)
        print("💳 PAYMENT PROCESSING (ADAPTER PATTERN)")
        print("="*50)

        payment_method = questionary.select(
            "Choose payment method:",
            choices=[
                questionary.Choice("💰 PIX (Instant)", "pix"),
                questionary.Choice("💳 Credit Card", "credit_card"),
                questionary.Choice("📄 Bank Slip (Boleto)", "boleto"),
                questionary.Choice("❌ Cancel", "cancel")
            ]
        ).ask()

        if payment_method == "cancel":
            return

        # Coletar dados conforme método
        customer_data = self._collect_payment_data(payment_method, booking)
        
        if not customer_data:
            print("❌ Payment cancelled")
            return

        # ADAPTER EM AÇÃO - Criar gateway apropriado
        print("\n⏳ Processing payment...")
        gateway = PaymentGatewayFactory.create_gateway(payment_method)
        
        # Processar (interface unificada!)
        result = gateway.process_payment(booking.price, customer_data)

        # Mostrar resultado
        if result["success"]:
            console.print(f"\n✅ {result['message']}", style="bold green")
            console.print(f"🔖 Transaction ID: {result['transaction_id']}", style="cyan")
            
            if payment_method == "boleto":
                console.print("\n📋 Instructions:", style="yellow")
                console.print("• Pay at any bank or authorized agent")
                console.print("• Payment confirmation: up to 2 business days")
        else:
            console.print(f"\n❌ {result['message']}", style="bold red")

        questionary.press_any_key_to_continue().ask()

    def _collect_payment_data(self, method: str, booking: Booking) -> dict:
        """Coleta dados de pagamento"""
        if method == "pix":
            key = questionary.text("PIX Key:").ask()
            return {"pix_key": key, "name": booking.passenger_name} if key else None

        elif method == "credit_card":
            card = questionary.text(
                "Card number (16 digits):",
                validate=lambda x: len(x) == 16 and x.isdigit()
            ).ask()
            
            if not card:
                return None
                
            cvv = questionary.text(
                "CVV:",
                validate=lambda x: len(x) == 3 and x.isdigit()
            ).ask()
            
            expiry = questionary.text("Expiry (MM/YY):").ask()
            
            return {
                "card_number": card,
                "cvv": cvv,
                "expiry": expiry,
                "name": booking.passenger_name
            }

        else:  # boleto
            return {
                "name": booking.passenger_name,
                "cpf": booking.passenger_cpf
            }

    def _checkin_with_notification(self, booking: Booking):
        """
        Faz check-in e envia notificações usando COMPOSITE PATTERN
        """
        # Check-in normal
        check_in_action(self.user, booking)

        # Se check-in foi bem sucedido, oferecer notificações
        if booking.status == BookingStatus.checked_in:
            print("\n" + "="*50)
            print("📧 SEND CONFIRMATION (COMPOSITE PATTERN)")
            print("="*50)

            send_notif = questionary.confirm(
                "Send check-in confirmation?"
            ).ask()

            if not send_notif:
                return

            # Escolher canais
            channels = questionary.checkbox(
                "Select notification channels:",
                choices=[
                    questionary.Choice("📧 Email", "email"),
                    questionary.Choice("📱 SMS", "sms"),
                    questionary.Choice("🔔 Push", "push"),
                ]
            ).ask()

            if not channels:
                return

            # COMPOSITE EM AÇÃO - Construir grupo de notificações
            builder = NotificationBuilder().set_name("Check-in Confirmation")

            if "email" in channels:
                builder.add_email(f"{self.user.username}@example.com")
            if "sms" in channels:
                builder.add_sms("+55 82 99999-9999")
            if "push" in channels:
                builder.add_push(self.user.id)

            # Criar mensagem customizada
            message = f"""
✅ CHECK-IN CONFIRMED

Booking ID: {booking.id}
Flight: {booking.flight.From} → {booking.flight.To}
Seat: {booking.seat_id if booking.seat_id else 'Not selected'}
Gate: A{booking.flight.id % 10 + 1}

Present yourself at the gate 30 minutes before departure.
Have a nice flight! ✈️
            """.strip()

            # Enviar para todos os canais de uma vez!
            notifications = builder.build()
            print("\n📤 Sending notifications...")
            notifications.send(message)
            print(f"✅ {notifications.get_recipients_count()} notifications sent!")

            questionary.press_any_key_to_continue().ask()

    def _cancel_with_refund(self, booking: Booking):
        """
        Cancela booking e processa reembolso usando ADAPTER
        """
        # Confirmação normal
        confirm = questionary.confirm(
            "Are you sure you want to cancel this booking?"
        ).ask()

        if not confirm:
            return

        if booking.owner_id != self.user.id:
            print("You don't own this booking!")
            return

        # Cancelar
        if not booking.cancel_booking():
            print("❌ Could not cancel booking")
            return

        print("✅ Booking cancelled successfully!")

        # Oferecer reembolso se já pagou
        process_refund = questionary.confirm(
            f"Process refund of R${booking.price:.2f}?"
        ).ask()

        if process_refund:
            print("\n💰 Processing refund...")
            print("(Using same payment method as original transaction)")
            
            # Simular que temos o transaction_id salvo
            # Em produção, você salvaria isso no booking
            transaction_id = f"SIMULATED-{booking.id}"
            
            # ADAPTER para reembolso
            gateway = PaymentGatewayFactory.create_gateway("pix")  # Exemplo
            success = gateway.refund(transaction_id, booking.price)
            
            if success:
                print("✅ Refund processed successfully!")
                print("Amount will be credited within 5-10 business days")
            else:
                print("❌ Could not process refund automatically")
                print("Please contact customer service")

        questionary.press_any_key_to_continue().ask()