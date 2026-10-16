from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from pydantic import BaseModel

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class TradePartnerSummary(BaseModel):
    partner: str
    exports_rm_mil: float
    imports_rm_mil: float
    total_trade_rm_mil: float
    net_balance_rm_mil: float
    share_of_total_pct: float

def get_trade_partner_summaries(year: str = "2026_8m") -> Tuple[List[TradePartnerSummary], Dict[str, float]]:
    df = pd.read_csv(DATA_DIR / "table_3_7_trade_partners.csv")
    exp_col = f"exp_{year}"
    imp_col = f"imp_{year}"

    total_all_trade = float((df[exp_col] + df[imp_col]).sum())
    total_all_exp = float(df[exp_col].sum())
    total_all_imp = float(df[imp_col].sum())

    summaries: List[TradePartnerSummary] = []
    hhi_total = 0.0
    hhi_exp = 0.0
    hhi_imp = 0.0

    for _, row in df.iterrows():
        exp_val = float(row[exp_col])
        imp_val = float(row[imp_col])
        tot_val = exp_val + imp_val
        net_val = exp_val - imp_val
        share_pct = round((tot_val / total_all_trade) * 100.0, 2)
        exp_share = (exp_val / total_all_exp) * 100.0
        imp_share = (imp_val / total_all_imp) * 100.0
        hhi_total += share_pct**2
        hhi_exp += exp_share**2
        hhi_imp += imp_share**2

        summaries.append(
            TradePartnerSummary(
                partner=str(row["partner"]),
                exports_rm_mil=exp_val,
                imports_rm_mil=imp_val,
                total_trade_rm_mil=tot_val,
                net_balance_rm_mil=net_val,
                share_of_total_pct=share_pct,
            )
        )

    summaries.sort(key=lambda x: x.total_trade_rm_mil, reverse=True)
    top3_share = sum(s.share_of_total_pct for s in summaries[:3])
    metrics = {
        "hhi_total_trade": round(hhi_total, 1),
        "hhi_exports": round(hhi_exp, 1),
        "hhi_imports": round(hhi_imp, 1),
        "top_3_concentration_pct": round(top3_share, 2),
        "gtri_2026_score": 66.03,
        "gtri_2026_rank": 23.0,
        "hormuz_crude_transit_pct": 40.0,
    }
    return summaries, metrics

def get_sankey_trade_flows() -> Dict[str, List[object]]:
    df_flows = pd.read_csv(DATA_DIR / "table_3_10_3_12_commodity_flows.csv")
    nodes: List[str] = []
    node_idx: Dict[str, int] = {}

    def get_node(name: str) -> int:
        if name not in node_idx:
            node_idx[name] = len(nodes)
            nodes.append(name)
        return node_idx[name]

    sources: List[int] = []
    targets: List[int] = []
    values: List[float] = []
    flow_labels: List[str] = []

    for _, row in df_flows.iterrows():
        ftype = str(row["flow_type"])
        comm = str(row["commodity"])
        partner = str(row["partner"])
        val = float(row["rm_2026_8m"])

        if ftype == "Import":
            s_id = get_node(f"Import: {partner}")
            t_id = get_node(f"Malaysia ({comm})")
        else:
            s_id = get_node(f"Malaysia ({comm})")
            t_id = get_node(f"Export: {partner}")

        sources.append(s_id)
        targets.append(t_id)
        values.append(val)
        flow_labels.append(f"{ftype} | {comm} -> {partner}: RM {val:,.0f}M")

    return {
        "nodes": nodes,
        "sources": sources,
        "targets": targets,
        "values": values,
        "labels": flow_labels,
    }
