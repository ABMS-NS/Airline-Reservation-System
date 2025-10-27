
from ycaro_airlines.adapters import PaymentGatewayFactory

gateway = PaymentGatewayFactory.create_gateway('pix')
result = gateway.process_payment(100.0, {
    'pix_key': 'teste@example.com',
    'name': 'Teste'
})

print('Sucesso:', result['success'])
print('ID:', result['transaction_id'])