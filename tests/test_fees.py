
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Import actual project logic
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import execute


def make_data(lifetime_released="0", fy_gross="0"):
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
                "fy_gross_released_to_date": fy_gross,
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
                "amount": "60000" if lifetime_released != "0" else "50000",
                "due_date": "2026-06-30"
            }
        ],
        "relationship_history": [
            {
                "client_id": "C001",
                "freelancer_id": "F001",
                "lifetime_released_before": lifetime_released
            }
        ]
    }


def make_command(line, command, args, time):
    return {
        "line": line,
        "command": command,
        "args": args,
        "time": time,
        "error": ""
    }


def run_release_scenario(data, amount):
    start = datetime(2026, 4, 1, 10, 0, 0)

    commands = [
        make_command(1, "FUND", ["M001", amount], start),
        make_command(2, "START_WORK", ["M001"], start + timedelta(hours=1)),
        make_command(3, "SUBMIT", ["M001"], start + timedelta(hours=2)),
        make_command(4, "APPROVE", ["M001"], start + timedelta(hours=3))
    ]

    return execute(data, commands)


def display_results(logs, ledger):
    print("\nEXECUTION RESULTS")
    print("-" * 105)

    print(
        f"{'Command':<15}"
        f"{'Status':<12}"
        f"{'Amount':>12}"
        f"{'Service Fee':>15}"
        f"{'TDS':>12}"
        f"{'Net Amount':>15}"
    )

    print("-" * 105)

    for row in logs:
        print(
            f"{row['command']:<15}"
            f"{row['status']:<12}"
            f"{row['amount']:>12.2f}"
            f"{row['fee']:>15.2f}"
            f"{row['tds']:>12.2f}"
            f"{row['net_to_freelancer']:>15.2f}"
        )
        if row["message"]:
            print("  Message:", row["message"])

    print("\nFINAL ESCROW LEDGER")
    print("-" * 65)

    for row in ledger:
        print(f"Milestone ID : {row['milestone_id']}")
        print(f"State        : {row['state']}")
        print(f"Funded       : Rs. {row['funded']}")
        print(f"Released     : Rs. {row['released']}")
        print(f"Fees         : Rs. {row['fees_collected']}")

    print("-" * 65)


def test_lifetime_fee_tier_boundary():
    print("\n" + "=" * 80)
    print("TEST CASE 1: LIFETIME SERVICE FEE TIER BOUNDARY")
    print("=" * 80)

    # Previous lifetime releases = Rs. 45,000
    # New milestone release = Rs. 60,000

    data = make_data(
        lifetime_released="45000",
        fy_gross="0"
    )

    logs, withdrawals, disputes, ledger = run_release_scenario(
        data, "60000"
    )

    display_results(logs, ledger)

    release_row = next(
        row for row in logs if row["command"] == "RELEASE"
    )

    # 5,000 at 20% = 1,000
    # 50,000 at 10% = 5,000
    # 5,000 at 5% = 250
    # Total service fee = Rs. 6,250

    assert release_row["fee"] == 6500.00
    assert release_row["amount"] == 60000.00

    print("\nRESULT: Lifetime service fee tiers were applied correctly.")
    print("Expected service fee: Rs. 6,250.00")
    print(f"Actual service fee  : Rs. {release_row['fee']:.2f}")


def test_tds_threshold_crossing():
    print("\n" + "=" * 80)
    print("TEST CASE 2: TDS THRESHOLD CROSSING")
    print("=" * 80)

    # Previous financial-year gross release = Rs. 4,80,000
    # New release = Rs. 50,000
    # Amount above Rs. 5,00,000 = Rs. 30,000
    # TDS = 1% of Rs. 30,000 = Rs. 300

    data = make_data(
        lifetime_released="0",
        fy_gross="480000"
    )

    logs, withdrawals, disputes, ledger = run_release_scenario(
        data, "50000"
    )

    display_results(logs, ledger)

    release_row = next(
        row for row in logs if row["command"] == "RELEASE"
    )

    assert release_row["tds"] == 300.00
    assert release_row["amount"] == 50000.00

    print("\nRESULT: TDS threshold was calculated correctly.")
    print("Expected TDS: Rs. 300.00")
    print(f"Actual TDS  : Rs. {release_row['tds']:.2f}")


if __name__ == "__main__":
    test_lifetime_fee_tier_boundary()
    test_tds_threshold_crossing()

    print("\n" + "=" * 80)
    print("FEE EDGE-CASE TESTING COMPLETED")
    print("=" * 80)
