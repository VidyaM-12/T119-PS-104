# T119 – PS-104: Freelance Marketplace Escrow, Milestone Release, Dispute and Fee-Tier Engine

## Project Overview

The Freelance Marketplace Escrow, Milestone Release, Dispute and Fee-Tier Engine is a command-file-driven application developed using Python.

The system manages freelance project payments through escrow funding, milestone tracking, payment releases, service fee calculations, dispute resolution, project cancellation and freelancer withdrawals.

The main objective is to ensure secure and accurate financial transactions while following the defined business rules of a freelance marketplace.

## Problem Statement

**PS-104 – Freelance Marketplace Escrow, Milestone Release, Dispute and Fee-Tier Engine**

- Domain: Marketplaces – Freelance Work
- Language: Python 3.10+
- Project Type: Command-file-driven application
- Team ID: T119
- Section: ISE D

## Key Features

1. **Project and Milestone Management**
   - Create projects with multiple milestones.
   - Track milestone amounts, due dates and states.

2. **Escrow Funding**
   - Fund milestones fully or individually.
   - Apply client processing fees.
   - Validate KYC requirements for higher funding amounts.

3. **Milestone Workflow**
   - Handle work submission, approval and revision requests.
   - Support automatic approval after the specified time limit.
   - Prevent invalid milestone state transitions.

4. **Freelancer Service Fee Calculation**
   - Apply service fee tiers based on lifetime billing with each client.
   - Split a single release across fee boundaries when required.
   - Apply reliability-level adjustments.

5. **Payment Release and TDS**
   - Calculate service fees and freelancer net payments.
   - Apply TDS according to the specified threshold.
   - Handle financial calculations and rounding.

6. **Dispute Management**
   - Manage evidence submission, mediation and arbitration.
   - Apply default-loss rules when evidence is not submitted.
   - Calculate arbitration fees and dispute award amounts.

7. **Cancellation and Refunds**
   - Handle client and freelancer cancellation rules.
   - Process refunds for eligible milestones.
   - Apply inactivity-based automatic cancellation.

8. **Freelancer Withdrawals**
   - Validate minimum withdrawal amounts.
   - Apply weekly withdrawal limits and withdrawal fees.
   - Enforce the three-day withdrawal hold.

9. **Output and Reporting**
   - Generate milestone logs.
   - Track payment releases, refunds and withdrawals.
   - Display project and milestone states.

## Technologies Used

- Python 3.10+
- CSV files for input data
- Python standard libraries
- Git and GitHub
- Visual Studio Code

## Project Structure

```text
T119-PS-104/
│
├── data/
│   ├── README.md
│   ├── clients.csv
│   ├── freelancers.csv
│   ├── projects.csv
│   ├── milestones.csv
│   ├── relationship_history.csv
│   └── commands.txt
│
├── docs/
│   ├── Design Document
│   └── Decision Log
│
├── output/
│   └── Generated output files
│
├── src/
│   └── main.py
│
└── README.md
```

## Requirements

- Python 3.10 or above
- Visual Studio Code or another Python-compatible editor

<<<<<<< HEAD
=======
```

>>>>>>> 553b687 (Updated final project files)
## Business Rules

The application follows the defined business rules covering:

- Milestone state transitions
- Escrow funding and processing fees
- KYC validation
- Automatic milestone approval
- Freelancer service fee tiers
- TDS calculations
- Dispute and arbitration workflows
- Project cancellation and refunds
- Withdrawal limits and holding periods
- Project inactivity and automatic cancellation

## Edge Case Handling

The system addresses the eight specified edge cases, including:

- Fee-tier splitting across boundaries.
- Auto-approval and revision request timing conflicts.
- Automatic dispute escalation after the fourth revision request.
- Evidence submission conflicts.
- Arbitration fee boundary calculations.
- TDS threshold crossing.
- Withdrawal hold boundary conditions.
- Project inactivity during mediation.

## Testing

The application was tested using the provided sample data and command files. The required business-rule scenarios and eight specified edge cases were checked against the generated outputs.

## Team Details

| Detail | Information |
|---|---|
| Team ID | T119 |
| Problem Statement | PS-104 |
| Section | ISE D |
| Member 1 | Vidya M |
| Member 2 | Vijay Suresh Vathare |

## Conclusion

The project implements a rule-based freelance marketplace engine that manages escrow funding, milestone payments, fee calculations, dispute resolution, cancellations and withdrawals. It aims to provide accurate financial processing and consistent enforcement of marketplace business rules.
