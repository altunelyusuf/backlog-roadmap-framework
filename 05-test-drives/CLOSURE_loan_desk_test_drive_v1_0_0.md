# Test drive of obligation set 2 — closure record, planned versus actual, and fit-gap

**Subject:** a library's book-loan desk, run as a complete project from mission to a shipped release.
**Purpose:** to find out whether the SDLC obligations added on 2026-09-11 are *complete* (a conformant
project can satisfy them) and *correct* (they refuse what should be refused), and to see what a
first-time adopter gets wrong.
**Register:** `05-test-drives/testdrive_loan_desk_v1_1_0.ttl`. Final state: **0 violations**, 72 advisories.
**Run by:** `brsf-session`, 2026-09-11, at the owner's instruction.

---

## 1. What the project set out to do

**Mission.** A member can borrow and return a book without a librarian keying anything twice, and the
desk always knows which copies are out and to whom.

**Boundary.** In scope: lending a copy, taking it back, and the record of which copies are out. Out of
scope: acquisitions, fines and inter-library loans — none is needed to borrow and return, and each
brings a payment system with it.

**Goals**, one for each way a goal can answer: a loan takes one pass at the desk rather than two; both
desk transactions are served and the record stays current; no money changes hands in this system.

**How success was to be measured**, with every baseline taken *before* any work:

| measure | at the start | target |
|---|---|---|
| keystroke passes to record one loan | 2 — watched at the desk | 1 |
| copies whose whereabouts the desk cannot state | 12 — shelf audit against the ledger | 0 |
| deliverables planned but not yet delivered | 2 | 0 |

## 2. What the obligations required, and what was produced

The project declared itself bound by the obligations at the moment it opened, so each planning step
had to produce its work before it could close.

| step | what it owed | what was produced |
|---|---|---|
| mission | the mission, alone | the statement above |
| scope | the domain things and a blueprint | *Copy*, *Loan*, *Member*, and the blueprint over them |
| goals | a use case, and both the ordinary and the refusal scenario | the borrow use case in four steps with its actors; the ordinary loan; the copy already out |
| objectives | the analysis-level activity and system-sequence models | how a loan happens at the desk today; member and system with the system as a black box |
| backlog | the analysis-level domain model and acceptance criteria | member/copy/loan as the library names them; three criteria in Given–When–Then |

**Eight models were produced, and the two levels stayed distinct** — which is the change this drive was
built to test:

| analysis level — the problem as it is | design level — the solution as built |
|---|---|
| how a loan happens at the desk today (activity) | components and their boundaries |
| member and system, system as a black box (sequence) | message order inside: desk → LoanService → CopyRepository |
| member, copy, loan as the library names them (class) | LoanService, CopyRepository, MemberDirectory (class) |
| | what a copy permits in each state: on shelf, out, lost |
| | the desk screen and its flow |

The class model and the sequence model each exist **twice, at both levels, as different artifacts**.
Under the old rules one drawing satisfied both and the domain was never analysed on its own terms.

**Fourteen engineering processes were carried to finished**, each producing the artifact its own
definition demands: the problem statement; the stated requirements; the component boundaries; the
design classes, message order and screens; an analysis note on why one service and not two; the built
transaction; evidence from an actual assembly; a test case with its data; verification and validation
evidence; the release; a working day of operation; a first-day fix (a due date off by one); and the
paper ledger closed and boxed with a record of what it leaves behind.

## 3. Planned versus actual

| | planned | actual |
|---|---|---|
| passes to record a loan | 2 → 1 | **1** — target met, watched over four loans after the change |
| copies unaccounted for | 12 → 0 | **4** — target not met; the remainder are returns, and returns were never in this window |
| deliverables delivered | 2 → 0 outstanding | **1 outstanding** — lending shipped, returning did not |
| window | 8 hours, 5 points committed | 8 hours measured, 5 points delivered |
| stories | 2 in scope | 1 finished, 1 still proposed |

**The honest reading.** One of three measures reached its target. The other two moved and stopped at
exactly the point the scope stopped: the desk cannot account for four copies because nobody has taught
it to take a book *back*, and the second deliverable is outstanding for the same reason. The plan was
not wrong about the direction, it was optimistic about how much one transaction could achieve — and
the measures say so without needing anyone's opinion.

## 4. Fit-gap against the obligations

**Fit.** All 37 required obligations were satisfiable and were satisfied by an ordinary, small project.
Nothing in the set proved impossible, contradictory, or unreachable. The level distinction survived
contact with real modelling: it was natural to draw both a domain model and a design model, and
irritating only where I had been sloppy.

**Gap — what the drive exposed, all of it in the modeller rather than the rules.** The project was
refused 113 times on its first run. Every refusal was work not done, and the pattern for doing it was
already recorded in this package's own archive, where 164 finished items satisfy the same rules:

| what was missing | count |
|---|---|
| finished items with no start point, no evidence, no verified evidence, no harness, no anchor, no audit date | 90 (6 demands × 15 items) |
| release with no shipped date, no basis, no decision, no member | 6 |
| domain things with no lifecycle coverage | 3 |
| test evidence with no specification, test data with no starting state | 4 |
| criteria of finished work naming no artifact | 3 |
| register with no commitment and no session record | 2 |
| measures read only before the work, never after | 1 |

**The one that matters most is the last.** With everything else supplied, the final refusal standing
was that a finished story claiming to move three measures had readings only from before it started.
That is the framework refusing to let work be called successful without measuring whether it was.

**The narrow question that remains** — to be discussed rather than decided here. Fourteen process tasks
each needed their own harness statement saying why the check on them is complete. That is verbose
(about one line each) rather than onerous, and two of the framework's own messages already say a task
"may inherit this from" the story it serves. Whether these per-item demands should be inherited from
the story, or genuinely owed by each task, is the open item.

## 5. Correction to an earlier report

An earlier handover from this session claimed that item-completion discipline and process-completion
discipline "have never been reconciled" and asked the owner to open a lineage to fix it. **That claim
is withdrawn.** It was drawn from the 113 refusals without first checking whether real work satisfies
the same rules — it does, 164 times in the archive — and the toy reached zero with no rule changed.
The correct finding is this document: the obligations work, the first-time adopter's mistakes are
predictable and worth publishing, and one narrow inheritance question is open.
