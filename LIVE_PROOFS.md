# StudioNet proof matrix

Contract: [0xa3e0C29460D6aEf591B5d49Ea98D618fd47973d6](https://explorer-studio.genlayer.com/address/0xa3e0C29460D6aEf591B5d49Ea98D618fd47973d6).

Source/fixture commit: `8bdba136fb0416c6391d1689c34ea3190fa30365`.

Deployed source matches `contracts/SourceBoundBookingClock.py` after LF/trailing-newline normalization. Normalized SHA-256: `4de2d9efbeae39b9f96a659fadcc75c90eaf65dd21e88d8e21cd1e1b2a148938`.

Dedicated StudioNet signer: `0x7a413BB4AB62E31d62d4cD9efC8C8a8Dae37FB42`. Gasless demo; no funds transferred or keys exported.

All ten intended transactions below were independently checked as **FINALIZED**, with raw leader execution and `MAJORITY_AGREE`. This is **not a claim of unanimous validators**. Expected execution errors demonstrate specific rejection paths; they are not successful bookings.

| Case | Transaction | Execution | Verified consequence |
|---|---|---|---|
| Deploy | [656fc2bf](https://explorer-studio.genlayer.com/tx/0x656fc2bf0233e77a0db1e1e2d9d83afc746c78aba98a0fa71cc87af455aed286) | SUCCESS | Contract installed; deployed source matched |
| Compile explicit timetable | [460decf3](https://explorer-studio.genlayer.com/tx/0x460decf34aaf51a0c2f64de7985b13fdab0c7c139fcee1295ac931df347d26cb) | SUCCESS | Independently fetched prose became READY with 68 open slots |
| Reserve Monday 09:00–10:00 UTC | [994a0a00](https://explorer-studio.genlayer.com/tx/0x994a0a001e93224cca8ad0c4018aba5f1ffffd5171b4052aa3d2b3a4d2a43dd8) | SUCCESS | booking1 RESERVED; two slots occupied; principal and evidence root bound |
| Overlap Monday 09:30 | [7aaafd6c](https://explorer-studio.genlayer.com/tx/0x7aaafd6c19a3039883893390866e0f16ed3a6e4b045585431c8d7b85877eb695) | Expected ERROR | `[EXPECTED] overlapping reservation` |
| Book during lunch closure | [1f3d4ab2](https://explorer-studio.genlayer.com/tx/0x1f3d4ab23105baf3d2ad3fc64aa67766cb4e92431b0c233d991bf19306c05bd3) | Expected ERROR | `[EXPECTED] outside observed opening hours` |
| Bound principal cancels | [387d0046](https://explorer-studio.genlayer.com/tx/0x387d0046930d08bd7fab6c791fc26de477b385ca3538b3b34067c1d4ad1b791f) | SUCCESS | booking1 CANCELLED; occupancy zero; historical RESERVE retained |
| Reuse cancelled ID | [9ad6fe88](https://explorer-studio.genlayer.com/tx/0x9ad6fe88eb660ce81b9146c70bfa8ae34273e80885e933c8c04eba54783f6561) | Expected ERROR | `[EXPECTED] spent booking ID` |
| Compile vague timetable | [11a70a31](https://explorer-studio.genlayer.com/tx/0x11a70a31d1b6e503236ec43a7e6df68426e965be18490d4e10ca213af6da4f76) | SUCCESS | Independently fetched source interpreted as AMBIGUOUS; no mask |
| Book ambiguous calendar | [c6efdaa8](https://explorer-studio.genlayer.com/tx/0xc6efdaa882f79d4f9f731cf28a1c3fbef59f889fa7398dcc05991dd492ea1642) | Expected ERROR | `[EXPECTED] calendar not ready` |
| Mismatched source hash | [63f09f2e](https://explorer-studio.genlayer.com/tx/0x63f09f2e610daa0816c19630f1205cd0990ffe5462fc4668835a6485e9c2fd1f) | SUCCESS | Full body fetched but hash differed; UNAVAILABLE, no mask |

## Observed evidence and masks

Both sources are **synthetic public fixtures** authored for this demo, not independently authoritative real-venue schedules. The contract proves interpretation of acquired committed documents and enforces calendar-local reservations. It does not verify physical service delivery, source authority or live availability.

- [Explicit fixture](https://raw.githubusercontent.com/Starling-spell/sourcebound-booking-clock/8bdba136fb0416c6391d1689c34ea3190fa30365/examples/opening-hours.txt): 651 bytes, SHA-256 `622e7ca5eb7d17035516129609ac4d602b9fc2fc88e2029234cabadde0b987ba`.
- [Ambiguous fixture](https://raw.githubusercontent.com/Starling-spell/sourcebound-booking-clock/8bdba136fb0416c6391d1689c34ea3190fa30365/examples/ambiguous-hours.txt): 177 bytes, SHA-256 `60cc54e7683fd94da32cdcb9ca8e583265899837df8cbb9594548deb20ab5789`.
- Calendar week: Monday **2026-10-12 00:00 UTC** through Monday 2026-10-19 00:00 UTC; `week_start=1791763200`.
- Monday, Tuesday, Thursday, Friday: slots `[18,24)` and `[26,34)`.
- Wednesday: `[20,28)`; Saturday: `[20,24)`; Sunday: closed.
- READY evidence root: `70ad9d0b8bbcf590331936c4c6ac1884ba19dc859407ed60a4e276c6b78cfe45`.
- AMBIGUOUS evidence root: `5777b58be6be10ab601eb580475358255ff7386739be005c79d54595cbda92c4`.
- Final journal: five append-only events, root `ea7b43dd68fb554de82fef32c43dd0a39c6d5285c4c377f14a6d3fcd25bc89ad`.

`node scripts/assert_state.mjs ADDRESS` passed exact masks, roots, principal/calendar bindings, released occupancy, fail-closed states and journal-chain assertions.

## Local versus network coverage

GenVM lint and SDK validation passed. Fifteen direct tests passed. Direct tests mock web/AI, do not execute validator callbacks, and are not real-world evidence.

Cross-calendar and third-party cancellation, deadline boundaries, malformed intervals and exact disagreement comparison are covered locally. They are **not claimed as live transaction proofs**. Network validators were exercised for the explicit and ambiguous semantic calendar calls. Disagreement blocks a consensus transition; no forced-disagreement test or stored CONFLICTED result is claimed.

## Excluded failed invocation

Transaction `0x8538acfbfcec9cba026d06897183755c6c34aa02b02594fda88accd774cb592d` finalized with a TypeError because CLI scalar parsing encoded an all-digit all-zero hash as an integer. It installed no calendar and is **excluded from the ten intended proofs**. The actual integrity test used a string-safe 64-character `f` hash and succeeded in recording UNAVAILABLE. Use SDK string arguments for numeric-only hash strings.

## Recheck

```powershell
node scripts/check.mjs --source 0xa3e0C29460D6aEf591B5d49Ea98D618fd47973d6
node scripts/check.mjs --success 0x460decf34aaf51a0c2f64de7985b13fdab0c7c139fcee1295ac931df347d26cb
node scripts/check.mjs --error 0x7aaafd6c19a3039883893390866e0f16ed3a6e4b045585431c8d7b85877eb695 'overlapping reservation'
node scripts/assert_state.mjs 0xa3e0C29460D6aEf591B5d49Ea98D618fd47973d6
```
