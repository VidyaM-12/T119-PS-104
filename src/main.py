
import csv
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
C = Decimal("0.01")
Z = Decimal("0.00")
LOG_FIELDS = ["line_no", "milestone_id", "command", "status", "from_state", "to_state", "amount", "fee", "tds", "net_to_freelancer", "message"]
WITHDRAW_FIELDS = ["line_no","freelancer_id","requested","status","fee","paid","available_after","message"]
DISPUTE_FIELDS = ["milestone_id","raised_by","outcome_pct_freelancer","arbitration_fee","fee_paid_by","freelancer_net","client_refund"]
LEDGER_FIELDS = ["project_id","milestone_id","state","funded","released","refunded","fees_collected"]
AWARDS = {Decimal(x) for x in ("0","25","50","75","100")}


def cash(x):
    return Decimal(str(x)).quantize(C, rounding=ROUND_HALF_UP)


def read_csv(name):
    p = DATA_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Missing input file: {p}")
    with p.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_data():
    return {n: read_csv(n + ".csv") for n in
            ("clients","freelancers","projects","milestones","relationship_history")}


def read_commands():
    p = DATA_DIR / "commands.txt"
    if not p.exists():
        raise FileNotFoundError(f"Missing input file: {p}")
    result = []
    with p.open(encoding="utf-8-sig") as f:
        for number, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [v.strip() for v in line.split("|")]
            item = {"line": number, "command": parts[0].upper(), "args": parts[2:]}
            try:
                item["time"] = datetime.strptime(parts[1], "%Y-%m-%d %H:%M:%S")
                item["error"] = ""
            except (ValueError, IndexError):
                item["time"] = None
                item["error"] = "Timestamp must be YYYY-MM-DD HH:MM:SS"
            result.append(item)
    return result


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: (f"{cash(row[k]):.2f}" if isinstance(row.get(k), Decimal)
                            else row.get(k, "")) for k in fields})


def truth(x):
    return str(x).strip().lower() in ("true", "yes", "1", "y")


