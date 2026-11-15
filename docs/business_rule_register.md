# BUSINESS RULE REGISTER

**Project:** Freelance Marketplace Escrow, Milestone Release, Dispute and Fee-Tier Engine

## 1. Project and Escrow Rules

**BR-01:** A project must contain milestones with an agreed amount and due date.

**BR-02:** Escrow can be funded fully or milestone by milestone.

**BR-03:** A milestone must be 100% funded before work can start.

**BR-04:** A client must have KYC verification if total project funding exceeds ₹5,00,000.

**BR-05:** A client must pay a processing fee of 3% of the funded amount, subject to a minimum of ₹50, when funding escrow.

**BR-06:** The client processing fee is never refunded.

## 2. Milestone Rules

**BR-07:** A milestone follows the specified states: CREATED, FUNDED, SUBMITTED, APPROVED, REVISION_REQUESTED, DISPUTED, RELEASED and REFUNDED.

**BR-08:** A freelancer cannot submit work for an unfunded milestone.

**BR-09:** A client can request a maximum of three revisions. The fourth revision request automatically escalates the milestone to DISPUTED.

**BR-10:** A submitted milestone is automatically approved and released if the client takes no action for 14 calendar days.

**BR-11:** If the client is inactive, the auto-approval period is 7 days.

**BR-12:** The auto-approval timer resets whenever the freelancer resubmits the milestone.

**BR-13:** A milestone in DISPUTED state must not be automatically approved.

## 3. Freelancer Service Fee Rules

**BR-14:** Service fees are calculated using the lifetime released amount between a particular client and freelancer.

**BR-15:** The service fee tiers are:
- First ₹50,000: 20%
- ₹50,001 to ₹5,00,000: 10%
- Above ₹5,00,000: 5%

**BR-16:** If a release crosses a fee-tier boundary, the amount must be divided and charged at the applicable rates for each tier.

**BR-17:** The freelancer receives the milestone amount after deducting the service fee and applicable TDS.

## 4. TDS Rules

**BR-18:** TDS is 1% under Section 194-O once cumulative gross releases to a freelancer in a financial year exceed ₹5,00,000.

**BR-19:** TDS applies only to the amount exceeding the ₹5,00,000 threshold.

**BR-20:** Financial calculations must be rounded to paise. Amounts are rounded to rupees during withdrawal.

## 5. Dispute Rules

**BR-21:** A dispute follows these stages: DISPUTED → EVIDENCE → MEDIATION → ARBITRATION → RESOLVED.

**BR-22:** Both parties have 5 days to submit evidence.

**BR-23:** A party that fails to submit evidence loses by default.

**BR-24:** The mediation period is 7 days.

**BR-25:** The arbitration decision must be made within 10 days.

**BR-26:** The arbitration fee is ₹2,000 or 5% of the milestone amount, whichever is higher, subject to a maximum of the milestone amount.

**BR-27:** The losing party pays the arbitration fee.

**BR-28:** The arbitrator can award 0%, 25%, 50%, 75% or 100% of the milestone amount to the freelancer.

**BR-29:** The freelancer service fee applies only to the amount awarded to the freelancer.

## 6. Client Cancellation Rules

**BR-30:** Unfunded milestones can be cancelled without charge.

**BR-31:** If a funded milestone has not been started, cancellation results in a 100% refund of the escrow amount. The processing fee is retained.

**BR-32:** A submitted milestone cannot be cancelled. It must be approved or disputed.

**BR-33:** Cancellation of an in-progress milestone results in a 100% refund.

**BR-34:** A ₹500 cancellation charge applies after the client's second such cancellation within 90 days.

## 7. Freelancer Cancellation Rules

**BR-35:** If a freelancer cancels an in-progress milestone, the client receives a 100% refund.

**BR-36:** The freelancer's reliability level decreases by one level: A to B or B to C.

**BR-37:** A Level C freelancer receives a 5-percentage-point increase in service fee rates until completing five clean releases.

## 8. Withdrawal Rules

**BR-38:** The minimum withdrawal amount is ₹1,000.

**BR-39:** The weekly withdrawal limit is ₹2,00,000 without enhanced KYC.

**BR-40:** The weekly withdrawal limit is ₹10,00,000 with enhanced KYC.

**BR-41:** A withdrawal fee of ₹25 applies to withdrawals below ₹10,000. Withdrawals above ₹10,000 are free.

**BR-42:** Funds released during the last three days are held and cannot be withdrawn.

## 9. Project Inactivity Rules

**BR-43:** A project with no event for 90 days is automatically cancelled.

**BR-44:** Funded milestones are fully refunded when a project is automatically cancelled due to inactivity.

**BR-45:** Processing fees are retained even when the escrow amount is refunded.

## 10. Rule Execution Priority

**BR-46:** Business rules must be processed in this order:

1. State validation.
2. Funding and KYC checks.
3. Service fee calculation using lifetime billing before the current release.
4. TDS threshold calculation.
5. Rounding.

**BR-47:** Dispute outcomes take priority over auto-approval timers.