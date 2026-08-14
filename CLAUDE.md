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

## ⚠ The Beast does not fit it — and the gap cannot be quantised away
96 GB (RTX PRO 6000) + 32 GB (5090) = 128 GB VRAM + 61.6 GB RAM = **189.6 GB addressable** (specs measured
2026-08-04, `minimax-h3/CLAUDE.md`). D: 5.3 TB free — storage was never the constraint.
- newest uncensored 579.5 GB = **3.1× over** · best REAP 478.5 GB = 2.5× over
- **smallest K3 quant that exists at all (UD-Q1_0) 466 GB = 2.5× over** — and that rung IS the gibberish zone
- full abliterated safetensors 1,561 GB = 8.2× over
⚠ Second wall: hellohazime measures **~3.0 tok/s decode** for a 478 GB build *fully resident* in 512 GB
unified memory (Mac Studio M3 Ultra). Streaming off NVMe is far worse.

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
