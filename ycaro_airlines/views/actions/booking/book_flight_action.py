"""
ycaro_airlines/views/actions/booking/book_flight_action.py

SUBSTITUIR O ARQUIVO EXISTENTE POR ESTE
Agora usa DECORATOR PATTERN para calcular preços
"""
import re
import questionary
from rich.table import Table
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models import Flight, Booking, Customer
from ycaro_airlines.views import console
from ycaro_airlines.models.flight import SeatStatus

# DECORATOR PATTERN
from ycaro_airlines.decorators import (
    BasicFlightPricing,
    SeatSelectionDecorator,
    BaggageDecorator,
    PriorityBoardingDecorator,
    InsuranceDecorator,
    LoyaltyDiscountDecorator
)

# ADAPTER PATTERN
from ycaro_airlines.adapters import PaymentGatewayFactory

# COMPOSITE PATTERN
from ycaro_airlines.composites import (
    NotificationBuilder,
    NotificationTemplate
)


def select_seat_action(booking: Booking):
    """Helper para selecionar assento"""
    seat = questionary.autocomplete(
        "Which seat do you want?",
        choices=[
            str(k)
            for k, v in booking.flight.seats.items()
            if v.status is SeatStatus.open
        ],
        validate=lambda x: True
        if x
        in {
            str(k)
            for k, v in booking.flight.seats.items()
            if v.status is SeatStatus.open
        }
        else False,
    ).ask()

    if not seat:
        return False

    seat = int(seat)
    booking.reserve_seat(seat)


