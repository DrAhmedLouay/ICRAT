"""
================================================================================
محرك الذكاء الاصطناعي ودعم القرار الهندسي المتقدم (AI-BIM Decision Hub Engine)
ICRAT 2.0 - Iraq Construction Risk Assessment & Decision Support Tool
المطور: Dr Ahmed Louay Ahmed
المرجع العلمي: أطروحة الدكتوراه في نمذجة معلومات البناء والذكاء الاصطناعي وإدارة المخاطر
معايير التوافق: ISO 31000:2018 / ISO 19650 / SCL Delay Protocol / PMI-SP / AGC BIMForum
المراجع الأكاديمية:
- Bitaraf et al. (2024): Multi-Criteria Clash Prioritisation Model
- Borkowski & Kubrat (2026): Conceptual AI Framework for Clash Triage & Noise Filtering
- Chahrour et al. (2020, 2021): Cost-Benefit Analysis of BIM Clash Resolution & 3-Tier Costing
- Ayman, Mahfouz & Alhady (2022): Integrated EDM & 4D BIM-Based Decision Support
- Hu & Castro-Lacouture (2018, 2019): Machine Learning Clash Relevance Prediction
- Nishat, Rauzy & Olsson (2025): Human-in-the-Loop Risk Assessment
- Okudan, Budayan & Dikmen (2021): Case-Based Reasoning for Construction Risk Management
- Case Study: Central Bank of Iraq Tower (CBI Tower Project)
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple
import math
import json
from datetime import datetime, timedelta
import numpy as np

# ----------------- 1. CONSTANTS & DOMAIN ONTOLOGY -----------------

DISCIPLINE_PAIRS = {
    ("MEP_HVAC", "STRUCTURAL_BEAM"): {"base_weight": 0.95, "desc_ar": "دكت تكييف رئيسي مع جسر خرساني حامل", "lead_time_days": 18},
    ("MEP_PIPE", "STRUCTURAL_COLUMN"): {"base_weight": 0.90, "desc_ar": "أنبوب تغذية/صرف مع عمود خرساني مسلح", "lead_time_days": 21},
    ("MEP_CABLE_TRAY", "STRUCTURAL_SLAB"): {"base_weight": 0.75, "desc_ar": "حامل كابلات كهربائية مع بلاطة السقف", "lead_time_days": 10},
    ("MEP_HVAC", "MEP_PIPE"): {"base_weight": 0.70, "desc_ar": "تداخل مجاري هواء التكييف مع أنابيب الإطفاء/المياه", "lead_time_days": 12},
    ("ARCH_DOOR", "MEP_CONDUIT"): {"base_weight": 0.40, "desc_ar": "تعارض مسار كابل مع فتحة باب معماري", "lead_time_days": 7},
    ("ARCH_CEILING", "MEP_DIFFUSER"): {"base_weight": 0.35, "desc_ar": "مخرج هواء مع السقف الثانوي المستعار", "lead_time_days": 5},
}

ZONE_CRITICALITY = {
    "PLANT_ROOM": {"weight": 1.0, "name_ar": "غرفة المكائن والمضخات المركزية (Plant Room)", "cost_mult": 1.4},
    "DATA_CENTER": {"weight": 1.0, "name_ar": "مركز البيانات والاتصالات (Data Center)", "cost_mult": 1.5},
    "ELECTRICAL_ROOM": {"weight": 0.9, "name_ar": "غرفة المحولات والقواطع الكهربائية الرئيسية", "cost_mult": 1.3},
    "BASEMENT_PARKING": {"weight": 0.75, "name_ar": "السرداب وطوابق مواقف السيارات ومسارات الخدمات", "cost_mult": 1.1},
    "TYPICAL_FLOOR": {"weight": 0.65, "name_ar": "الطوابق المتكررة والمكاتب الإدارية", "cost_mult": 1.0},
    "ROOF_TOP": {"weight": 0.80, "name_ar": "السطح الفني وأبراج التبريد (Chillers)", "cost_mult": 1.25},
    "CORRIDOR": {"weight": 0.70, "name_ar": "الممرات الرئيسية ومسارات الخدمات المشتركة", "cost_mult": 1.05}
}

# ----------------- 2. AI CLASH TRIAGE & MULTI-CRITERIA SCORING -----------------

def calculate_clash_priority_score(
    clash: Dict[str, Any],
    p6_activity: Optional[Dict[str, Any]] = None,
    tolerance_mm: float = 10.0
) -> Dict[str, Any]:
    """
    حساب درجة الأولوية المركبة للتعارض (Composite Priority Score - Ψ)
    استناداً إلى نموذج Bitaraf et al. (2024) و Borkowski & Kubrat (2026)
    """
    penetration_mm = float(clash.get("penetration_depth_mm", clash.get("penetration", 50.0)))
    
    # 1. تصفية الضوضاء وتصنيف الصلة (Noise Filtering & Relevance)
    is_false_positive = penetration_mm <= tolerance_mm
    relevance_prob = 0.15 if is_false_positive else min(0.99, 0.50 + (penetration_mm / 250.0) * 0.45)
    
    # 2. عمق التداخل (Penetration Severity: 0 - 1.0)
    norm_penetration = min(1.0, max(0.0, penetration_mm / 200.0))
    
    # 3. وزن التخصص والعنصر (Discipline & Element Criticality: 0 - 1.0)
    disc_a = clash.get("discipline_a", "MEP_HVAC")
    disc_b = clash.get("discipline_b", "STRUCTURAL_BEAM")
    pair_info = DISCIPLINE_PAIRS.get((disc_a, disc_b), DISCIPLINE_PAIRS.get((disc_b, disc_a), {"base_weight": 0.65, "desc_ar": "تعارض متعدد التخصصات", "lead_time_days": 10}))
    w_element = pair_info["base_weight"]
    
    # 4. الأثر على المسار الحرج في بريمافيرا P6 (Critical Path Proximity: 0 - 1.0)
    is_critical_p6 = False
    total_float = 10
    activity_name = "غير محدد"
    if p6_activity:
        total_float = p6_activity.get("total_float", 0)
        is_critical_p6 = (total_float == 0)
        activity_name = p6_activity.get("name_ar", p6_activity.get("name", "نشاط إنشائي"))
        crit_score = 1.0 if is_critical_p6 else max(0.2, 1.0 - (total_float / 30.0))
    else:
        # استنتاج ذكي للمرحلة الإنشائية والنشاط والمسار الحرج وفق الحيز والتخصص
        z_k = clash.get("zone", "TYPICAL_FLOOR")
        d_k = clash.get("discipline", "MEP_STR")
        
        if z_k == "BASEMENT":
            activity_name = "أعمال الأساسات وجدران السرداب وعزل المياه"
            total_float = 0 if "STR" in d_k else 4
        elif z_k == "PODIUM_GROUND":
            activity_name = "الهيكل الإنشائي - الطابق الأرضي والميزانين"
            total_float = 0 if ("STR" in d_k and penetration_mm > 40) else 8
        elif z_k == "ROOF_PLANT":
            activity_name = "تركيب مبردات ومكائن التكييف بالسطح (Chillers)"
            total_float = 14
        else:
            if "STR" in d_k:
                activity_name = "صب الخرسانة المسلحة للأعمدة والجسور والأسقف"
                total_float = 0 if penetration_mm > 70 else 6
            elif "MEP" in d_k:
                activity_name = "تمديدات مجاري الهواء وشبكات الأنابيب الرئيسية"
                total_float = 12
            else:
                activity_name = "أعمال الأسقف الثانوية والإنهاءات المعمارية"
                total_float = 22

        is_critical_p6 = (total_float == 0)
        crit_score = 1.0 if is_critical_p6 else max(0.2, 1.0 - (total_float / 30.0))
        
    # 5. كثافة العناصر وحساسية الحيز (Spatial Density & Zone Risk: 0 - 1.0)
    zone_key = clash.get("zone", "TYPICAL_FLOOR")
    zone_info = ZONE_CRITICALITY.get(zone_key, ZONE_CRITICALITY["TYPICAL_FLOOR"])
    zone_weight = zone_info["weight"]
    
    # 6. كثافة العناصر المحيطة (Surrounding Element Density: 0 - 1.0)
    density_count = int(clash.get("adjacent_elements_count", 6))
    density_score = min(1.0, density_count / 12.0)
    
    # 7. الكلفة التقديرية لإعادة العمل (Remediation Cost Impact: 0 - 1.0)
    if w_element >= 0.85 and penetration_mm >= 50:
        cost_tier = "MAJOR"
        est_cost_usd = round(15200.0 * zone_info["cost_mult"], 0)
        cost_score = 0.95
        delay_days = pair_info["lead_time_days"]
    elif w_element >= 0.60 or penetration_mm >= 25:
        cost_tier = "MEDIUM"
        est_cost_usd = round(4800.0 * zone_info["cost_mult"], 0)
        cost_score = 0.60
        delay_days = max(5, int(pair_info["lead_time_days"] * 0.6))
    else:
        cost_tier = "MINOR"
        est_cost_usd = round(1200.0 * zone_info["cost_mult"], 0)
        cost_score = 0.25
        delay_days = 2

    # معادلة الدرجة المركبة (Bitaraf 2024 Multi-Criteria Score)
    psi_score = (
        0.25 * norm_penetration +
        0.25 * crit_score +
        0.20 * w_element +
        0.10 * density_score +
        0.10 * zone_weight +
        0.10 * cost_score
    ) * 100.0
    
    # تصنيف الشدة وفق ISO 31000
    if is_false_positive:
        iso_category = "FALSE_POSITIVE"
        iso_level_ar = "تفاوت مسموح (False Positive / Noise)"
        badge_color = "#94A3B8"
        suggested_strategy = "ACCEPT"
    elif psi_score >= 70 or is_critical_p6:
        iso_category = "CRITICAL"
        iso_level_ar = "خطر حرج غير مقبول (Critical / High Priority)"
        badge_color = "#DC2626"
        suggested_strategy = "AVOID"
    elif psi_score >= 40:
        iso_category = "MODERATE"
        iso_level_ar = "خطر متوسط (Moderate / ALARP)"
        badge_color = "#D97706"
        suggested_strategy = "MITIGATE"
    else:
        iso_category = "LOW"
        iso_level_ar = "خطر طفيف مقبول (Low / Routine)"
        badge_color = "#059669"
        suggested_strategy = "ACCEPT"
        
    # تفسير التنبؤ الذكي (SHAP-inspired Explainability)
    shap_factors = [
        {"factor": "عمق التداخل الفراغي", "impact_pct": round(norm_penetration * 25, 1), "desc": f"{penetration_mm:.0f} مم"},
        {"factor": "المسار الحرج لجدول P6", "impact_pct": round(crit_score * 25, 1), "desc": "حرج (Float=0)" if is_critical_p6 else f"سماحية {total_float} يوم"},
        {"factor": "أهمية العنصر والتخصص", "impact_pct": round(w_element * 20, 1), "desc": pair_info["desc_ar"]},
        {"factor": "حساسية الحيز والطابق", "impact_pct": round(zone_weight * 10, 1), "desc": zone_info["name_ar"]},
        {"factor": "كثافة الفضاء المحيط", "impact_pct": round(density_score * 10, 1), "desc": f"{density_count} عناصر مجاورة"}
    ]
    shap_factors.sort(key=lambda x: x["impact_pct"], reverse=True)
    
    base_l = clash.get("likelihood", 5)
    base_c = clash.get("consequence", 4)
    base_2d_score = base_l * base_c
    if base_2d_score >= 20:
        base_2d_level = "🔴 شدة كبيرة/كارثية (2D)"
    elif base_2d_score >= 12:
        base_2d_level = "🟠 شدة متوسطة (2D)"
    else:
        base_2d_level = "🟡 شدة طفيفة (2D)"

    if is_critical_p6:
        delta_explanation = "🚨 تصعيد الخطر: يهدد المسار الحرج لـ P6 مباشرة (Float = 0)"
    elif total_float >= 10:
        delta_explanation = f"🟢 خفض الخطر: حماية المسار الحرج (سماحية +{total_float} يوم)"
    else:
        delta_explanation = f"🟡 معالجة مجدولة (سماحية +{total_float} يوم)"

    el1 = str(clash.get("element_id_1", "13178084"))
    el2 = str(clash.get("element_id_2", "25046673"))
    it1 = str(clash.get("item1_name", "M_Duct / Pipe"))
    it2 = str(clash.get("item2_name", "STR_ConcreteBeam"))
    el_pair = clash.get("element_ids_formatted") or f"{el1} ⚔️ {el2}"
    it_pair = clash.get("item_names_formatted") or f"{it1} ⚔️ {it2}"

    return {
        "clash_id": clash.get("id", "CLASH_01"),
        "title_ar": clash.get("title_ar", "تعارض إنشائي-كهروميكانيكي"),
        "element_id_1": el1,
        "element_id_2": el2,
        "item1_name": it1,
        "item2_name": it2,
        "element_ids_formatted": el_pair,
        "item_names_formatted": it_pair,
        "is_false_positive": is_false_positive,
        "relevance_probability": round(relevance_prob, 2),
        "priority_score": round(psi_score, 1),
        "baseline_2d_score": base_2d_score,
        "baseline_2d_level": base_2d_level,
        "delta_explanation": delta_explanation,
        "iso_category": iso_category,
        "iso_level_ar": iso_level_ar,
        "badge_color": badge_color,
        "cost_tier": cost_tier,
        "estimated_rework_cost_usd": est_cost_usd,
        "estimated_delay_days": delay_days,
        "is_critical_p6": is_critical_p6,
        "p6_activity_name": activity_name,
        "total_float_days": total_float,
        "zone_name_ar": zone_info["name_ar"],
        "suggested_iso_strategy": suggested_strategy,
        "responsible_discipline": clash.get("responsible_party", "مهندس MEP / التنسيق"),
        "shap_explanation": shap_factors,
        "treatment_recommendation_ar": get_case_based_treatment(cost_tier, is_critical_p6, pair_info["desc_ar"])
    }

# ----------------- 3. CASE-BASED REASONING (CBRisk) -----------------

def get_case_based_treatment(cost_tier: str, is_critical: bool, clash_desc: str) -> str:
    """استرجاع التوصية الإنشائية وفق الاستدلال القائم على الحالات (Okudan et al., 2021)"""
    if is_critical and cost_tier == "MAJOR":
        return f"🔴 إجراء فوري: عقد ورشة تنسيق طارئة بين مصمم الهيكل ومقاول MEP لإعادة توجيه المسار في نموذج BIM خلال 48 ساعة قبل صب الخرسانة لتفادي تعطيل المسار الحرج."
    elif cost_tier == "MAJOR":
        return f"🟠 إعادة مسار دكت/أنبوب رئيسي في نموذج الـ 3D مع فحص منسوب السقف الثانوي وتحديث فتحات الجسور مسبقاً (Sleeves)."
    elif cost_tier == "MEDIUM":
        return f"🟡 استخدام وصلات مرنة (Flexible Offsets) وتنسيق التعليقات الميكانيكية (Trapeze Hangers) وتوثيق التعديل في مخططات الـ As-Built."
    else:
        return f"🟢 معالجة موقعية ضمن التفاوتات المعمارية المسموحة بدون الحاجة لأمر تغيير (Variation Order)."

# ----------------- 4. 4D SPATIO-TEMPORAL SCHEDULE RISK PROJECTION -----------------

def project_clash_schedule_risk_network(
    clashes: List[Dict[str, Any]],
    activities: List[Dict[str, Any]],
    project_start_date: str = "2026-09-01"
) -> Dict[str, Any]:
    """
    تحليل الشبكة الزمنية الفراغية 4D والتنبؤ بمخاطر التلكؤ قبل وقوعها بأسابيع
    (Zhang & Hu, 2011; Ayman et al., 2022)
    """
    analyzed_clashes = []
    total_rework_cost = 0.0
    total_critical_delays = 0
    threatened_activities = set()
    
    act_lookup = {str(a.get("id", "")): a for a in activities}
    
    for idx, c in enumerate(clashes):
        matched_act = None
        if "linked_activity_id" in c and c["linked_activity_id"] in act_lookup:
            matched_act = act_lookup[c["linked_activity_id"]]
        elif activities:
            matched_act = activities[idx % len(activities)]
            
        res = calculate_clash_priority_score(c, matched_act)
        analyzed_clashes.append(res)
        
        if not res["is_false_positive"]:
            total_rework_cost += res["estimated_rework_cost_usd"]
            if res["is_critical_p6"]:
                total_critical_delays += res["estimated_delay_days"]
                if matched_act:
                    threatened_activities.add(matched_act.get("id", f"ACT_{idx}"))

    total_count = len(clashes)
    noise_count = sum(1 for c in analyzed_clashes if c["is_false_positive"])
    critical_count = sum(1 for c in analyzed_clashes if c["iso_category"] == "CRITICAL")
    moderate_count = sum(1 for c in analyzed_clashes if c["iso_category"] == "MODERATE")
    
    return {
        "total_clashes": total_count,
        "noise_filtered_count": noise_count,
        "noise_filtered_pct": round((noise_count / total_count * 100.0), 1) if total_count > 0 else 0.0,
        "actionable_clashes_count": total_count - noise_count,
        "critical_clashes_count": critical_count,
        "moderate_clashes_count": moderate_count,
        "total_projected_rework_cost_usd": total_rework_cost,
        "total_critical_path_delay_days": total_critical_delays,
        "threatened_activities_count": len(threatened_activities),
        "analyzed_clashes": analyzed_clashes
    }

# ----------------- 5. BCF (BIM COLLABORATION FORMAT) EXPORT -----------------

def export_clash_triage_to_bcf_json(analyzed_clashes: List[Dict[str, Any]], project_name: str = "CBI Tower Project") -> str:
    """تصدير تقرير التنسيق والقرارات الذكية بصيغة BCF المهيكلة للتبادل مع Revit و Navisworks"""
    topics = []
    for c in analyzed_clashes:
        if c["is_false_positive"]:
            continue
        topic = {
            "guid": c["clash_id"],
            "title": f"[{c["iso_category"]}] {c["title_ar"]}",
            "priority": "HIGH" if c["iso_category"] == "CRITICAL" else "NORMAL",
            "status": "OPEN",
            "assigned_to": c["responsible_discipline"],
            "creation_date": datetime.now().isoformat(),
            "priority_score": c["priority_score"],
            "rework_cost_usd": c["estimated_rework_cost_usd"],
            "delay_impact_days": c["estimated_delay_days"],
            "iso_31000_strategy": c["suggested_iso_strategy"],
            "description": c["treatment_recommendation_ar"],
            "shap_explanation": c["shap_explanation"]
        }
        topics.append(topic)
        
    bcf_container = {
        "project": project_name,
        "bcf_version": "2.1",
        "standard": "ISO 19650 / ISO 31000:2018",
        "generated_by": "ICRAT 2.0 AI-BIM Engineering Decision Hub",
        "timestamp": datetime.now().isoformat(),
        "total_actionable_topics": len(topics),
        "topics": topics
    }
    return json.dumps(bcf_container, ensure_ascii=False, indent=2)
