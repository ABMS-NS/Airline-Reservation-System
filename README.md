# Ycaro Airlines - Sistema de Reservas de Voos

Projeto desenvolvido para a disciplina de Projeto de Software do semestre 2025.1

## Descrição

Sistema de reservas de companhia aérea com interface de linha de comando, implementado em Python usando arquitetura MVC e padrões de design como Repository e Composite.

## Funcionalidades Implementadas

### ✅ Completamente Funcionais
- **Busca de Voos**: Filtros por preço, cidade, data de partida/chegada e ID
- **Gerenciamento de Reservas**: Reservar, cancelar e modificar reservas
- **Check-in Online**: Sistema completo de check-in com validação
- **Seleção de Assentos**: Escolha e mudança de assentos disponíveis
- **Informações de Bagagem**: Taxas e políticas de bagagem
- **Reservas Multi-Cidade**: Voos com múltiplas conexões
- **Sistema de Fidelidade**: Ganho e uso de pontos de fidelidade
- **Programa de Fidelidade**: Sistema básico funcional, resgate de prêmios implementado
- **Atendimento ao Cliente**: Estrutura de tickets criada, chat básico

## Padrões Comportamentais Implementados
- **Template Method**: views/menu.py
- **Strategy Method e um pouco de Template**: models/flights.py e strategy/
- **State**: states/ e booking.py

## Padrões Estruturais Implementados

### Decorator Pattern
- **Localização**: `ycaro_airlines/decorators/`
- **Uso**: Sistema de pricing dinâmico com extras opcionais
- **Classes principais**: `BasicFlightPricing`, `SeatSelectionDecorator`, `BaggageDecorator`

### Adapter Pattern
- **Localização**: `ycaro_airlines/adapters/`
- **Uso**: Integração com múltiplos sistemas de pagamento
- **Classes principais**: `PaymentGateway`, `PixAdapter`, `CreditCardAdapter`, `BoletoAdapter`

### Composite Pattern
- **Localização**: `ycaro_airlines/composites/`
- **Uso**: Sistema de notificações hierárquico
- **Classes principais**: `NotificationComponent`, `NotificationGroup`, `NotificationBuilder`

## Arquivos com Tratamento de Erros

### ycaro_airlines/views/booking_menu.py

**Try-Catch Genérico: Captura exceções inesperadas no fluxo principal**

Por quê: Evita crashes do sistema e fornece feedback ao usuário
Exemplo: Erros durante carregamento de bookings ou operações de menu


**Validação de Entrada com sanitize_text():**

Por quê: Previne dados malformados (strings vazias, None, espaços)
Exemplo: Validação de IDs de booking, nomes, emails


**Validação de Estado de Objetos:**

Por quê: Garante que objetos têm dados válidos antes de operações
Exemplo: Verifica se user.id existe e é inteiro válido antes de buscar bookings


**Validação de Permissões:**

Por quê: Segurança - usuários só podem modificar suas próprias reservas
Exemplo: Verifica booking.owner_id == user.id antes de operações


**Validação de Regras de Negócio:**

Por quê: Respeita regras do State Pattern (ex: não pode cancelar após check-in)
Exemplo: Chama booking.can_cancel() antes de permitir cancelamento


**Validação de Formatos com Regex:**

Por quê: Garante dados em formatos corretos (CPF, email, cartão de crédito)
Exemplo: CPF deve seguir padrão \d{3}\.\d{3}\.\d{3}\-\d{2}


**AttributeError Específico:**

Por quê: Detecta corrupção de dados ou problemas de serialização
Exemplo: Captura quando atributos esperados não existem em objetos



### ycaro_airlines/views/actions/booking/book_flight_action.py

**Validação de Tipo de Usuário:**

Por quê: Apenas clientes podem fazer reservas
Exemplo: isinstance(self.user, Customer)


**Validação de Input com Questionary:**

Por quê: Garante que usuário escolhe opções válidas
Exemplo: Validadores customizados em questionary.text(validate=...)


**Try-Catch em Operações de Pagamento:**

Por quê: Falhas de pagamento não devem quebrar o fluxo de reserva
Exemplo: Captura erros do PaymentGateway e informa usuário


**Validação de Disponibilidade:**

Por quê: Previne reserva de assentos já ocupados
Exemplo: Filtra seats por status SeatStatus.open



### ycaro_airlines/models/flight.py 

**ValueError para Validações de Negócio:**

Por quê: Impede criação de voos com dados inválidos
Exemplos:

Capacidade negativa: if capacity < 0: raise ValueError
Data de partida no passado: if departure_date < datetime.today(): raise ValueError
Chegada antes da partida: if arrival_date < departure_date: raise ValueError
Preço negativo: if price < 0: raise ValueError





4. ycaro_airlines/models/customer.py
Tipos de Tratamento:

ValueError em Operações de Pontos:

Por quê: Previne operações inválidas no sistema de fidelidade
Exemplos:

