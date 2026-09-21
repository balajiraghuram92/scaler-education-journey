Source: Downloads/machine-coding/lesson_14.txt (Scaler Companion AI-generated class revision notes)

Comprehensive Revision Notes: Designing and Coding Splitwise
Overview
In this session, we continued our discussion on designing and coding the Splitwise application. We focused on creating a class diagram using the noun-spotting method, addressed complex relationship handling, and formulated a schema design to correspond with our classes. We also touched upon how CLI will handle inputs using the command pattern and set the stage for further coding in the next session.

Class Diagram: The Noun-Spotting Method
Method: Examine each requirement to identify nouns, determining if each should be a class or an attribute.
Key Classes Identified:
User: stores user information like ID, name, phone number, and password.
Expense: records details such as ID, description, the total amount, and participants.
Group: encompasses group details including ID, name, admin, list of users, and expenses.
ExpenseUser: captures the relationship between expenses and users, defining who paid or owed how much.
Handling "Transaction" as a Concept with ExpenseType
Problem: Introducing a Transaction class seemed necessary but posed redundancy and complicated balance calculations.
Solution: Utilize a dummy Expense with an ExpenseType enum to distinguish between real expenses and settlement transactions.
ExpenseType: NORMAL for regular expenses, PAYMENT for settlements.
Schema Design
We designed five main tables avoiding unnecessary enums as lookup tables:
Users: id, name, phone, password, created_at, updated_at.
Groups: id, title, description, admin_id, created_at, updated_at.
Group Members: group_id, user_id for many-to-many user-group relationships.
Expenses: id, description, amount, created_by, group_id, expense_type, created_at, updated_at.
Expense Users: tracks expense-user relationships with fields like expense_id, user_id, amount, and expense_user_type.
Example of Dynamic Expense Adjustment
For instance, if A owes B ₹700:

Original condition: A paid ₹1000, should get back ₹300; B paid nothing, should pay ₹700.
Dummy expense captures this settlement: B now "pays" ₹700 as an expense ("dummy expense"), simulating payment to A.
Command Pattern for CLI Input
Initial Naive Approach: main() handles all commands using a series of if-else conditions.
Problems: Violates Single Responsibility Principle, growing complexity as more commands are added.
Refined Design with Command Pattern:
Command Interface: Created an interface Command with two methods: matches() to check if a command applies, and execute() to perform the command.
CommandExecutor: Manages a list of commands and delegates execution based on matched input.
Active Architecture
Main Flow: main() initializes a CommandExecutor and processes inputs.
Execution: Commands are identified and invoked dynamically, satisfying SRP and allowing easy scalability.
Conclusion
This session focused on structuring our application design and schema creatively and efficiently, ensuring classes and relations are well-defined and implementing command pattern for CLI input handling. Proper structure is pivotal both for comprehension and efficient future coding tasks in Splitwise. In our next class, we will delve deeper into relationships between models, complete the real coding for this foundation, and implement the settle-up feature in its entirety.

