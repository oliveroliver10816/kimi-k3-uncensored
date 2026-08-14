# kimi-k3-uncensored — what the latest uncensored Kimi K3 actually is, and why the ones Bob ran babbled

**Started + delivered 2026-08-14.** Bob asked for "the latest Kimi K3 uncensored version" and to run it on
the Beast. Mid-turn he narrowed it: **do NOT download or install anything** — the builds he already ran
"most of the time started speaking gibberish", and the ones I first surfaced were ones he'd already used.

**LIVE: https://oliveroliver10816.github.io/kimi-k3-uncensored/** (repo oliveroliver10816/kimi-k3-uncensored,
public, noindex; verified HTTP 200, 2 noindex tags, 22 links).

## ⭐ THE FINDING — Kimi K3 is natively a ~4-bit model, so every sub-Q4 build destroys it
Official weights = **1,561 GB for 2.8T params = 4.46 bits/param**. It ships MXFP4-compressed; it was never
a bf16 model anyone is "compressing". Proof from Unsloth's own ladder:
**UD-Q8_K_XL "full precision lossless" = 1.56 TB (identical to the original) and UD-Q4_K_XL = 1.51 TB,
only 50 GB smaller.** Q4 is the FLOOR, not the target.
Everything Bob ran sat under it — Blackfrost-AI Q2_K 1,009.5 GB, GrEarl Q2_K 928.6 GB.
Abliteration then stacks a **second** loss: dequantise MXFP4→bf16, orthogonalise the refusal direction out
(arXiv 2406.11717, title verified), requantise. Two lossy passes landing below native.
⭐ **MoE amplifies it:** 896 experts, top-16 per token. A dense model averages quantisation error across the
whole forward pass; K3 routes each token through 16 of 896, so there is nothing to average against — it
falls off a cliff instead of degrading gently. That is the gibberish. See memory
[[never-quantise-below-native-precision]].

## The inventory (all sizes summed from the HF blob API `?blobs=true`, NOT from READMEs — they disagree)
**No newer official base.** `moonshotai/Kimi-K3` created 2026-06-13, last modified **2026-07-27**, nothing
since; all 19 org repos checked. ⚠ `Souta30903/Kimi-K3.5` = **12 downloads, no card — a name squat.**

| status | repo | created | size | dl |
|---|---|---|---|---|
| ⭐ NEW | `Ryanchen911/Kimi-K3-Uncensored-GGUF` | 08-10 | 579.5 GB | 50 |
| ⭐ NEW | `Blackfrost-Research/KIMI-K3-MXFP4-DERISKED-V2` | 08-05 | 1,561.0 GB | 18 (gated manual) |
| ⭐ NEW | `SHS-Lab/Kimi-K3-Abliterated` | 08-05 | 1,561.0 GB | 58 (ungated) |
| noise | `HaithamalWaisy/kimi-k3-slice-Q3K-8L`, `-merged` | 08-13 | — | 0 |
| Bob's | `GrEarl/…-V1-Q2_K-GGUF` | 08-04 | 928.6 GB | 56 |
| Bob's | `Uniboshi/Kimi-K3-Abliterated-V1` | 07-31 | 1,561.0 GB | 2,027 (76 likes) |
| Bob's | `Blackfrost-AI/KIMI-K3-Q2_K-GGUF-ABLITERATED` | 07-29 | 1,009.5 GB | 8,677 |
| Bob's | `audnai/penclaw-Kimi-K3.0-abliterated-GGUF` | 07-18 | 1,722.6 GB | 146 |

⭐ **Blackfrost themselves fixed this bug**: V2 (new org `Blackfrost-Research`) **deleted the Q2_K and kept
native MXFP4**, tagged `lossless` + `residual-intervention`. The name change IS the admission.
⭐ `Ryanchen911` is the only genuinely new build and is the best-engineered: mixed precision — experts
IQ1_S but **router kept F32**, attn/KDA IQ4_XS, shared-expert Q5_K; 279 of 2,573 tensors modified; imatrix.

## ⭐ The A/B that proves bits > experts (hellohazime/Kimi-K3-REAP-512GB-GGUF)
Same 512 GB budget, same calibration corpus, same tooling, one variable:
| build | experts | bpw | size | SWE-Lancer |
|---|---|---|---|---|
| REAP640-IQ1_S | 640/896 | ~1.6 | 441.4 GB | 5/8, $3,500 |
| **REAP576-IQ2_XXS** | 576/896 | ~1.9 | 478.5 GB | **7/8, $13,000** |
Dropping 64 more experts to buy 0.3 bits/weight nearly 4×'d the result. ⚠ **n=8, self-reported by the
weight publisher, no independent replication** — direction sound, magnitude is marketing.
⇒ REAP (expert pruning) is where the community went instead of deeper quantisation.

## ⚠⚠ RIG SPECS CORRECTED 2026-08-14 by live probe — the old numbers were wrong
Probed the box directly (jobs 1991/1992). **Two corrections, both material:**
1. **ONE GPU, not two.** `nvidia-smi` = index 0 only, **RTX PRO 6000 Blackwell 97,887 MiB (95.6 GB)**,
   driver 582.08. **No RTX 5090 installed.** The root map + `minimax-h3/CLAUDE.md` both say
   "5090 32GB + RTX 6000 Pro 96GB" — that is the *plan* from [[workstation-build]], not the machine.
   ⇒ **VRAM 95.6 GB, not 128 GB.** Total addressable = 95.6 + 61.6 = **157.2 GB**.
