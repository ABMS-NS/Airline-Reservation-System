from rich.console import Console

from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Tuple
import questionary

from ycaro_airlines.models.user import User


# TODO: implement composite pattern
class UIView(ABC):
    title: str = ""

    def __init_subclass__(cls, title: str = "") -> None:
        return super().__init_subclass__()

    def __init__(self, user: User | None, parent: "UIView | None"):
        self.__parent: UIView | None = parent
        self.__user: User | None = user

    @abstractmethod
    def operation(self) -> "UIView | None":
        pass

    @property
    def parent(self) -> "UIView | None":
        return self.__parent

    @parent.setter
    def parent(self, value: "UIView"):
        self.__parent = value

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, value: User):
        self.__user = value


class MenuView(UIView, ABC):
    def __init__(
        self,
        user: User | None = None,
        parent: "UIView | None" = None,
        children: list[UIView] = [],
    ):
        self.__children = children
        super().__init__(user, parent)

    def operation(self) -> UIView | None:
        choices: list[questionary.Choice] = [
            questionary.Choice(children.title, children) for children in self.children
        ]

        choices.append(questionary.Choice(title="Go Back", value=self.parent))

        selected_child = questionary.select(self.title, choices=choices).ask()

        if selected_child == "Go Back":
            return self.parent

        return selected_child

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, children: list[UIView]):
        self.__children = children

    def add(self, children: Iterable[UIView]):
        for o in children:
            self.children.append(o)
            o.parent = self


class ActionView(UIView, ABC):
    @abstractmethod
    def operation(self) -> UIView | None:
        pass


console = Console()


def menu_factory(title: str, options: list[Tuple[str, Callable]]):
    choices: list[questionary.Choice] = [
        questionary.Choice(c[0], c[1]) for c in options
    ]
    choices.append(questionary.Choice("Go Back", value=""))

    def menu() -> Any:
        while True:
            selection = questionary.select(title, choices=choices).ask()
            match selection:
                case "":
                    break
                case None:
                    break
                case _:
                    selection()

    return menu
