"""
Integrada com os 3 padrões estruturais - VERSÃO CORRIGIDA
"""
from functools import partial
from typing import Callable, Tuple
import questionary
from ycaro_airlines.views import console, menu_factory
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models.booking import Booking, BookingStatus
from ycaro_airlines.models.flight import SeatStatus
from ycaro_airlines.models.customer import Customer
import re

# ADAPTER para pagamentos
from ycaro_airlines.adapters import PaymentGatewayFactory

# COMPOSITE para notificações
from ycaro_airlines.composites import (
    NotificationBuilder,
    NotificationTemplate
)


def sanitize_text(value: str) -> str | None:
    """Trim and normalize text inputs. Return None if input isn't a string or is empty after strip."""
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    v = value.strip()
    return v if v != "" else None


def is_valid_email(email: str) -> bool:
    """Validação simples de email"""
    if not email or not isinstance(email, str):
        return False
    return re.fullmatch(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", email.strip()) is not None


def select_seat_action(booking: Booking):
    """Helper para selecionar assento"""
    try:
        # Obter lista de assentos disponíveis
        available_seats = [
            str(k) for k, v in booking.flight.seats.items()
            if v.status is SeatStatus.open
        ]
        
        if not available_seats:
            print("❌ No seats available!")
            return False
        
        seat_input = questionary.autocomplete(
            "Which seat do you want?",
            choices=available_seats
        ).ask()

        seat_input = sanitize_text(seat_input)
        if not seat_input:
            return False

        # Validar se o assento escolhido está disponível
        if seat_input not in available_seats:
            print(f"❌ Seat {seat_input} is not available!")
            return False

        # Converter para inteiro e reservar
        if not seat_input.isdigit():
            print(f"❌ Seat must be a number: {seat_input}")
            return False

        seat = int(seat_input)
        return booking.reserve_seat(seat)
        
    except ValueError as e:
        print(f"❌ Invalid seat number: {e}")
        return False
    except Exception as e:
        print(f"❌ Error selecting seat: {e}")
        return False


class BookingMenu(ActionView):
    title: str = "See Bookings"

    def operation(self) -> UIView | None:
        try:
            if self.user is None:
                raise ValueError("User must be logged")

            # Defensive check: ensure user has an integer id assigned
            user_id_attr = getattr(self.user, "id", None)
            if user_id_attr is None or not isinstance(user_id_attr, int):
                print("❌ Invalid or missing user id on the current user object")
                print(f"   user object repr: {repr(self.user)}")
                print(f"   user.id value: {user_id_attr} (type: {type(user_id_attr)})")
                print("   Please ensure User/Customer instances are created via the provided constructors so they receive an id.")
                questionary.press_any_key_to_continue().ask()
                return self.parent

            # Mostrar todas as reservas
            Booking.print_bookings_table(self.user.id, console)

            bookings = Booking.list_customer_bookings(self.user.id)
            
            if len(bookings) == 0:
                print("📋 There are no bookings to manage!")
                questionary.press_any_key_to_continue().ask()
                return self.parent

            # Criar lista de IDs válidos
            valid_ids = {str(b.id) for b in bookings}

            # Selecionar booking para gerenciar
            booking_id = questionary.autocomplete(
                "Type the id of the booking you wish to manage: (type 'q' to go back)",
                choices=[str(i.id) for i in bookings]
            ).ask()

            booking_id = sanitize_text(booking_id)
            if not booking_id or booking_id == "q":
                return self.parent

            # Validar ID
            if booking_id not in valid_ids:
                print(f"❌ Invalid booking ID: {booking_id}")
                questionary.press_any_key_to_continue().ask()
                return self

            booking = Booking.get(int(booking_id))

            if booking is None:
                print(f"❌ Booking not found: {booking_id}")
                questionary.press_any_key_to_continue().ask()
                return self

            # Mostrar detalhes do booking
            booking.print_booking_table(console)

            # Menu de opções baseado no status
            if booking.status == BookingStatus.booked:
                options: list[Tuple[str, Callable]] = [
                    ("🪑 Change Seat", partial(self._change_seat, booking=booking)),
                    ("✅ Online Check-in", partial(self._checkin_with_notification, booking=booking)),
                    ("💳 Process Payment", partial(self._process_payment, booking=booking)),
                    ("❌ Cancel Booking", partial(self._cancel_with_refund, booking=booking)),
                ]
            elif booking.status == BookingStatus.checked_in:
                options = [
                    ("🎫 View Ticket", partial(booking.print_booking_table, console=console)),
                    ("📧 Resend Confirmation", partial(self._resend_confirmation, booking=booking)),
                ]
            else:  # cancelled
                options = [
                    ("📋 View Booking Details", partial(booking.print_booking_table, console=console)),
                ]

            menu_factory("Booking Management", options)()

            return self.parent
            
        except ValueError as e:
            print(f"❌ Error: {e}")
            questionary.press_any_key_to_continue().ask()
            return self.parent
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            questionary.press_any_key_to_continue().ask()
            return self.parent

    def _change_seat(self, booking: Booking):
        """Muda assento do booking"""
        try:
            if self.user is None:
                print("❌ No user logged in!")
                questionary.press_any_key_to_continue().ask()
                return
                
            if booking is None:
                print("❌ Invalid booking!")
                questionary.press_any_key_to_continue().ask()
                return
            
            if not booking.can_change_seat():
                print(f"❌ Cannot change seat in current status: {booking.state.get_status_name()}")
                questionary.press_any_key_to_continue().ask()
                return

            if select_seat_action(booking):
                print(f"✅ Seat changed to {booking.seat_id}")
            else:
                print("❌ Could not change seat")
            
            questionary.press_any_key_to_continue().ask()
            
        except AttributeError as e:
            print(f"❌ Attribute error: {e}")
            print("This might be a data corruption issue. Please try again.")
            questionary.press_any_key_to_continue().ask()
        except Exception as e:
            print(f"❌ Error changing seat: {e}")
            questionary.press_any_key_to_continue().ask()

    def _checkin_with_notification(self, booking: Booking):
        """
        Faz check-in e envia notificações usando COMPOSITE PATTERN
        """
        try:
            # Verificar se usuário está logado
            if self.user is None:
                print("❌ No user logged in!")
                questionary.press_any_key_to_continue().ask()
                return
                
            # Verificar propriedade do booking
            if self.user.id != booking.owner_id:
                print("❌ You aren't the owner of this booking!")
                questionary.press_any_key_to_continue().ask()
                return

            # Confirmar nome do passageiro
            name_confirmation = questionary.text(
                "Confirm passenger name:"
            ).ask()

            name_confirmation = sanitize_text(name_confirmation)
            if not name_confirmation:
                print("❌ Name confirmation cancelled or empty")
                questionary.press_any_key_to_continue().ask()
                return

            if not re.fullmatch(r"^[a-zA-Z ]+$", name_confirmation):
                print("❌ Invalid name format! Use only letters and spaces")
                questionary.press_any_key_to_continue().ask()
                return

            if name_confirmation != sanitize_text(booking.passenger_name):
                print("❌ Incorrect name!")
                questionary.press_any_key_to_continue().ask()
                return

            # Confirmar CPF do passageiro
            cpf_confirmation = questionary.text(
                "Confirm passenger CPF (format: 123.456.789-12):"
            ).ask()

            cpf_confirmation = sanitize_text(cpf_confirmation)
            if not cpf_confirmation:
                print("❌ CPF confirmation cancelled or empty")
                questionary.press_any_key_to_continue().ask()
                return

            if not re.fullmatch(r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$", cpf_confirmation):
                print("❌ Invalid CPF format! Use: 123.456.789-12")
                questionary.press_any_key_to_continue().ask()
                return

            if cpf_confirmation != sanitize_text(booking.passenger_cpf):
                print("❌ Incorrect CPF!")
                questionary.press_any_key_to_continue().ask()
                return

            # Confirmar check-in
            confirm_check_in = questionary.confirm(
                "Are you sure you want to check-in this booking?"
            ).ask()

            if not confirm_check_in:
                questionary.press_any_key_to_continue().ask()
                return

            # Garantir que tem assento selecionado
            if booking.seat_id is None:
                print("⚠️  You need to select a seat first!")
                if not select_seat_action(booking):
                    print("❌ Check-in cancelled - no seat selected")
                    questionary.press_any_key_to_continue().ask()
                    return

            # Perguntar se quer mudar de assento
            confirm_change_seat = questionary.confirm(
                "Do you want to change seats?"
            ).ask()
            
            if confirm_change_seat:
                select_seat_action(booking)

            # Realizar check-in
            if not booking.check_in():
                print("❌ Couldn't check-in booking")
                questionary.press_any_key_to_continue().ask()
                return

            # Dar pontos de fidelidade
            if isinstance(self.user, Customer):
                points = int(booking.price // 10)
                self.user.gain_loyalty_points(points)
                print(f"✅ You earned {points} loyalty points!")

            # Oferecer notificações
            print("\n" + "="*50)
            print("📧 SEND CONFIRMATION (COMPOSITE PATTERN)")
            print("="*50)

            send_notif = questionary.confirm(
                "Send check-in confirmation?"
            ).ask()

            if not send_notif:
                questionary.press_any_key_to_continue().ask()
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

            if not channels or not isinstance(channels, list):
                questionary.press_any_key_to_continue().ask()
                return

            # COMPOSITE EM AÇÃO - Construir grupo de notificações
            builder = NotificationBuilder().set_name("Check-in Confirmation")

            if "email" in channels:
                username = sanitize_text(getattr(self.user, 'username', None))
                if username:
                    email_addr = f"{username}@example.com"
                    if is_valid_email(email_addr):
                        builder.add_email(email_addr)
                    else:
                        print(f"⚠️ Skipping invalid generated email: {email_addr}")
                else:
                    print("⚠️ No username available to build email; skipping email channel")
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
            
        except Exception as e:
            print(f"❌ Error during check-in: {e}")
            questionary.press_any_key_to_continue().ask()

    def _resend_confirmation(self, booking: Booking):
        """Reenvia confirmação de check-in"""
        self._send_notification(booking, "Check-in confirmation resent")

    def _send_notification(self, booking: Booking, title: str):
        """Helper para enviar notificações"""
        channels = questionary.checkbox(
            "Select notification channels:",
            choices=[
                questionary.Choice("📧 Email", "email"),
                questionary.Choice("📱 SMS", "sms"),
                questionary.Choice("🔔 Push", "push"),
            ]
        ).ask()

        channels = channels if isinstance(channels, list) else None
        if not channels:
            return

        builder = NotificationBuilder().set_name(title)

        if "email" in channels:
            username = sanitize_text(getattr(self.user, 'username', None))
            if username:
                email_addr = f"{username}@example.com"
                if is_valid_email(email_addr):
                    builder.add_email(email_addr)
                else:
                    print(f"⚠️ Skipping invalid generated email: {email_addr}")
            else:
                print("⚠️ No username available to build email; skipping email channel")
        if "sms" in channels:
            builder.add_sms("+55 82 99999-9999")
        if "push" in channels:
            builder.add_push(self.user.id)

        message = NotificationTemplate.booking_confirmation(
            booking.id,
            f"{booking.flight.From} → {booking.flight.To}"
        )

        notifications = builder.build()
        notifications.send(message)
        print(f"✅ {notifications.get_recipients_count()} notifications sent!")
        questionary.press_any_key_to_continue().ask()

    def _process_payment(self, booking: Booking):
        """
        Processa pagamento usando ADAPTER PATTERN
        """
        try:
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

            payment_method = sanitize_text(payment_method)
            if not payment_method or payment_method == "cancel":
                return

            # Coletar dados conforme método
            customer_data = self._collect_payment_data(payment_method, booking)
            
            if not customer_data:
                print("❌ Payment cancelled")
                questionary.press_any_key_to_continue().ask()
                return

            # ADAPTER EM AÇÃO - Criar gateway apropriado
            print("\n⏳ Processing payment...")
            # validate method before creating gateway
            if payment_method not in ("pix", "credit_card", "boleto"):
                print("❌ Unsupported payment method")
                questionary.press_any_key_to_continue().ask()
                return

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
            
        except Exception as e:
            print(f"❌ Error processing payment: {e}")
            questionary.press_any_key_to_continue().ask()

    def _collect_payment_data(self, method: str, booking: Booking) -> dict:
        """Coleta dados de pagamento"""
        try:
            if method == "pix":
                key = questionary.text("PIX Key (email, phone, or CPF):").ask()
                key = sanitize_text(key)
                if not key:
                    print("❌ PIX key is required")
                    return None

                # basic validation: if looks like email, validate; else ensure minimal length
                if "@" in key:
                    if not is_valid_email(key):
                        print("❌ Invalid PIX email key")
                        return None
                else:
                    if len(re.sub(r"\D", "", key)) < 6:
                        print("❌ PIX key looks too short")
                        return None

                return {"pix_key": key, "name": sanitize_text(booking.passenger_name) or ""}

            elif method == "credit_card":
                card = questionary.text("Card number (16 digits):").ask()
                card = sanitize_text(card)
                if not card:
                    print("❌ Card number is required")
                    return None

                # remove spaces and dashes
                card_clean = re.sub(r"\s+|-", "", card)
                if len(card_clean) != 16 or not card_clean.isdigit():
                    print("❌ Invalid card number! Must be 16 digits")
                    return None

                cvv = questionary.text("CVV (3 digits):").ask()
                cvv = sanitize_text(cvv)
                if not cvv:
                    print("❌ CVV is required")
                    return None

                if len(cvv) != 3 or not cvv.isdigit():
                    print("❌ Invalid CVV! Must be 3 digits")
                    return None

                expiry = questionary.text("Expiry date (MM/YY):").ask()
                expiry = sanitize_text(expiry)
                if not expiry:
                    print("❌ Expiry date is required")
                    return None

                if not re.fullmatch(r"^\d{2}/\d{2}$", expiry):
                    print("❌ Invalid expiry format! Use MM/YY")
                    return None

                return {
                    "card_number": card_clean,
                    "cvv": cvv,
                    "expiry": expiry,
                    "name": sanitize_text(booking.passenger_name) or ""
                }

            else:  # boleto
                cpf = sanitize_text(getattr(booking, 'passenger_cpf', None))
                if not cpf or not re.fullmatch(r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$", cpf):
                    print("❌ Invalid or missing CPF for boleto")
                    return None
                return {
                    "name": sanitize_text(booking.passenger_name) or "",
                    "cpf": cpf
                }
                
        except Exception as e:
            print(f"❌ Error collecting payment data: {e}")
            return None

    def _cancel_with_refund(self, booking: Booking):
        """
        Cancela booking e processa reembolso usando ADAPTER
        """
        try:
            if not booking.can_cancel():
                print(f"❌ Cannot cancel booking in status: {booking.state.get_status_name()}")
                questionary.press_any_key_to_continue().ask()
                return

            confirm = questionary.confirm(
                "Are you sure you want to cancel this booking?"
            ).ask()

            if not confirm:
                return

            if booking.owner_id != self.user.id:
                print("❌ You don't own this booking!")
                questionary.press_any_key_to_continue().ask()
                return

            # Cancelar usando State Pattern
            if not booking.cancel_booking():
                print("❌ Could not cancel booking")
                questionary.press_any_key_to_continue().ask()
                return

            print("✅ Booking cancelled successfully!")

            # Oferecer reembolso
            process_refund = questionary.confirm(
                f"Process refund of R${booking.price:.2f}?"
            ).ask()

            if process_refund:
                print("\n💰 Processing refund...")
                print("(Using same payment method as original transaction)")
                
                transaction_id = f"SIMULATED-{booking.id}"
                
                gateway = PaymentGatewayFactory.create_gateway("pix")
                success = gateway.refund(transaction_id, booking.price)
                
                if success:
                    print("✅ Refund processed successfully!")
                    print("Amount will be credited within 5-10 business days")
                else:
                    print("❌ Could not process refund automatically")
                    print("Please contact customer service")

            questionary.press_any_key_to_continue().ask()
            
        except Exception as e:
            print(f"❌ Error cancelling booking: {e}")
            questionary.press_any_key_to_continue().ask()