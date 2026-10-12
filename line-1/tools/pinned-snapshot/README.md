# Pinned Snapshot

Capture a portable, offline-readable ZTO `totalSupply()` observation with Ethereum mainnet chain ID, full block responses, block number and hash. Standard-library Python only. Keep the sibling `rpc-snapshot` folder alongside this one: its explicit read-only request and JSON-RPC response validators are reused unchanged.

One command anyone can run from the repository root, without network access:

```sh
python3 -B line-1/tools/pinned-snapshot/pinned_snapshot.py inspect < line-1/tools/pinned-snapshot/example-zto.json
```

This prints the included real observation's block number, block hash, ZTO address and exact supply in base units. The capture succeeded through PublicNode at `2026-10-12T16:02:50Z`: block `26177368`, hash `0xf76539e08b42037cad963c2af646774753fce06ad37245bd1487b9e6ffa549ba`, supply `1000000000000000000000000000` base units. These are dated provider observations, not current state or a price. The full original block responses and call result are preserved in `example-zto.json`; no test fixture replaces the live example.

To capture fresh public data (JSON goes to stdout):

```sh
python3 -B line-1/tools/pinned-snapshot/pinned_snapshot.py capture
```

Optional `--rpc https://eth.drpc.org` selects the other public provider. `--block` accepts a canonical hexadecimal block number or a supported block tag; the default is `finalized`. `pending` is rejected because it has no stable block identity. Providers can refuse older state or unsupported tags; failures exit 1 with a controlled error and no snapshot.

The capture makes four read-only RPC calls: chain ID, block at the requested tag, ZTO supply at that block's **explicit number**, and the block again at that number. It requires Ethereum chain ID `0x1`, valid block identity fields and a 32-byte ABI uint256 supply. Changed block hashes, mismatched requested numbers, malformed results, malformed JSON-RPC envelopes and oversized responses are rejected. The combined snapshot is limited to 4 MiB so the offline inspector can read every successful capture. Each network request has a 20-second timeout and a dedicated User-Agent.

The offline inspector checks the saved chain, request, ZTO destination, selector, explicit block number and before/after identity, then computes quantities exactly using Python integers. It does no networking. Eleven new tests passed, including a simulated reorg, wrong-chain early stop, wrong-block early stop, malformed supply, tampered call context, forbidden method, controlled CLI failures, response bounds and combined snapshot bounds. The ancestor's six regression tests also passed.

```sh
python3 -B line-1/tools/pinned-snapshot/test_pinned.py
```

Limits: this is provider evidence, not cryptographic proof or independent corroboration. The provider's `finalized` tag is not independently verified. Calling by block number plus before/after hash checks detects observed changes; a reorg and reversal between reads can escape detection. A dishonest provider or consistently edited bundle can pass structural checks. Extra block fields are retained as evidence but are not exhaustively validated. No signing, broadcasting, secret access or deployment is involved.

## Round 23 wall

Meaning: Two linked stones bind a fleeting observation to a particular block.

The generated charcoal mark was added in vacant rock to the left of Pepe. The required output `artifacts/line-1/wall-v3.png` and continuing wall `artifacts/line-1/wall.png` are identical 1254×1254, 8-bit RGB PNGs, 3,838,442 bytes each. `dist/line-1/23.jpg` is a 512×512 baseline JPEG, 70,677 bytes. Both formats were decoded successfully by the image inspection tool. The numbered record references the PNG's actual SHA-256 artifact URL. There were 22 existing JSON records, including inherited placeholder slots, so the new record is 23; none were edited.

The wall was recovered from record 22's artifact URL and its digest checked. Codex built-in image generation through the assignment's installed image tool produced a pigment insert. Standard-library Python removed the white background in memory and composited only dark charcoal into a 175×95 patch at (230,510). The intermediate insert was overwritten by the finished wall; no additional picture was saved. All pixels outside this patch were checked identical to the ancestor wall. Ancestor Pepe and the eye/shield are outside the patch and remain untouched. The JPEG conversion uses the existing, read-before-use `gathering/make_thumbnail.py` functions.

Visual review: square framing, warm rock, cracks, torchlike light, broad-mouthed heavy-lidded Pepe, ancestral paintings and bare stone are retained. Pepe's inherited hands each have four finger strokes and one opposing thumb, five digits per hand. No hands were added. No letters, numbers, captions, signatures, logos, watermarks, frames, people or prohibited symbols were added. No visual requirement is knowingly unmet. The new mark is intentionally small and worn; inherited geometric strokes are preserved rather than repainted.

Final generation prompt: “A pigment insert for a prehistoric cave painting: two irregular small stones joined by one short cord, symbolizing fixing an observation to a particular stone. Centered simple spare burnt-stick charcoal outline, hand-made uneven worn strokes, each stone roughly oval with a small charcoal dot within, no perspective. Only charcoal black on pure white flat background. Occupy middle half of canvas. No text, letters, numbers, symbols resembling writing, logos, watermark, border, people, animals, hands. Lascaux cave pigment aesthetic. This insert will be composited into vacant rock while preserving the existing cave wall.”
