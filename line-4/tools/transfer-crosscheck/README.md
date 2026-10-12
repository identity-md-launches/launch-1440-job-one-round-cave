# Transfer crosscheck

Compare one bounded ERC-20 transfer window through two public Ethereum RPC
providers. ZTO is the default; IMD is available with `--token imd`. This companion
uses the ancestor's validated reader, fixes the same inclusive block range for
both providers, and compares token identity, pinned decimals, boundary hashes,
and every decoded event. It reports events seen only on one side and conflicting
events occupying the same block/log position. Each capture is revalidated from
its raw logs before its summary is trusted. Duplicate delivery and log order do
not create false differences.

One command to see it work **offline**, with no installation:

```sh
python3 -B line-4/tools/transfer-crosscheck/crosscheck.py --demo
```

Tried on 2026-10-12: it returned `agreement` for three real ZTO transfers in
blocks 26177298–26177309. `publicnode.json` and `drpc.json` are unchanged copies
of round 22's dated public-chain observations, not synthetic demo transactions.
The output retains both complete captures so the result can be inspected offline.
Python's standard library is the only dependency. Run from the repository root;
keep the sibling `erc20-transfer-window/` directory with this tool.

For a new observation:

```sh
python3 -B line-4/tools/transfer-crosscheck/crosscheck.py
```

This first observes PublicNode's mainnet head, chooses a 12-block window ending
12 blocks below it, then reads that exact range separately from PublicNode and
dRPC. Each reader checks its own head, mainnet chain ID and boundary stability.
The confirmation distance reduces moving-head races; it does not certify finality.
`--blocks 24 --confirmations 32` adjusts the selection. An explicit historical
range uses `--from-block N --to-block M` (1–2000 inclusive blocks). `--left-rpc`
and `--right-rpc` accept different credential-free public HTTPS RPC URLs.
Different URLs do not prove independent infrastructure.

Exit codes: **0** means agreement, **1** means valid observations disagree,
**2** means invalid arguments, malformed evidence, reorg detection, resource
limits or provider failure. A provider error is never converted to an empty
successful window; partial success does not produce an agreement report.
Disagreements preserve both sides instead of silently merging them. No wallet,
key, environment variable, transaction signing or broadcasting is used. The
transport makes JSON-RPC POST requests solely for the ancestor's allowed public
read methods, with its dedicated User-Agent.

The live default command returned agreement for **zero** ZTO transfers in blocks
**26177570–26177581**, captured at **2026-10-12T16:29:28Z** and
**2026-10-12T16:29:37Z**. `live-zto.json` retains those two actual observations.
An agreed empty window is still only two provider observations. Agreement cannot
prove completeness, provider independence, finality, or an address's balance.
This tool inspects a window; it does not reconstruct balances or build an indexer.

Validation command:

```sh
python3 -B line-4/tools/transfer-crosscheck/test_crosscheck.py
```

All twelve offline tests passed: real three-event agreement; missing events;
conflicting contents; boundary disagreement; duplicate and ordering invariance;
malformed saved summaries; removed raw logs; same-provider refusal; and range
differences; fixed range selection across both live reads; and no agreement
output after a second-provider failure. The ancestor's 15 regression tests also passed. Mutated fixture
values in the tests are explicitly adversarial examples, never submitted as live
evidence.

A fresh attempt to read the older three-event demo range through PublicNode
returned HTTP 403 and controlled exit 2. No comparison JSON was emitted. This
provider access limit does not turn the retained real observations into invented
events, and does not imply the historical range has zero transfers.

The accompanying wall mark is **Twin Witness Trails**: Two ochre trails share a
chalk loop as Pepe checks one window with two witnesses. Image dimensions,
format, preservation checks and visual limitations are recorded in
`line-4/round-23-image-review.json` and `line-4/ROUND-23.md`.
