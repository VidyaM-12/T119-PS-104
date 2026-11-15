# Edge Case Test Cases – PS-104

## EC-01: Service Fee Tier Boundary Split

**Objective:**

To verify that the system correctly calculates the service fee when a milestone release crosses the ₹50,000 lifetime billing threshold.

**Related Business Rules:** BR-14, BR-15, BR-16

**Test Input:**

- Previous lifetime billing: ₹45,000
- Milestone ID: MS-001
- Milestone release amount: ₹60,000

**Test Scenario:**

A freelancer has already received ₹45,000 in lifetime billing from a client. The client approves a new milestone release of ₹60,000. The system must apply the applicable service fee rates to each portion of the release.

**Expected Result:**

- First ₹5,000 charged at 20% = ₹1,000
- Remaining ₹55,000 charged at 10% = ₹5,500
- Total service fee = ₹6,500
- TDS = ₹0
- Net amount to freelancer = ₹53,500

**Actual Result:**

- Gross release = ₹60,000
- Service fee = ₹6,500
- TDS = ₹0
- Net amount to freelancer = ₹53,500

**Test Status:** PASS

**Conclusion:**

The system correctly splits the milestone release across the applicable service fee tiers. The actual service fee matches the expected fee of ₹6,500.

**Evidence:** `output/milestone_log.csv` – MS-001 RELEASE record.

## EC-02: Auto-Approval Before Revision Request

**Objective:**

To verify that the system automatically approves and releases a milestone when the 14-day approval period expires before processing a revision request.

**Related Business Rules:** BR-10, BR-12

**Test Input:**

- Milestone ID: MS-004
- Submission date: 1 June 2026, 10:00 AM
- Auto-approval deadline: 15 June 2026, 10:00 AM
- Revision request time: 15 June 2026, 3:00 PM

**Test Scenario:**

A freelancer submits a milestone on 1 June 2026. The client does not take any action within the 14-day approval period. On 15 June 2026, after the deadline, the client attempts to request a revision.

**Expected Result:**

- The system checks the auto-approval timer before processing the revision request.
- The milestone is automatically approved and released.
- The revision request is rejected because the milestone is no longer in the SUBMITTED state.
- The final milestone state is RELEASED.

**Actual Result:**

- AUTO_APPROVE – ACCEPTED.
- REQUEST_REVISION – REJECTED.
- Rejection message: "Revision only allowed after submission."
- Final state of MS-004 in the escrow ledger: RELEASED.

**Test Status:** PASS

**Conclusion:**

The system correctly evaluates the 14-day auto-approval timer before processing the revision request. The milestone is automatically approved and released, and the subsequent revision request is rejected.

**Evidence:**

- `output/milestone_log.csv` – MS-004 AUTO_APPROVE and REQUEST_REVISION records.
- `output/escrow_ledger.csv` – Final state of MS-004.

## EC-03: Fourth Revision Request Automatically Opens a Dispute

**Objective:**

To verify that the system automatically opens a dispute when a client requests a fourth revision for the same milestone.

**Related Business Rules:** BR-09, BR-21

**Test Input:**

- Milestone ID: MS-007
- Initial funded amount: ₹30,000
- Revision requests: 4

**Test Scenario:**

A freelancer submits milestone MS-007. The client requests revisions three times, and the freelancer resubmits the milestone after each revision. When the client requests a fourth revision, the system must automatically open a dispute instead of accepting another revision.

**Expected Result:**

- The first three revision requests are accepted.
- The fourth revision request automatically changes the milestone state to DISPUTED.
- The system records the reason for opening the dispute.
- No further normal revision request is allowed.

**Actual Result:**

- First revision request – ACCEPTED.
- Second revision request – ACCEPTED.
- Third revision request – ACCEPTED.
- Fourth revision request – ACCEPTED.
- Previous state: SUBMITTED.
- New state: DISPUTED.
- Log message: "Fourth revision opened dispute."

**Test Status:** PASS

**Conclusion:**

The system correctly accepts up to three revision requests and automatically opens a dispute when the fourth revision is requested.

**Evidence:**

- `output/milestone_log.csv` – MS-007 revision request records, including the fourth request.
- `output/escrow_ledger.csv` – Milestone MS-007 dispute state.

## EC-04: Both Parties Fail to Submit Dispute Evidence

**Objective:**

