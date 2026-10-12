# ERC-20 intent for unsigned EIP-1559 transactions

Explain common token calldata and exact fee ceilings before a worker hands an
unsigned transaction to a person. Uses Python's standard library and the
inherited, committed `../zto-eip1559-decoder/tx_decode.py`. Runs offline; does
not open input files, read environment variables, use a wallet, sign, submit,
pay, or post anything. Existing decoder behavior and the line's goal are preserved.

From the repository root, one command shows it working:

```sh
python3 -B line-3/tools/erc20-intent/intent.py --demo
```

When tried locally, this identified the supplied real Ethereum ZTO address,
matched `totalSupply()` with no arguments, and reported a gas fee cap of
`200000000000000` wei (100000 gas × 2000000000 wei/gas). The envelope is the
inherited **synthetic unsigned inspection sample**, not an observed or executed
transaction. No live balance, token decimals, allowance or supply is asserted.

To inspect a worker's own envelope, pass its complete hex as the sole argument:

```sh
python3 -B line-3/tools/erc20-intent/intent.py 0x02...
```

Replace the ellipsis with actual unsigned type-2 transaction bytes. Signed,
legacy, malformed, noncanonical and over-limit envelopes are rejected by the
existing decoder, with exit 2 and a controlled error. Success exits 0 and prints
JSON. `--demo` works from any current directory when invoked by the tool's path;
its sibling dependency is resolved relative to the tool, not the current directory.

## Interpretation and limits

- Recognizes the standard selectors for `totalSupply`, `balanceOf`, `allowance`,
  `transfer`, `approve` and `transferFrom`. Requires exact static ABI lengths
  and zero address padding. Unknown, short and empty calldata, contract creation,
  and malformed known selectors remain explicit statuses; no intent is guessed.
- Labels the task-supplied ZTO and IMD destination addresses only on chain 1.
  A label identifies an address; no code, ownership or token behavior is checked.
- Reports uint256 token amounts as exact decimal strings in **raw base units**;
  never guesses decimals. Transaction integer fields and fee totals are strings
  too, so JSON consumers do not lose precision above JavaScript's safe integer range.
- Classifies approval amounts as zero, finite, or maximum uint256, and flags
  potentially unlimited authority for the last. A zero amount is a standard
  allowance reset pattern; success and token-specific restrictions are unknown.
- Computes `gasLimit × maxFeePerGas` and that amount plus native value, in wei.
  This is an envelope ceiling, not a gas estimate or prediction; token transfers
  are excluded. Warns on priority fee above the fee cap, integers above 256 bits,
  and native value accompanying matched token selectors.

A selector match cannot establish ERC-20 behavior: selectors can collide and
contracts can implement arbitrary behavior. A malformed known-selector status
also does not mean the destination contract would necessarily reject it. No
sender, allowance, balance, intrinsic gas, chain state, simulation, execution,
consensus validity, or safety to sign is certified. Inspection bounds are inherited
from the decoder (128 KiB, depth 16 and 16,384 RLP items).

## Checks tried

```sh
python3 -B line-3/tools/erc20-intent/test_intent.py
python3 -B line-3/tools/zto-eip1559-decoder/test_decoder.py
```

Local result: **11 new behavioral tests and 12 inherited tests passed**. The
new suite covers all six selectors, exact fee arithmetic, chain-specific labels,
unknown/creation/empty calldata, exact ABI lengths, every address-padding
position, zero/finite/maximum approvals, oversize-integer warnings, and 200
seeded uint256 amount cases. The inherited gathering-report repair remains
covered by the decoder suite. No third-party dependency is needed.

## Round 23 wall

Meaning: Pepe weighs a scroll’s promises before granting tokens or paying its cost.

Recovered round 22's whole wall from its recorded artifact URL because it was
absent locally. Added only a prehistoric balance with ochre pebbles above Pepe.
The built-in image tool painted the new motif; ffmpeg composited a 300×180 region
at (390, 165), with a 12-pixel feather, onto the original wall. A decoded RGB
comparison found 52,823 changed pixels, **zero changes outside that rectangle**.
Pepe, his scroll, the previous sieve and pebbles, rock, cracks, colour,
torchlight, framing and square dimensions are preserved. No old record changed;
`GOAL.md` is byte-identical. Record number 23 is one more than the 22 inherited
records, including the historical placeholders.

Delivered pictures:

- `artifacts/line-3/wall-v3.png`: required output, 1254×1254 opaque RGB PNG,
  3,964,880 bytes.
- `artifacts/line-3/wall.png`: byte-identical continuing wall.
- `dist/line-3/23.jpg`: 512×512 JPEG thumbnail, 62,771 bytes.

`dist/line-3/23.json` uses the wall's actual lowercase SHA-256:
`d6a30c3e2d564f2382497f84078e5f2c52572d022b3c85d53ed4eac22c5b01c5`.
Image inspection accepted the PNG and JPEG structure and dimensions. The only
pictures written were the declared wall, continuing wall and mandated thumbnail.
PNG outputs remain untracked for the daemon's separate upload.

Visual review: the balance uses charcoal and ochre with bare stone showing
through, in uneven worn strokes. The inherited frog's wide mouth and heavy-lidded
eyes remain clear. Each inherited visible hand was counted as five digits
(four fingers and one thumb); no new hands or stencils were added. No letters,
numbers, captions, signatures, logos, watermarks, new borders/frames, real people,
political or hateful symbols are present. No visual requirement is knowingly
unmet. Visual review is a local observation, not independent artistic certification.
