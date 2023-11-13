# MadSplit_Bot

Telegram bot to manage transactions amongst various parties. Interact via private message or add it to a group!

Try it out here: [t.me/madsplit_bot](https://t.me/madsplit_bot)

## Commands
- `/add` to add a transaction to the list.
- `/list` to view the current pending transactions.
- `/detail` followed by a number from `/list` to show details of a transaction.
- `/delete` followed by a number from `/list` to remove a transaction.
- `/settle` to settle up all pending transactions. This will remove all transactions.

### Examples
```
/add Dinner, 456, John
Andy, 123
Bob, 78.25

/add Drinks, 654, Bob
Andy, 99.5
John
Mary

/add Brunch, 99, Andy
Bob
John
```

Keying in `/list` should then give you an output like this:

```
1. Dinner, 456.0, John
2. Drinks, 654.0, Bob
3. Brunch, 99.0, Andy
```

You can then reference the list index to delete a transaction or view more details about it.

```
/detail 1

/delete 2
```

Finally once you're happy with the transactions recorded. Use `/settle` to calculate the final tally!
- This operation will also remove all transaction data stored.


## How it works
1. If a debtor's amount is specified in a transaction, that share will first be deducted from the amount.
2. The remaining amount will be split amongst all debtors that do not have an amount specified.
3. The bot will then calculate all relationships between transactions to come up with a final tally.

### Tips
- Make sure the spelling of each name is consistent across transactions. The name is not case sensitive.
- Amounts support up to 2 decimal digits. Any rounding difference in division will go to the payer.
- Each transaction requires at least 1 debtor. Otherwise what's the point honestly.