To verify the system's handling of a dispute when neither the client nor the freelancer submits evidence within the permitted evidence period.

**Related Business Rules:** BR-21, BR-22, BR-23

**Test Input:**

- Milestone ID: MS-010
- Dispute date: 13 June 2026
- Dispute raised by: CLIENT
- Evidence submitted by client: None
- Evidence submitted by freelancer: None

**Test Scenario:**

A dispute is opened for milestone MS-010. Neither the client nor the freelancer submits evidence during the evidence submission period. The system must handle the absence of evidence according to the dispute rules.

**Expected Result:**

- The system identifies that neither party submitted evidence.
- The dispute is resolved according to the default evidence rule.
- The appropriate dispute outcome is recorded.
- The milestone reaches the correct final state.

**Actual Result:**

- DISPUTE – ACCEPTED.
- No EVIDENCE command was recorded for either party.
- ARBITRATION_AWARD – REJECTED.
- Rejection message: "Arbitration decision deadline exceeded (10 days)."
- Later, AUTO_CANCEL_INACTIVE – ACCEPTED.
- Final milestone state: REFUNDED.
- Refund amount: ₹20,000.

**Test Status:** PARTIAL PASS

**Conclusion:**

The system correctly identifies the dispute and handles the absence of evidence from both parties. However, the final dispute outcome is not clearly defined when both parties fail to submit evidence. This creates an ambiguity between BR-22 and BR-23 . The milestone is eventually refunded through the 90-day inactivity rule. Further clarification of the business rules is required to determine the immediate dispute outcome.

**Evidence:**

- `data/commands.txt` – MS-010 DISPUTE and ARBITRATION_AWARD commands.
- `output/milestone_log.csv` – MS-010 dispute, rejected arbitration, and automatic cancellation records.
- `output/escrow_ledger.csv` – Final REFUNDED state of MS-010.

## EC-05: Arbitration Fee on a ₹40,000 Milestone

**Objective:**

To verify that the system correctly calculates the arbitration fee when the milestone amount is ₹40,000.

**Related Business Rules:** BR-23

**Test Input:**

- Milestone ID: MS-013
- Milestone amount: ₹40,000
- Arbitration fee: ₹2,000
- Arbitration award: 75% to freelancer

**Test Scenario:**

A dispute is raised for milestone MS-013, which has a funded amount of ₹40,000. Both parties submit evidence, mediation fails, and the dispute proceeds to arbitration. The arbitration fee must be calculated according to the project rules.

**Expected Result:**

- Arbitration fee = ₹2,000.
- The fee must be correctly recorded.
- The arbitration award of 75% must be applied to the milestone.
- The freelancer receives the correct net amount after applicable deductions.
- The remaining milestone amount is refunded to the client.

**Actual Result:**

- DISPUTE – ACCEPTED.
- Client evidence – ACCEPTED.
- Freelancer evidence – ACCEPTED.
- MEDIATION_FAILED – ACCEPTED.
- ARBITRATION_AWARD – ACCEPTED.
- Arbitration fee recorded = ₹2,000.
- Fee paid by = CLIENT.
- Freelancer gross award = ₹30,000.
- Service fee = ₹5,000.
- TDS = ₹0.
- Freelancer net amount = ₹27,000.
- Client refund = ₹10,000.
- Final milestone state = RELEASED.

**Test Status:** PASS

**Conclusion:**

The system correctly records the arbitration fee of ₹2,000 for the ₹40,000 milestone and applies the 75% arbitration award. The freelancer receives ₹27,000 after the service fee deduction, and ₹10,000 is refunded to the client.

**Evidence:**

- `output/disputes.csv` – MS-013 arbitration fee and award details.
- `output/milestone_log.csv` – MS-013 ARBITRATION_AWARD record.
- `output/escrow_ledger.csv` – Final milestone state and financial details.

## EC-06: TDS Calculation When Cumulative Releases Cross ₹5 Lakh

**Objective:**

To verify that the system correctly deducts TDS only on the portion of a release that exceeds the financial year's cumulative gross release threshold of ₹5,00,000.

**Related Business Rules:** BR-17, BR-18, BR-19

**Test Input:**

- Freelancer ID: FRL-006
- Previous financial-year cumulative gross releases: ₹4,80,000
- Milestone ID: MS-016
- New milestone release: ₹50,000
- TDS rate: 1%

**Test Scenario:**

