"""
test_structural_patterns.py

Demonstra os 3 padrões estruturais implementados:
1. DECORATOR - Sistema de Pricing Dinâmico
2. ADAPTER - Sistemas de Pagamento
3. COMPOSITE - Sistema de Notificações
"""

from ycaro_airlines.models import Flight, Customer, Booking


def test_decorator_pattern():
    """Testa o Decorator Pattern com pricing"""
    print("=" * 60)
    print("1. DECORATOR PATTERN - Sistema de Pricing Dinâmico")
    print("=" * 60)
    
    from ycaro_airlines.decorators import (
        BasicFlightPricing,
        SeatSelectionDecorator,
        BaggageDecorator,
        PriorityBoardingDecorator,
        InsuranceDecorator,
        LoyaltyDiscountDecorator
    )
    
    # Criar voo
    Flight.mock_flight()
    flight = list(Flight.flights.values())[0]
    
    print(f"\n✈️  Voo: {flight.From} → {flight.To}")
    print(f"💰 Preço base: R${flight.price:.2f}\n")
    
    # Cenário 1: Passagem básica
    print("📦 Cenário 1: Passagem Básica")
    basic = BasicFlightPricing(flight)
    print(f"   {basic.get_description()}")
    print(f"   Preço: R${basic.get_price():.2f}")
    print(f"   Features: {', '.join(basic.get_features())}\n")
    
    # Cenário 2: Passagem + Extras
    print("📦 Cenário 2: Passagem com Extras")
    with_extras = InsuranceDecorator(
        PriorityBoardingDecorator(
            BaggageDecorator(
                SeatSelectionDecorator(basic),
                num_bags=2
            )
        ),
        insurance_type="premium"
    )
    print(f"   Preço: R${with_extras.get_price():.2f}")
    print(f"   Features:")
    for feature in with_extras.get_features():
        print(f"      • {feature}")
    
    # Cenário 3: Com desconto de fidelidade
    print("\n📦 Cenário 3: Com Desconto de Fidelidade (15%)")
    with_discount = LoyaltyDiscountDecorator(with_extras, discount_percent=15)
    print(f"   Preço original: R${with_extras.get_price():.2f}")
    print(f"   Preço com desconto: R${with_discount.get_price():.2f}")
    print(f"   Economia: R${with_extras.get_price() - with_discount.get_price():.2f}\n")


def test_adapter_pattern():
    """Testa o Adapter Pattern com pagamentos"""
    print("=" * 60)
    print("2. ADAPTER PATTERN - Sistemas de Pagamento")
    print("=" * 60)
    
    from ycaro_airlines.adapters.payment_adapters import (
        PaymentGatewayFactory,
        PixAdapter,
        CreditCardAdapter,
        BoletoAdapter
    )
    
    amount = 450.00
    
    # Teste PIX
    print("\n💰 Teste 1: Pagamento via PIX")
    pix_gateway = PaymentGatewayFactory.create_gateway("pix")
    pix_result = pix_gateway.process_payment(amount, {
        "pix_key": "joao@example.com",
        "name": "João Silva"
    })
    print(f"   Status: {'✅ Aprovado' if pix_result['success'] else '❌ Rejeitado'}")
    print(f"   ID: {pix_result['transaction_id']}")
    print(f"   Mensagem: {pix_result['message']}\n")
    
    # Teste Cartão
    print("💳 Teste 2: Pagamento via Cartão de Crédito")
    card_gateway = PaymentGatewayFactory.create_gateway("credit_card")
    card_result = card_gateway.process_payment(amount, {
        "card_number": "1234567890123456",
        "cvv": "123",
        "name": "JOAO SILVA",
        "expiry": "12/25"
    })
    print(f"   Status: {'✅ Aprovado' if card_result['success'] else '❌ Rejeitado'}")
    print(f"   ID: {card_result['transaction_id']}")
    print(f"   Mensagem: {card_result['message']}\n")
    
    # Teste Boleto
    print("📄 Teste 3: Geração de Boleto")
    boleto_gateway = PaymentGatewayFactory.create_gateway("boleto")
    boleto_result = boleto_gateway.process_payment(amount, {
        "name": "João Silva",
        "cpf": "123.456.789-12"
    })
    print(f"   Status: {'✅ Gerado' if boleto_result['success'] else '❌ Erro'}")
    print(f"   Código de Barras: {boleto_result['transaction_id']}")
    print(f"   Mensagem: {boleto_result['message']}\n")
    
    # Demonstrar interface unificada
    print("🔄 Demonstração: Interface Unificada")
    print("   Todos os gateways implementam os mesmos métodos:")
    print("   • process_payment()")
    print("   • refund()")
    print("   • get_transaction_status()")
    print("   Isso permite trocar o gateway sem mudar o código cliente!\n")


