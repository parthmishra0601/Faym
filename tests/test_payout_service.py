import pytest

from src.payout_system.models import Sale, SaleStatus
from src.payout_system.service import PayoutService


def test_advance_payout_is_processed_once_and_balance_updates():
    service = PayoutService()
    sale = Sale(id="s1", user_id="john", brand="brand_1", status=SaleStatus.PENDING, earning=40)
    service.create_sale(sale)

    advance = service.process_advance_payout("s1")
    assert advance is not None
    assert advance.amount == 4
    assert sale.advance_paid == 4

    second_attempt = service.process_advance_payout("s1")
    assert second_attempt is None
    assert service.get_balance("john").withdrawable_balance == 4


def test_reconciliation_approved_sale_sets_final_payout():
    service = PayoutService()
    sale = Sale(id="s2", user_id="john", brand="brand_1", status=SaleStatus.PENDING, earning=30)
    service.create_sale(sale)
    service.process_advance_payout("s2")

    service.reconcile_sale("s2", SaleStatus.APPROVED)
    assert service.get_balance("john").withdrawable_balance == 30


def test_reconciliation_rejected_sale_adjusts_advance_paid():
    service = PayoutService()
    sale = Sale(id="s3", user_id="john", brand="brand_1", status=SaleStatus.PENDING, earning=50)
    service.create_sale(sale)
    service.process_advance_payout("s3")

    service.reconcile_sale("s3", SaleStatus.REJECTED)
    assert service.get_balance("john").withdrawable_balance == 0


def test_withdrawal_rate_limit_and_failed_recovery():
    service = PayoutService()
    sale = Sale(id="s4", user_id="john", brand="brand_1", status=SaleStatus.PENDING, earning=100)
    service.create_sale(sale)
    service.process_advance_payout("s4")
    service.reconcile_sale("s4", SaleStatus.APPROVED)

    payout = service.withdraw("john", 40)
    assert payout.amount == 40

    with pytest.raises(ValueError):
        service.withdraw("john", 10)

    failed = service.mark_payout_failed(payout.id, "bank_issue")
    assert failed.status == "failed"
    assert service.get_balance("john").withdrawable_balance == 100


def test_dashboard_summary_reflects_sales_state():
    service = PayoutService()
    service.create_sale(Sale(id="s5", user_id="john", brand="brand_1", status=SaleStatus.PENDING, earning=40))
    service.create_sale(Sale(id="s6", user_id="jane", brand="brand_2", status=SaleStatus.APPROVED, earning=70))
    service.create_sale(Sale(id="s7", user_id="doe", brand="brand_3", status=SaleStatus.REJECTED, earning=90))

    summary = service.get_dashboard_summary()

    assert summary["total_sales"] == 3
    assert summary["pending_sales"] == 1
    assert summary["approved_sales"] == 1
    assert summary["rejected_sales"] == 1
    assert summary["total_earnings"] == 200


def test_export_snapshot_contains_summary_and_entity_details():
    service = PayoutService()
    sale = Sale(id="s8", user_id="john", brand="brand_1", status=SaleStatus.PENDING, earning=40)
    service.create_sale(sale)
    service.process_advance_payout("s8")
    service.reconcile_sale("s8", SaleStatus.APPROVED)

    snapshot = service.get_export_snapshot()

    assert snapshot["summary"]["total_sales"] == 1
    assert snapshot["summary"]["approved_sales"] == 1
    assert snapshot["sales"][0]["status"] == "approved"
    assert snapshot["balances"]["john"]["withdrawable_balance"] == 40
