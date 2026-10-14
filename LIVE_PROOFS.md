# Proof matrix

Deployed source and bounded live lifecycle verified on StudioNet. Tests and live evidence remain separate.

| Property | Local evidence | Live status |
|---|---|---|
| Independent acquisition | incoming and resident failures, hashes, tamper tests | Incoming and resident sources refetched; wrong-hash input recorded BYPASS |
| Semantic hit protects entry | paraphrase hit changes actual victim from A to B | Distinct-hash paraphrase HIT protected A; C then evicted B |
| Unknown / inconsistent matching | bypass leaves both queues unchanged | Local only |
| Replay | nonce cannot reset receipt or touch queues | Finalized expected ERROR; sequence/head/residency unchanged |
| TTL and public purge | protected lifetime not extended; history preserved | Local only |
| Capacity / demotion | 12,288 complete six-access schedules | Capacity and protected eviction verified; overflow demotion local only |
| Validator substance | extracted actual callback checks fresh observation equality | Real DIFFERENT and SAME/DIFFERENT vectors finalized with majority agreement |

Public fixtures are synthetic document contents, not real-world delivery evidence.

## Matching source

- [StudioNet contract](https://explorer-studio.genlayer.com/address/0x8acF9007220093ab3bbfB02CdE3012C0965882cc)
- [Pinned contract source](https://github.com/stoneforger10/meaning-cache-2q/blob/43fc2d996378d69e448652dbf1eb49b9995b37f7/contracts/MeaningCache2Q.py)
- Source/fixture commit: `43fc2d996378d69e448652dbf1eb49b9995b37f7`.
- Normalized deployed source SHA-256: `9ae18a601dd2e53888d8b7965e32192dffa8febff31605c8bb12511472f53faa`.
- Dedicated encrypted-keystore test signer: `0x7a413BB4AB62E31d62d4cD9efC8C8a8Dae37FB42`.
- Capacity 2, protected capacity 1, retention 518400 seconds. No funds moved.

## Finalized lifecycle proofs

The first six receipts below are FINALIZED / leader SUCCESS / MAJORITY_AGREE.
The seventh is an intentional finalized execution ERROR with `replay` matched.
CLI banners were not used as execution proofs. No unanimous-validator claim.

| Operation | Transaction | Readback |
|---|---|---|
| Deployment | [6c1f74e6](https://explorer-studio.genlayer.com/tx/0x6c1f74e6556f1b612dd55d42b6f097a8eab221a6d20862d3e271d5ce5cfcff2a) | Exact source match; empty two-slot cache |
| A admission | [74349cea](https://explorer-studio.genlayer.com/tx/0x74349ceae6d6ccea0d7c0b30152701d702a04905733a04c274d9bf917391de7b) | Cold MISS; probation `[A]`; no equivalence AI needed for an empty cache |
| B admission | [438d8a98](https://explorer-studio.genlayer.com/tx/0x438d8a98d045acc57b06ac08836e2cb3759dfb0917a14fabf4939200b1241a23) | `[DIFFERENT]`; MISS; probation `[A,B]` |
| A paraphrase | [fc2ef134](https://explorer-studio.genlayer.com/tx/0xfc2ef1341bde9f15af3d2da0acce2b80c8c1d3145ed08709ec089dcbf1fddcd5) | `[SAME,DIFFERENT]`; HIT; protected `[A]`, probation `[B]` |
| C admission | [a6cc134c](https://explorer-studio.genlayer.com/tx/0xa6cc134c8c4793577cdba33057e8150afdbfbb03952512041c55716c5f62b332) | `[DIFFERENT,DIFFERENT]`; evicted B, retained protected A, probation `[C]` |
| Wrong-hash source | [cc9eb1c7](https://explorer-studio.genlayer.com/tx/0xcc9eb1c72de14f2394e2344b5231fc034da9a06f3dab3a55a106e9f2228fd99a) | BYPASS / EVIDENCE_FAILURE; queues unchanged; audit event appended |
| Replay of `first` | [2a0298d8](https://explorer-studio.genlayer.com/tx/0x2a0298d8cdbb5c1816a35e2775543a59df009610414d333565bad744e8313012) | Expected ERROR; still five events and same final head |

The semantic effect is concrete: before the paraphrase hit, A was probation LRU
and would have been evicted by the next miss under the deterministic policy.
Consensus on the differently worded source promoted A, so the next actual miss
evicted B instead. The counterfactual policy is locally tested; the actual protected
eviction and state transitions above are onchain.

## Source commitments and final state

| Pinned fixture | Raw SHA-256 |
|---|---|
| `examples/a.txt` | `411a072754439ccced8d2cf0bb3976aaa9d5b822d04e7d18812b428c9f963cab` |
| `examples/a-paraphrase.txt` | `c7e2d93338859db183a9598b3b8eb59b74dd75e542e23e82f7f933097881acee` |
| `examples/b.txt` | `d3ab945312d49c8d0abf3637c1c8fe455afcbcf691275f52e233c17abd561310` |
| `examples/c.txt` | `04701b52a727819d3d35bf9dc0fd3eff58ccd65c7e991c50b699d2b06c8a7c67` |

- A representative: `a6e0b129a7ce0a5aa834add777667a8bec4452a3aa8b6eea9ea6ee1122d1f08c` (protected).
- B representative: `8c9a78788e6afcf07da7877dd47bca52e27cd20e41c149d393cba4bc522caa10` (evicted; immutable record retained).
- C representative: `e2e7927b3952d8f83fc2de23ac866006ee50ca75efd26f53ee5e79dcc153b28a` (probation).
- Final sequence 5; journal head `9a80985bd3aed13a7d603f451b5f5a81d7808c0ddbe0a2eae685cd0a7db7baea`.

The inspector recomputed the complete hash chain, principal-bound receipt lookups,
admitted-entry roots, source-to-resident bindings, deterministic decision gates,
queue transitions, eviction/demotion fields and final layout. No raw validator
configuration or wallet secrets are included.

## Additional failed attempt, not a BYPASS proof

[2aa7dc56](https://explorer-studio.genlayer.com/tx/0x2aa7dc562eca36301a549d041ab56fe05dd3295d64b86ddeec5c432accb8cfd0)
finalized with execution ERROR and `TypeError`. The first bad-source test used a
digit-only all-zero argument that the CLI passed as an integer rather than a hash
string. The cache remained at sequence 4 with unchanged queues/head. This is not
counted as successful source-failure handling. After verifying failed execution and
unchanged state, the script used a letter-containing wrong hash; the separate
`cc9eb1c7` transaction above exercised the intended BYPASS branch.

## Local validation and unrun live cases

- GenVM lint and SDK semantic validation pass; informational newer-runner warning.
- 25 local tests pass, including 12,288 complete six-access sequences over four meanings.
- 3 GenLayer SDK calldata roundtrips pass.
- Direct tests mock web/AI and run the leader. Actual nested-validator callback tests
  are not a distributed disagreement experiment.
- UNKNOWN, multiple SAME, resident unavailability, identical-text contradiction,
  overflow demotion and TTL purge remain locally tested only.
- The synthetic documents do not establish real production policy or service delivery.
- No production audit, universal model correctness, global novelty or points guarantee.

Read-only verification:

```powershell
node scripts/check.mjs --source 0x8acF9007220093ab3bbfB02CdE3012C0965882cc
node scripts/inspect.mjs 0x8acF9007220093ab3bbfB02CdE3012C0965882cc
node scripts/check.mjs --error 0x2a0298d8cdbb5c1816a35e2775543a59df009610414d333565bad744e8313012 replay
```
