# Security boundaries

Experimental StudioNet primitive; not audited, no funds, payments, physical venue enforcement or legal/ownership certification.

## Threats

- Source substitution: commit-pinned URL and full SHA-256, independently recomputed by every validator.
- Fabricated hours: no caller mask or summary; AI interprets fetched complete prose. Correlated model mistakes and prompt injection are residual risks, not eliminated by hashing.
- Unknown timezone/dates/closures: no availability; READY requires a complete explicit UTC interpretation.
- Double booking: transaction-serialized occupancy validation and update in one write.
- Third-party cancellation: sender must match immutable reservation principal.
- Cross-calendar cancellation: reservation keys bind both calendar and booking IDs.
- Replay: cancelled IDs remain permanently spent, including failed calendar IDs.
- Time abuse: transaction timestamp, future bounded UTC week, cannot book started slots or cancel started bookings.
- History mutation: append-only journal roots bind previous event, contract, evidence and reservation changes.

Calendars are independent namespaces. Two calendars may describe the same resource and both reserve it; this contract never claims global physical-resource exclusivity. Public registration is not proof of authority. Public free booking is vulnerable to Sybil-based capacity denial; an integrating application needs admission control before real deployment.

Reports bind immutable documents, not live freshness. Restrict use to published schedule commitments with an appropriate operational owner. A calendar cannot be updated or administratively rewritten after registration. External changes need a new calendar and an explicit migration policy outside this contract.

Malformed AI output rejects consensus rather than normalizing an unsafe mask. Network exceptions abort acquisition; no availability is installed. Semantic disagreement does not guarantee a locally stored failure state.

Report issues privately through the repository owner's GitHub contact; do not post credentials or undisclosed sensitive evidence.
