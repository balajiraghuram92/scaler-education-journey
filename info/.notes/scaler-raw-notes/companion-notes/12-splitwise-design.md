Source: Downloads/machine-coding/lesson_13.txt (Scaler Companion AI-generated class revision notes)

Comprehensive Revision Notes: Design Splitwise
Overview
In this class, we explored designing the backend for the expense-sharing application, Splitwise. The session focused on understanding user requirements, how group expenditures work, and the process of settling debts among users using as few transactions as possible. We explored the mathematical foundation and algorithmic complexity involved in achieving optimal debt settlements.

Understanding Splitwise
Splitwise: An expense management and sharing application that helps groups of people track and settle their shared expenses.
Primary Functions:
Track expenses among friends/family members.
Calculate who owes whom and how much.
Allow users to settle debts efficiently.
Requirements for Splitwise
User and Group Management
User Profile:

Fields: Name, phone number, email, password.
A user can participate in various groups or outside groups for expense sharing.
Groups:

Users can create groups (e.g., "Goa Trip", "Flatmates") for sorting expenses.
Only the group creator can add or remove members.
A group allows users to collectively manage expenses that involve all members.
Expense Management
Expense Entry:
An expense can be logged with a group or between individual users.
Expenses require details like who paid and who should pay, ensuring that the sum of amounts paid equals the sum of amounts owed.
Viewing Balances
Users can view:
Total Owed: Their net balance across all interactions.
History: Specific expenses they have participated in.
Group-specific histories if they are part of a group.
Settle Up
Individual Settle-Up:

Users can request settlement with another user; the application should show a list of transactions needed to settle debts fully.
Group Settle-Up:

Intended to clean up all expenses within a group to bring all participants to net zero within that group context.
Core Algorithm: Settle-Up Using Transactions
Data Structure: Expense Entries
Each expense has:

Paid By: Records who actually paid what amount.
Owed By: Captures each participant's share of the owed amount.
Calculating Net Position
For each user, compute how much extra or less they have paid across all expenses:

Formula: For each expense,
extra_amount += whoPaid[person] - whoHadToPay[person]
The final sum for a person determines if they are owed money (> 0) or owe money (< 0).
Example
Assume expenses:

Expense 1: A paid Rs 1000, A owed Rs 500, B owed Rs 500, etc.
Compute extra_amount for each contributor, ensuring each person's net position in all transactions is accurately captured.
Settle-Up Algorithm: Greedy Approach
Separate debtors and creditors into two groups: those who GET money and those who GIVE.
Use data structures like min-heaps and max-heaps to efficiently match the biggest debtor with the biggest creditor.
Perform transactions to bring either the giver or receiver to a net zero, thereby reducing the problem iteratively.
Greedy Matching:

From GET and GIVE groups, make transactions that settle at least one party fully.
Continuously balance transactions using heaps to pop the highest amounts needing settling.
Complexity
Time Complexity: Optimum solution runs in O(n log n), where each transaction derives from a binary heap operation (log n) over at most n-1 iterations.
Conclusion
The class successfully broke down the practical implementation of a debt-settling algorithm for Splitwise, focusing on efficiency and accuracy. These methods provide a real-world application for algorithmic design, emphasizing the balance between technical correctness and practical usability. Understanding these concepts is vital for crafting software solutions that can handle complex interactions seamlessly.

