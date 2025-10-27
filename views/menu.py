from abc import ABC, abstractmethod
from typing import Iterable
import questionary

from ycaro_airlines.models.user import User


# TODO: implement composite pattern
class UIView(ABC):
#Classe abstrata que define o template
    title: str = ""

    def __init_subclass__(cls, title: str = "") -> None:
        return super().__init_subclass__()

    def __init__(self, user: User | None, parent: "UIView | None"):
        self.__parent: UIView | None = parent
        self.__user: User | None = user

    @abstractmethod
    def operation(self) -> "UIView | None": # Método abstrato que subclasses implementam
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


class MenuView(UIView, ABC): #Utiliza o template
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


class ActionView(UIView, ABC): #Outra implementação do template
    @abstractmethod
    def operation(self) -> UIView | None:
        pass
