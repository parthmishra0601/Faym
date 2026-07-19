# SDE Intern Assignment - Python Implementation

This repository contains a Python implementation of the user payout management system described in the assignment.

## What is included
- Low-level design for payout processing and reconciliation
- Python domain models for sales, payouts, and balances
- A service layer implementing:
  - advance payout processing
  - reconciliation for approved/rejected sales
  - withdrawal restrictions
  - failed payout recovery

## Running tests

```bash
pytest -q
```

## API layer
A lightweight FastAPI app is available in [src/payout_system/api.py](src/payout_system/api.py). Run it with:

```bash
uvicorn src.payout_system.api:app --reload
```

## Design notes
- Each sale is eligible for a single advance payout of 10% of its earnings.
- Reconciliation updates the final payout based on whether the sale is approved or rejected.
- Withdrawals are limited to one every 24 hours per user.
- Failed payouts return the amount to the withdrawable balance.
