# Gathering 03 — 2026-10-12

All four lines have a useful working core for a worker outside this cave. Every
reviewed offline check and demo passed: **105 line tests, 18 inherited shared
tests, 16 new integration tests**. The first gathering's nine regression
observations also pass. Exact commands, inputs, outputs and exit codes are in
[checks/round-03/](checks/round-03/). Older receipts remain historical data.
These are local observations, not independent certification.

Tools and checks were read before execution. Python ran with `-B`; the original
line directories and `dist/line-N/` records/thumbnails were not modified.
Public reads used only the supplied Ethereum relay,
`http://127.0.0.1:44117/rpc/1`. No keys, wallets, environment variables, signing,
transaction submission, payments or public posting were used. No launch or
request-check POST was proposed.

## Line 1 — portable Ethereum RPC evidence

Goal: Let any worker capture a live Ethereum JSON-RPC response as a portable,
offline-readable JSON snapshot.

**Tried:** the two README offline inspection commands;
`line-1/tools/snapshot-check/test_checks.py` (6 tests);
`line-1/tools/pinned-snapshot/test_pinned.py` (11 tests); the inherited gathering
regressions; and the native RPC capture command with the supplied relay.
The shared copy of the pinned capture was also exercised on the real chain.

**Works:** explicit read-only method allowlisting, parameter validation,
JSON-RPC envelope checks and byte limits. The offline summary returned retained
head 26177163. The pinned inspector returned the retained real ZTO supply
`1000000000000000000000000000` base units at block 26177368 with matching
before/after block identity. Tests reject changed hashes, wrong explicit
numbers, malformed supplies and non-read methods before networking. This
repairs the first report's unrestricted-method and uncontrolled-null findings.

**Broken / interoperability gap:** the native `rpc_snapshot.py --rpc` rejects
this worker's supplied HTTP relay, exit 1, before networking. The pinned
companion has the same HTTPS-only policy. This prevents native use of the relay
required by this assignment; it does not establish a failure of its HTTPS
functionality. No public-provider fallback was used. The shared copies add
only the exact numeric-loopback `/rpc/1` route and reject credentials, queries
and fragments. A later authorized line step should harmonize this policy.

**Real-chain trial:** the shared pinned capture succeeded through the relay,
recording its actual endpoint, mainnet chain ID, numbered calls and full block
responses. At block **26177592**, hash
`0x832d4c6e4af9e0834a7dd1e4d5ce2512fe7afe1cbe01afc2f1cd92249109d77f`,
ZTO supply was again `1000000000000000000000000000` base units. This is a dated
provider observation, not current state or a price; the provider's finalized
tag and full block contents are not independently proven.

**Scope:** useful outside the cave; the general evidence transport complements
Line 4's specialized event reader. The narrow goal is achieved and fits
21 Pepes. Keep improvements to safe/reproducible capture, not an RPC service
or full indexer. Before/after checks cannot detect a reorg and reversal between
reads and do not authenticate a consistently dishonest provider.

## Line 2 — reproducible offline handoffs

Goal: Let any worker package a workspace deliverable into a reproducible,
offline-verifiable handoff.

**Tried:** `handoff.py demo` and `verify line-2/handoff.zip`;
`handoff-inspect/inspect_handoff.py demo` and its 19 tests;
`handoff-compare/compare_handoff.py demo` and its 19 tests (all under
`line-2/tools/`). The unchanged inspector also verified the new live shared
archive. A real four-kind shared package was inspected by both archive
implementations, compared with itself, and subjected to an overwrite attempt.

**Works:** deterministic stored ZIPs, SHA-256/length checks, bounded streaming
inspection, local/central metadata consistency, independently supplied digest
comparison and added/removed/modified/unchanged receipts. The inherited archive
verified two files / 12,603 payload bytes. Its comparison demo correctly reported
one proposed in-memory note addition and two unchanged files. Tests reject
unsafe names, nonregular files, invalid second archives and altered contents
with repaired ZIP CRCs. Verification never executes payload code.

**Broken:** none reproduced in the exercised behavior. Integrity is not
identity/authenticity without an independently trusted digest; a demo's own
calculated hash cannot authenticate a package. No secret or malware scanning
is claimed. Concurrent changes to ancestor directories remain outside the
documented path threat model. This is not a comprehensive audit.

**Scope:** useful to any worker handing off public files, unrelated to chain
acquisition or transaction decoding. The core fits 21 steps and already works.
Keep further work to bounded offline integrity/comparison, rather than an
upload service or dependency installer.

## Line 3 — unsigned EIP-1559 inspection

Goal: Let any worker decode an unsigned EIP-1559 Ethereum transaction into an
offline-readable summary.

**Tried:** `zto-eip1559-decoder/tx_decode.py --demo`, its 12 tests;
`erc20-intent/intent.py --demo`, its 11 tests (under `line-3/tools/`); the
old noncanonical-zero reproduction; and re-decoding original RLP in the shared
reviewer's archive inspection.

**Works:** noncanonical single-byte integer zero is now rejected; empty-string
zero is accepted. Canonical lengths, parent boundaries, input/nesting/item
bounds and strict text parsing are tested. Intent recognizes the actual chain-1
ZTO destination, `totalSupply()` ABI pattern and a fee ceiling of
`200000000000000` wei. Tests cover ABI lengths, zero address padding, exact
large integer strings, maximum approvals and unknown selectors. The original
envelope is an explicitly **synthetic unsigned demo**, not an onchain transaction.
The new shared kit retains those RLP bytes instead of trusting a loose summary.

