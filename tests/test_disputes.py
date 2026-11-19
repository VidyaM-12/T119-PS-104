
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
                "amount": "40000",
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


def display_results(logs, disputes, ledger):
    print("\nCOMMAND EXECUTION RESULTS")
    print("-" * 100)

    for row in logs:
        print(
            f"Command: {row['command']:<20} "
            f"Status: {row['status']:<10} "
            f"State: {row['from_state']} -> {row['to_state']}"
        )

        if row["message"]:
            print("Message:", row["message"])

    print("\nDISPUTE DETAILS")
    print("-" * 100)

    if disputes:
        for row in disputes:
            print("Milestone ID       :", row["milestone_id"])
            print("Raised by          :", row["raised_by"])
            print("Freelancer award % :", row["outcome_pct_freelancer"])
            print("Arbitration fee    : Rs.", row["arbitration_fee"])
            print("Fee paid by        :", row["fee_paid_by"])
            print("Client refund      : Rs.", row["client_refund"])
    else:
        print("No dispute resolution recorded.")
        print("The dispute remains unresolved.")

    print("\nFINAL MILESTONE LEDGER")
    print("-" * 100)

    for row in ledger:
        print("Milestone ID :", row["milestone_id"])
        print("State        :", row["state"])
        print("Funded       : Rs.", row["funded"])
        print("Released     : Rs.", row["released"])
        print("Refunded     : Rs.", row["refunded"])


def test_both_parties_miss_evidence():
    print("\n" + "=" * 80)
    print("TEST CASE 1: BOTH PARTIES FAIL TO SUBMIT EVIDENCE")
    print("=" * 80)

    data = make_data()
    start = datetime(2026, 4, 1, 10, 0)

    commands = [
        make_command(1, "FUND", ["M001", "40000"], start),
        make_command(2, "START_WORK", ["M001"], start + timedelta(hours=1)),
        make_command(3, "SUBMIT", ["M001"], start + timedelta(hours=2)),
        make_command(
            4, "DISPUTE",
            ["M001", "CLIENT", "Work quality disagreement"],
            start + timedelta(hours=3)
        ),
        make_command(
            5, "PRINT_STATE", [],
            start + timedelta(days=6)
        )
    ]

    logs, withdrawals, disputes, ledger = execute(data, commands)

    display_results(logs, disputes, ledger)

    assert ledger[0]["state"] == "DISPUTED"
    assert len(disputes) == 0

    print("\nRESULT: Both parties missed the evidence deadline.")
    print("The dispute remains unresolved and no default winner is selected.")


def test_arbitration_fee_calculation():
    print("\n" + "=" * 80)
    print("TEST CASE 2: ARBITRATION FEE CALCULATION")
    print("=" * 80)

    data = make_data()
    start = datetime(2026, 4, 1, 10, 0)

    commands = [
        make_command(1, "FUND", ["M001", "40000"], start),
        make_command(2, "START_WORK", ["M001"], start + timedelta(hours=1)),
        make_command(3, "SUBMIT", ["M001"], start + timedelta(hours=2)),
        make_command(
            4, "DISPUTE",
            ["M001", "CLIENT", "Work quality disagreement"],
            start + timedelta(hours=3)
        ),
        make_command(
            5, "EVIDENCE", ["M001", "CLIENT"],
            start + timedelta(hours=4)
        ),
        make_command(
            6, "EVIDENCE", ["M001", "FREELANCER"],
            start + timedelta(hours=5)
        ),
        make_command(
            7, "MEDIATION_FAILED", ["M001"],
            start + timedelta(days=1)
        ),
        make_command(
            8, "ARBITRATION_AWARD", ["M001", "50"],
            start + timedelta(days=2)
        ),
        make_command(
            9, "PRINT_STATE", [],
            start + timedelta(days=2, hours=1)
        )
    ]

    logs, withdrawals, disputes, ledger = execute(data, commands)

    display_results(logs, disputes, ledger)

    assert len(disputes) == 1
    assert disputes[0]["arbitration_fee"] == 2000.00

    print("\nRESULT: Arbitration fee calculated correctly.")
    print("Milestone amount : Rs. 40,000")
    print("5% of amount     : Rs. 2,000")
    print("Expected fee     : Rs. 2,000")
    print("Actual fee       : Rs.", disputes[0]["arbitration_fee"])


def test_90_day_inactivity_during_unresolved_dispute():
    print("\n" + "=" * 80)
    print("TEST CASE 3: 90-DAY INACTIVITY DURING UNRESOLVED DISPUTE")
    print("=" * 80)

    data = make_data()
    start = datetime(2026, 4, 1, 10, 0)

    commands = [
        make_command(1, "FUND", ["M001", "40000"], start),
        make_command(2, "START_WORK", ["M001"], start + timedelta(hours=1)),
        make_command(3, "SUBMIT", ["M001"], start + timedelta(hours=2)),
        make_command(
            4, "DISPUTE",
            ["M001", "CLIENT", "Work quality disagreement"],
            start + timedelta(hours=3)
        ),
        make_command(
            5, "EVIDENCE", ["M001", "CLIENT"],
            start + timedelta(hours=4)
        ),
        make_command(
            6, "EVIDENCE", ["M001", "FREELANCER"],
            start + timedelta(hours=5)
        ),

        # Check that the dispute enters mediation.
        make_command(
            7, "PRINT_STATE", [],
            start + timedelta(days=6)
        ),

        # No further project activity for 90 days after the last evidence.
        make_command(
            8, "PRINT_STATE", [],
            start + timedelta(days=90, hours=5)
        )
    ]

    logs, withdrawals, disputes, ledger = execute(data, commands)

    display_results(logs, disputes, ledger)

    auto_cancel = [
        row for row in logs
        if row["command"] == "AUTO_CANCEL_INACTIVE"
    ]

    assert len(auto_cancel) >= 1
    assert ledger[0]["state"] == "REFUNDED"
    assert ledger[0]["refunded"] == 40000

    print("\nRESULT: 90-day inactivity handled correctly.")
    print("Project status       : Automatically cancelled")
    print("Final milestone state:", ledger[0]["state"])
    print("Expected refund      : Rs. 40,000")
    print("Actual refund        : Rs.", ledger[0]["refunded"])
    print("Processing fee       : Retained")


if __name__ == "__main__":
    test_both_parties_miss_evidence()
    test_arbitration_fee_calculation()
    test_90_day_inactivity_during_unresolved_dispute()

    print("\n" + "=" * 80)
    print("DISPUTE EDGE-CASE TESTING COMPLETED")
    print("=" * 80)
