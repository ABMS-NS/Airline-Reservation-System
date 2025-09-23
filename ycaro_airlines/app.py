from ycaro_airlines.views.menu import UIView

import os
from ycaro_airlines.models.user import User


def clear_screen():
    os.system("clear")


class App:
    def __init__(self, first_screen: UIView) -> None:
        self.current_screen = first_screen
        self.logged_user: User | None = None

    def run(self):
        print("---- Bem vindo a Ycaro Airlines! ----")

        while True:
            # clear_screen()
            if (next_screen := self.current_screen.operation()) is None:
                break

            self.current_screen = next_screen