class BookFlightAction(ActionView):
    title: str = "Book Flight"

    def operation(self) -> UIView | None:
        if self.user is None:
            return self.parent

        if not isinstance(self.user, Customer):
            return self.parent

        # Selecionar voo
        flight_id = questionary.autocomplete(
            "Type the id of the flight you want to book:(type q to go back)",
            choices=[str(k) for k, _ in Flight.flights.items()],
            validate=lambda x: True
            if x in {str(k) for k, _ in Flight.flights.items()} or x == "q"
            else False,
        ).ask()

        if flight_id == "q" or not flight_id:
            return self.parent

        flight = Flight.flights[int(flight_id)]
        flight.print_flight_table(console)

        wants_to_book = questionary.confirm(
            "Are you sure you want to book this flight?"
        ).ask()

        if not wants_to_book:
            return self.parent

        # Dados do passageiro
        passenger_name = questionary.text("Type passenger name:").ask()
        passenger_cpf = questionary.text(
            "Type passenger cpf",
            validate=lambda x: True
            if re.fullmatch(r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$", x)
            else False,
        ).ask()
        
        if not passenger_name or not passenger_cpf:
            print("Operation Cancelled")
            return self.parent

        # ============================================
        # 🎨 DECORATOR PATTERN - Construir pacote
        # ============================================
        print("\n💼 Building your flight package...")
        
        # Começar com preço base
        pricing = BasicFlightPricing(flight)
        print(f"Base price: R${pricing.get_price():.2f}")

        # Perguntar sobre extras
        extras = questionary.checkbox(
            "Select additional services:",
            choices=[
                questionary.Choice("🪑 Seat Selection (+R$40.00)", "seat"),
                questionary.Choice("🧳 Extra Baggage (+R$149.99/bag)", "baggage"),
                questionary.Choice("⚡ Priority Boarding (+R$59.90)", "priority"),
                questionary.Choice("🛡️  Travel Insurance", "insurance"),
            ]
        ).ask()

        # Aplicar decorators baseado nas escolhas
        if "seat" in extras:
            pricing = SeatSelectionDecorator(pricing)
            print("  + Seat Selection: R$40.00")

        if "baggage" in extras:
            num_bags = int(questionary.text(
                "How many extra bags?",
                default="1",
                validate=lambda x: x.isdigit() and int(x) > 0
            ).ask())
            pricing = BaggageDecorator(pricing, num_bags)
            print(f"  + {num_bags}x Extra Baggage: R${149.99 * num_bags:.2f}")

        if "priority" in extras:
            pricing = PriorityBoardingDecorator(pricing)
            print("  + Priority Boarding: R$59.90")

        if "insurance" in extras:
            insurance_type = questionary.select(
                "Insurance type:",
                choices=[
                    questionary.Choice("Basic (R$29.90)", "basic"),
                    questionary.Choice("Premium (R$79.90)", "premium")
                ]
            ).ask()
            pricing = InsuranceDecorator(pricing, insurance_type)
            print(f"  + Insurance ({insurance_type}): R${29.90 if insurance_type == 'basic' else 79.90:.2f}")

        # Desconto de fidelidade
        if self.user.loyalty_points.points >= 100:
            wants_discount = questionary.confirm(
                f"Use loyalty points for discount? (you have: {self.user.loyalty_points.points} points)"
            ).ask()

            if wants_discount:
                discount_options = []
                
                if self.user.loyalty_points.points >= 100:
                    discount_options.append(questionary.Choice("10% discount (100 points)", (10, 100)))
                if self.user.loyalty_points.points >= 200:
                    discount_options.append(questionary.Choice("15% discount (200 points)", (15, 200)))
                if self.user.loyalty_points.points >= 300:
                    discount_options.append(questionary.Choice("25% discount (300 points)", (25, 300)))

                if discount_options:
                    selected = questionary.select(
                        "Choose discount:",
                        choices=discount_options
                    ).ask()

                    discount_pct, points_cost = selected
                    pricing = LoyaltyDiscountDecorator(pricing, discount_pct)
                    self.user.spend_loyalty_points(points_cost)
                    print(f"  - Loyalty Discount ({discount_pct}%)")

        # Mostrar resumo
        final_price = pricing.get_price()
        self._print_summary(pricing, final_price)

        confirm = questionary.confirm("Confirm booking?").ask()
        if not confirm:
            print("❌ Booking cancelled")
            return self.parent

        # Criar booking
        booking = Booking(
            flight_id=flight.id,
            owner_id=self.user.id,
            passenger_name=passenger_name,
            passenger_cpf=passenger_cpf,
            price=final_price,
        )

        # Selecionar assento se escolheu essa opção
        if "seat" in extras:
            select_seat_action(booking)

        print(f"\n✅ Flight booked! Booking ID: {booking.id}")

        # ============================================
        # 🔌 ADAPTER PATTERN - Processar pagamento
        # ============================================
        process_payment = questionary.confirm(
            "Process payment now?"
        ).ask()

        if process_payment:
            payment_success = self._process_payment(booking)
            
            if payment_success:
                # ============================================
                # 🌳 COMPOSITE PATTERN - Enviar notificações
                # ============================================
                self._send_notifications(booking, flight)

        return self.parent

    def _print_summary(self, pricing, final_price):
        """Mostra resumo do pacote"""
        table = Table(title="📋 Booking Summary")
        table.add_column("Item", style="cyan")
        table.add_column("Included", style="white")

        for feature in pricing.get_features():
            table.add_row("✓", feature)

        table.add_row("", "")
        table.add_row("TOTAL", f"R${final_price:.2f}", style="bold green")

        console.print(table)

    def _process_payment(self, booking: Booking) -> bool:
        """Processa pagamento usando ADAPTER PATTERN"""
        print("\n💳 Payment Processing")
        print("-" * 50)

        payment_method = questionary.select(
            "Choose payment method:",
            choices=[
                questionary.Choice("💰 PIX", "pix"),
                questionary.Choice("💳 Credit Card", "credit_card"),
                questionary.Choice("📄 Bank Slip (Boleto)", "boleto"),
            ]
        ).ask()

        # Coletar dados de pagamento
        customer_data = {}

        if payment_method == "pix":
            pix_key = questionary.text("PIX Key (email, phone, CPF):").ask()
            if not pix_key:
                return False
            customer_data = {
                "pix_key": pix_key,
                "name": booking.passenger_name
            }

        elif payment_method == "credit_card":
            card_number = questionary.text(
                "Card number (16 digits):",
                validate=lambda x: len(x) == 16 and x.isdigit()
            ).ask()
            cvv = questionary.text(
                "CVV (3 digits):",
                validate=lambda x: len(x) == 3 and x.isdigit()
            ).ask()
            expiry = questionary.text(
                "Expiry (MM/YY):",
                validate=lambda x: len(x) == 5 and x[2] == '/'
            ).ask()

            if not all([card_number, cvv, expiry]):
                return False

            customer_data = {
                "card_number": card_number,
                "cvv": cvv,
                "expiry": expiry,
                "name": booking.passenger_name
            }

        else:  # boleto
            customer_data = {
                "name": booking.passenger_name,
                "cpf": booking.passenger_cpf
            }

        # ADAPTER EM AÇÃO - Interface unificada!
        gateway = PaymentGatewayFactory.create_gateway(payment_method)
        result = gateway.process_payment(booking.price, customer_data)

        if result["success"]:
            print(f"\n✅ {result['message']}")
            print(f"🔖 Transaction ID: {result['transaction_id']}")
            return True
        else:
            print(f"\n❌ Payment failed: {result['message']}")
            return False

    def _send_notifications(self, booking: Booking, flight: Flight):
        """Envia notificações usando COMPOSITE PATTERN"""
        print("\n📧 Notification Preferences")
        print("-" * 50)

        channels = questionary.checkbox(
            "How do you want to receive booking confirmation?",
            choices=[
                questionary.Choice("📧 Email", "email"),
                questionary.Choice("📱 SMS", "sms"),
                questionary.Choice("🔔 Push Notification", "push"),
                questionary.Choice("💬 WhatsApp", "whatsapp"),
            ]
        ).ask()

        if not channels:
            print("No notifications selected")
            return

        # Construir grupo de notificações
        builder = NotificationBuilder().set_name(f"Booking {booking.id} Confirmation")

        if "email" in channels:
            email = questionary.text(
                "Email:",
                default=f"{self.user.username}@example.com"
            ).ask()
            builder.add_email(email)

        if "sms" in channels:
            phone = questionary.text(
                "Phone number:",
                default="+55 82 99999-9999"
            ).ask()
            builder.add_sms(phone)

        if "push" in channels:
            builder.add_push(self.user.id)

        if "whatsapp" in channels:
            phone = questionary.text(
                "WhatsApp number:",
                default="+55 82 99999-9999"
            ).ask()
            builder.add_whatsapp(phone)

        # Criar mensagem
        message = NotificationTemplate.booking_confirmation(
            booking.id,
            f"{flight.From} → {flight.To}"
        )

        # Enviar para todos os canais!
        notifications = builder.build()
        print("\n📤 Sending notifications...")
        notifications.send(message)
        print(f"✅ {notifications.get_recipients_count()} notifications sent successfully!")