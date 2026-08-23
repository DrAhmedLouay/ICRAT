"""
What-If Mitigation Scenario Comparator & Decision Simulator
محرك مقارنة السيناريوهات التفاعلي: الوضع الحالي (Pre-Mitigation) مقابل الوضع بعد المعالجة (Post-Mitigation)
"""

from typing import Dict, List, Any
import numpy as np
import simulation_engine
import iraqi_risk_db

def simulate_mitigation_scenario(
    base_activities: List[Dict[str, Any]],
    base_risks: List[Dict[str, Any]],
    base_meta: Dict[str, Any],
    levers: Dict[str, bool],
    iterations: int = 2000,
    random_seed: int = 42
) -> Dict[str, Any]:
    """محاكاة وتطبيق رافعات المعالجة الهندسية ومقارنة النتائج الحسابية جنباً إلى جنب"""
    
    # 1. نسخ الأنشطة والمخاطر لإنشاء السيناريو المعالج
    mitigated_activities = [dict(a) for a in base_activities]
    mitigated_risks = [dict(r) for r in base_risks]
    mitigated_meta = dict(base_meta)

    # 2. تطبيق تأثير رافعات المعالجة (Mitigation Levers)
    
    # رافعة 1: تأمين السيولة وصرف السلف
    if levers.get("lever_cash_flow", True):
        mitigated_meta["cash_flow_deficit_pct"] = max(0.0, float(mitigated_meta.get("cash_flow_deficit_pct", 15.0)) * 0.2)
        for r in mitigated_risks:
            if r.get("category") == "FINANCIAL_CASHFLOW":
                r["probability"] = max(1, int(r["probability"]) - 2)
                r["impact"] = max(1, int(r["impact"]) - 2)
                if "schedule_delay_days" in r:
                    o, m, p = r["schedule_delay_days"]
                    r["schedule_delay_days"] = (int(o * 0.3), int(m * 0.3), int(p * 0.3))

    # رافعة 2: حسم تعارضات التنسيق عبر نمذجة BIM
    if levers.get("lever_bim_coordination", True):
        mitigated_meta["unresolved_rfis"] = max(0, int(mitigated_meta.get("unresolved_rfis", 4)) - 3)
        for r in mitigated_risks:
            if r.get("category") in ["PROCEDURAL_REDTAPE", "SITE_SPATIAL"]:
                r["probability"] = max(1, int(r["probability"]) - 2)
                r["impact"] = max(1, int(r["impact"]) - 1)

    # رافعة 3: تسريع لجان أوامر الغيار
    if levers.get("lever_fast_change_orders", True):
        mitigated_meta["pending_change_orders"] = max(0, int(mitigated_meta.get("pending_change_orders", 2)) - 2)
        for r in mitigated_risks:
            if "أوامر التغيير" in r.get("title_ar", "") or "أوامر الغيار" in r.get("title_ar", ""):
                r["probability"] = 1
                r["impact"] = max(1, int(r["impact"]) - 2)

    # رافعة 4: تأهيل وضمانات المقاولين الثانويين
    if levers.get("lever_subcontractor", True):
        mitigated_meta["subcontractor_performance"] = min(100.0, float(mitigated_meta.get("subcontractor_performance", 75.0)) + 20.0)
        for r in mitigated_risks:
            if r.get("category") == "CONTRACTOR_LABOR":
                r["probability"] = max(1, int(r["probability"]) - 2)
                r["impact"] = max(1, int(r["impact"]) - 1)

    # رافعة 5: التخليص الكمركي المسبق
    if levers.get("lever_customs", True):
        for r in mitigated_risks:
            if r.get("category") == "SUPPLY_CHAIN_CUSTOMS":
                r["probability"] = 1
                r["impact"] = max(1, int(r["impact"]) - 2)

    # 3. تشغيل محاكاة السيناريو الأساسي (Baseline)
    base_sim = simulation_engine.MonteCarloSimulator(
        activities=base_activities,
        risks=base_risks,
        iterations=iterations,
        schedule_cost_correlation=0.75,
        daily_overhead_rate=base_meta.get("daily_overhead_usd", 3000.0),
        random_seed=random_seed
    ).run_simulation()

    base_isrs = iraqi_risk_db.compute_iraqi_stalling_risk_score(
        risk_register=base_risks,
        unresolved_rfis_count=base_meta.get("unresolved_rfis", 4),
        pending_change_orders=base_meta.get("pending_change_orders", 2),
        cash_flow_deficit_pct=base_meta.get("cash_flow_deficit_pct", 15.0),
        subcontractor_performance_score=base_meta.get("subcontractor_performance", 75.0)
    )

    # 4. تشغيل محاكاة السيناريو المعالج (Mitigated)
    mit_sim = simulation_engine.MonteCarloSimulator(
        activities=mitigated_activities,
        risks=mitigated_risks,
        iterations=iterations,
        schedule_cost_correlation=0.75,
        daily_overhead_rate=mitigated_meta.get("daily_overhead_usd", 3000.0),
        random_seed=random_seed
    ).run_simulation()

    mit_isrs = iraqi_risk_db.compute_iraqi_stalling_risk_score(
        risk_register=mitigated_risks,
        unresolved_rfis_count=mitigated_meta.get("unresolved_rfis", 1),
        pending_change_orders=mitigated_meta.get("pending_change_orders", 0),
        cash_flow_deficit_pct=mitigated_meta.get("cash_flow_deficit_pct", 3.0),
        subcontractor_performance_score=mitigated_meta.get("subcontractor_performance", 95.0)
    )

    # 5. حساب الفروقات المحققة (Deltas & Savings)
    base_p80_d = base_sim["duration_percentiles"]["P80"]
    mit_p80_d = mit_sim["duration_percentiles"]["P80"]
    days_saved = max(0.0, base_p80_d - mit_p80_d)

    base_p80_c = base_sim["cost_percentiles"]["P80"]
    mit_p80_c = mit_sim["cost_percentiles"]["P80"]
    cost_saved = max(0.0, base_p80_c - mit_p80_c)

    isrs_reduction = max(0.0, base_isrs["isrs_score"] - mit_isrs["isrs_score"])

    return {
        "base_p80_duration": base_p80_d,
        "mit_p80_duration": mit_p80_d,
        "days_saved": days_saved,
        "days_saved_pct": (days_saved / base_p80_d) * 100.0 if base_p80_d > 0 else 0.0,
        
        "base_p80_cost": base_p80_c,
        "mit_p80_cost": mit_p80_c,
        "cost_saved": cost_saved,
        "cost_saved_pct": (cost_saved / base_p80_c) * 100.0 if base_p80_c > 0 else 0.0,
        
        "base_isrs": base_isrs["isrs_score"],
        "mit_isrs": mit_isrs["isrs_score"],
        "isrs_reduction": isrs_reduction,
        
        "base_sim": base_sim,
        "mit_sim": mit_sim,
        "base_isrs_obj": base_isrs,
        "mit_isrs_obj": mit_isrs
    }
