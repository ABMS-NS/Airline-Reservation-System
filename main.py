from ycaro_airlines.views.account_menus import AccountsMenu, accounts_menu
from ycaro_airlines.models import Flight, Customer
from ycaro_airlines.app import App


def main():
    # Criar usuários de teste
    test_user1 = Customer(username="joao")
    test_user1.gain_loyalty_points(300)  # Dar alguns pontos
    
    test_user2 = Customer(username="maria") 
    test_user2.gain_loyalty_points(150)
    
    # Criar voos mock
    for _ in range(15):
        Flight.mock_flight()
        
    # Debug - mostrar usuários criados
    print("=== USUÁRIOS DE TESTE ===")
    for user in Customer.list():
        print(f"Username: {user.username}, Pontos: {user.loyalty_points.points}")
    print("========================")
    
    myapp = App(AccountsMenu())
    myapp.run()


if __name__ == "__main__":
    main()
