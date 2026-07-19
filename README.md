 Faym - User Payout Management System

Faym is a Python-based payout management dashboard that simulates affiliate sales processing, advance payouts, reconciliation, balance tracking, withdrawals, and exportable system snapshots. It is implemented as a FastAPI web app with a polished dashboard-style interface.

 Overview
This project models a simple payout workflow for users and sales:
- Create sales
- Process advance payouts
- Reconcile sales as approved or rejected
- Track withdrawable balances
- Allow withdrawals with rate limiting
- Recover failed payouts
- Export a snapshot of the current system state

The UI is designed as a professional operations dashboard with interactive controls, live metrics, filters, and quick actions.

 Project Structure
- src/payout_system/models.py - core domain models such as Sale, Payout, and UserBalance
- src/payout_system/service.py - business logic for payout handling and dashboard summaries
- src/payout_system/api.py - FastAPI routes for the web app
- src/payout_system/index.html - dashboard frontend
- tests/test_payout_service.py - automated tests for core service behavior

 Features
- Sales creation and tracking
- Advance payout processing at 10% of earnings
- Reconciliation logic for approved and rejected sales
- Dynamic dashboard summary for totals and statuses
- Balance visibility per user
- Withdrawal flow with 24-hour restriction
- Failed payout recovery
- Exportable snapshot of sales, payouts, and balances
- Interactive dashboard with filters, terminal-style commands, and action feedback

 Installation

 1. Clone the repository
git clone https://github.com/parthmishra0601/Faym.git
cd Faym

 2. Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate

On Windows PowerShell:
python -m venv .venv
.\.venv\Scripts\Activate.ps1

 3. Install dependencies
pip install -r requirements.txt

 Run Locally

 Start the FastAPI app
uvicorn src.payout_system.api:app --reload

Then open:
http://127.0.0.1:8000/

 API Endpoints
- POST /sales - create a sale
- POST /sales/{sale_id}/advance - process an advance payout
- POST /sales/{sale_id}/reconcile - reconcile a pending sale
- GET /balances/{user_id} - fetch user balance
- GET /dashboard - get dashboard summary
- GET /sales-view - get sales rows for the dashboard
- GET /payouts-view - get payout rows
- GET /users-view - get balances view
- POST /withdrawals/{user_id} - withdraw funds
- GET /export - export a snapshot of the current state

 Example Workflow
1. Create a sale through the dashboard or API.
2. Process an advance payout.
3. Reconcile the sale as approved or rejected.
4. Check the user balance.
5. Withdraw funds if available.
6. Export the final snapshot.

 Business Rules
- Each sale can receive only one advance payout.
- Advance payout is 10% of the sale earning.
- Rejected sales adjust the balance by reversing the advance.
- Approved sales credit the remaining amount to the balance.
- Withdrawals are limited to one every 24 hours per user.
- Failed payouts can be recovered and re-credit the balance.

 Tests
Run the test suite with:
pytest -q

 Current test coverage
The project includes tests for:
- advance payout processing
- approval and rejection reconciliation
- withdrawal rules and failed payout recovery
- dashboard summary values
- export snapshot correctness

 Snapshot Examples
The app exposes a structured snapshot that includes:
- summary of total sales, pending, approved, rejected, and earnings
- sales list with status and payout data
- payouts list with amount and status
- balances with withdrawable amounts

Example snapshot structure:
{
  "summary": {
    "total_sales": 1,
    "pending_sales": 0,
    "approved_sales": 1,
    "rejected_sales": 0,
    "total_earnings": 40
  },
  "sales": [
    {
      "id": "sale_001",
      "user_id": "john_doe",
      "brand": "brand_1",
      "status": "approved",
      "earning": 40,
      "advance_paid": 4
    }
  ],
  "payouts": [
    {
      "id": "payout_sale_001_advance",
      "user_id": "john_doe",
      "amount": 4,
      "status": "completed"
    }
  ],
  "balances": {
    "john_doe": {
      "withdrawable_balance": 40,
      "last_withdrawal_at": null
    }
  }
}

 Deployment
The project includes basic deployment configuration for common platforms:
- Procfile
- runtime.txt
- Dockerfile

 Deploy with Docker
docker build -t payout-app .
docker run -p 8000:8000 payout-app

 Deploy with a Python hosting platform
Use the FastAPI app entry point:
uvicorn src.payout_system.api:app --host 0.0.0.0 --port $PORT

 Screenshots from Localhost
You can capture screenshots of the app running at http://127.0.0.1:8000/ to showcase:
- Dashboard overview with live metrics
- Sales and payout management panels
- User balance and withdrawal actions
- Export snapshot results

Suggested screenshot order:
1. Dashboard home view
2. Sales management view
3. Payouts and balances view
4. Export snapshot output
Embedded screenshots :

Dashboard home view:

<img width="945" height="435" alt="image" src="https://github.com/user-attachments/assets/0e40f0e0-a3f6-4265-a01c-80aa786f7729" />




Sales management view:
<img width="947" height="441" alt="image" src="https://github.com/user-attachments/assets/c2025be2-8ca9-4aa6-869b-fd1970d037b8" />


Export snapshot output:
<img width="938" height="387" alt="image" src="https://github.com/user-attachments/assets/3ff9ef1f-ff79-4337-b133-96b64d4a8f4d" />


 Notes
- The current implementation uses in-memory storage, so data resets when the server restarts.
- For persistent production deployment, a database layer would be the next step.