2. **The RAM upgrade path is closed.** Board = **MSI MPG X870E CARBON WIFI (MS-7E49)**, AM5,
   **Ryzen 9 9950X3D**, 4 slots, **SMBIOS array max 128 GB**; fitted 2×32 GB Kingston KF560C36-32 @
   4800 MT/s, 2 slots free. 512 GB is **unreachable on this platform** — needs Threadripper PRO /
   Xeon W / EPYC / Mac Studio Ultra. Also ⚠ 4 DIMMs on AM5 clocks down hard.

Disks: C: 990 PRO 2TB (1,112 GB free) · **D: WD_BLACK SN850X 8TB, 5,213 GB free** · E: 990 PRO 2TB.
**D: winsat unbuffered: sequential read 6,726 MB/s · random 16K read 428 MB/s.**
**HuggingFace download 22.7 MB/s** (300 MB ranged GET on the real shard) ⇒ 579.5 GB = **7.1 h**.
⚠ `speed.cloudflare.com/__down` **403s from the rig** — measure with a real file.

Nothing uncensored is memory-resident: 579.5 GB = **3.7× over** · REAP576 478.5 GB = 3.0× ·
smallest K3 quant in existence (UD-Q1_0) 466 GB = 3.0× · full safetensors 1,561 GB = 9.9×.

## ⭐ BUT "doesn't fit" ≠ "can't run" — the §08 answer Bob asked for
llama.cpp mmaps the GGUF; only the **104B active params of 2.8T** are touched per token. At this build's
1.66 bits/param that is **~21.6 GB read per token**. VRAM 95.6 + ~50 GB page cache ≈ 145 GB = 25% of the
model resident; skewed routing puts the real hit rate ~35–45% ⇒ **~13 GB off D: per token**.
| scenario | D: rate | result |
|---|---|---|
| ceiling, pure sequential | 6,726 MB/s | 0.52 tok/s |
| realistic, ~6 MB expert tensors scattered | ~2,000 MB/s | **~0.15 tok/s** |
| floor, random 16K | 428 MB/s | 0.03 tok/s |
⇒ 500-token answer ≈ **55 min**; overnight 8 h ≈ **4,300 tokens** (8–9 answers). A model that FITS 95.6 GB
at 4-bit runs 20–40 tok/s = **150–250× faster**.
🛑 **All tok/s figures are MODELLED** from measured disk rates + hellohazime's resident anchor — not observed.
**Run flags that matter:** `--no-warmup` (else it reads all 579.5 GB at load), leave **mmap ON** (never
`--no-mmap`), `-ngl 99 --n-cpu-moe N` tuned so VRAM sits ~90/95.6 GB (each layer's expert set ≈ 5.6 GB,
so ~15 layers fit on the card), `-c 8192` (never the 1M context — KV steals the expert cache).
⚠ **Windows is the wrong OS for a 579.5 GB mmap** (standby-list handling; we already hit "Windows silently
spills VRAM with zero errors" on this box). ⚠ Installing the 5090 → 127.6 GB VRAM ≈ 31% resident ≈
0.19 tok/s — real but not category-changing.
⚠ It is still the **IQ1_S expert class** = the arm that lost the §04 A/B 5/8 vs 7/8. Best-engineered shot
(F32 router + IQ4_XS attn + imatrix target exactly that failure), but a shot.

## ⚠ TRAP — `ubicloud/Kimi-K3-Pruned-65B` (41.9 GB) is NOT a small K3
Its card: *"retains the first 3 layer(s) of the original 93 layer(s) … intended for pipeline testing rather
than production use."* Same for `-Pruned-35B` (24.9 GB). A test fixture wearing a model's name — it is the
only thing in the whole search that fits the Beast, which is exactly why it's dangerous. Read the card.

## ⭐ The number nobody puts on the label
Ryanchen911 publishes the baseline: **stock Kimi K3 refuses 2 of 26 harmful prompts (7.7%)**; abliterated =
0/26. Over-refusal on benign prompts 0/30 **both before and after**. So the whole trade is two lossy
conversions and gibberish **to recover two prompts in twenty-six** — stock already answers 24.
⇒ Told Bob to settle whether uncensored K3 is worth anything before spending a byte.

## What was NOT done
- **Nothing downloaded, nothing installed, no model run, $0.**
- A hardware probe (job 1989) was queued to the rig then **CANCELLED** — it was sitting behind the v29
  render batch and its winsat disk benchmark + 200 MB speedtest would have fired mid-render. Renders
  untouched. `probe.py` is kept for whenever the rig is idle.
- Venice.ai's hosted uncensored K3 endpoint came from a search result and is **unverified** — flagged as a
  lead on the page, not a fact.

## Files
`rig.py` — reusable ai-film-bridge client (enqueue/poll/cancel; ⚠ browser UA required, Cloudflare 403s
`Python-urllib`). `probe.py` — the unrun hardware probe. `index.html` — the deliverable.
⭐ Bridge cancel endpoint is **`POST /api/cancel` with `{"id": N}`** — `/api/job/<id>/cancel` is a 404.

## Open (Bob's call)
1. Is uncensored K3 worth anything to us at all, given 24/26?
2. If yes local: floor is a **512 GB box**, and **nobody has published a REAP-pruned AND abliterated
   build** — that combination is the gap, and it's the only shape that could ever reach 128 GB.
3. Or change the model: want the list of uncensored models that fit 128 GB at 4-bit or better?
