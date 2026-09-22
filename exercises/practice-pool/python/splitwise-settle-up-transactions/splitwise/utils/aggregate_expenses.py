from typing import List, Dict

from splitwise.models import Expense, User, ExpenseUser, ExpenseType


def aggregate_expenses(
        expenses: List[Expense]
) -> Dict[User, float]:

    condensed_expenses = {}
    for expense in expenses:
        expense_users = ExpenseUser.objects.filter(
            expense=expense
        )
        for expense_user in expense_users:
            user = expense_user.user
            if user not in condensed_expenses:
                condensed_expenses[user] = 0
            if expense_user.expense_type == ExpenseType.PAID.value:
                condensed_expenses[user] += expense_user.amount
            else:
                condensed_expenses[user] -= expense_user.amount

    return condensed_expenses
