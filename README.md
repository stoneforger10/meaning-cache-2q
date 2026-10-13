# MeaningCache2Q

Consensus-grounded online semantic working-set cache for GenLayer. Two live queues
implement a segmented-LRU policy: first-use documents enter probation; reuse by a
semantically equivalent document protects the existing representative from eviction.
This is not the full textbook 2Q algorithm: no ghost queue is implemented.

Experimental, unaudited. No tokens, graph proposals, owner finalization, certificates,
capabilities, service-delivery verification or assertions of factual truth.

## Problem / why GenLayer

Applications need a shared bounded working set whose identities survive paraphrase.
Byte equality cannot recognize rewording, and topical similarity can wrongly merge
negations, changed numbers or narrower conditions. A normal contract can enforce
cache replacement, but cannot independently judge complete semantic equivalence.

Here AI consensus changes a material runtime decision: reuse and promotion versus
admission and eviction. The caller cannot submit labels, choose a representative,
select a victim or protect an entry. Validators acquire the complete source bodies
themselves, not provider summaries or caller-provided interpretations.

```text
public pinned source + SHA-256 + authenticated request nonce
 -> independent fetch of incoming AND every unexpired resident document
 -> independent full-meaning comparison vector
 -> exact decision-bearing report agreement
 -> HIT: reuse representative; promote/touch protected queue
    MISS: admit source; evict probation LRU if full
    BYPASS: no reuse, admission, promotion, demotion or eviction
 -> immutable request journal + bounded working-set state
```

## Mechanism comparison

This is an online replacement policy, not a domain-renamed graph transition or
an immutable batch index. Semantic equivalence is a shared subroutine also used
by deduplication systems; no invention of semantic equality or segmented LRU is
claimed. Unlike SemanticQuotientIndex, requests arrive separately over time and
alter residency, promotion, demotion and eviction. Unlike SemanticYieldAllocator,
there are no arm statistics, reward learning or next-trial allocation.

## State transitions

```text
nonresident --distinct access--> probation MRU
probation --equivalent access--> protected MRU
protected --equivalent access--> protected MRU (touch)
protected overflow --> demote protected LRU to probation MRU
full + distinct access --> evict probation LRU; admit at probation MRU
expired --> permissionless purge, or prune on next successful HIT/MISS
uncertain / failed acquisition / inconsistent equivalence --> BYPASS; queues unchanged
```

Queue order is LRU to MRU. Protected capacity is `floor(capacity/2)`, leaving at
least one probation slot. Entry expiration is fixed at admission and never extended
by a hit. Historical entries and request receipts remain readable after eviction
or expiry. Residency is bounded; total audit history is **not** bounded or erased.
This coordinates canonical working sets; it does not promise reduced chain storage,
lower inference costs or faster HTTP responses.

## Consensus and deterministic guards

The adapter constructs a GitHub raw HTTPS URL using a full commit SHA and restricted
path segments. Every request independently fetches the incoming document and all
unexpired resident sources, checks full-response SHA-256, HTTP 200, UTF-8 and size.
No truncation is silently accepted. Models compare complete normalized bodies,
including conditions, quantities, modality, scope and negation.

Leader and validators independently reproduce `SAME / DIFFERENT / UNKNOWN` per
resident. Exact equality covers the request and principal, deadline, before-layout,
resident identities, source URLs/statuses/hashes/full text, entire label vector and
derived HIT/MISS/BYPASS decision. No confidence tolerance or schema-only validation.

Any UNKNOWN blocks all reuse and mutation of queues. Two SAME results for separate
representatives fail closed as inconsistent equivalence; they cannot select an
arbitrary winner. Identical full text judged non-SAME also bypasses. The deterministic
block recomputes these gates before applying the queue algorithm. Malformed AI
output or distributed disagreement rolls back; it is not a fabricated stored conflict.

## Security boundary