A freelancer has already received cumulative gross releases of ₹4,80,000 during the financial year. A new milestone of ₹50,000 is approved and released. The system must deduct TDS only on the portion exceeding ₹5,00,000.

**Expected Result:**

- Remaining threshold amount = ₹20,000.
- Amount subject to TDS = ₹30,000.
- TDS = 1% of ₹30,000 = ₹300.
- Service fee = ₹2,500.
- Net amount = ₹50,000 − ₹2,500 − ₹300 = ₹47,200.

**Actual Result:**

- Gross release = ₹50,000.
- Service fee = ₹2,500.
- TDS = ₹300.
- Net amount = ₹47,200.
- Final milestone state = RELEASED.

**Test Status:** PASS

**Conclusion:**

The system correctly calculates TDS on only the ₹30,000 portion exceeding the ₹5,00,000 financial-year threshold.

**Evidence:**

- `output/milestone_log.csv` – MS-016 RELEASE record.
- `output/escrow_ledger.csv` – MS-016 final release details.

## EC-07: Withdrawal at the Three-Day Unlock Boundary

**Objective:**

To verify that the system checks the three-day withdrawal hold period before processing a freelancer's withdrawal request.

**Related Business Rules:** BR-17, BR-20

**Test Input:**

- Freelancer ID: FRL-010
- Milestone ID: MS-019
- Release date and time: 7 October 2026, 12:00 AM
- Withdrawal request date and time: 10 October 2026, 12:00 AM
- Withdrawal request amount: ₹15,000

**Test Scenario:**

A milestone is released, and the freelancer requests a withdrawal exactly three days after the release. The system must check the available released and unlocked balance before processing the request.

**Expected Result:**

- The three-day hold period must be completed.
- The system must check the freelancer's available balance.
- If the requested amount exceeds the available balance, the withdrawal must be rejected.

**Actual Result:**

- MS-019 release – ACCEPTED.
- Net amount released to freelancer = ₹13,500.
- Withdrawal request of ₹15,000 – REJECTED.
- Available released and unlocked balance = ₹13,500.
- Rejection message: "Insufficient released and unlocked balance."

**Test Status:**  PASS

**Conclusion:**

**Test Status:** PASS

**Conclusion:**

The system correctly applies the three-day withdrawal hold period. At exactly three days after the release, the net amount of ₹13,500 becomes available for withdrawal. The ₹15,000 request is correctly rejected because it exceeds the available balance.

**Evidence:**

- `data/commands.txt` – MS-019 approval and FRL-010 withdrawal commands.
- `output/withdrawals.csv` – FRL-010 withdrawal record.
- `output/milestone_log.csv` – MS-019 release record.

## EC-08: Project Inactivity Reaches 90 Days During a Dispute

**Objective:**

To verify that the system automatically cancels an inactive project and refunds the escrow amount when the 90-day inactivity period is reached, even when a milestone is in a dispute.

**Related Business Rules:** BR-21, BR-22

**Test Input:**

- Milestone ID: MS-021
- Project ID: PRJ-008
- Funded amount: ₹30,000
- Dispute date: 21 May 2026
- Last recorded evidence date: 25 May 2026
- Automatic inactivity cancellation date: 24 August 2026

**Test Scenario:**

A dispute is opened for milestone MS-021. Both parties submit evidence, but no further activity is recorded. When the project reaches the 90-day inactivity period, the system checks the inactivity timer and automatically cancels the milestone.

**Expected Result:**

- The system identifies 90 days of project inactivity.
- The automatic cancellation process is triggered.
- The escrow amount is refunded to the client.
- The final milestone state becomes REFUNDED.

**Actual Result:**

- DISPUTE – ACCEPTED.
- Freelancer evidence – ACCEPTED.
- Client evidence – ACCEPTED.
- AUTO_CANCEL_INACTIVE – ACCEPTED.
- Previous state = DISPUTED.
- New state = REFUNDED.
- Refund amount = ₹30,000.

**Test Status:** PASS

**Conclusion:**

The system correctly detects project inactivity and automatically refunds the ₹30,000 escrow amount. The milestone reaches the REFUNDED state.

**Evidence:**

- `data/commands.txt` – MS-021 dispute and evidence commands.
- `output/milestone_log.csv` – MS-021 AUTO_CANCEL_INACTIVE record.
- `output/escrow_ledger.csv` – MS-021 final REFUNDED state.