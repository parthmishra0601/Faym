from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class SaleStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class Sale:
    id: str
    user_id: str
    brand: str
    status: SaleStatus
    earning: int
    advance_paid: int = 0
    advance_transferred_at: Optional[datetime] = None
    reconciled_at: Optional[datetime] = None
    payout_id: Optional[str] = None


@dataclass
class Payout:
    id: str
    user_id: str
    amount: int
    status: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    released_at: Optional[datetime] = None
    failure_reason: Optional[str] = None


@dataclass
class UserBalance:
    user_id: str
    withdrawable_balance: int = 0
    last_withdrawal_at: Optional[datetime] = None
