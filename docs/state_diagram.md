# STATE DIAGRAM

**Project:** Freelance Marketplace Escrow, Milestone Release, Dispute and Fee-Tier Engine

## 1. Milestone State Diagram

```mermaid
stateDiagram-v2
    [*] --> CREATED
    CREATED --> FUNDED
    FUNDED --> SUBMITTED
    SUBMITTED --> APPROVED
    SUBMITTED --> REVISION_REQUESTED
    SUBMITTED --> DISPUTED
    REVISION_REQUESTED --> SUBMITTED
    REVISION_REQUESTED --> DISPUTED
    APPROVED --> RELEASED
    DISPUTED --> RELEASED
    DISPUTED --> REFUNDED
    FUNDED --> REFUNDED
    RELEASED --> [*]
    REFUNDED --> [*]
```

## 2. Dispute State Diagram

```mermaid
stateDiagram-v2
    [*] --> DISPUTED
    DISPUTED --> EVIDENCE
    EVIDENCE --> MEDIATION
    MEDIATION --> ARBITRATION
    ARBITRATION --> RESOLVED
    RESOLVED --> [*]
```