Ganhar pontos negativos: if amount < 0: raise ValueError
Gastar mais pontos que possui: if amount > self.points: raise ValueError


### ycaro_airlines/adapters/payment_adapters.py

**ValueError em Factory:**

Por quê: Garante que apenas métodos de pagamento suportados sejam usados
Exemplo: if not gateway_class: raise ValueError(f"Tipo de pagamento desconhecido")



### ycaro_airlines/models/base_model.py

**Try-Catch em Migração de Dados:**

Por quê: Evita falhas durante migração de repositórios antigos
Exemplo: try: del repo.data[item_id] except Exception: pass



## Requisitos do Sistema

- Python 3.8+
- Bibliotecas listadas em `requirements.txt`

## Instalação e Execução

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd ycaro-airlines
```

### 2. Criar Ambiente Virtual (Recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Executar o Sistema
```bash
python main.py
```

## Como Usar

### Login e Cadastro
- Execute o sistema e escolha "Sign Up" para criar uma conta
- Use "Login" para entrar com usuário existente
- **Usuários de teste disponíveis**: `joao` (300 pontos), `maria` (150 pontos)

### Navegação
- Use as setas ↑↓ para navegar nos menus
- Enter para selecionar
- "Go Back" para voltar ao menu anterior

### Funcionalidades Principais

#### Buscar e Reservar Voos
1. Menu Principal → "Search Flights Menu"
2. "Book Flight" para reserva simples
3. "Book Multiple Flights" para conexões
4. Siga as instruções na tela

#### Gerenciar Reservas
1. Menu Principal → "See Bookings"
2. Digite o ID da reserva para gerenciar
3. Opções: cancelar, mudar assento, fazer check-in

#### Sistema de Fidelidade
1. Menu Principal → "Loyalty Program"
2. "View My Points" - ver pontos atuais
3. "View Available Rewards" - ver prêmios disponíveis
4. "Redeem Points for Rewards" - resgatar prêmios

## Arquitetura do Projeto

### Estrutura de Pastas
```
ycaro-airlines/
├── main.py                    # Ponto de entrada
├── ycaro_airlines/
│   ├── app.py                # Aplicação principal
│   ├── models/               # Modelos de dados
│   │   ├── base_model.py     # Classe base
│   │   ├── user.py           # Usuários
│   │   ├── customer.py       # Clientes
│   │   ├── flight.py         # Voos
│   │   ├── booking.py        # Reservas
│   │   └── loyalty.py        # Sistema de fidelidade
│   └── views/                # Interface do usuário
│       ├── menu.py           # Classes base de menu
│       ├── account_menus.py  # Login/cadastro
│       ├── customer_menu.py  # Menu principal
│       ├── loyalty_menu.py   # Menu de fidelidade
│       └── actions/          # Ações específicas
```

### Padrões de Design Utilizados
- **Repository Pattern**: Gerenciamento de dados em memória
- **Composite Pattern**: Estrutura hierárquica de menus
- **MVC Architecture**: Separação entre modelo, visão e controle

### Tecnologias
- **Pydantic**: Validação e serialização de dados
- **Rich**: Formatação de tabelas e interface
- **Questionary**: Menus interativos no terminal
- **Textual**: Framework de TUI (Text User Interface)

## Sistema de Pontos de Fidelidade

### Como Ganhar Pontos
- **Check-in**: 10% do valor da passagem em pontos
- **Reservas**: Pontos baseados no valor gasto

### Como Usar Pontos
- **Descontos**: 1 ponto = R$ 1,00 de desconto
- **Prêmios**: Resgate no menu de fidelidade

### Prêmios Disponíveis
- Desconto 10% (100 pontos)
- Desconto 25% (250 pontos)  
- Bagagem Grátis (150 pontos)
- Voo Nacional Grátis (500 pontos)

## Dados de Teste

### Usuários Pré-cadastrados
- **joao**: 300 pontos de fidelidade
- **maria**: 150 pontos de fidelidade

### Voos Mock
- 15 voos são criados automaticamente ao iniciar
- Rotas entre: Maceió, Recife, Aracaju, João Pessoa
- Preços entre R$ 100 - R$ 400

## Desenvolvimento

### Adicionando Novas Funcionalidades
1. Criar modelo em `models/`
2. Criar ação em `views/actions/`
3. Integrar ao menu apropriado

### Estrutura de Commits
- `feat:` para novas funcionalidades
- `fix:` para correções de bugs
- `docs:` para documentação
- `refactor:` para refatoração

## Bugs Conhecidos e Correções

### Bugs Corrigidos na Versão Atual
- ✅ Sistema de login funcional
- ✅ Validação de pontos de fidelidade
- ✅ Geração consistente de IDs


## Licença

Projeto acadêmico desenvolvido para fins educacionais.

## Contato

Desenvolvido para a disciplina de Projeto de Software - 2025.1

---

- **Última atualização**: Setembro 2025
- **Feito por**: Alison Bruno Martires Soares
- **Refatorado de**: Ycaro
