from app.core.database import initialize_database


COMPANY_NAME = "AI Venture Factory"


def start_company():
    initialize_database()

    print("=" * 60)
    print(f"{COMPANY_NAME} — COMPANY CORE")
    print("=" * 60)
    print("Company database initialized.")
    print("Company status: ONLINE")
    print("=" * 60)