def test_composite_pattern():
    """Testa o Composite Pattern com notificações"""
    print("=" * 60)
    print("3. COMPOSITE PATTERN - Sistema de Notificações")
    print("=" * 60)
    
    from ycaro_airlines.composites.notification_system import (
        NotificationBuilder,
        NotificationGroup,
        NotificationTemplate,
        EmailNotification,
        SMSNotification,
        PushNotification
    )
    
    # Cenário 1: Notificação individual
    print("\n📧 Cenário 1: Notificação Individual (Leaf)")
    single = EmailNotification("joao@example.com")
    message = NotificationTemplate.booking_confirmation(
        booking_id=123,
        flight_info="Maceió → Recife"
    )
    single.send(message)
    print(f"   Destinatários: {single.get_recipients_count()}\n")
    
    # Cenário 2: Grupo simples
    print("📱 Cenário 2: Grupo de Notificações (Composite)")
    group = NotificationBuilder() \
        .set_name("Confirmação de Reserva") \
        .add_email("joao@example.com") \
        .add_sms("+55 82 99999-9999") \
        .add_push(1) \
        .build()
    
    group.send(message)
    print(f"   Destinatários: {group.get_recipients_count()}\n")
    
    # Cenário 3: Grupos aninhados (árvore)
    print("🌳 Cenário 3: Grupos Aninhados (Árvore de Composite)")
    
    # Criar grupo principal
    main_group = NotificationGroup("Notificação de Atraso - Voo YC-123")
    
    # Subgrupo 1: Passageiro 1
    passenger1 = NotificationGroup("João Silva")
    passenger1.add(EmailNotification("joao@example.com"))
    passenger1.add(SMSNotification("+55 82 91111-1111"))
    passenger1.add(PushNotification(1))
    
    # Subgrupo 2: Passageiro 2
    passenger2 = NotificationGroup("Maria Santos")
    passenger2.add(EmailNotification("maria@example.com"))
    passenger2.add(SMSNotification("+55 82 92222-2222"))
    
    # Subgrupo 3: Passageiro 3
    passenger3 = NotificationGroup("Pedro Costa")
    passenger3.add(EmailNotification("pedro@example.com"))
    passenger3.add(PushNotification(3))
    
    # Adicionar subgrupos ao grupo principal
    main_group.add(passenger1)
    main_group.add(passenger2)
    main_group.add(passenger3)
    
    # Enviar para todos de uma vez
    delay_message = NotificationTemplate.flight_delay(
        flight_info="Maceió → Recife",
        new_time="16:30 (atraso de 2h)",
        reason="Condições meteorológicas adversas"
    )
    
    main_group.send(delay_message)
    
    print(f"\n   📊 Estatísticas:")
    print(f"      Passageiros: 3")
    print(f"      Total de notificações: {main_group.get_recipients_count()}")
    print(f"      Estrutura: 1 grupo principal → 3 subgrupos → {main_group.get_recipients_count()} notificações leaf\n")


