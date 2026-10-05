# SourceBoundBookingClock

An evidence-compiled reservation primitive: turn independently fetched prose opening hours into an immutable UTC availability mask, then reserve non-overlapping intervals against it. No graph proposals, certificates, confidence scores, or consumption tokens.

## Problem and GenLayer boundary

An ordinary contract can reject double bookings, but cannot reliably interpret “closed for lunch, then reopens until five” in a public timetable. A private LLM could silently invent availability. Here the **consequential AI output is the exact bookable slot mask**. Leader and validators independently fetch the pinned document and interpret its complete meaning. Exact report equality is required before that mask can authorize any reservation.

The registrant chooses a resource, source commitment and future week. These are configuration, not proof of venue ownership or real-world availability. The contract acquires the source itself; callers cannot submit an interpreted timetable or mask.

```text
commit-pinned HTTPS document
  → independent full-body fetch and SHA-256 check
  → independent semantic interpretation of seven UTC days
  → exact evidence + availability-mask agreement
  → immutable calendar
  → exclusive interval reservation / principal-only cancellation
```

```text
calendar ID unused → READY | AMBIGUOUS | UNAVAILABLE (immutable)
READY + future open unoccupied interval → RESERVED
RESERVED + bound principal + before start → CANCELLED
cancelled booking ID stays spent; a new ID may reuse released slots
```

## Architecture, not a renamed graph

Storage consists of immutable evidence-compiled calendars, 336-character occupancy bitmaps, calendar-scoped reservations, and an append-only hash-linked journal. There are no nodes, dependency edges, parent versions, proposal resolution, certificate issuance, owner replacement of accepted state, or one-time execution capabilities. Availability interpretation materially changes which reservations are permitted.

## Consensus

Each nondeterministic execution fetches the complete document, checks HTTP status, size, UTF-8 decoding and exact content hash, then asks an LLM to interpret opening periods and exclusions. Only explicit UTC schedules are supported. Unknown timezone, incomplete days or ambiguous exceptions yield AMBIGUOUS with no slots. Invalid structured AI output forces a consensus failure rather than granting availability.

Validators independently repeat acquisition and interpretation. They compare the entire report, including specification, source body, status, hash, availability mask and state, without score tolerance. Disagreement prevents the transaction from installing a calendar; it is not fabricated into a stored CONFLICTED result. Agreement on an unknown interpretation installs an immutable AMBIGUOUS calendar which rejects reservations.

## API

`create_calendar(calendar_id, resource, source, expected_hash, week_start)`

`reserve(calendar_id, booking_id, first_slot, slot_count)`

`cancel(calendar_id, booking_id)`

Views: `get_calendar`, `get_occupancy`, `get_reservation`, `history`.

Slot zero is Monday 00:00 UTC. Each slot is 30 minutes; a week has 336 slots. Maximum reservation length is eight slots. The week must begin on a future UTC Monday within sixty days. Reservations cannot start in the past; cancellation is available only before the reserved interval starts. All interval boundaries are half-open.

## Security model and limitations

- Complete source responses are independently acquired, never supplied as summaries.
- Public sources must be raw GitHub URLs pinned to a full commit SHA; no arbitrary hostname, private endpoint, mutable branch or query string is accepted.
- Registrants choose their source. Pinning proves content integrity, **not authority, truth, current freshness, or ownership of a physical resource**.
- Schedules are immutable, calendar-local and date-bounded. Later external changes do not alter existing bookings; use an independently reviewed operational process before offering real reservations.
- Reservations bind calendar ID, booking ID, transaction principal and evidence root. Cancellation cannot cross calendars or cancel another principal's booking.
- Calendar and booking IDs cannot be reused. Cancellation releases occupancy without deleting the historical reservation or its journal events.
- The public, free reservation pool has no Sybil resistance, payment, admission control or venue enforcement. It is infrastructure for experiments, not a production booking service.
- Prompt injection and correlated model errors remain risks. No audit or guaranteed real-world correctness is claimed. See [SECURITY.md](SECURITY.md).

## Example

The synthetic Demo Observatory timetable says Monday opens nine to noon, closes for lunch, then opens one to five. Consensus-derived slots are `[18,24)` and `[26,34)`. A booking at 18 for two slots succeeds; a booking overlapping slot 19 fails; noon slot 24 is closed. The principal can cancel and free slots, but cannot reuse the old booking ID.

The examples are **synthetic public fixtures**, not evidence that an actual observatory delivered a service. [LIVE_PROOFS.md](LIVE_PROOFS.md) will list only verified receipts and readbacks.

## Install and test

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/SourceBoundBookingClock.py --json
python -m pytest tests -q
npm install
```

Direct tests mock web/AI and do not execute network validators. The Windows harness narrowly defers upstream open-temp-file deletion and explicitly refreshes its cached message timestamp for time-travel tests. No deadline checks are bypassed.

## Deploy and interact

Use a dedicated encrypted CLI wallet. Never paste or commit private keys.

```powershell
npm install -g genlayer@0.39.2
genlayer network set studionet
genlayer account use YOUR_DEDICATED_ACCOUNT
genlayer account unlock
genlayer deploy --contract contracts/SourceBoundBookingClock.py
genlayer receipt DEPLOYMENT_HASH --stdout --stderr
genlayer code CONTRACT_ADDRESS
```

Before registering an example, pin the repository commit and independently compute the raw response SHA-256. Supply a future UTC Monday Unix timestamp, not a current/past week.

```powershell
genlayer write CONTRACT_ADDRESS create_calendar --args room 'Demo Observatory' PINNED_RAW_URL FULL_BODY_SHA256 FUTURE_MONDAY_TIMESTAMP
genlayer write CONTRACT_ADDRESS reserve --args room booking1 18 2
genlayer write CONTRACT_ADDRESS cancel --args room booking1
node scripts/check.mjs --source CONTRACT_ADDRESS
node scripts/check.mjs --success TRANSACTION_HASH
node scripts/view.mjs CONTRACT_ADDRESS get_calendar '["room"]'
```

Every write must have a FINALIZED receipt **and the expected execution result**. An expected rejection is recorded separately from successful execution. Compare Explorer's source with this repository and assert state readbacks. Never auto-retry a broadcast with an uncertain outcome.
