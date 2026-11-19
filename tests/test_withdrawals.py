
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Import actual project logic
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import execute


def make_data():
    return {
        "clients": [
            {
                "client_id": "C001",
                "kyc_verified": "false",
                "account_status": "ACTIVE"
            }
        ],
        "freelancers": [
            {
                "freelancer_id": "F001",
                "reliability_level": "A",
                "fy_gross_released_to_date": "0",
                "enhanced_kyc": "false",
                "clean_releases_since_demotion": "0"
            }
        ],
        "projects": [
            {
                "project_id": "P001",
                "client_id": "C001",
                "freelancer_id": "F001",
                "created_date": "2026-04-01"
            }
        ],
        "milestones": [
            {
                "milestone_id": "M001",
                "project_id": "P001",
                "amount": "10000",
                "due_date": "2026-06-30"
            }
        ],
        "relationship_history": []
    }


def make_command(line, command, args, time):
    return {
        "line": line,
        "command": command,
        "args": args,
        "time": time,
        "error": ""
    }


def display_results(logs, withdrawals, ledger):
    print("\nCOMMAND EXECUTION RESULTS")
    print("-" * 90)

    for row in logs:
        print(
            f"Command: {row['command']:<15} "
            f"Status: {row['status']:<10} "
            f"State: {row['from_state']} -> {row['to_state']}"
        )

        if row["message"]:
            print("Message:", row["message"])

    print("\nWITHDRAWAL RESULTS")
    print("-" * 90)

    for row in withdrawals:
        print(f"Freelancer ID : {row['freelancer_id']}")
        print(f"Requested     : Rs. {row['requested']}")
        print(f"Status        : {row['status']}")
        print(f"Withdrawal fee: Rs. {row['fee']}")
        print(f"Amount paid   : Rs. {row['paid']}")
        print(f"Available after: Rs. {row['available_after']}")
        print(f"Message       : {row['message']}")
        print("-" * 90)

    print("\nFINAL MILESTONE LEDGER")

    for row in ledger:
        print("Milestone ID :", row["milestone_id"])
        print("State        :", row["state"])
        print("Released     : Rs.", row["released"])


def test_three_day_withdrawal_hold():
    print("\n" + "=" * 80)
    print("TEST CASE: WITHDRAWAL THREE-DAY HOLD")
    print("=" * 80)

    data = make_data()
    start = datetime(2026, 4, 1, 10, 0)

    commands = [
        make_command(
            1, "FUND", ["M001", "10000"], start
        ),
        make_command(
            2, "START_WORK", ["M001"],
            start + timedelta(hours=1)
        ),
        make_command(
            3, "SUBMIT", ["M001"],
            start + timedelta(hours=2)
        ),
        make_command(
            4, "APPROVE", ["M001"],
            start + timedelta(hours=3)
        ),

        # Attempt withdrawal after 2 days.
        make_command(
            5, "WITHDRAW", ["F001", "1000"],
            start + timedelta(days=2, hours=3)
        ),

        # Attempt withdrawal exactly after 3 days.
        make_command(
            6, "WITHDRAW", ["F001", "1000"],
            start + timedelta(days=3, hours=3)
        )
    ]

    logs, withdrawals, disputes, ledger = execute(data, commands)

    display_results(logs, withdrawals, ledger)

    assert len(withdrawals) == 2

    assert withdrawals[0]["status"] == "REJECTED"
    assert withdrawals[1]["status"] == "ACCEPTED"

    assert withdrawals[1]["fee"] == 25.00
    assert withdrawals[1]["paid"] == 975.00

    print("\nEXPECTED RESULTS")
    print("Day 2 withdrawal : REJECTED")
    print("Day 3 withdrawal : ACCEPTED")
    print("Withdrawal fee   : Rs. 25.00")
    print("Amount paid      : Rs. 975.00")

    print("\nACTUAL RESULTS")
    print("Day 2 withdrawal :", withdrawals[0]["status"])
    print("Day 3 withdrawal :", withdrawals[1]["status"])
    print("Withdrawal fee   : Rs.", withdrawals[1]["fee"])
    print("Amount paid      : Rs.", withdrawals[1]["paid"])

    print("\nRESULT: Three-day withdrawal hold checked successfully.")


if __name__ == "__main__":
    test_three_day_withdrawal_hold()

    print("\n" + "=" * 80)
    print("WITHDRAWAL EDGE-CASE TESTING COMPLETED")
    print("=" * 80)
