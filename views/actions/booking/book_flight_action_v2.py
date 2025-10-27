"""
ycaro_airlines/views/actions/booking/book_flight_action_v2.py

VERSÃO MELHORADA usando Decorator Pattern
"""
import re
import questionary
from rich.table import Table
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models import Flight, Booking, Customer
from ycaro_airlines.views import console
from ycaro_airlines.models.flight import SeatStatus
from ycaro_airlines.decorators import (
    BasicFlightPricing,
    LoyaltyDiscountDecorator,
    SeatSelectionDecorator,
    BaggageDecorator,
    PriorityBoardingDecorator,
    InsuranceDecorator
)


class BookFlightActionV2(ActionView):
    title: str = "Book Flight (Enhanced)"

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

        # Confirmar interesse
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

        # AQUI COMEÇA O DECORATOR PATTERN!
        # Criar pricing base
        pricing = BasicFlightPricing(flight)
        
        print(f"\n💰 Preço base: R${pricing.get_price():.2f}\n")

        # ===== EXTRAS OPCIONAIS =====
        extras_choices = [
            ("Seleção de assento (+R$40.00)", "seat"),
            ("Bagagem extra (+R$149.99/un)", "baggage"),
            ("Embarque prioritário (+R$59.90)", "priority"),
            ("Seguro viagem", "insurance"),
        ]

        selected_extras = questionary.checkbox(
            "Selecione extras desejados:",
            choices=[questionary.Choice(label, value) for label, value in extras_choices]
        ).ask()

        # Aplicar decorators baseado nas escolhas
        if "seat" in selected_extras:
            pricing = SeatSelectionDecorator(pricing)
        
        if "baggage" in selected_extras:
            num_bags = int(questionary.text(
                "Quantas bagagens extras?",
                default="1",
                validate=lambda x: x.isdigit() and int(x) > 0
            ).ask())
            pricing = BaggageDecorator(pricing, num_bags)
        
        if "priority" in selected_extras:
            pricing = PriorityBoardingDecorator(pricing)
        
        if "insurance" in selected_extras:
            insurance_type = questionary.select(
                "Tipo de seguro:",
                choices=["basic", "premium"]
            ).ask()
            pricing = InsuranceDecorator(pricing, insurance_type)

        # ===== DESCONTO DE FIDELIDADE =====
        if self.user.loyalty_points.points >= 100:
            use_discount = questionary.confirm(
                f"Usar pontos de fidelidade? (você tem {self.user.loyalty_points.points} pontos)"
            ).ask()
            
            if use_discount:
                discount_options = [
                    ("10% de desconto (100 pontos)", 10, 100),
                    ("15% de desconto (200 pontos)", 15, 200),
                    ("25% de desconto (300 pontos)", 25, 300),
                ]
                
                available = [
                    questionary.Choice(f"{label}", (pct, cost))
                    for label, pct, cost in discount_options
                    if cost <= self.user.loyalty_points.points
                ]
                
                if available:
                    selected = questionary.select(
                        "Escolha o desconto:",
                        choices=available
                    ).ask()
                    
                    discount_pct, points_cost = selected
                    pricing = LoyaltyDiscountDecorator(pricing, discount_pct)
                    self.user.spend_loyalty_points(points_cost)

        # ===== RESUMO FINAL =====
        self._print_booking_summary(pricing)
        
        if not questionary.confirm("Confirmar reserva?").ask():
            print("❌ Reserva cancelada")
            return self.parent

        # Criar booking
        final_price = pricing.get_price()
        booking = Booking(
            flight_id=flight.id,
            owner_id=self.user.id,
            passenger_name=passenger_name,
            passenger_cpf=passenger_cpf,
            price=final_price,
        )

        # Selecionar assento se escolheu essa opção
        if "seat" in selected_extras:
            seat_id = self._select_seat(flight)
            if seat_id:
                booking.reserve_seat(seat_id)

        print(f"\n✅ Voo reservado com sucesso! Booking ID: {booking.id}")
        print(f"💰 Valor total: R${final_price:.2f}")
        
        return self.parent

    def _print_booking_summary(self, pricing):
        """Mostra resumo da reserva usando as features do decorator"""
        table = Table(title="📋 Resumo da Reserva")
        table.add_column("Item", style="cyan")
        table.add_column("Descrição", style="white")
        
        for feature in pricing.get_features():
            table.add_row("✓", feature)
        
        table.add_row("", "")  # linha vazia
        table.add_row("TOTAL", f"R${pricing.get_price():.2f}", style="bold green")
        
        console.print(table)

    def _select_seat(self, flight: Flight) -> int | None:
        """Auxiliar para seleção de assento"""
        available_seats = [
            str(k) for k, v in flight.seats.items()
            if v.status is SeatStatus.open
        ]
        
        if not available_seats:
            print("❌ Não há assentos disponíveis")
            return None
        
        seat = questionary.autocomplete(
            "Escolha o assento:",
            choices=available_seats,
            validate=lambda x: x in available_seats
        ).ask()
        
        return int(seat) if seat else None