# PS-104 – Freelance Marketplace Escrow, Milestone Release, Dispute and Fee-Tier Engine — Sample Data Pack
Prepared by 10 SECONDS for Team T119.

## Files
| File | What it holds | Rows |
|---|---|---|
| clients.csv | Clients | 12 |
| freelancers.csv | Freelancers with FY release totals | 20 |
| projects.csv | Projects (client ↔ freelancer) | 25 |
| milestones.csv | Milestones per project with amounts | 77 |
| relationship_history.csv | Lifetime released per client↔freelancer pair before the period | 31 |
| commands.txt | ~200 milestone/dispute events + 40 withdrawals + statements, May–Oct 2026 | 239 |

## Column reference
Conventions: dates `YYYY-MM-DD`; timestamps `YYYY-MM-DD HH:MM:SS` (24h, IST, no timezone suffix); money in Rs as plain decimals with 2 places (no commas, no symbol); percentages as plain numbers (12.5 = 12.5%); booleans `true`/`false`; IDs uppercase with a fixed prefix. Row counts in the Files table exclude the header row (and comment lines in command files).

### clients.csv
| Column | Type | Units/format | Allowed values | Notes |
|---|---|---|---|---|
| client_id | string | CLI-NNN |  | PK |
| client_name | string |  |  |  |
| city | string |  |  |  |
| kyc_verified | boolean |  | true/false | needed above Rs 5 lakh funding per project |
| account_status | string |  | ACTIVE/INACTIVE | INACTIVE → 7-day auto-approval clock |

### freelancers.csv
| Column | Type | Units/format | Allowed values | Notes |
|---|---|---|---|---|
| freelancer_id | string | FRL-NNN |  | PK |
| freelancer_name | string |  |  |  |
| gender | string |  | M/F |  |
| city | string |  |  |  |
| reliability_level | string |  | A/B/C |  |
| fy_gross_released_to_date | money | Rs |  | gross releases in FY 2026-27 before the first command |
| enhanced_kyc | boolean |  | true/false | weekly withdrawal limit 10 lakh if true |
| clean_releases_since_demotion | integer |  |  | for level-C recovery |

### projects.csv
| Column | Type | Units/format | Allowed values | Notes |
|---|---|---|---|---|
| project_id | string | PRJ-NNN |  | PK |
| client_id | string |  | clients.client_id |  |
| freelancer_id | string |  | freelancers.freelancer_id |  |
| title | string |  |  |  |
| created_date | date | YYYY-MM-DD |  | inactivity clock starts here if no event |

### milestones.csv
| Column | Type | Units/format | Allowed values | Notes |
|---|---|---|---|---|
| milestone_id | string | MS-NNN |  | PK |
| project_id | string |  | projects.project_id |  |
| seq | integer |  |  | order within project |
| amount | money | Rs |  |  |
| due_date | date | YYYY-MM-DD |  |  |

### relationship_history.csv
| Column | Type | Units/format | Allowed values | Notes |
|---|---|---|---|---|
| client_id | string |  | clients.client_id |  |
| freelancer_id | string |  | freelancers.freelancer_id |  |
| lifetime_released_before | money | Rs |  | lifetime released for this pair before the period (fee-tier base) |

### commands.txt
| Column | Type | Units/format | Allowed values | Notes |
|---|---|---|---|---|
| line | text | COMMAND/args | see below |  |

## Command file format
`commands.txt` holds one command per line in the form `COMMAND_NAME|arg1|arg2|...`. Commands MUST be processed in file order (top to bottom). Lines starting with `#` are comments and blank lines are ignored. Argument order per command:

| Command | Arguments (in order) | Meaning |
|---|---|---|
| FUND | ts/milestone_id/amount | client funds escrow (processing fee charged) |
| START_WORK | ts/milestone_id | sets work-started flag |
| SUBMIT | ts/milestone_id | freelancer submits |
| APPROVE | ts/milestone_id | client approves → release |
| REQUEST_REVISION | ts/milestone_id/note | max 3; 4th → DISPUTED |
| DISPUTE | ts/milestone_id/raised_by/reason | raised_by CLIENT/FREELANCER |
| EVIDENCE | ts/milestone_id/party | evidence filed by CLIENT/FREELANCER |
| MEDIATION_FAILED | ts/milestone_id | mediation ends without settlement → ARBITRATION |
| ARBITRATION_AWARD | ts/milestone_id/freelancer_pct | 0/25/50/75/100 → RESOLVED |
| CANCEL_MILESTONE | ts/milestone_id/by | by CLIENT/FREELANCER |
| WITHDRAW | ts/freelancer_id/amount | withdrawal request |
| STATEMENT | ts/project_id | print escrow ledger for the project |
| PRINT_STATE | ts | evaluate timers and print all milestone states |

