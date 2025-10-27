from typing import Callable, Tuple

import questionary
from ycaro_airlines.views import menu_factory, customer_menu
from ycaro_airlines.views.menu import ActionView, MenuView, UIView
from ycaro_airlines.views.customer_menu import CustomerMenu
from ycaro_airlines.models.customer import Customer
from ycaro_airlines.models.user import User


def login_action():
    username = questionary.select(
        "Select a user to login:",
        choices=[v.username for v in Customer.list()],
    ).ask()

    if username is None:
        return

    user = Customer.get_by_username(username)

    if user is None:
        print("Invalid Username!")
        return

    customer_menu(user)


def signup_action():
    username = questionary.text(
        "Username:",
        default="",
        validate=lambda x: (
            True if x not in {v.username for v in Customer.list()} else False
        ),
    ).ask()
    Customer(username=username)
    print("Sign Up Successful!")


def accounts_menu():
    options: list[Tuple[str, Callable]] = [
        ("Login", login_action),
        ("Sign up", signup_action),
    ]

    menu_factory("Accounts Menu", options=options)()


class LoginMenu(MenuView):
    title: str = "Login"

    def operation(self) -> UIView | None:
        choices: list[questionary.Choice] = [
            questionary.Choice(user.username, user) for user in User.list()
        ]

        choices.append(questionary.Choice(title="Go Back", value=self.parent))

        selected_user = questionary.select(self.title, choices=choices).ask()

        if selected_user == self.parent:
            return self.parent

        self.user = selected_user

        user = self.user
        if user is None:
            print("Invalid User")
            return self.parent

        return CustomerMenu(user, parent=self.parent)


class SignupAction(ActionView):
    title: str = "Sign Up"

    def operation(self):
        username = questionary.text(
            "Username:",
            default="",
            validate=lambda x: (
                True if x not in {v.username for v in User.list()} else False
            ),
        ).ask()

        Customer(username=username)

        print("Sign Up Successful!")
        print(User.list())

        return self.parent


class AccountsMenu(MenuView):
    title: str = "Accounts Menu"

    def __init__(self, user: User | None = None, parent: "UIView | None" = None):
        self.children: list[UIView] = [
            LoginMenu(user, self),
            SignupAction(user, self),
        ]
        super().__init__(user=user, children=self.children, parent=parent)
