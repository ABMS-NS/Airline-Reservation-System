"""
ycaro_airlines/views/actions/payment_action.py

Action para processar pagamentos usando Adapter Pattern
"""
import questionary
from rich.table import Table
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.views import console
from ycaro_airlines.models.booking import Booking
from ycaro_airlines.adapters.payment_adapters import (
    PaymentGatewayFactory,
    PaymentStatus
)


class PaymentAction(ActionView):
    title: str = "Process Payment"
    
    def __init__(self, booking: Booking, user, parent):
        self.booking = booking
        super().__init__(user, parent)
    
    def operation(self) -> UIView | None:
        # Mostrar resumo do pagamento
        self._show_payment_summary()
        
        # Escolher método de pagamento
        payment_method = questionary.select(
            "Escolha o método de pagamento:",
            choices=[
                questionary.Choice("💰 PIX", "pix"),
                questionary.Choice("💳 Cartão de Crédito", "credit_card"),
                questionary.Choice("📄 Boleto Bancário", "boleto"),
                questionary.Choice("❌ Cancelar", "cancel")
            ]
        ).ask()
        
        if payment_method == "cancel":
            return self.parent
        
        # Coletar dados conforme método escolhido
        customer_data = self._collect_payment_data(payment_method)
        
        if not customer_data:
            print("❌ Pagamento cancelado")
            return self.parent
        
        # AQUI USA O ADAPTER PATTERN!
        # Criar gateway apropriado usando Factory
        gateway = PaymentGatewayFactory.create_gateway(payment_method)
        
        # Processar pagamento (interface unificada independente do método)
        print("\n⏳ Processando pagamento...")
        result = gateway.process_payment(self.booking.price, customer_data)
        
        # Mostrar resultado
        self._show_payment_result(result, payment_method)
        
        questionary.press_any_key_to_continue().ask()
        return self.parent
    
    def _show_payment_summary(self):
        """Mostra resumo do valor a pagar"""
        table = Table(title="💰 Resumo do Pagamento")
        table.add_column("Item", style="cyan")
        table.add_column("Valor", style="green", justify="right")
        
        table.add_row("Voo", f"{self.booking.flight.From} → {self.booking.flight.To}")
        table.add_row("Passageiro", self.booking.passenger_name)
        table.add_row("", "")  # linha vazia
        table.add_row("TOTAL A PAGAR", f"R$ {self.booking.price:.2f}", style="bold green")
        
        console.print(table)
    
    def _collect_payment_data(self, payment_method: str) -> dict:
        """Coleta dados específicos de cada método de pagamento"""
        
        if payment_method == "pix":
            pix_key = questionary.text(
                "Digite sua chave PIX (CPF, e-mail, telefone ou aleatória):"
            ).ask()
            
            if not pix_key:
                return None
            
            return {
                "pix_key": pix_key,
                "name": self.booking.passenger_name
            }
        
        elif payment_method == "credit_card":
            print("\n💳 Dados do Cartão de Crédito")
            
            card_number = questionary.text(
                "Número do cartão (16 dígitos):",
                validate=lambda x: len(x) == 16 and x.isdigit()
            ).ask()
            
            if not card_number:
                return None
            
            cardholder = questionary.text(
                "Nome no cartão:",
                default=self.booking.passenger_name
            ).ask()
            
            expiry = questionary.text(
                "Validade (MM/AA):",
                validate=lambda x: len(x) == 5 and x[2] == '/'
            ).ask()
            
            cvv = questionary.text(
                "CVV (3 dígitos):",
                validate=lambda x: len(x) == 3 and x.isdigit()
            ).ask()
            
            if not all([cardholder, expiry, cvv]):
                return None
            
            return {
                "card_number": card_number,
                "name": cardholder,
                "expiry": expiry,
                "cvv": cvv
            }
        
        elif payment_method == "boleto":
            cpf = questionary.text(
                "CPF do pagador:",
                default=self.booking.passenger_cpf
            ).ask()
            
            if not cpf:
                return None
            
            return {
                "name": self.booking.passenger_name,
                "cpf": cpf
            }
        
        return None
    
    def _show_payment_result(self, result: dict, payment_method: str):
        """Mostra resultado do pagamento"""
        
        if result["success"]:
            console.print(f"\n✅ {result['message']}", style="bold green")
            console.print(f"🔖 ID da Transação: {result['transaction_id']}", style="cyan")
            
            if payment_method == "boleto":
                console.print("\n📋 Instruções:", style="yellow")
                console.print("1. Salve o código de barras acima")
                console.print("2. Pague em qualquer banco até a data de vencimento")
                console.print("3. O pagamento será confirmado em até 2 dias úteis")
            
            elif payment_method == "pix":
                console.print("\n📋 Pagamento via PIX confirmado instantaneamente!", style="green")
        
        else:
            console.print(f"\n❌ {result['message']}", style="bold red")
            console.print("Tente novamente ou escolha outro método de pagamento.", style="yellow")