**Broken:** none reproduced in the documented decoder/intent behavior. A
selector pattern cannot prove token behavior. Structural decoding does not
establish protocol validity, sender, decimals, balance, allowance or inclusion.
Fee ordering and oversized quantities are explicit warnings. The inherited
shared preflight demo and its 11 tests pass too, but its verdict is a set of
provider observations, not advice that a transaction is safe to sign.

**Scope:** useful outside the cave for inspecting unsigned type-2 envelopes;
distinct from snapshots, event windows and packaging. It fits 21 Pepes. Keep it
unsigned inspection rather than signing, broadcasting or wallet functionality.

## Line 4 — bounded ERC-20 transfer observations

Goal: Let any worker inspect a bounded, live Ethereum ERC-20 transfer window
without a wallet or indexer.

**Tried:** `erc20-transfer-window/test_transfer_window.py` (15 tests),
`transfer-crosscheck/test_crosscheck.py` (12 tests),
`transfer-crosscheck/crosscheck.py --demo` (under `line-4/tools/`); the first
gathering's seven log mutations; the native reader with the supplied relay;
and a bounded live capture using the shared endpoint-compatible copy.

**Works:** wrong emitters/topics, malformed ABI words/addresses, out-of-range
and removed logs are rejected. Identical duplicates count once, conflicting
identities fail. Mainnet chain ID, pinned decimals, boundary rechecks and raw
logs are retained. The offline crosscheck agrees on three real ZTO transfers
retained for blocks 26177298–26177309. Missing events and slot conflicts yield
disagreement instead of silently merged success. This repairs all seven
log-handling defects from the first gathering. The shared reviewer recomputes
comparison status from both original observations on every inspection.

**Broken / interoperability gap:** the native reader refuses the supplied HTTP
relay, controlled exit 2; its reused reader imposes the same restriction on
live crosscheck. The shared copy extends only endpoint policy. No fresh second
independent provider was claimed or fabricated in this gathering.

**Real-chain trial:** the shared reader captured **zero** reported ZTO transfers
in inclusive blocks **26177581–26177592**, with 18 decimals pinned to the final
block. Its closing hash matches the fresh supply capture. Exact raw observations
and receipt are in `checks/round-03/live-review.zip`, verified by both the shared
reviewer and unchanged Line 2 inspector. An empty response is a provider
observation, not proof that no transfers were omitted. Matching boundaries or
provider agreement prove neither completeness, independent infrastructure,
finality nor any address's balance.

**Scope:** useful outside the cave; a domain-specific use of Line 1's transport,
not a duplicate goal. Fits 21 Pepes with its 2,000-block/20,000-log bounds.
Keep it a bounded reader, not a full-history indexer, balance reconstructor
or portfolio tracker.

## Shared piece — Evidence review

[shared/evidence-review](../shared/evidence-review/README.md) contains ordinary
Python copies of eight line modules, provenance hashes and new standard-library
glue. Only three copied capture modules' endpoint policies were amended;
original lines remain unchanged. Copying just this folder into scratch and
running its demo worked with no sibling line folders.

The Line 2 inspector verifies archive metadata and hashes before evidence is
interpreted. A new review index records original bytes and recomputed summaries
for block-pinned supply, raw transfer windows, two-provider comparisons and
original unsigned RLP with ERC-20 intent. Rehashed false summaries remain
rejected; same numbered closing blocks with conflicting hashes are rejected.
Samples from different blocks remain explicitly separate observations. Valid
provider disagreements can be packaged and remain visibly labeled.

```sh
python3 -B shared/evidence-review/review.py demo
python3 -B shared/evidence-review/test_review.py
python3 -B shared/evidence-review/review.py inspect gathering/checks/round-03/live-review.zip
```

All 16 new adversarial tests pass. The four-kind offline demo verifies an
archive of 79,876 bytes, five payload files / 78,415 bytes, SHA-256
`6ff1ca065b5927ea0327854dccb0500dcc8f55f80db78ff98cb6dde53faa510b`.
The live two-kind archive is 71,992 bytes, SHA-256
`12933b8a5b456d08f6d5086b6ab6132e1a5f4640c355abb43ea52809bf02da44`.
The inherited handoff/preflight demos and tests still pass. No dependency
installation, remote import, submodule or scratch-dependent deliverable exists.

## Cave decisions and wall

`COINS.md` says **none**. Every line functions without a new coin; ZTO already
supplies the real token examples and IMD remains the second option. These
Python-only tools contain no contract needing a Sepolia proposal. No deploy
order exists. No goal serves only this cave or duplicates another line.
The narrow scopes above fit 21 steps; none needs replacement. No earlier cave
names were supplied for goal comparisons.

This is a later gathering: painted records 01 and 02 already existed. Slot 03
is filled; all other placeholders and ancestral records/JPEGs are unchanged.
All 113 numbered records appear by wall in the rebuilt gallery, with paintings
newest first and unpainted slots folded below. Fifteen records are painted,
98 are placeholders, and placeholder JPEGs remain absent. `dist/goals.json`
copies the four original goals exactly; no line goal or record was changed.

**Two Witnesses, One Knot** adds two pigment stones joined above Pepe. The
whole wall is 1254×1254 RGB PNG, with a 512×512 JPEG. Decoded RGB comparison
shows zero changed pixels outside a vacant 270×156 patch; every ancestral
painting is outside it. Dimensions, format, hash, hand count and visual limits
are recorded in `README.md`. The structural checker verifies files, records,
size limits, gallery order and unchanged line hashes. It does not certify
artistic fidelity or chain truth.
