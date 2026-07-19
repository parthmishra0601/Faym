from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .models import Sale, SaleStatus
from .service import PayoutService

app = FastAPI(title="User Payout Management System")
service = PayoutService()


@app.get("/")
def root():
    return FileResponse(Path(__file__).with_name("index.html"))


@app.post("/sales", response_model=dict)
def create_sale(sale: Sale):
    created = service.create_sale(sale)
    return {"id": created.id, "user_id": created.user_id, "status": created.status.value}


@app.post("/sales/{sale_id}/advance")
def process_advance_payout(sale_id: str):
    payout = service.process_advance_payout(sale_id)
    if not payout:
        raise HTTPException(status_code=409, detail="Advance payout already processed or sale not pending")
    return {"id": payout.id, "amount": payout.amount, "status": payout.status}


@app.post("/sales/{sale_id}/reconcile")
def reconcile_sale(sale_id: str, new_status: str):
    try:
        status = SaleStatus(new_status.lower())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Status must be approved or rejected") from exc

    try:
        sale = service.reconcile_sale(sale_id, status)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"id": sale.id, "status": sale.status.value}


@app.get("/balances/{user_id}")
def get_balance(user_id: str):
    balance = service.get_balance(user_id)
    return {"user_id": balance.user_id, "withdrawable_balance": balance.withdrawable_balance}


@app.get("/dashboard")
def get_dashboard():
    return service.get_dashboard_summary()


@app.get("/sales-view")
def get_sales_view():
    rows = []
    for sale in service.sales.values():
        rows.append({
            "id": sale.id,
            "user_id": sale.user_id,
            "brand": sale.brand,
            "status": sale.status.value,
            "earning": sale.earning,
            "advance_paid": sale.advance_paid,
        })
    return rows


@app.get("/payouts-view")
def get_payouts_view():
    rows = []
    for payout in service.payouts.values():
        rows.append({
            "id": payout.id,
            "user_id": payout.user_id,
            "amount": payout.amount,
            "status": payout.status,
        })
    return rows


@app.get("/users-view")
def get_users_view():
    rows = []
    for user_id, balance in service.balances.items():
        rows.append({
            "user_id": user_id,
            "withdrawable_balance": balance.withdrawable_balance,
            "last_withdrawal_at": balance.last_withdrawal_at.isoformat() if balance.last_withdrawal_at else None,
        })
    return rows


@app.post("/withdrawals/{user_id}")
def withdraw(user_id: str, amount: int):
    payout = service.withdraw(user_id, amount)
    return {"id": payout.id, "user_id": payout.user_id, "amount": payout.amount, "status": payout.status}


@app.get("/export")
def export_snapshot():
    return service.get_export_snapshot()
