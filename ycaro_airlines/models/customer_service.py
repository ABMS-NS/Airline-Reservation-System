from typing import Tuple
from ycaro_airlines.models.base_model import BaseModel
from ycaro_airlines.models.user import Roles, User


class CustomerServiceWorker(User):
    def __init__(self, username: str, *args, **kwargs) -> None:
        role = Roles.CustomerService

        super().__init__(username=username, role=role, *args, **kwargs)

    @property
    def issues(self):
        return filter(lambda x: True if x.worker_id == self.id else False, Issue.list())

    def add_issue(self, issue_id: int) -> "Issue | None":
        if (issue := Issue.get(issue_id)) is None:
            return None

        issue.worker_id = self.id

        return issue


class Issue(BaseModel):
    worker_id: int
    customer_id: int | None
    title: int
    description: str
    booking_id: int

    def __init__(
        self,
        title: str,
        description: str,
        customer_id: int,
        booking_id: int,
        *args,
        **kwargs,
    ):
        super().__init__(
            title=title,
            description=description,
            customer_id=customer_id,
            worker_id=None,
            booking_id=booking_id,
            *args,
            **kwargs,
        )

    def __str__(self):
        return f"{self.id} | {self.title} | {self.worker.username}"

    @property
    def worker(self):
        if (worker := CustomerServiceWorker.get(self.worker_id)) is None:
            raise ValueError(f"This issue with id:{self.id} doesn't have a worker")
        return worker


class IssueChat:
    def __init__(self, issue: Issue):
        self.issue = issue
        self.messages: list[Tuple[Roles, str]] = []

    def send_message(self, sender: User, content: str):
        if sender.role is None:
            raise ValueError("Sender must have a role")

        self.messages.append((sender.role, content))
