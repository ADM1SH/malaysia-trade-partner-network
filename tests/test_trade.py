from src.trade_model import get_trade_partner_summaries, get_sankey_trade_flows

def test_trade_summaries():
    summaries, metrics = get_trade_partner_summaries("2026_8m")
    assert len(summaries) == 10
    assert summaries[0].partner == "China"
    assert metrics["hhi_total_trade"] > 1000.0

def test_sankey():
    sankey = get_sankey_trade_flows()
    assert len(sankey["nodes"]) > 10
    assert len(sankey["sources"]) == len(sankey["targets"]) == len(sankey["values"])