def test_integration():
    """Testa os 3 padrões trabalhando juntos"""
    print("=" * 60)
    print("4. INTEGRAÇÃO - Os 3 Padrões Juntos")
    print("=" * 60)
    
    print("\n🎯 Simulação: Reserva Completa de Voo\n")
    
    # Criar usuário e voo
    user = Customer(username="teste_patterns")
    user.gain_loyalty_points(250)
    
    Flight.mock_flight()
    flight = list(Flight.flights.values())[0]
    
    print(f"👤 Cliente: {user.username} ({user.loyalty_points.points} pontos)")
    print(f"✈️  Voo: {flight.From} → {flight.To}\n")
    
    # PASSO 1: DECORATOR - Montar pacote
    print("📦 PASSO 1: Montar Pacote (DECORATOR)")
    from ycaro_airlines.decorators import (
        BasicFlightPricing,
        SeatSelectionDecorator,
        BaggageDecorator,
        LoyaltyDiscountDecorator
    )
    
    pricing = BasicFlightPricing(flight)
    pricing = SeatSelectionDecorator(pricing)
    pricing = BaggageDecorator(pricing, num_bags=1)
    pricing = LoyaltyDiscountDecorator(pricing, discount_percent=10)
    
    print(f"   Preço final: R${pricing.get_price():.2f}")
    print(f"   Itens: {', '.join(pricing.get_features())}\n")
    
    # PASSO 2: Criar reserva
    booking = Booking(
        flight_id=flight.id,
        owner_id=user.id,
        passenger_name="João Silva",
        passenger_cpf="123.456.789-12",
        price=pricing.get_price()
    )
    print(f"✅ Reserva criada: Booking #{booking.id}\n")
    
    # PASSO 3: ADAPTER - Processar pagamento
    print("💳 PASSO 2: Processar Pagamento (ADAPTER)")
    from ycaro_airlines.adapters.payment_adapters import PaymentGatewayFactory
    
    gateway = PaymentGatewayFactory.create_gateway("pix")
    payment_result = gateway.process_payment(booking.price, {
        "pix_key": "joao@example.com",
        "name": "João Silva"
    })
    
    print(f"   Status: {'✅ Aprovado' if payment_result['success'] else '❌ Rejeitado'}")
    print(f"   Transação: {payment_result['transaction_id']}\n")
    
    # PASSO 4: COMPOSITE - Enviar notificações
    print("📧 PASSO 3: Enviar Notificações (COMPOSITE)")
    from ycaro_airlines.composites.notification_system import (
        NotificationBuilder,
        NotificationTemplate
    )
    
    notifications = NotificationBuilder() \
        .set_name(f"Confirmação - Booking {booking.id}") \
        .add_email("joao@example.com") \
        .add_sms("+55 82 99999-9999") \
        .add_push(user.id) \
        .build()
    
    message = NotificationTemplate.booking_confirmation(
        booking.id,
        f"{flight.From} → {flight.To}"
    )
    
    notifications.send(message)
    print(f"   ✅ {notifications.get_recipients_count()} notificações enviadas\n")
    
    print("🎉 Processo completo! Os 3 padrões trabalharam juntos:")
    print("   1. DECORATOR criou o pacote customizado")
    print("   2. ADAPTER processou o pagamento")
    print("   3. COMPOSITE enviou as notificações\n")


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("TESTES DOS PADRÕES ESTRUTURAIS")
    print("=" * 60 + "\n")
    
    # Criar alguns voos de teste
    for _ in range(5):
        Flight.mock_flight()
    
    # Executar testes
    test_decorator_pattern()
    print("\n")
    
    test_adapter_pattern()
    print("\n")
    
    test_composite_pattern()
    print("\n")
    
    test_integration()
    
    print("=" * 60)
    print("TODOS OS TESTES CONCLUÍDOS! ✅")
    print("=" * 60)


if __name__ == "__main__":
    main()