def validate_input_data(data):
    """Validate required columns, unique IDs, and foreign-key relationships."""
    required = {
        "clients": {"client_id", "kyc_verified", "account_status"},
        "freelancers": {"freelancer_id", "reliability_level", "fy_gross_released_to_date", "enhanced_kyc"},
        "projects": {"project_id", "client_id", "freelancer_id", "created_date"},
        "milestones": {"milestone_id", "project_id", "amount", "due_date"},
        "relationship_history": {"client_id", "freelancer_id", "lifetime_released_before"},
    }
    for table, columns in required.items():
        if table not in data:
            raise ValueError(f"Missing input table: {table}")
        for row_no, row in enumerate(data[table], start=2):
            missing = columns - set(row)
            if missing:
                raise ValueError(f"{table}.csv row {row_no}: missing columns {sorted(missing)}")
    client_ids = [r["client_id"] for r in data["clients"]]
    freelancer_ids = [r["freelancer_id"] for r in data["freelancers"]]
    project_ids = [r["project_id"] for r in data["projects"]]
    milestone_ids = [r["milestone_id"] for r in data["milestones"]]
    for label, values in (("client_id", client_ids), ("freelancer_id", freelancer_ids),
                          ("project_id", project_ids), ("milestone_id", milestone_ids)):
        if len(values) != len(set(values)):
            raise ValueError(f"Duplicate {label} found in input CSV files")
    clients, freelancers, projects = set(client_ids), set(freelancer_ids), set(project_ids)
    for row in data["projects"]:
        if row["client_id"] not in clients:
            raise ValueError(f"Project {row['project_id']} refers to unknown client")
        if row["freelancer_id"] not in freelancers:
            raise ValueError(f"Project {row['project_id']} refers to unknown freelancer")
    projects_with_milestones = {row["project_id"] for row in data["milestones"]}
    for pid in projects:
        if pid not in projects_with_milestones:
            raise ValueError(f"Project {pid} must contain at least one milestone")
    for row in data["milestones"]:
        if row["project_id"] not in projects:
            raise ValueError(f"Milestone {row['milestone_id']} refers to unknown project")
        if cash(row["amount"]) <= Z:
            raise ValueError(f"Milestone {row['milestone_id']} must have a positive amount")
        try:
            datetime.strptime(row["due_date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValueError(f"Milestone {row['milestone_id']} must have a valid due_date (YYYY-MM-DD)")


def print_state(milestones):
    """Display the current state of every milestone in ID order."""
    print("\n" + "=" * 86)
    print("FINAL ESCROW MILESTONE STATE")
    print("=" * 86)
    print(f"{'Milestone ID':<16}{'Project ID':<16}{'State':<20}{'Funded':>12}{'Released':>12}{'Refunded':>12}")
    print("-" * 86)
    for mid, m in sorted(milestones.items()):
        print(f"{mid:<16}{m['project']:<16}{m['state']:<20}{m['funded']:>12.2f}{m['released']:>12.2f}{m['refunded']:>12.2f}")
    print("=" * 86)


def print_statement(project_id, milestones):
    """Display the escrow statement for all milestones belonging to one project."""
    rows = [(mid, m) for mid, m in sorted(milestones.items()) if m["project"] == project_id]
    if not rows:
        raise ValueError(f"No milestones found for project {project_id}")
    print("\n" + "=" * 86)
    print(f"ESCROW STATEMENT — {project_id}")
    print("=" * 86)
    print(f"{'Milestone ID':<16}{'State':<20}{'Funded':>12}{'Released':>12}{'Refunded':>12}{'Fees':>12}")
    print("-" * 86)
    for mid, m in rows:
        print(f"{mid:<16}{m['state']:<20}{m['funded']:>12.2f}{m['released']:>12.2f}{m['refunded']:>12.2f}{m['fees']:>12.2f}")
    print("-" * 86)
    totals = {key: sum((m[key] for _, m in rows), Z) for key in ("funded", "released", "refunded", "fees")}
    print(f"{'PROJECT TOTAL':<36}{totals['funded']:>12.2f}{totals['released']:>12.2f}{totals['refunded']:>12.2f}{totals['fees']:>12.2f}")
    print("=" * 86)


def validate_output_rows(logs, withdrawals, disputes, ledger):
    """Check output rows before writing the four evaluation CSV files."""
    schemas = ((logs, LOG_FIELDS, "milestone log"),
               (withdrawals, WITHDRAW_FIELDS, "withdrawals"),
               (disputes, DISPUTE_FIELDS, "disputes"),
               (ledger, LEDGER_FIELDS, "escrow ledger"))
    for rows, fields, label in schemas:
        for index, row in enumerate(rows, start=1):
            missing = [field for field in fields if field not in row]
            if missing:
                raise ValueError(f"{label} row {index} missing fields: {missing}")
    allowed = {"ACCEPTED", "REJECTED"}
    if any(row["status"] not in allowed for row in logs):
        raise ValueError("Milestone log contains an invalid status")
    if any(row["status"] not in allowed for row in withdrawals):
        raise ValueError("Withdrawals output contains an invalid status")


def fy_start(t):
    return datetime(t.year if t.month >= 4 else t.year-1, 4, 1)


def fee_for(amount, lifetime, level="A", clean=0):
    remaining, lifetime, total = cash(amount), cash(lifetime), Z
    extra = Decimal(".05") if level == "C" and int(clean or 0) < 5 else Z
    while remaining > Z:
        if lifetime < 50000:
            boundary, rate = Decimal(50000), Decimal(".20")
        elif lifetime < 500000:
            boundary, rate = Decimal(500000), Decimal(".10")
        else:
            boundary, rate = None, Decimal(".05")
        part = remaining if boundary is None else min(remaining, boundary-lifetime)
        total += part * (rate+extra)
        remaining -= part
        lifetime += part
    return cash(total)


def tds_for(amount, fy_total):
    amount, fy_total = cash(amount), cash(fy_total)
    taxable = min(amount, max(Z, fy_total+amount-Decimal(500000)))
    return cash(taxable * Decimal(".01"))


def execute(data, commands):
    clients = {r["client_id"]: r for r in data["clients"]}
    freelancers = {r["freelancer_id"]: r for r in data["freelancers"]}
    projects = {r["project_id"]: r for r in data["projects"]}
    ms = {}
    by_project = defaultdict(list)
    for r in data["milestones"]:
        mid = r["milestone_id"]
        ms[mid] = dict(id=mid, project=r["project_id"], amount=cash(r["amount"]),
                       state="CREATED", funded=Z, released=Z, refunded=Z, fees=Z,
                       started=False, submitted=None, revisions=0, dispute_stage="",
                       raised_by="", reason="", dispute_at=None, evidence=set(),
                       mediation_at=None, arbitration_at=None, resolved=False)
        by_project[r["project_id"]].append(mid)

    logs, withdrawals, disputes = [], [], []
    releases = defaultdict(list)
    fy_totals = {}
    withdrawn = defaultdict(list)
    cancel_history = defaultdict(list)
    last_event = {}
    final_ledger_snapshot = None
    for pid, p in projects.items():
        try: last_event[pid] = datetime.strptime(p["created_date"], "%Y-%m-%d")
        except (ValueError, KeyError): last_event[pid] = datetime.min

    active_mid = ""

    def log(line, cmd, status, before="", after="", amount=Z, fee=Z, tax=Z, net=Z, msg=""):
        normalized_status = "ACCEPTED" if status in ("SUCCESS", "ACCEPTED") else "REJECTED"
        logs.append(dict(line_no=line, milestone_id=active_mid, command=cmd,
                         status=normalized_status, from_state=before, to_state=after,
                         amount=cash(amount), fee=cash(fee), tds=cash(tax),
                         net_to_freelancer=cash(net), message=msg))

    def project_of(m):
        return projects[m["project"]]

    def relationship_total(m):
        p = project_of(m)
        total = sum((cash(r["lifetime_released_before"]) for r in data["relationship_history"]
                     if r["client_id"] == p["client_id"] and r["freelancer_id"] == p["freelancer_id"]), Z)
        total += sum((v["released"] for v in ms.values()
                      if projects[v["project"]]["client_id"] == p["client_id"]
                      and projects[v["project"]]["freelancer_id"] == p["freelancer_id"]), Z)
        return cash(total)

    def release(m, t):
        p = project_of(m)
        fid = p["freelancer_id"]
        fr = freelancers[fid]
        gross = cash(m["funded"]-m["released"]-m["refunded"])
        if gross <= Z: raise ValueError("No funded balance to release")
        service = fee_for(gross, relationship_total(m), fr.get("reliability_level","A").upper(),
                          fr.get("clean_releases_since_demotion",0))
        key = (fid, fy_start(t))
        fy = fy_totals.get(key, cash(fr.get("fy_gross_released_to_date",0)))
        tax = tds_for(gross, fy)
        net = cash(gross-service-tax)
        m["released"] += gross
        m["fees"] += service
        m["state"] = "RELEASED"
        fy_totals[key] = cash(fy+gross)
        releases[fid].append((t, net))
        if fr.get("reliability_level","").upper() == "C":
            fr["clean_releases_since_demotion"] = str(int(fr.get("clean_releases_since_demotion",0))+1)
        return gross, service, tax, net

    def begin_arbitration(m, at):
        m["dispute_stage"] = "ARBITRATION"
        if m.get("arbitration_at") is None:
            m["arbitration_at"] = at

    def approve_and_release(m, t, line, cmd, message):
        before = m["state"]
        m["state"] = "APPROVED"
        log(line, cmd, "SUCCESS", before, "APPROVED", msg="Client approval recorded")
        gross, service, tax, net = release(m, t)
        log(line, "RELEASE", "SUCCESS", "APPROVED", m["state"], gross, service, tax, net, message)

    def resolve(m, pct, t, line, cmd):
        pct = Decimal(str(pct))
        if pct not in AWARDS: raise ValueError("Award must be 0, 25, 50, 75 or 100")
        p = project_of(m)
        fid, fr = p["freelancer_id"], freelancers[p["freelancer_id"]]
        gross = cash(m["funded"]-m["released"]-m["refunded"])
        award = cash(gross*pct/100)
        refund = cash(gross-award)
        service = fee_for(award, relationship_total(m), fr.get("reliability_level","A").upper(),
                          fr.get("clean_releases_since_demotion",0)) if award else Z
        key = (fid, fy_start(t))
        fy = fy_totals.get(key, cash(fr.get("fy_gross_released_to_date",0)))
        tax = tds_for(award, fy) if award else Z
        net = cash(award-service-tax)
        arb = min(gross, max(Decimal(2000), cash(gross*Decimal(".05"))))
        # A 50-50 award has no losing party; the register does not define who pays.
        payer = "CLIENT" if pct > 50 else "FREELANCER" if pct < 50 else "UNSPECIFIED (50-50 TIE)"
        m["released"] += award
        m["refunded"] += refund
        m["fees"] += service+arb
        m["state"] = "RELEASED" if award else "REFUNDED"
        m["resolved"] = True
        m["dispute_stage"] = "RESOLVED"
        fy_totals[key] = cash(fy+award)
        if award: releases[fid].append((t,net))
        disputes.append(dict(milestone_id=m["id"], raised_by=m["raised_by"],
                             outcome_pct_freelancer=pct, arbitration_fee=arb,
                             fee_paid_by=payer, freelancer_net=net, client_refund=refund))
        log(line,cmd,"SUCCESS","DISPUTED",m["state"],award,service+arb,tax,net,"Dispute resolved")

    def timers(now, line, skip_auto_mid=None):
        nonlocal active_mid
        for m in ms.values():
            if m["id"] != skip_auto_mid and m["state"] == "SUBMITTED" and m["submitted"]:
                client = clients[project_of(m)["client_id"]]
                days = 7 if client.get("account_status","").upper() == "INACTIVE" else 14
                if now >= m["submitted"]+timedelta(days=days):
                    before = m["state"]
                    active_mid = m["id"]
                    approve_and_release(m,now,line,"AUTO_APPROVE","Automatic approval timer")
            if m["state"] == "DISPUTED" and not m["resolved"] and m["dispute_at"]:
                if now > m["dispute_at"]+timedelta(days=5):
                    missing = {"CLIENT","FREELANCER"}-m["evidence"]
                    if len(missing) == 1:
                        active_mid = m["id"]
                        winner = next(iter(m["evidence"]))
                        resolve(m,100 if winner=="FREELANCER" else 0,now,line,"EVIDENCE_DEFAULT")
                    elif len(missing) == 2 and m["dispute_stage"] in ("DISPUTED", "EVIDENCE"):
                        # No default winner is defined when both parties miss evidence.
                        # Keep the case unresolved and continue through mediation.
                        m["dispute_stage"] = "MEDIATION"
                        m["mediation_at"] = m["dispute_at"] + timedelta(days=5)
                    elif not missing and not m["mediation_at"]:
                        m["dispute_stage"],m["mediation_at"] = "MEDIATION",m["dispute_at"]+timedelta(days=5)
            if (
                m["state"] == "DISPUTED"
                and m["dispute_stage"] == "MEDIATION"
                and m["mediation_at"]
            ):
                project_last_event = last_event.get(m["project"])

                inactivity_due = (
                    project_last_event is not None
                    and now >= project_last_event + timedelta(days=90)
                )

                if (
                    now >= m["mediation_at"] + timedelta(days=7)
                    and not inactivity_due
                ):
                    begin_arbitration(
                        m,
                        m["mediation_at"] + timedelta(days=7)
                    )
        for pid, last in list(last_event.items()):
            if now >= last + timedelta(days=90):
                for mid in by_project[pid]:
                    m = ms[mid]

                    remaining_escrow = cash(
                        m["funded"] - m["released"] - m["refunded"]
                    )

                    if (
                        m["state"] not in ("RELEASED", "REFUNDED")
                        and remaining_escrow > Z
                    ):
                        before = m["state"]
                        active_mid = m["id"]

                        m["refunded"] = cash(
                            m["refunded"] + remaining_escrow
                        )
                        m["state"] = "REFUNDED"

                        log(
                            line,
                            "AUTO_CANCEL_INACTIVE",
                            "SUCCESS",
                            before,
                            m["state"],
                            remaining_escrow,
                            Z, Z, Z,
                            "Project inactive for 90 days; escrow refunded"
                        )

                last_event[pid] = now

    for item in commands:
        line, cmd, args, now = item["line"], item["command"], item["args"], item["time"]
        if item["error"]:
            log(line,cmd,"REJECTED",msg=item["error"]); continue
        target_mid = args[0] if args and cmd not in ("WITHDRAW", "STATEMENT", "PRINT_STATE") else None
        timers(now, line, skip_auto_mid=target_mid if cmd == "DISPUTE" else None)
        m = ms.get(args[0]) if args and cmd not in ("WITHDRAW", "STATEMENT", "PRINT_STATE") else None
        active_mid = m["id"] if m else ""
        try:
            if cmd=="FUND":
                if len(args)!=2 or not m: raise ValueError("FUND needs milestone_id and amount")
                before=m["state"]; amount=cash(args[1])
                if m["state"] not in ("CREATED","FUNDED"): raise ValueError("Milestone cannot be funded now")
                if amount<=0 or amount>m["amount"]-m["funded"]: raise ValueError("Invalid funding amount")
                p=project_of(m); cl=clients[p["client_id"]]
                total=sum((v["funded"] for v in ms.values() if v["project"]==m["project"]),Z)
                if total+amount>500000 and not truth(cl.get("kyc_verified","false")):
                    raise ValueError("Client KYC required above Rs. 5,00,000 project funding")
                fee=max(cash(amount*Decimal(".03")),Decimal("50"))
                m["funded"]+=amount; m["fees"]+=fee
                if m["funded"]==m["amount"]: m["state"]="FUNDED"
                log(line,cmd,"SUCCESS",before,m["state"],amount,fee,msg="Escrow funded; processing fee retained")
                last_event[m["project"]]=now

            elif cmd=="START_WORK":
                if len(args)!=1 or not m: raise ValueError("START_WORK needs milestone_id")
                before=m["state"]
                if m["state"]!="FUNDED" or m["funded"]!=m["amount"]: raise ValueError("Milestone must be fully funded")
                m["started"]=True
                log(line,cmd,"SUCCESS",before,before,msg="Work started")
                last_event[m["project"]]=now

            elif cmd=="SUBMIT":
                if len(args)!=1 or not m: raise ValueError("SUBMIT needs milestone_id")
                before=m["state"]
                if m["state"] not in ("FUNDED","REVISION_REQUESTED") or not m["started"]:
                    raise ValueError("Only started and funded work can be submitted")
                m["state"]="SUBMITTED"; m["submitted"]=now
                log(line,cmd,"SUCCESS",before,m["state"],msg="Submitted; approval timer started or reset")
                last_event[m["project"]]=now

            elif cmd=="APPROVE":
                if len(args)!=1 or not m: raise ValueError("APPROVE needs milestone_id")
                before=m["state"]
                if m["state"]!="SUBMITTED": raise ValueError("Only submitted work can be approved")
                approve_and_release(m,now,line,cmd,"Approved and released")
                last_event[m["project"]]=now

            elif cmd=="REQUEST_REVISION":
                if len(args)!=2 or not m: raise ValueError("REQUEST_REVISION needs milestone_id and note")
                before=m["state"]
                if m["state"]!="SUBMITTED": raise ValueError("Revision only allowed after submission")
                m["revisions"]+=1
                if m["revisions"]>=4:
                    m["state"]="DISPUTED"; m["dispute_stage"]="DISPUTED"
                    m["raised_by"]="CLIENT"; m["reason"]=args[1]; m["dispute_at"]=now
                else: m["state"]="REVISION_REQUESTED"
                log(line,cmd,"SUCCESS",before,m["state"],msg="Fourth revision opened dispute" if m["state"]=="DISPUTED" else "Revision requested")
                last_event[m["project"]]=now

            elif cmd=="DISPUTE":
                if len(args)!=3 or not m: raise ValueError("DISPUTE needs milestone_id, party, reason")
                before=m["state"]; party=args[1].upper()
                if party not in ("CLIENT","FREELANCER"): raise ValueError("Party must be CLIENT or FREELANCER")
                if m["state"] not in ("SUBMITTED","REVISION_REQUESTED"): raise ValueError("Milestone cannot be disputed now")
                m.update(state="DISPUTED",dispute_stage="DISPUTED",raised_by=party,
                         reason=args[2],dispute_at=now,evidence=set())
                log(line,cmd,"SUCCESS",before,m["state"],msg="Dispute opened; evidence window started")
                last_event[m["project"]]=now

            elif cmd=="EVIDENCE":
                if len(args)!=2 or not m: raise ValueError("EVIDENCE needs milestone_id and party")
                party=args[1].upper()
                if party not in ("CLIENT","FREELANCER") or m["state"]!="DISPUTED" or m["resolved"]:
                    raise ValueError("Invalid evidence submission")
                if now>m["dispute_at"]+timedelta(days=5): raise ValueError("Evidence window expired")
                if party in m["evidence"]: raise ValueError("Party already submitted evidence")
                before=m["state"]; m["evidence"].add(party)
                if len(m["evidence"])==2: m["dispute_stage"]="MEDIATION"; m["mediation_at"]=now
                else: m["dispute_stage"]="EVIDENCE"
                log(line,cmd,"SUCCESS",before,m["state"],msg="Evidence recorded")
                last_event[m["project"]]=now

            elif cmd=="MEDIATION_FAILED":
                if len(args)!=1 or not m or m["state"]!="DISPUTED" or m["dispute_stage"] not in ("MEDIATION", "ARBITRATION"):
                    raise ValueError("Milestone must have completed or be completing mediation")
                begin_arbitration(m,now)
                log(line,cmd,"SUCCESS",m["state"],m["state"],msg="Mediation ended; arbitration active")
                last_event[m["project"]]=now

            elif cmd=="ARBITRATION_AWARD":
                if len(args)!=2 or not m or m["state"]!="DISPUTED" or m["resolved"] or m["dispute_stage"]!="ARBITRATION":
                    raise ValueError("ARBITRATION_AWARD requires an unresolved dispute in ARBITRATION stage")
                if m.get("arbitration_at") is None:
                    raise ValueError("Arbitration start date is missing")
                if now > m["arbitration_at"] + timedelta(days=10):
                    raise ValueError("Arbitration decision deadline exceeded (10 days)")
                resolve(m,args[1],now,line,cmd)
                last_event[m["project"]]=now

            elif cmd=="CANCEL_MILESTONE":
                if len(args)!=2 or not m: raise ValueError("CANCEL_MILESTONE needs milestone_id and party")
                before=m["state"]; party=args[1].upper()
                if party not in ("CLIENT","FREELANCER"): raise ValueError("Party must be CLIENT or FREELANCER")
                if m["state"] in ("SUBMITTED","REVISION_REQUESTED","DISPUTED","RELEASED","REFUNDED"):
                    raise ValueError("Submitted, disputed or completed milestone cannot be cancelled")
                p=project_of(m); refund=cash(m["funded"]-m["released"]-m["refunded"]); charge=Z
                if m["started"] and party=="CLIENT":
                    cid=p["client_id"]
                    recent=[d for d in cancel_history[cid] if now-d<=timedelta(days=90)]
                    if len(recent)>=2: charge=Decimal("500")
                    cancel_history[cid].append(now)
                if m["started"] and party=="FREELANCER":
                    fr=freelancers[p["freelancer_id"]]
                    level=fr.get("reliability_level","A").upper()
                    fr["reliability_level"]="B" if level=="A" else "C" if level=="B" else "C"
                    fr["clean_releases_since_demotion"]="0"
                m["refunded"]+=refund; m["fees"]+=charge; m["state"]="REFUNDED"
                log(line,cmd,"SUCCESS",before,m["state"],refund,charge,msg="Cancelled; escrow refunded; processing fee retained")
                last_event[m["project"]]=now

            elif cmd=="WITHDRAW":
                if len(args)!=2 or args[0] not in freelancers: raise ValueError("WITHDRAW needs valid freelancer_id and amount")
                fid=args[0]; fr=freelancers[fid]
                amount=cash(args[1]).quantize(Decimal("1"),rounding=ROUND_HALF_UP)
                if amount<1000: raise ValueError("Minimum withdrawal is Rs. 1,000")
                enhanced=truth(fr.get("enhanced_kyc","false"))
                limit=Decimal(1000000 if enhanced else 200000)
                monday=(now-timedelta(days=now.weekday())).replace(hour=0,minute=0,second=0)
                sunday=monday+timedelta(days=7)
                week=sum((r["requested"] for r in withdrawn[fid] if monday<=r["time"]<sunday),Z)
                unlocked=sum((net for rt,net in releases[fid] if now>=rt+timedelta(days=3)),Z)
                already=sum((r["requested"] for r in withdrawn[fid]),Z)
                available=cash(max(Z,unlocked-already))
                fee=Decimal(25) if amount<10000 else Z
                status="ACCEPTED"; msg="Withdrawal processed"
                if week+amount>limit: status,msg="REJECTED","Weekly withdrawal limit exceeded"
                elif amount>available: status,msg="REJECTED","Insufficient released and unlocked balance"
                paid=cash(amount-fee) if status=="ACCEPTED" else Z
                if status=="ACCEPTED": withdrawn[fid].append(dict(time=now,requested=amount,paid=paid))
                withdrawals.append(dict(line_no=line,freelancer_id=fid,requested=amount,status=status,
                                        fee=fee if status=="ACCEPTED" else Z,paid=paid,
                                        available_after=cash(available-amount) if status=="ACCEPTED" else available,
                                        message=msg))

            elif cmd == "STATEMENT":
                if len(args) != 1 or args[0] not in projects:
                    raise ValueError("STATEMENT needs a valid project_id")
                print_statement(args[0], ms)

            elif cmd == "PRINT_STATE":
                if len(args) != 0:
                    raise ValueError("PRINT_STATE does not take arguments")
                print_state(ms)
                final_ledger_snapshot = [
                    dict(project_id=item["project"], milestone_id=mid, state=item["state"],
                         funded=item["funded"], released=item["released"],
                         refunded=item["refunded"], fees_collected=item["fees"])
                    for mid, item in sorted(ms.items())
                ]
            else:
                raise ValueError("Unknown command: "+cmd)

        except (ValueError, InvalidOperation, KeyError) as e:
            state = m["state"] if m else ""
            log(line, cmd, "REJECTED", state, state, msg=str(e))
            if cmd == "WITHDRAW" and not any(row["line_no"] == line for row in withdrawals):
                fid = args[0] if args else ""
                try:
                    requested = cash(args[1]) if len(args) > 1 else Z
                except (InvalidOperation, ValueError):
                    requested = Z
                withdrawals.append(dict(line_no=line, freelancer_id=fid, requested=requested,
                                         status="REJECTED", fee=Z, paid=Z,
                                         available_after=Z, message=str(e)))

    ledger = final_ledger_snapshot if final_ledger_snapshot is not None else [
        dict(project_id=item["project"], milestone_id=mid, state=item["state"],
             funded=item["funded"], released=item["released"],
             refunded=item["refunded"], fees_collected=item["fees"])
        for mid, item in sorted(ms.items())
    ]
    return logs, withdrawals, disputes, ledger


def main():
    data = load_data()
    validate_input_data(data)
    commands = read_commands()
    logs, withdrawals, disputes, ledger = execute(data, commands)
    validate_output_rows(logs, withdrawals, disputes, ledger)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR/"milestone_log.csv",LOG_FIELDS,logs)
    write_csv(OUTPUT_DIR/"withdrawals.csv",WITHDRAW_FIELDS,withdrawals)
    write_csv(OUTPUT_DIR/"disputes.csv",DISPUTE_FIELDS,disputes)
    write_csv(OUTPUT_DIR/"escrow_ledger.csv",LEDGER_FIELDS,ledger)
    print("PS-104 execution completed.")
    print(f"Commands read: {len(commands)}")
    print(f"Milestone log rows: {len(logs)}")
    print(f"Withdrawal rows: {len(withdrawals)}")
    print(f"Resolved disputes: {len(disputes)}")
    print(f"Final ledger rows: {len(ledger)}")
    print(f"Output folder: {OUTPUT_DIR}")
    print("Output validation: PASSED")


if __name__=="__main__":
    main()
