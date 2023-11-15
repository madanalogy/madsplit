TRANSACTION_FORMAT = '''== Format ==

/add Label, Amount, Payer_Name
Debtor_Name, [Optional_Amount]
Debtor_Name, [Optional_Amount]

Use the command /examples to show examples'''

EXAMPLES = '''== Examples ==

John paid for dinner, everyone pays exactly what they ordered:
/add Dinner, 242, John
Andy, 62
Bob, 78

Bob paid for drinks, evenly split amongst all parties:
/add Drinks, 654, Bob
Andy
John

Andy paid for breakfast, and boy was he not happy about that:
/add Breakfast, 120, Andy
Andy, 10
Mary
Bob
John

Bob was gonna cab back with Mary but John asked if they could add a stop:
/add Cab Ride, 42.50, Bob
John, 7.50
Mary'''

COMMANDS = '''- /add to add a transaction to the list.
- /list to view the current pending transactions.
- /detail followed by a number from /list to show details of a transaction.
- /delete followed by a number from /list to remove a transaction.
- /settle to settle up all pending transactions. This will remove all transactions.
- /help to bring up the available instructions and format.'''

ASSUMPTIONS = '''Tips:
- Make sure the spelling of each name is consistent across transactions. The name is not case sensitive.
- Amounts support up to 2 decimal digits. There might be a small rounding difference in division.
- If the payer is also a debtor in the same transaction, there must be an amount indicated.
- Each transaction requires at least 1 debtor.'''

EXPLAINER = '''How it works:
- If a debtor's amount is specified in a transaction, that share will first be deducted from the amount.
- The remaining amount will be split evenly amongst the payer and all debtors that do not have an amount specified.
- The payer will not be included in the even split only if the payer is also a debtor with an amount specified.
- The /settle command will then calculate all relationships between transactions to come up with a final tally.

{ASSUMPTIONS}'''.format(ASSUMPTIONS=ASSUMPTIONS)

INSTRUCTIONS = '''{COMMANDS}

{TRANSACTION_FORMAT}

{EXPLAINER}'''.format(COMMANDS=COMMANDS, TRANSACTION_FORMAT=TRANSACTION_FORMAT, EXPLAINER=EXPLAINER)

INTRO = '''Hey there, here's how you can use me :)

{INSTRUCTIONS}

Feel free to text me directly for more privacy or add me to a group for more transparency!'''.format(INSTRUCTIONS=INSTRUCTIONS)

ERROR_GENERIC = '''Hey sorry I didn't quite get that. Please see the command list below:

{COMMANDS}'''.format(COMMANDS=COMMANDS)

ERROR_ADD_FORMAT = '''Think you got the format wrong for that one. Please see the format below:

{TRANSACTION_FORMAT}'''.format(TRANSACTION_FORMAT=TRANSACTION_FORMAT)

ERROR_PRECONDITION = '''You're missing out on one of the requirements below:

{ASSUMPTIONS}'''.format(ASSUMPTIONS=ASSUMPTIONS)

ERROR_EMPTY_LIST = "Nothing here yet! Use the /add command to add transactions."

ERROR_SUM_MISMATCH = "The math is not mathing. Please re-check the values you added."