An exact source commitment establishes which document was compared, **not** who is
truthful or whether anything happened outside the source. The public fixtures are
synthetic propositions, not proof of operational compliance or service delivery.
All text is treated as untrusted data; prompt injection and correlated model error
remain risks. No universal correctness, production safety or reviewer acceptance
is promised. See [SECURITY.md](SECURITY.md).

The cache is public and can suffer Sybil churn. Every caller has 64 access nonces;
this is a bound, not Sybil resistance. No privileged owner can arbitrarily replace
an entry. Any unavailable resident source blocks semantic reuse/admission until
its fixed TTL expires or the source recovers. Public purge prevents permanent
expiry locks; no credits or funds can be stranded.

Freshness means refetch during the request, execution before its deadline, and
resident TTL eligibility. A pinned historic document is not proof of current facts.

## API

Constructor: `MeaningCache2Q(capacity, retention_seconds)`; capacity 2–4, retention
60–604800 seconds. UTF-8 documents: 20–4096 raw bytes, 20–2000 normalized characters.

- `access(nonce, owner, repo, commit, path, expected_hash, deadline)` — one atomic access.
- `purge()` — anyone, only when some resident has expired.
- `get_cache`, `get_entry`, `get_event`, `get_receipt`, `request_key` — read-only inspection.

Request identity binds the contract, authenticated creator and nonce. Replays fail
before acquisition, and a completed nonce cannot be overwritten. Every access and
purge appends a hash-linked before/after journal event. No consumable certificate exists.

## Install / test

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/genvm-lint check contracts/MeaningCache2Q.py --json
.venv/Scripts/python -m pytest tests -q
npm ci --ignore-scripts
npm run check:sdk
npm install -g genlayer@0.39.2
```

Direct tests mock web/AI and execute the leader, not a distributed validator network.
Actual nested-validator callback tests independently invoke observation and reject
changed labels, source bodies/hashes, request bindings and decisions. 12,288 complete
six-access sequences exercise the queue kernel across capacities 2, 3 and 4. The
Windows test shim only defers the runner's open-message-temp-file unlink.

## Deploy / demo

```powershell
genlayer network set studionet
genlayer account use YOUR_ENCRYPTED_TEST_KEYSTORE
genlayer account unlock
genlayer deploy --contract contracts/MeaningCache2Q.py --args 2 518400
```

First commit/push fixtures and calculate their raw SHA-256. All accesses use that
full published commit. Do not substitute a mutable branch URL.

```powershell
$deadline=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()+518400
genlayer write ADDRESS access --args first stoneforger10 meaning-cache-2q FULL_COMMIT examples/a.txt RAW_A_SHA256 $deadline
genlayer write ADDRESS access --args second stoneforger10 meaning-cache-2q FULL_COMMIT examples/b.txt RAW_B_SHA256 $deadline
genlayer write ADDRESS access --args reuse stoneforger10 meaning-cache-2q FULL_COMMIT examples/a-paraphrase.txt RAW_PARAPHRASE_SHA256 $deadline
genlayer write ADDRESS access --args third stoneforger10 meaning-cache-2q FULL_COMMIT examples/c.txt RAW_C_SHA256 $deadline
node scripts/inspect.mjs ADDRESS
```

Inspect each FINALIZED receipt's expected execution result and read state before
sending the next write. A CLI success banner alone is not proof. After A, B, a
paraphrase of A, C: A should be protected and B evicted. Without the semantic hit,
A would have been the victim. This is the consequential AI effect to verify live.

`check.mjs --source ADDRESS` compares normalized Explorer source with the local
contract. `--success HASH` verifies finalized leader success and majority agreement;
`--error HASH EXPECTED_TEXT` verifies an intentional execution error. Do not print
raw Studio receipts: they may include sensitive validator configuration.

The optional one-shot signed-payload transport never exports keys and caches unknown
failures as well as successes within its process. Never restart a failed broadcast
without inspecting the receipt or wallet history. StudioNet is gasless; no funding.
See [LIVE_PROOFS.md](LIVE_PROOFS.md) for verified evidence, not planned transactions.
