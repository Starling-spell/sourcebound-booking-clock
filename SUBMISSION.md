# Builder submission

Contribution type: Builder → Intelligent Contracts

Contribution date: use the actual implementation/deployment date shown by the finalized receipts.

## Title

SourceBoundBookingClock — Evidence-Compiled Reservations

## Description

SourceBoundBookingClock compiles prose schedules into UTC availability and enforces exclusive interval reservations. No graph, certificate or one-time capability lifecycle.

Leader and validators independently fetch a commit-pinned HTTPS document, verify its complete SHA-256 commitment, and interpret opening periods, breaks, closed days and timezone. Exact equality of the complete evidence report and availability mask is required. Ambiguous or unavailable evidence exposes no bookable slots.

Reservations bind calendar, principal, interval and evidence root. Overlaps and closed-hour bookings fail; only the bound principal can cancel before start. Cancellation releases occupancy but permanently spends the booking ID. A hash-linked journal preserves history.

StudioNet proofs cover semantic compilation, booking, cancellation, overlap/closure/replay rejection and ambiguous/hash-mismatched evidence. Demo sources are synthetic; no venue ownership or physical delivery is certified.

## Evidence

- Repository: https://github.com/Starling-spell/sourcebound-booking-clock
- Contract: https://github.com/Starling-spell/sourcebound-booking-clock/blob/main/contracts/SourceBoundBookingClock.py
- README: https://github.com/Starling-spell/sourcebound-booking-clock/blob/main/README.md
- Ten-proof matrix: https://github.com/Starling-spell/sourcebound-booking-clock/blob/main/LIVE_PROOFS.md
- Explorer contract: https://explorer-studio.genlayer.com/address/0xa3e0C29460D6aEf591B5d49Ea98D618fd47973d6
- Semantic compilation: https://explorer-studio.genlayer.com/tx/0x460decf34aaf51a0c2f64de7985b13fdab0c7c139fcee1295ac931df347d26cb
- Reservation: https://explorer-studio.genlayer.com/tx/0x994a0a001e93224cca8ad0c4018aba5f1ffffd5171b4052aa3d2b3a4d2a43dd8
- Closure rejection: https://explorer-studio.genlayer.com/tx/0x1f3d4ab23105baf3d2ad3fc64aa67766cb4e92431b0c233d991bf19306c05bd3
- Cancellation: https://explorer-studio.genlayer.com/tx/0x387d0046930d08bd7fab6c791fc26de477b385ca3538b3b34067c1d4ad1b791f
- Replay rejection: https://explorer-studio.genlayer.com/tx/0x9ad6fe88eb660ce81b9146c70bfa8ae34273e80885e933c8c04eba54783f6561
- Ambiguous interpretation: https://explorer-studio.genlayer.com/tx/0x11a70a31d1b6e503236ec43a7e6df68426e965be18490d4e10ca213af6da4f76

No unanimous-validator, external authority, guaranteed acceptance or points claim. All intended receipts are FINALIZED with their expected execution results; the CLI encoding error is excluded.
