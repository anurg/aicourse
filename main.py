class InsufficientBalanceError(Exception):
    pass

def withdraw(balance, amount):
    if amount >balance:
        # raise ValueError("Insufficient Balance")
        raise InsufficientBalanceError("Amount cannot be more than Balance")
    return balance -amount

withdraw(1000,1500)
