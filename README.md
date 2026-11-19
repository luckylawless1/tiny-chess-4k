# Tiny Chess 4K

A complete chess engine in a single `main.py` of **4,030 bytes**, built for
the make.fun bounty [tiny-chess-01](https://make.fun/bounty/tiny-chess-01).
The readable source (~11.9 KB) is minified and LZMA-packed into the file;
at startup it decompresses and executes itself in memory. Python 3 stdlib
only; no other repo file is read.

## How it plays

- **Board**: 0x88 mailbox with incremental make/unmake — material, tapered
  phase, pawn bitboards and a zobrist key (seeded PRNG constants) are
  maintained incrementally. Full rules: castling, en passant, promotions,
  check/stalemate, repetition and 100-ply draws.
- **Search**: negamax alpha-beta with PVS, iterative deepening under a
  fixed budget of 55,000 nodes per move (never wall-clock, so replays are
  move-identical), transposition table, null-move pruning, check
  extensions, and quiescence folded into the main search (captures,
  promotions, check evasions). Ordering: TT move, MVV-LVA, promotions.
- **Evaluation**: PeSTO tapered piece-square tables blended by phase,
  quantized to fit, plus passed-pawn bonuses from pawn-span masks.

Local practice vs the kit gauntlet: Elo 1451 / 1654 / 1451 on trials
0 / 1 / 2; 6 wins in a local 8-game final-style gauntlet, including wins
over the nodes-1M and nodes-2M house engines.
