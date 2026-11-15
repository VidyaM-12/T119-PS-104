# REQUIREMENT ANALYSIS

## 1. Project Title
Freelance Marketplace Escrow, Milestone Release, Dispute and Fee-Tier Engine.

## 2. Problem Statement

The project aims to develop a command-file-driven freelance marketplace payment management engine using Python.

The system manages project creation, milestone funding, escrow management, milestone submissions, approvals, revisions, automatic approvals, dispute resolution, arbitration, cancellations and freelancer withdrawals.

It also calculates service fees, client processing fees and Tax Deducted at Source (TDS) according to predefined business rules.

## 3. Project Objectives

1. To manage clients, freelancers and freelance projects.
2. To create and manage project milestones.
3. To manage escrow funding and payments.
4. To process milestone submissions, approvals and revisions.
5. To implement automatic milestone approval.
6. To calculate freelancer service fees based on lifetime billing.
7. To calculate TDS according to the specified financial-year threshold.
8. To manage disputes, evidence submission, mediation and arbitration.
9. To implement project cancellation and refund rules.
10. To process freelancer withdrawals with applicable restrictions.
11. To maintain financial transaction records and generate reports.

## 4. Functional Requirements

### FR-01: Project Management
The system must allow projects to be created with multiple milestones, each having an amount and due date.

### FR-02: Escrow Funding
The system must support full or per-milestone funding and calculate client processing fees.

### FR-03: Milestone Management
The system must process milestone submissions, approvals, revision requests, automatic approvals and releases.

### FR-04: Fee Calculation
The system must calculate freelancer service fees according to lifetime billing with each client.

### FR-05: TDS Calculation
The system must calculate TDS according to the specified financial-year release threshold.

### FR-06: Dispute Management
The system must manage evidence submission, mediation, arbitration and dispute outcomes.

### FR-07: Cancellation Management
The system must process client and freelancer cancellations according to milestone status.

### FR-08: Withdrawal Management
The system must calculate available withdrawal balances and enforce minimum amounts, weekly limits and withdrawal fees.

### FR-09: Inactivity Management
The system must automatically cancel inactive projects according to the specified inactivity period.

### FR-10: Reporting
The system must print escrow ledgers, milestone states, dispute outcomes and withdrawal statements.

## 5. Non-Functional Requirements

1. Accuracy: Financial calculations must be accurate to paise.
2. Reliability: The system must follow all specified business rules.
3. Maintainability: The code must be organised into separate modules.
4. Testability: Every business rule must have corresponding test cases.
5. Validation: Invalid commands and operations must be handled safely.
6. Consistency: State transitions and financial records must remain consistent.
7. Portability: The application must run using Python 3.10 or later.

## 6. Technology Requirements

- Programming Language: Python 3.10+
- Development Environment: Visual Studio Code
- Input Data: CSV and command files
- Version Control: Git and GitHub
- Testing Framework: Python unittest

## 7. Project Scope

The project covers freelance project management, escrow funding, milestone processing, payment calculations, dispute resolution, cancellation, refunds and withdrawals.

The application will operate through input command files and generate outputs in the format specified by the assignment.