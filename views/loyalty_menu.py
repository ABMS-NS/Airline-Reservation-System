from ycaro_airlines.views.menu import MenuView, ActionView, UIView
from ycaro_airlines.views import console
from ycaro_airlines.models.loyalty import LoyaltyProgram
from ycaro_airlines.models.user import User
import questionary
from rich.table import Table

class ViewPointsAction(ActionView):
    title: str = "View My Points"
    
    def operation(self) -> UIView | None:
        if self.user is None:
            return self.parent
        
        table = Table(title="Your Loyalty Points")
        table.add_column("Current Points", justify="center")
        table.add_row(str(self.user.loyalty_points.points))
        console.print(table)
        
        questionary.press_any_key_to_continue().ask()
        return self.parent

class ViewRewardsAction(ActionView):
    title: str = "View Available Rewards"
    
    def operation(self) -> UIView | None:
        if self.user is None:
            return self.parent
            
        available_rewards = LoyaltyProgram.get_available_rewards(self.user.loyalty_points.points)
        
        table = Table(title="Available Rewards")
        table.add_column("Name")
        table.add_column("Description") 
        table.add_column("Cost (Points)")
        table.add_column("Type")
        
        for reward in available_rewards:
            table.add_row(
                reward.name,
                reward.description,
                str(reward.points_cost),
                reward.reward_type.value
            )
        
        console.print(table)
        questionary.press_any_key_to_continue().ask()
        return self.parent

class RedeemPointsAction(ActionView):
    title: str = "Redeem Points for Rewards"
    
    def operation(self) -> UIView | None:
        if self.user is None:
            return self.parent
            
        available_rewards = LoyaltyProgram.get_available_rewards(self.user.loyalty_points.points)
        
        if not available_rewards:
            console.print("No rewards available with your current points!", style="red")
            questionary.press_any_key_to_continue().ask()
            return self.parent
        
        choices = [
            questionary.Choice(f"{r.name} ({r.points_cost} points)", r) 
            for r in available_rewards
        ]
        
        selected_reward = questionary.select(
            "Select reward to redeem:",
            choices=choices
        ).ask()
        
        if selected_reward:
            confirm = questionary.confirm(
                f"Redeem {selected_reward.name} for {selected_reward.points_cost} points?"
            ).ask()
            
            if confirm:
                self.user.spend_loyalty_points(selected_reward.points_cost)
                console.print(f"Reward '{selected_reward.name}' redeemed successfully!", style="green")
        
        return self.parent

class LoyaltyMenu(MenuView):
    title: str = "Loyalty Program"
    
    def __init__(self, user: User, parent: "UIView | None" = None):
        self.children: list[UIView] = [
            ViewPointsAction(user, self),
            ViewRewardsAction(user, self),
            RedeemPointsAction(user, self),
        ]
        super().__init__(user=user, children=self.children, parent=parent)