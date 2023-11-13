TRANSACTION_FORMAT = '''== Format ==

/add Label, Amount, Payer Name
Debtor Name, [Optional Amount]
Debtor Name, [Optional Amount]'''

EXAMPLES = '''== Examples ==

/add Dinner, 456, John
Andy, 123
Bob, 78

/add Drinks, 654, Bob
Andy
John
Mary'''

COMMANDS = '''- /add to add a transaction to the list.
- /list to view the current pending transactions.
- /detail followed by a number from /list to show details of a transaction.
- /delete followed by a number from /list to remove a transaction.
- /settle to settle up all pending transactions. This will remove all transactions.
- /help to bring up the available instructions and format.'''

ASSUMPTIONS = '''- Amounts support up to 2 decimal digits. Any rounding difference in division will go to the payer.
- Each transaction requires at least 1 debtor. Otherwise what's the point honestly.'''

EXPLAINER = '''How it works:
- If a debtor's amount is specified in a transaction, that share will first be deducted from the amount.
- The remaining amount will be split amongst all debtors that do not have an amount specified.
- The bot will then calculate all relationships between transactions to come up with a final tally.

Tips:
- Make sure the spelling of each name is consitent across transactions. The name is not case sensitive.
{ASSUMPTIONS}'''.format(ASSUMPTIONS=ASSUMPTIONS)

INSTRUCTIONS = '''{COMMANDS}
{TRANSACTION_FORMAT}
{EXAMPLES}
{EXPLAINER}'''.format(COMMANDS=COMMANDS, TRANSACTION_FORMAT=TRANSACTION_FORMAT, EXAMPLES=EXAMPLES, EXPLAINER=EXPLAINER)

INTRO = '''Hey there, here's how you can use me ;)
{INSTRUCTIONS}'''.format(INSTRUCTIONS=INSTRUCTIONS)

ERROR_GENERIC = '''Hey sorry I didn't quite get that. Please see the command list below:
{COMMANDS}'''.format(COMMANDS=COMMANDS)

ERROR_ADD_FORMAT = '''Think you got the format wrong for that one. PLease see the format below:
{TRANSACTION_FORMAT}
{EXAMPLES}'''.format(TRANSACTION_FORMAT=TRANSACTION_FORMAT, EXAMPLES=EXAMPLES)

ERROR_PRECONDITION = '''You're missing out on one of the requirements below:
{ASSUMPTIONS}
'''.format(ASSUMPTIONS=ASSUMPTIONS)
