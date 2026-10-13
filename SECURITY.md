# Security model

Unaudited experimental infrastructure. No money, native value or remote execution.
Do not use semantic matches as proof of fact, service delivery, legal permission,
clinical safety or actor honesty. Source publishers control their document contents.

## Enforced properties

- One atomic authenticated access, immutable principal/contract/nonce binding.
- No caller label, source summary, selected representative, protection flag or victim.
- Independent refetch of **all material documents**, including cached evidence.
- Full raw hashes, strict UTF-8, bounded complete bodies, no truncation.
- Exact independent label and full-report equality; unknown or inconsistent matching bypasses.
- Two SAME matches or identical-text/non-SAME disagreement cannot authorize reuse.
- Fixed admission TTL; hits cannot extend retention; public expiry purge.
- Incoming and resident source failures cannot evict, promote or admit anything.
- Immutable entry records, receipts and hash-linked journal; no history reset.
- Fixed public GitHub raw host and full commit; no arbitrary endpoints, branch refs,
  traversal, query/fragment, credential-bearing URL or caller HTTP headers.
- 2–4 residents, protected size at most floor(capacity/2), no duplicate resident roots.
- 64 completed requests per principal; network-level resource limits remain necessary.

## Residual risks

- Open access has no Sybil resistance or anti-churn admission fee; not a production public cache.
- An unavailable resident source can block reuse until recovery/TTL, even if stored bytes remain.
- Prompt injection and correlated model error can produce wrong SAME/DIFFERENT judgments.
  Exact validator agreement is not a proof of correctness. No numerical confidence is accepted.
- Unknown/model failure can reduce liveness. Fail-closed behavior intentionally sacrifices hits.
- Historic document identity and cache TTL do not prove publication freshness or current truth.
- Residency is bounded, but onchain historical entries and reports grow and are never deleted.
  Purging is not a privacy-erasure promise or a total-storage compression mechanism.
- Transactions may be ordered to affect LRU order. Source integrity and nonce binding persist;
  no fairness guarantee or chain-independent proof-root interpretation is provided.
- Stored receipts are audit records, not certificates or bearer permissions.

Report reproducible issues privately to the repository owner. Never include wallet
credentials, tokens, password material or raw validator configuration in reports.
