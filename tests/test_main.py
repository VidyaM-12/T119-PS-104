
import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Import the actual main program from src
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import cash, fee_for, tds_for, execute


def make_data(amount="10000", kyc="true"):
    return {
        "clients": [{
            "client_id": "C1",
            "account_status": "ACTIVE",
            "kyc_verified": kyc
        }],
        "freelancers": [{
            "freelancer_id": "F1",
            "reliability_level": "A",
            "clean_releases_since_demotion": "0",
            "fy_gross_released_to_date": "0",
            "enhanced_kyc": "true"
        }],
        "projects": [{
            "project_id": "P1",
            "client_id": "C1",
            "freelancer_id": "F1",
            "created_date": "2026-01-01"
        }],
        "milestones": [{
            "milestone_id": "M1",
            "project_id": "P1",
            "amount": amount
        }],
        "relationship_history": []
    }


def command(number, name, args, time):
    return {
        "line": number,
        "command": name,
        "args": args,
        "time": time,
        "error": ""
    }


class TestPS104(unittest.TestCase):

    def test_currency_rounding(self):
        self.assertEqual(
            cash("100.456"),
            Decimal("100.46")
        )

    def test_service_fee_tiers(self):
        self.assertEqual(
            fee_for("60000", "0"),
            Decimal("11000.00")
        )

    def test_reliability_level_c_surcharge(self):
        self.assertEqual(
            fee_for("50000", "0", "C", 0),
            Decimal("12500.00")
        )

    def test_tds_threshold(self):
        self.assertEqual(
            tds_for("100000", "450000"),
            Decimal("500.00")
        )

    def test_partial_funding_and_start_work(self):
        data = make_data()

        commands = [
            command(1, "FUND", ["M1", "5000"],
                    datetime(2026, 1, 1, 10, 0)),
            command(2, "START_WORK", ["M1"],
                    datetime(2026, 1, 1, 10, 1)),
            command(3, "FUND", ["M1", "5000"],
                    datetime(2026, 1, 1, 10, 2)),
            command(4, "START_WORK", ["M1"],
                    datetime(2026, 1, 1, 10, 3))
        ]

        logs, _, _, ledger = execute(data, commands)

        self.assertEqual(logs[0]["status"], "ACCEPTED")
        self.assertEqual(logs[1]["status"], "REJECTED")
        self.assertEqual(logs[2]["status"], "ACCEPTED")
        self.assertEqual(logs[3]["status"], "ACCEPTED")
        self.assertEqual(ledger[0]["state"], "FUNDED")

    def test_kyc_required_above_five_lakh(self):
        data = make_data("600000", "false")

        commands = [
            command(1, "FUND", ["M1", "600000"],
                    datetime(2026, 1, 1, 10, 0))
        ]

        logs, _, _, ledger = execute(data, commands)

        self.assertEqual(logs[0]["status"], "REJECTED")
        self.assertEqual(ledger[0]["funded"], Decimal("0.00"))

    def test_fourth_revision_opens_dispute(self):
        data = make_data()

        commands = [
            command(1, "FUND", ["M1", "10000"],
                    datetime(2026, 1, 1, 10, 0)),
            command(2, "START_WORK", ["M1"],
                    datetime(2026, 1, 1, 10, 1))
        ]

        current = datetime(2026, 1, 1, 10, 2)
        line = 3

        for revision in range(4):
            commands.append(
                command(line, "SUBMIT", ["M1"], current)
            )
            line += 1
            current += timedelta(minutes=1)

            commands.append(
                command(line, "REQUEST_REVISION",
                        ["M1", f"Revision {revision + 1}"],
                        current)
            )
            line += 1
            current += timedelta(minutes=1)

        logs, _, _, ledger = execute(data, commands)

        self.assertEqual(logs[-1]["status"], "ACCEPTED")
        self.assertEqual(ledger[0]["state"], "DISPUTED")

    def test_dispute_arbitration_award(self):
        data = make_data()

        commands = [
            command(1, "FUND", ["M1", "10000"],
                    datetime(2026, 1, 1, 10, 0)),
            command(2, "START_WORK", ["M1"],
                    datetime(2026, 1, 1, 10, 1)),
            command(3, "SUBMIT", ["M1"],
                    datetime(2026, 1, 1, 10, 2)),
            command(4, "DISPUTE",
                    ["M1", "CLIENT", "Work issue"],
                    datetime(2026, 1, 1, 10, 3)),
            command(5, "EVIDENCE", ["M1", "CLIENT"],
                    datetime(2026, 1, 1, 10, 4)),
            command(6, "EVIDENCE", ["M1", "FREELANCER"],
                    datetime(2026, 1, 1, 10, 5)),
            command(7, "MEDIATION_FAILED", ["M1"],
                    datetime(2026, 1, 1, 10, 6)),
            command(8, "ARBITRATION_AWARD", ["M1", "50"],
                    datetime(2026, 1, 1, 10, 7))
        ]

        logs, _, disputes, ledger = execute(data, commands)

        arbitration_log = [
            row for row in logs
            if row["command"] == "ARBITRATION_AWARD"
        ]

        self.assertEqual(len(arbitration_log), 1)
        self.assertEqual(arbitration_log[0]["status"], "ACCEPTED")
        self.assertEqual(len(disputes), 1)
        self.assertEqual(
            disputes[0]["client_refund"],
            Decimal("5000.00")
        )
        self.assertEqual(ledger[0]["state"], "RELEASED")

    def test_withdrawal_three_day_hold(self):
        data = make_data()

        release_time = datetime(2026, 1, 1, 10, 3)

        commands = [
            command(1, "FUND", ["M1", "10000"],
                    datetime(2026, 1, 1, 10, 0)),
            command(2, "START_WORK", ["M1"],
                    datetime(2026, 1, 1, 10, 1)),
            command(3, "SUBMIT", ["M1"],
                    datetime(2026, 1, 1, 10, 2)),
            command(4, "APPROVE", ["M1"], release_time),
            command(5, "WITHDRAW", ["F1", "1000"],
                    release_time + timedelta(days=2)),
            command(6, "WITHDRAW", ["F1", "1000"],
                    release_time + timedelta(days=3))
        ]

        _, withdrawals, _, _ = execute(data, commands)

        self.assertEqual(withdrawals[0]["status"], "REJECTED")
        self.assertEqual(withdrawals[1]["status"], "ACCEPTED")

    def test_processing_fee_minimum(self):
        data = make_data("1000")

        commands = [
            command(1, "FUND", ["M1", "1000"],
                    datetime(2026, 1, 1, 10, 0))
        ]

        logs, _, _, _ = execute(data, commands)

        self.assertEqual(
            logs[0]["fee"],
            Decimal("50.00")
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
