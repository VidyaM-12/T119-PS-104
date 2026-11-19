
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Import the actual main program
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import execute


def make_data():
    """Create sample data for milestone edge-case testing."""
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
                "created_date": "2026-01-01"
            }
        ],
        "milestones": [
            {
                "milestone_id": "M001",
                "project_id": "P001",
                "amount": "10000",
                "due_date": "2026-02-28"
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


def display_results(logs, ledger):
    print("\nEXECUTION RESULTS")
    print("-" * 100)

    print(
        f"{'Command':<20}"
        f"{'Status':<12}"
        f"{'From State':<22}"
        f"{'To State':<22}"
        f"{'Message'}"
    )

    print("-" * 100)

    for row in logs:
        print(
            f"{row['command']:<20}"
            f"{row['status']:<12}"
            f"{row['from_state']:<22}"
            f"{row['to_state']:<22}"
            f"{row['message']}"
        )

    print("\nFINAL MILESTONE STATE")
    print("-" * 50)

    for row in ledger:
        print(f"Milestone ID : {row['milestone_id']}")
        print(f"Final State  : {row['state']}")
        print(f"Funded       : Rs. {row['funded']}")
        print(f"Released     : Rs. {row['released']}")
        print(f"Refunded     : Rs. {row['refunded']}")

    print("-" * 50)


def test_auto_approval_revision_collision():
    print("\n" + "=" * 75)
    print("TEST CASE 1: AUTO-APPROVAL AND REVISION DEADLINE COLLISION")
    print("=" * 75)

    start = datetime(2026, 1, 1, 10, 0, 0)

    commands = [
        make_command(1, "FUND", ["M001", "10000"], start),
        make_command(2, "START_WORK", ["M001"], start + timedelta(hours=1)),
        make_command(3, "SUBMIT", ["M001"], start + timedelta(hours=2)),

        # Revision request arrives exactly after the 14-day deadline
        make_command(
            4,
            "REQUEST_REVISION",
            ["M001", "Please make corrections"],
            start + timedelta(days=14, hours=2)
        )
    ]

    logs, withdrawals, disputes, ledger = execute(make_data(), commands)

    display_results(logs, ledger)

    assert ledger[0]["state"] == "RELEASED"
    assert any(row["command"] == "AUTO_APPROVE" for row in logs)
    assert logs[-1]["status"] == "REJECTED"

    print("\nRESULT: Auto-approval happened before the revision request.")
    print("The revision request was rejected because the milestone was already released.")


def test_fourth_revision_opens_dispute():
    print("\n" + "=" * 75)
    print("TEST CASE 2: FOURTH REVISION REQUEST AUTOMATICALLY OPENS DISPUTE")
    print("=" * 75)

    start = datetime(2026, 2, 1, 10, 0, 0)

    commands = [
        make_command(1, "FUND", ["M001", "10000"], start),
        make_command(2, "START_WORK", ["M001"], start + timedelta(minutes=10)),
        make_command(3, "SUBMIT", ["M001"], start + timedelta(minutes=20)),

        make_command(
            4, "REQUEST_REVISION",
            ["M001", "First revision"],
            start + timedelta(minutes=30)
        ),
        make_command(5, "SUBMIT", ["M001"], start + timedelta(minutes=40)),

        make_command(
            6, "REQUEST_REVISION",
            ["M001", "Second revision"],
            start + timedelta(minutes=50)
        ),
        make_command(7, "SUBMIT", ["M001"], start + timedelta(minutes=60)),

        make_command(
            8, "REQUEST_REVISION",
            ["M001", "Third revision"],
            start + timedelta(minutes=70)
        ),
        make_command(9, "SUBMIT", ["M001"], start + timedelta(minutes=80)),

        make_command(
            10, "REQUEST_REVISION",
            ["M001", "Fourth revision"],
            start + timedelta(minutes=90)
        )
    ]

    logs, withdrawals, disputes, ledger = execute(make_data(), commands)

    display_results(logs, ledger)

    assert ledger[0]["state"] == "DISPUTED"
    assert logs[-1]["status"] == "ACCEPTED"
    assert "Fourth revision opened dispute" in logs[-1]["message"]

    print("\nRESULT: Fourth revision request successfully opened a dispute.")
    print("Final milestone state: DISPUTED")


if __name__ == "__main__":
    test_auto_approval_revision_collision()
    test_fourth_revision_opens_dispute()

    print("\n" + "=" * 75)
    print("MILESTONE EDGE-CASE TESTING COMPLETED")
    print("=" * 75)
