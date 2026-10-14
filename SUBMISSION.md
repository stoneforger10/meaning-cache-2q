# Contribution form

Contribution Type: Builder → Intelligent Contracts

Contribution Date: 2026-10-13 (actual work date; do not backdate)

## Title (56/80)

MeaningCache2Q — Source-Grounded Semantic Cache Eviction

## Notes / Description (987/1000)

```text
MeaningCache2Q is a reusable online semantic working-set cache. Each access binds a public Git commit and SHA-256. The contract fetches incoming and all unexpired resident documents; callers cannot provide labels, representatives or eviction choices.

Leader and validators independently judge complete meaning equivalence and must exactly reproduce the full evidence/decision report. UNKNOWN, inconsistent matches and acquisition failures bypass without changing residency.

A semantic HIT reuses and protects a representative. A MISS admits a document and evicts probation LRU when full. Protected overflow demotes its LRU. Fixed TTLs never extend on hits; expiry purge is public. Principal/contract-bound nonces and immutable hash-linked journals prevent replay and history resets.

StudioNet proofs show a paraphrase protecting A so C evicts B, bad evidence preserving queues, and replay rejection. Synthetic fixtures compare document meaning, not factual truth or delivered service.
```

## Evidence URLs

Paste one URL per evidence field. Prioritize repository, source, proof ledger,
Explorer contract, semantic HIT, protected eviction and replay if slots are limited.

- [GitHub repository](https://github.com/stoneforger10/meaning-cache-2q)
- [Contract source](https://github.com/stoneforger10/meaning-cache-2q/blob/43fc2d996378d69e448652dbf1eb49b9995b37f7/contracts/MeaningCache2Q.py)
- [README](https://github.com/stoneforger10/meaning-cache-2q/blob/main/README.md)
- [Complete proof ledger](https://github.com/stoneforger10/meaning-cache-2q/blob/main/LIVE_PROOFS.md)
- [Explorer contract](https://explorer-studio.genlayer.com/address/0x8acF9007220093ab3bbfB02CdE3012C0965882cc)
- [Deployment](https://explorer-studio.genlayer.com/tx/0x6c1f74e6556f1b612dd55d42b6f097a8eab221a6d20862d3e271d5ce5cfcff2a)
- [Semantic paraphrase HIT](https://explorer-studio.genlayer.com/tx/0xfc2ef1341bde9f15af3d2da0acce2b80c8c1d3145ed08709ec089dcbf1fddcd5)
- [Protected eviction](https://explorer-studio.genlayer.com/tx/0xa6cc134c8c4793577cdba33057e8150afdbfbb03952512041c55716c5f62b332)
- [Bad-source BYPASS](https://explorer-studio.genlayer.com/tx/0xcc9eb1c72de14f2394e2344b5231fc034da9a06f3dab3a55a106e9f2228fd99a)
- [Expected replay rejection](https://explorer-studio.genlayer.com/tx/0x2a0298d8cdbb5c1816a35e2775543a59df009610414d333565bad744e8313012)

## Evidence limits

Six successful finalized lifecycle receipts and one expected replay error are
verified. One earlier CLI argument-type failure is separately disclosed and is
not a BYPASS proof. UNKNOWN, overflow demotion and TTL purge are local-only tests.
Fixtures are synthetic public document contents. No truth/service certification,
production security audit, full textbook 2Q implementation, globally new invention,
review acceptance or points award is claimed.
