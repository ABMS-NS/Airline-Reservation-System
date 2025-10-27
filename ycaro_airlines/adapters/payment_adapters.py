"""
ycaro_airlines/adapters/payment_adapters.py

Adapter Pattern para Integração de Sistemas de Pagamento
Permite usar diferentes gateways com interface unificada
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any
from enum import Enum


class PaymentStatus(Enum):
    """Status de pagamento"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"


# ===== TARGET INTERFACE =====
class PaymentGateway(ABC):
    """Interface unificada para todos os gateways de pagamento"""
    
    @abstractmethod
    def process_payment(self, amount: float, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um pagamento
        
        Returns:
            Dict com: {
                'success': bool,
                'transaction_id': str,
                'message': str,
                'status': PaymentStatus
            }
        """
        pass
    
    @abstractmethod
    def refund(self, transaction_id: str, amount: float) -> bool:
        """Realiza estorno"""
        pass
    
    @abstractmethod
    def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Consulta status da transação"""
        pass


# ===== ADAPTEES (Sistemas Externos com APIs diferentes) =====

class PixPaymentSystem:
    """Sistema PIX (API em português)"""
    
    def __init__(self):
        self.transacoes = {}
    
    def realizar_pagamento_pix(self, valor: float, chave_pix: str, nome: str) -> Dict[str, Any]:
        """API do PIX usa nomes em português"""
        print(f"[PIX] Processando pagamento de R${valor:.2f} para {nome}")
        
        codigo = f"PIX-{int(datetime.now().timestamp())}"
        self.transacoes[codigo] = {
            "valor": valor,
            "chave": chave_pix,
            "status": "aprovado"
        }
        
        return {
            "sucesso": True,
            "codigo_transacao": codigo,
            "mensagem": "Pagamento aprovado via PIX"
        }
    
    def estornar_pix(self, codigo: str, valor: float) -> Dict[str, bool]:
        """Estorna pagamento PIX"""
        print(f"[PIX] Estornando R${valor:.2f} - Transação {codigo}")
        if codigo in self.transacoes:
            self.transacoes[codigo]["status"] = "estornado"
            return {"sucesso": True}
        return {"sucesso": False}
    
    def consultar_status(self, codigo: str) -> str:
        """Retorna: aprovado, pendente, rejeitado, estornado"""
        if codigo in self.transacoes:
            return self.transacoes[codigo]["status"]
        return "nao_encontrado"


class CreditCardProcessor:
    """Sistema de cartão de crédito (API legada em inglês)"""
    
    def __init__(self):
        self.transactions = {}
    
    def charge_card(self, card_number: str, cvv: str, amount: float, 
                    cardholder: str, expiry: str) -> tuple[bool, str]:
        """API antiga retorna tupla (success, transaction_id)"""
        print(f"[CARD] Charging ${amount:.2f} to card ending in {card_number[-4:]}")
        
        # Simula validação
        if len(card_number) == 16 and len(cvv) == 3:
            trans_id = f"CC-{int(datetime.now().timestamp())}"
            self.transactions[trans_id] = {
                "amount": amount,
                "status": "approved",
                "card_last4": card_number[-4:]
            }
            return (True, trans_id)
        
        return (False, "")
    
    def void_transaction(self, trans_id: str) -> bool:
        """Cancela transação"""
        print(f"[CARD] Voiding transaction {trans_id}")
        if trans_id in self.transactions:
            self.transactions[trans_id]["status"] = "voided"
            return True
        return False
    
    def check_status(self, trans_id: str) -> int:
        """Retorna código: 0=pending, 1=approved, 2=rejected, 3=voided"""
        if trans_id not in self.transactions:
            return -1
        
        status_map = {
            "pending": 0,
            "approved": 1,
            "rejected": 2,
            "voided": 3
        }
        return status_map.get(self.transactions[trans_id]["status"], -1)


class BoletoSystem:
    """Sistema de boleto bancário"""
    
    def __init__(self):
        self.boletos = {}
    
    def gerar_boleto(self, valor: float, nome_pagador: str, cpf: str) -> str:
        """Gera boleto e retorna código de barras"""
        print(f"[BOLETO] Gerando boleto de R${valor:.2f} para {nome_pagador}")
        
        codigo_barras = f"BOLETO-{int(datetime.now().timestamp())}"
        self.boletos[codigo_barras] = {
            "valor": valor,
            "pagador": nome_pagador,
            "cpf": cpf,
            "pago": False
        }
        
        return codigo_barras
    
    def verificar_pagamento(self, codigo_barras: str) -> bool:
        """Verifica se boleto foi pago"""
        if codigo_barras in self.boletos:
            return self.boletos[codigo_barras]["pago"]
        return False
    
    def simular_pagamento(self, codigo_barras: str):
        """Simula pagamento do boleto (para testes)"""
        if codigo_barras in self.boletos:
            self.boletos[codigo_barras]["pago"] = True


# ===== ADAPTERS =====

class PixAdapter(PaymentGateway):
    """Adapta o sistema PIX para a interface unificada"""
    
    def __init__(self):
        self.pix_system = PixPaymentSystem()
    
    def process_payment(self, amount: float, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        # Adapta os parâmetros
        chave_pix = customer_data.get("pix_key")
        nome = customer_data.get("name")
        
        # Chama API do PIX
        resultado = self.pix_system.realizar_pagamento_pix(amount, chave_pix, nome)
        
        # Adapta o retorno para o formato esperado
        return {
            "success": resultado["sucesso"],
            "transaction_id": resultado["codigo_transacao"],
            "message": resultado["mensagem"],
            "status": PaymentStatus.APPROVED if resultado["sucesso"] else PaymentStatus.REJECTED
        }
    
    def refund(self, transaction_id: str, amount: float) -> bool:
        resultado = self.pix_system.estornar_pix(transaction_id, amount)
        return resultado["sucesso"]
    
    def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        status = self.pix_system.consultar_status(transaction_id)
        
        # Mapeia status do PIX para enum unificado
        status_map = {
            "aprovado": PaymentStatus.APPROVED,
            "pendente": PaymentStatus.PENDING,
            "rejeitado": PaymentStatus.REJECTED,
            "estornado": PaymentStatus.REFUNDED
        }
        return status_map.get(status, PaymentStatus.REJECTED)


class CreditCardAdapter(PaymentGateway):
    """Adapta o processador de cartão para a interface unificada"""
    
    def __init__(self):
        self.card_processor = CreditCardProcessor()
    
    def process_payment(self, amount: float, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        # Extrai dados do cartão
        card_number = customer_data.get("card_number")
        cvv = customer_data.get("cvv")
        cardholder = customer_data.get("name")
        expiry = customer_data.get("expiry")
        
        # Chama API antiga (retorna tupla)
        success, trans_id = self.card_processor.charge_card(
            card_number, cvv, amount, cardholder, expiry
        )
        
        # Adapta retorno para formato moderno
        return {
            "success": success,
            "transaction_id": trans_id if success else "",
            "message": "Pagamento aprovado" if success else "Pagamento rejeitado",
            "status": PaymentStatus.APPROVED if success else PaymentStatus.REJECTED
        }
    
    def refund(self, transaction_id: str, amount: float) -> bool:
        return self.card_processor.void_transaction(transaction_id)
    
    def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        code = self.card_processor.check_status(transaction_id)
        
        # Mapeia código numérico para enum
        code_map = {
            0: PaymentStatus.PENDING,
            1: PaymentStatus.APPROVED,
            2: PaymentStatus.REJECTED,
            3: PaymentStatus.REFUNDED
        }
        return code_map.get(code, PaymentStatus.REJECTED)


class BoletoAdapter(PaymentGateway):
    """Adapta o sistema de boleto para a interface unificada"""
    
    def __init__(self):
        self.boleto_system = BoletoSystem()
    
    def process_payment(self, amount: float, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        nome = customer_data.get("name")
        cpf = customer_data.get("cpf")
        
        # Gera boleto
        codigo_barras = self.boleto_system.gerar_boleto(amount, nome, cpf)
        
        return {
            "success": True,
            "transaction_id": codigo_barras,
            "message": f"Boleto gerado. Código: {codigo_barras}",
            "status": PaymentStatus.PENDING
        }
    
    def refund(self, transaction_id: str, amount: float) -> bool:
        # Boleto não pode ser estornado após pagamento
        print(f"[BOLETO] Boletos não podem ser estornados automaticamente")
        return False
    
    def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        pago = self.boleto_system.verificar_pagamento(transaction_id)
        return PaymentStatus.APPROVED if pago else PaymentStatus.PENDING


# ===== FACTORY PARA SELECIONAR ADAPTER =====

class PaymentGatewayFactory:
    """Factory para criar o adapter apropriado"""
    
    @staticmethod
    def create_gateway(payment_type: str) -> PaymentGateway:
        gateways = {
            "pix": PixAdapter,
            "credit_card": CreditCardAdapter,
            "boleto": BoletoAdapter
        }
        
        gateway_class = gateways.get(payment_type.lower())
        if not gateway_class:
            raise ValueError(f"Tipo de pagamento desconhecido: {payment_type}")
        
        return gateway_class()