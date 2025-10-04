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

### ⚠️ Parcialmente Implementadas
- **Pedidos Especiais**: Interface criada, funcionalidade em desenvolvimento

## Padrões Comportamentais Implementados
- **Template Method**: views/menu.py

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
