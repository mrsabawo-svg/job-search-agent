from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def read(path): return yaml.safe_load((ROOT/path).read_text())
def test_enabled_sources_are_only_ats():
    items=read('sources/approved_sources.yaml')['approved_sources']
    assert {x['id'] for x in items if x['enabled']}=={'greenhouse','lever','ashby'}
def test_watchlist_is_not_approved():
    blocked={x['domain'] for x in read('sources/watchlist.yaml')['watchlist']}
    enabled={d for x in read('sources/approved_sources.yaml')['approved_sources'] if x['enabled'] for d in x['domains']}
    assert blocked.isdisjoint(enabled)
