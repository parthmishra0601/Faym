# Low-Level Design

## Overview
The payout system is modeled around three core entities:
- Sale: tracks sales, status, earnings, and advance payout state.
- Payout: represents an individual payout transfer or withdrawal action.
- UserBalance: stores the user’s withdrawable balance and the last withdrawal timestamp.

## Core workflows
1. Advance payout processing
   - For each pending sale, the system computes 10% of the sale earnings.
   - The advance payout is transferred only once per sale.
2. Reconciliation
   - Pending sales are reconciled to approved or rejected.
   - Approved sales receive the remaining payout after subtracting the advance already paid.
   - Rejected sales create a negative adjustment equal to the earlier advance payout.
3. Withdrawal
   - A user can withdraw only once every 24 hours.
4. Failed payout recovery
   - Failed payouts return the amount to the withdrawable balance so it can be withdrawn again.

## Suggested schema
```sql
CREATE TABLE sales (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  brand TEXT NOT NULL,
  status TEXT NOT NULL,
  earning INTEGER NOT NULL,
  advance_paid INTEGER NOT NULL DEFAULT 0,
  advance_transferred_at TEXT,
  reconciled_at TEXT,
  payout_id TEXT
);

CREATE TABLE payouts (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  amount INTEGER NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  released_at TEXT,
  failure_reason TEXT
);

CREATE TABLE user_balances (
  user_id TEXT PRIMARY KEY,
  withdrawable_balance INTEGER NOT NULL DEFAULT 0,
  last_withdrawal_at TEXT
);
```

## Design choices
- The service layer owns all business rules so the API and tests remain thin.
- Balance updates are applied immediately to keep the system consistent.
- Failure handling is explicit so recovery actions are deterministic.
