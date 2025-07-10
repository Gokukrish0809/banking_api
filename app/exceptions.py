from decimal import Decimal


class AccountNotFoundError(Exception):
    def __init__(self, account_number: int):
        super().__init__(f"Account {account_number} not found")
        self.account_number = account_number


class InsufficientFundsError(Exception):
    def __init__(self, balance: Decimal, amount: Decimal):
        super().__init__(
            f"Insufficient funds : balance={balance}, attempted transfer = {amount}"
        )
        self.balance = balance
        self.amount = amount


class SameAccountError(Exception):
    def __init__(self, account_number: int):
        super().__init__(f"Can not transfer to the same account : {account_number}")
        self.account_number = account_number
