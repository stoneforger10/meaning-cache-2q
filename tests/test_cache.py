import ast
import hashlib
import itertools
import json
import re
from pathlib import Path
from types import SimpleNamespace
import pytest

TREE = ast.parse(Path('contracts/MeaningCache2Q.py').read_text())
NS = {'json': json, 'hashlib': hashlib, 're': re, 'LABELS': ('SAME', 'DIFFERENT', 'UNKNOWN')}
exec(compile(ast.Module(body=[n for n in TREE.body if isinstance(n, ast.FunctionDef)
     and n.name not in ('clock', 'no_value')], type_ignores=[]), '<actual-helpers>', 'exec'), NS)
NOW = 1791892800


def addr(value):
    return '0x' + value.hex() if isinstance(value, bytes) else str(value)


@pytest.fixture
def cache(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.warp('2026-10-13T12:00:00Z')
    return direct_deploy('contracts/MeaningCache2Q.py', 2, 3600)


def access(c, vm, nonce, file, labels=None, bad=False, body=None, status=200):
    vm.clear_mocks()
    for name in ('a', 'a-paraphrase', 'b', 'c'):
        raw = Path(f'examples/{name}.txt').read_bytes()
        vm.mock_web(r'.*/' + name + r'\.txt', {'status': status if name == file else 200,
                    'body': body if name == file and body is not None else raw})
    if labels is not None:
        vm.mock_llm(r'(?s).*MEANING CACHE.*', json.dumps({'labels': labels}))
    sha = '0' * 64 if bad else hashlib.sha256(Path(f'examples/{file}.txt').read_bytes()).hexdigest()
    c.access(nonce, 'stoneforger10', 'meaning-cache-2q', 'a' * 40, f'examples/{file}.txt', sha, NOW + 6000)


def receipt(c, alice, nonce):
    return c.get_receipt(addr(alice), nonce)


def test_semantic_hit_protects_actual_eviction_victim(cache, direct_vm, direct_alice):
    access(cache, direct_vm, 'first', 'a')
    a = receipt(cache, direct_alice, 'first')['representative']
    access(cache, direct_vm, 'second', 'b', ['DIFFERENT'])
    b = receipt(cache, direct_alice, 'second')['representative']
    assert cache.get_cache()['probation'] == [a, b]
    access(cache, direct_vm, 'reuse', 'a-paraphrase', ['SAME', 'DIFFERENT'])
    hit = receipt(cache, direct_alice, 'reuse')
    assert hit['outcome'] == 'HIT' and hit['representative'] == a
    assert hit['sources'][0]['hash'] != hit['sources'][1]['hash']
    assert cache.get_cache()['probation'] == [b] and cache.get_cache()['protected'] == [a]
    access(cache, direct_vm, 'third', 'c', ['DIFFERENT', 'DIFFERENT'])
    miss = receipt(cache, direct_alice, 'third')
    c = miss['representative']
    assert miss['evicted'] == b
    assert cache.get_cache()['probation'] == [c] and cache.get_cache()['protected'] == [a]
    # Eviction changes working-set residency, not immutable source history.
    assert cache.get_entry(b)['text'].startswith('The temporary debug logs')
    previous = ''
    for i in range(4):
        record = cache.get_event(i)
        root = record.pop('root')
        assert root == NS['digest'](record)
        assert record['binding']['before']['head'] == previous
        assert record['binding']['before']['sequence'] == i
        assert record['after']['sequence'] == i + 1
        previous = root
    assert cache.get_cache()['head'] == previous


def test_without_hit_oldest_probation_is_evicted(cache, direct_vm, direct_alice):
    access(cache, direct_vm, 'first', 'a')
    a = receipt(cache, direct_alice, 'first')['representative']
    access(cache, direct_vm, 'second', 'b', ['DIFFERENT'])
    access(cache, direct_vm, 'third', 'c', ['DIFFERENT', 'DIFFERENT'])
    assert receipt(cache, direct_alice, 'third')['evicted'] == a


def test_protected_overflow_demotes_lru(cache, direct_vm, direct_alice):
    access(cache, direct_vm, 'first', 'a')
    a = receipt(cache, direct_alice, 'first')['representative']
    access(cache, direct_vm, 'second', 'b', ['DIFFERENT'])
    b = receipt(cache, direct_alice, 'second')['representative']
    access(cache, direct_vm, 'reuse-a', 'a-paraphrase', ['SAME', 'DIFFERENT'])
    access(cache, direct_vm, 'reuse-b', 'b', ['SAME', 'DIFFERENT'])
    assert receipt(cache, direct_alice, 'reuse-b')['demoted'] == a
    assert cache.get_cache()['protected'] == [b] and cache.get_cache()['probation'] == [a]


@pytest.mark.parametrize('labels', [['UNKNOWN', 'DIFFERENT'], ['SAME', 'UNKNOWN'], ['SAME', 'SAME']])
def test_uncertain_or_nontransitive_never_touches(cache, direct_vm, direct_alice, labels):
    access(cache, direct_vm, 'first', 'a')
    access(cache, direct_vm, 'second', 'b', ['DIFFERENT'])
    before = cache.get_cache()
    access(cache, direct_vm, 'uncertain', 'c', labels)
    r = receipt(cache, direct_alice, 'uncertain')
    assert r['outcome'] == 'BYPASS' and not r['representative'] and not r['evicted']
    assert cache.get_cache()['probation'] == before['probation']
    assert cache.get_cache()['protected'] == before['protected']


def test_identical_text_cannot_be_distinct(cache, direct_vm, direct_alice):
    access(cache, direct_vm, 'first', 'a')
    access(cache, direct_vm, 'contradiction', 'a', ['DIFFERENT'])
    r = receipt(cache, direct_alice, 'contradiction')
    assert r['outcome'] == 'BYPASS' and r['reason'] == 'IDENTITY_CONTRADICTION'
    assert len(cache.get_cache()['probation']) == 1


@pytest.mark.parametrize('case', ['bad_hash', 'http', 'tamper', 'encoding'])
def test_fake_or_missing_evidence_no_eviction(cache, direct_vm, direct_alice, case):
    access(cache, direct_vm, 'first', 'a')
    before = cache.get_cache()
    kwargs = {'bad': True} if case == 'bad_hash' else {'status': 503} if case == 'http' else {
        'body': b'forged evidence bytes do not match source'} if case == 'tamper' else {'body': b'\xff' * 80}
    access(cache, direct_vm, 'fake', 'b', ['SAME'], **kwargs)
    r = receipt(cache, direct_alice, 'fake')
    assert r['outcome'] == 'BYPASS' and r['reason'] == 'EVIDENCE_FAILURE'
    assert cache.get_cache()['probation'] == before['probation']


def test_unavailable_resident_cannot_be_reused(cache, direct_vm, direct_alice):
    access(cache, direct_vm, 'first', 'a')
    before = cache.get_cache()
    direct_vm.clear_mocks()
    direct_vm.mock_web(r'.*/a\.txt', {'status': 503, 'body': b'unavailable'})
    raw = Path('examples/a-paraphrase.txt').read_bytes()
    direct_vm.mock_web(r'.*/a-paraphrase\.txt', {'status': 200, 'body': raw})
    direct_vm.mock_llm(r'(?s).*', json.dumps({'labels': ['SAME']}))
    cache.access('resident-failure', 'stoneforger10', 'meaning-cache-2q', 'a' * 40,
                 'examples/a-paraphrase.txt', hashlib.sha256(raw).hexdigest(), NOW + 6000)
    assert receipt(cache, direct_alice, 'resident-failure')['outcome'] == 'BYPASS'
    assert cache.get_cache()['probation'] == before['probation']


def test_replay_does_not_reset_or_touch(cache, direct_vm, direct_alice):
    access(cache, direct_vm, 'first', 'a')
    before, r = cache.get_cache(), receipt(cache, direct_alice, 'first')
    with direct_vm.expect_revert('replay'):
        access(cache, direct_vm, 'first', 'b', ['DIFFERENT'])
    assert cache.get_cache() == before and receipt(cache, direct_alice, 'first') == r


def test_namespace_binding(cache, direct_vm, direct_alice, direct_bob):
    access(cache, direct_vm, 'first', 'a')
    direct_vm.sender = direct_bob
    access(cache, direct_vm, 'first', 'b', ['DIFFERENT'])
    assert receipt(cache, direct_alice, 'first')['root'] != receipt(cache, direct_bob, 'first')['root']
    assert cache.request_key(addr(direct_alice), 'first') != cache.request_key(addr(direct_bob), 'first')


def warp(vm, text):
    vm.warp(text)
    from genlayer import gl
    gl.message_raw['datetime'] = text


def test_expiry_permissionless_and_not_refreshed_on_hit(cache, direct_vm, direct_alice, direct_bob):
    access(cache, direct_vm, 'first', 'a')
    a = receipt(cache, direct_alice, 'first')['representative']
    warp(direct_vm, '2026-10-13T12:30:00Z')
    access(cache, direct_vm, 'reuse', 'a-paraphrase', ['SAME'])
    assert cache.get_entry(a)['expires'] == NOW + 3600
    with direct_vm.expect_revert('nothing expired'):
        cache.purge()
    warp(direct_vm, '2026-10-13T13:00:00Z')
    direct_vm.sender = direct_bob
    cache.purge()
    assert cache.get_cache()['probation'] == cache.get_cache()['protected'] == []
    assert cache.get_event(2)['expired'] == [a]
    assert cache.get_entry(a)['text']  # historical retention is not privacy deletion


def test_expired_entry_cannot_semantically_hit(cache, direct_vm, direct_alice):
    access(cache, direct_vm, 'first', 'a')
    a = receipt(cache, direct_alice, 'first')['representative']
    warp(direct_vm, '2026-10-13T13:00:00Z')
    access(cache, direct_vm, 'after-expiry', 'a-paraphrase')
    r = receipt(cache, direct_alice, 'after-expiry')
    assert r['outcome'] == 'MISS' and r['representative'] != a and r['binding']['expired'] == [a]


def test_expired_request_reverts_before_acquisition(cache, direct_vm):
    with direct_vm.expect_revert('deadline'):
        cache.access('expired', 'stoneforger10', 'meaning-cache-2q', 'a' * 40,
                     'examples/a.txt', '0' * 64, NOW)
    assert cache.get_cache()['sequence'] == 0


@pytest.mark.parametrize('value', [{'labels': [True]}, {'labels': ['PASS']}, {'labels': [], 'score': 100},
    [], '{"labels":["SAME"],"labels":["DIFFERENT"]}'])
def test_malformed_vector(value):
    assert NS['parse_labels'](value, 1) is None


def test_llm_error_rolls_back(cache, direct_vm):
    access(cache, direct_vm, 'first', 'a')
    before = cache.get_cache()
    with direct_vm.expect_revert('malformed equivalence'):
        access(cache, direct_vm, 'bad-llm', 'b', ['SAME', 'SAME'])
    assert cache.get_cache() == before


def test_actual_validator_refetches_and_checks_all_material_fields():
    klass = next(n for n in TREE.body if isinstance(n, ast.ClassDef))
    entry = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == 'access')
    callback = next(n for n in entry.body if isinstance(n, ast.FunctionDef) and n.name == 'validate')
    class Return:
        def __init__(self, data): self.calldata = data
    report = {'labels': ['SAME'], 'sources': [{'hash': 'actual', 'text': 'actual text'}],
              'binding': {'request': 'a'}, 'outcome': 'HIT'}
    calls = []
    def observe():
        calls.append(True)
        return report
    local = {'gl': SimpleNamespace(vm=SimpleNamespace(Return=Return)), 'observe': observe,
             'equivalent': NS['equivalent']}
    exec(compile(ast.Module(body=[callback], type_ignores=[]), '<actual-callback>', 'exec'), local)
    assert local['validate'](Return(report))
    for field, value in [('labels', ['DIFFERENT']), ('sources', [{'hash': 'fake', 'text': 'claimed'}]),
                         ('binding', {'request': 'b'}), ('outcome', 'MISS')]:
        assert not local['validate'](Return(dict(report, **{field: value})))
    assert len(calls) == 5 and not local['validate'](object()) and len(calls) == 5


def test_exhaustive_online_two_queue_invariants():
    # Every possible six-access sequence over four meanings, for three capacities.
    for capacity in (2, 3, 4):
        for sequence in itertools.product('abcd', repeat=6):
            p, q = [], []
            for item in sequence:
                old = p + q
                kind = 'HIT' if item in old else 'MISS'
                result = NS['two_queue'](p, q, kind, item, capacity)
                p, q = result['probation'], result['protected']
                assert len(p) + len(q) <= capacity and len(q) <= capacity // 2
                assert len(set(p + q)) == len(p + q) and item in p + q
                if result['evicted']:
                    assert kind == 'MISS' and result['evicted'] not in q
                bypass = NS['two_queue'](p, q, 'BYPASS', '', capacity)
                assert bypass['probation'] == p and bypass['protected'] == q
