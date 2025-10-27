import questionary
from ycaro_airlines.views.menu import ActionView, UIView
from ycaro_airlines.models.booking import Booking
from ycaro_airlines.models.customer_service import Issue
from ycaro_airlines.models.user import User


def create_special_requests_action(user: User, Booking: Booking):
    selection = questionary.checkbox(
        "What do you wish to request?",
        choices=["accessibility", "dietary restrictions"],
    ).ask()

    confirm = questionary.confirm(
        f"Are you sure you want to submit the following special requests?{selection}"
    )

    pass


# TODO: implement
class CreateIssueAction(ActionView):
    def operation(self) -> UIView | None:
        if self.user is None:
            raise ValueError("Must have a logged user")
        booking = questionary.select(
            "Which booking did you have an issue?",
            choices=[
                questionary.Choice(f"flight_id = {b.flight_id}", b)
                for b in Booking.list_customer_bookings(self.user.id)
            ],
        ).ask()
        issue_title = questionary.text("What is your issue?").ask()
        issue_description = questionary.text("Issue Description").ask()

        Issue(
            title=issue_title,
            description=issue_description,
            customer_id=self.user.id,
            booking_id=booking.id,
        )
        return self.parent


def create_issue_action(user: User):
    booking = questionary.select(
        "Which booking did you have an issue?",
        choices=[
            questionary.Choice(f"flight_id = {b.flight_id}", b)
            for b in Booking.list_customer_bookings(user.id)
        ],
    ).ask()
    issue_title = questionary.text("What is your issue?").ask()
    issue_description = questionary.text("Issue Description").ask()

    Issue(
        title=issue_title,
        description=issue_description,
        customer_id=user.id,
        booking_id=booking.id,
    )


# TODO: implement
def chat_with_customer_service_action(user: User):
    pass