## Planted scenarios
Every edge case from the brief is planted at a known location, followed by extra traps. Line numbers refer to `commands.txt` counting from line 1 including comment lines.
- **Release of Rs 60,000 when lifetime is Rs 45,000 (tier split)** — PRJ-001 / MS-001 amount 60000.00; relationship CLI-001↔FRL-001 lifetime_released_before 45000.00; APPROVE at line 21 → 5000 at 20%, 55000 at 10%.
- **Auto-approval day 14 landing on the same day as a revision request** — PRJ-002 first milestone SUBMIT at 2026-06-01 10:00:00 (line 35); REQUEST_REVISION on 2026-06-15 15:00:00 (line 63) — day 14 (auto-approval fires at submit + 14×24 h = 10:00, before the request).
- **Fourth revision request (auto-dispute)** — PRJ-003 first milestone: four REQUEST_REVISION lines, the 4th at line 41 → auto-DISPUTED; dispute then runs to an award (line 65).
- **Both parties submit no evidence (default-loss rule conflict)** — PRJ-004 first milestone DISPUTE at line 61 with no EVIDENCE from either party; ARBITRATION_AWARD 0% at line 80 — your BR must state how the default-loss rule resolves when both default.
- **Arbitration fee 5% equals exactly Rs 2,000 on a Rs 40,000 milestone** — PRJ-005 milestone of 40000.00 disputed (line 66), award 75% to freelancer (line 78); losing party pays max(2000, 5% × 40000) = 2000 exactly.
- **Cumulative releases crossing Rs 5 lakh within one release** — FRL-006 has fy_gross_released_to_date 480000.00; APPROVE of a 50000.00 milestone at line 86 crosses Rs 5 lakh mid-release → TDS 1% on the 30000 above the threshold only.
- **Withdrawal request including funds released 3 days ago at midnight boundary** — PRJ-007 APPROVE/release at 2026-10-07 00:00:00 (line 220); WITHDRAW by FRL-010 at 2026-10-10 00:00:00 (line 222) — exactly 3 days: hold boundary.
- **Project inactivity reaching 90 days while a milestone is in MEDIATION** — PRJ-008: dispute enters MEDIATION after evidence (last event line 27, 2026-05-25); no further event until PRINT_STATE (line 241) 90+ days later.
- Trap — CLI-004 is not KYC_VERIFIED; cumulative funding of PRJ-009 crosses Rs 5 lakh at line 53 (reject); SUBMIT on an unfunded milestone at line 56 (reject).
- Trap — duplicate FUND of an already funded milestone at line 52; this line is deliberately out of timestamp order (earlier than the line before it) — process in file order.
- Trap — CLI-008 is INACTIVE: milestone submitted at line 129 auto-approves after 7 days, not 14.
- Trap — WITHDRAW below the Rs 1,000 minimum (line 145); withdrawal under Rs 10,000 attracts the Rs 25 fee (line 148); WITHDRAW of 250000.00 by FRL-006 at line 212: enhanced KYC lifts the weekly cap to 10 lakh, but the request exceeds the available (released, un-held) balance → reject for insufficient funds.

## What is NOT in this pack
Expected outputs are not provided for this set. Validate your engine with your own test suite against the rules in your brief (BR-01 … BR-nn). A separate hidden input set with the same schema will be used at final evaluation; outputs are compared field-for-field, so follow the column formats above exactly in your own output.

## Output format expected at evaluation
Produce the following CSV files (header row, same conventions as above, rows in the order stated). Column names are case-sensitive.

### `milestone_log.csv`
One row per command line affecting a milestone (and one per timer-triggered transition, with line_no of the command that triggered evaluation). status ACCEPTED/REJECTED.

Columns, in order: `line_no`, `milestone_id`, `command`, `status`, `from_state`, `to_state`, `amount`, `fee`, `tds`, `net_to_freelancer`, `message`

### `withdrawals.csv`
One row per WITHDRAW line.

Columns, in order: `line_no`, `freelancer_id`, `requested`, `status`, `fee`, `paid`, `available_after`, `message`

### `disputes.csv`
One row per dispute, in order of resolution.

Columns, in order: `milestone_id`, `raised_by`, `outcome_pct_freelancer`, `arbitration_fee`, `fee_paid_by`, `freelancer_net`, `client_refund`

### `escrow_ledger.csv`
Final state per milestone at PRINT_STATE, ordered by milestone_id.

Columns, in order: `project_id`, `milestone_id`, `state`, `funded`, `released`, `refunded`, `fees_collected`

## Notes and assumptions
- The 14/7-day auto-approval clock runs from the SUBMIT timestamp in whole 24-hour days.
- Week for withdrawal limits = Monday–Sunday calendar week.
- Financial year = 1 April 2026 – 31 March 2027.
