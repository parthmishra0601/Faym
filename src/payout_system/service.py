from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from .models import Payout, Sale, SaleStatus, UserBalance


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PayoutService:
    def __init__(self) -> None:
        self.sales: Dict[str, Sale] = {}
        self.payouts: Dict[str, Payout] = {}
        self.balances: Dict[str, UserBalance] = {}

    def create_sale(self, sale: Sale) -> Sale:
        self.sales[sale.id] = sale
        self.balances.setdefault(sale.user_id, UserBalance(user_id=sale.user_id))
        return sale

    def process_advance_payout(self, sale_id: str) -> Optional[Payout]:
        sale = self.sales.get(sale_id)
        if not sale:
            raise KeyError(f"Sale {sale_id} not found")
        if sale.status != SaleStatus.PENDING:
            return None
        if sale.advance_paid > 0:
            return None

        advance_amount = int(sale.earning * 0.10)
        if advance_amount <= 0:
            return None

        payout = Payout(
            id=f"payout_{sale.id}_advance",
            user_id=sale.user_id,
            amount=advance_amount,
            status="completed",
        )
        sale.advance_paid = advance_amount
        sale.advance_transferred_at = _now()
        self.payouts[payout.id] = payout
        self._credit_balance(sale.user_id, advance_amount)
        return payout

    def reconcile_sale(self, sale_id: str, new_status: SaleStatus) -> Sale:
        sale = self.sales.get(sale_id)
        if not sale:
            raise KeyError(f"Sale {sale_id} not found")
        if sale.status != SaleStatus.PENDING:
            raise ValueError("Only pending sales can be reconciled")
        if new_status not in {SaleStatus.APPROVED, SaleStatus.REJECTED}:
            raise ValueError("Only approved or rejected statuses are allowed")

        sale.status = new_status
        sale.reconciled_at = _now()

        if new_status == SaleStatus.APPROVED:
            final_amount = sale.earning - sale.advance_paid
            if final_amount > 0:
                self._credit_balance(sale.user_id, final_amount)
        else:
            adjustment = -sale.advance_paid
            self._credit_balance(sale.user_id, adjustment)

        return sale

    def withdraw(self, user_id: str, amount: int) -> Payout:
        balance = self.balances.setdefault(user_id, UserBalance(user_id=user_id))
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if balance.withdrawable_balance < amount:
            raise ValueError("Insufficient withdrawable balance")
        if balance.last_withdrawal_at and _now() - balance.last_withdrawal_at < timedelta(hours=24):
            raise ValueError("Only one withdrawal every 24 hours is allowed")

        payout = Payout(id=f"payout_{len(self.payouts) + 1}", user_id=user_id, amount=amount, status="completed")
        balance.withdrawable_balance -= amount
        balance.last_withdrawal_at = _now()
        payout.released_at = _now()
        self.payouts[payout.id] = payout
        return payout

    def recover_failed_payout(self, payout_id: str) -> Payout:
        payout = self.payouts.get(payout_id)
        if not payout:
            raise KeyError(f"Payout {payout_id} not found")
        if payout.status != "failed":
            raise ValueError("Only failed payouts can be recovered")

        self._credit_balance(payout.user_id, payout.amount)
        payout.status = "recovered"
        payout.released_at = _now()
        return payout

    def mark_payout_failed(self, payout_id: str, reason: str) -> Payout:
        payout = self.payouts.get(payout_id)
        if not payout:
            raise KeyError(f"Payout {payout_id} not found")
        payout.status = "failed"
        payout.failure_reason = reason
        self._credit_balance(payout.user_id, payout.amount)
        return payout

    def get_balance(self, user_id: str) -> UserBalance:
        return self.balances.setdefault(user_id, UserBalance(user_id=user_id))

    def get_dashboard_summary(self) -> dict:
        status_counts = {status.value: 0 for status in SaleStatus}
        total_earnings = 0

        for sale in self.sales.values():
            status_counts[sale.status.value] += 1
            total_earnings += sale.earning

        return {
            "total_sales": len(self.sales),
            "pending_sales": status_counts[SaleStatus.PENDING.value],
            "approved_sales": status_counts[SaleStatus.APPROVED.value],
            "rejected_sales": status_counts[SaleStatus.REJECTED.value],
            "total_earnings": total_earnings,
        }

    def get_export_snapshot(self) -> dict:
        return {
            "summary": self.get_dashboard_summary(),
            "sales": [
                {
                    "id": sale.id,
                    "user_id": sale.user_id,
                    "brand": sale.brand,
                    "status": sale.status.value,
                    "earning": sale.earning,
                    "advance_paid": sale.advance_paid,
                }
                for sale in self.sales.values()
            ],
            "payouts": [
                {
                    "id": payout.id,
                    "user_id": payout.user_id,
                    "amount": payout.amount,
                    "status": payout.status,
                }
                for payout in self.payouts.values()
            ],
            "balances": {
                user_id: {
                    "withdrawable_balance": balance.withdrawable_balance,
                    "last_withdrawal_at": balance.last_withdrawal_at.isoformat() if balance.last_withdrawal_at else None,
                }
                for user_id, balance in self.balances.items()
            },
        }

    def _credit_balance(self, user_id: str, amount: int) -> None:
        balance = self.balances.setdefault(user_id, UserBalance(user_id=user_id))
        balance.withdrawable_balance += amount
