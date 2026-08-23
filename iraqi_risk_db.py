"""
Iraqi Construction Risk Database & Assessment Engine (ICRAT)
قاعدة بيانات ومعايير تقييم مخاطر بيئة التشييد العراقية وخوارزمية مؤشر التلكؤ (ISRS)
"""

from typing import Dict, List, Any
import numpy as np

# تصنيفات المخاطر في بيئة التشييد العراقية
RISK_CATEGORIES = {
    "FINANCIAL_LIQUIDITY": {
        "name_ar": "التمويل والسيولة وسعر الصرف",
        "name_en": "Financial & Liquidity Risks",
        "weight": 0.25,
        "icon": "💰",
        "description": "تأخر السلف المالية وتخصيصات الموازنة وتذبذب سعر الصرف الموازي"
    },
    "PROCUREMENT_SUPPLY": {
        "name_ar": "التجهيز والاستيراد والسيطرة النوعية",
        "name_en": "Procurement & Supply Chain",
        "weight": 0.20,
        "icon": "🚢",
        "description": "المنافذ الحدودية والموانئ وفحوصات الجهاز المركزي للتقييس والسيطرة النوعية"
    },
    "ADMIN_CONTRACTUAL": {
        "name_ar": "الإجراءات وأوامر الغيار والتعارضات",
        "name_en": "Admin & Change Orders",
        "weight": 0.20,
        "icon": "📑",
        "description": "بطء لجان أوامر التغيير وتعارضات البنى التحتية والتجاوزات على الموقع"
    },
    "WORKFORCE_SAFETY": {
        "name_ar": "الكوادر والعمالة والمقاولون الثانويون",
        "name_en": "Workforce & Subcontractors",
        "weight": 0.15,
        "icon": "👷‍♂️",
        "description": "نقص الكوادر التخصصية المعتمدة وملاءة المقاولين الثانويين ومعايير HSE"
    },
    "CLIMATE_ENVIRONMENT": {
        "name_ar": "الطقس والحرارة والظروف البيئية",
        "name_en": "Climate & Environment",
        "weight": 0.10,
        "icon": "☀️",
        "description": "حرارة الصيف القصوى (≥50°C) والعواصف الغبارية والمياه الجوفية الكبريتية"
    },
    "SOCIAL_SECURITY": {
        "name_ar": "البيئة المجتمعية والأمنية والموقع",
        "name_en": "Social & Site Constraints",
        "weight": 0.10,
        "icon": "🛡️",
        "description": "النزاعات العشائرية ومطالبات التشغيل وتصاريح المرور والمخلفات الحربية"
    }
}

# سجل المخاطر المعياري لبيئة العمل العراقية
DEFAULT_IRAQI_RISK_REGISTER = [
    {
        "id": "FIN_01",
        "category": "FINANCIAL_LIQUIDITY",
        "title_ar": "تأخر صرف سلف الإنجاز وسلف التشغيل الحكومية",
        "title_en": "Delayed Interim & Running Payment Certificates",
        "probability": 4,  # Scale 1-5
        "impact": 5,       # Scale 1-5
        "affected_wbs": "جميع الأنشطة / التدفق النقدي العام للمشروع",
        "schedule_delay_days": (30, 90, 180),  # Optimistic, Most Likely, Pessimistic (Days)
        "cost_impact_pct": (5, 12, 25),        # Impact on project budget (%)
        "mitigation_ar": "فتح خط ائتماني مصرفي مسبق، تضمين شرط الفائدة التأخيرية أو الدفع الجزئي، وتوثيق التوقفات رسمياً استناداً للشروط العامة لمقاولات الهندسة المدنية (المادة 69).",
        "mitigated_prob": 2,
        "mitigated_impact": 3
    },
    {
        "id": "FIN_02",
        "category": "FINANCIAL_LIQUIDITY",
        "title_ar": "تذبذب سعر صرف الدولار مقابل الدينار في السوق الموازي",
        "title_en": "Parallel FX Rate Volatility (USD / IQD)",
        "probability": 4,
        "impact": 4,
        "affected_wbs": "استيراد المواد والمعدات التخصصية وعقود التجهيز",
        "schedule_delay_days": (15, 45, 90),
        "cost_impact_pct": (4, 10, 20),
        "mitigation_ar": "تثبيت عقود التوريد بالعملة المحلية مع بنود مرنة لتعديل الأسعار وفق قرارات مجلس الوزراء العراقي، واستخدام منصة التحويل الرسمية للبنك المركزي.",
        "mitigated_prob": 2,
        "mitigated_impact": 2
    },
    {
        "id": "PROC_01",
        "category": "PROCUREMENT_SUPPLY",
        "title_ar": "تأخر التخليص الكمركي في ميناء أم قصر والمنافذ البرية",
        "title_en": "Customs Clearance Delays at Ports & Borders",
        "probability": 4,
        "impact": 4,
        "affected_wbs": "توريد المعدات والمواد الإنشائية المستوردة",
        "schedule_delay_days": (20, 60, 120),
        "cost_impact_pct": (2, 6, 12),
        "mitigation_ar": "إصدار الإعفاءات الكمركية من الوزارة المستفيدة مبكراً، واستخدام نظام التخليص المسبق والتعاقد مع مخلصين كمركيين معتمدين.",
        "mitigated_prob": 2,
        "mitigated_impact": 2
    },
    {
        "id": "PROC_02",
        "category": "PROCUREMENT_SUPPLY",
        "title_ar": "فشل المواد في فحوصات السيطرة النوعية (COSQC) وإعادة التوريد",
        "title_en": "Material Failure in COSQC Tests & Re-Procurement",
        "probability": 3,
        "impact": 4,
        "affected_wbs": "أعمال الخرسانة، حديد التسليح، الأنابيب، العوازل",
        "schedule_delay_days": (15, 40, 75),
        "cost_impact_pct": (2, 5, 10),
        "mitigation_ar": "إلزام الموردين بشهادات منشأ وفحص مسبق من مختبرات طرف ثالث معتمدة، وتجهيز دفعات اختبارية قبل الشحن الشامل.",
        "mitigated_prob": 1,
        "mitigated_impact": 2
    },
    {
        "id": "ADM_01",
        "category": "ADMIN_CONTRACTUAL",
        "title_ar": "بطء لجان إقرار أوامر التغيير (أوامر الغيار) وتمديد المدد",
        "title_en": "Bureaucratic Delays in Approving Variation Orders",
        "probability": 5,
        "impact": 5,
        "affected_wbs": "الأعمال التكميلية والمستحدثة والتصاميم المعدلة",
        "schedule_delay_days": (45, 90, 210),
        "cost_impact_pct": (5, 15, 30),
        "mitigation_ar": "التوثيق الفوري للاختلافات الميدانية عبر أوامر موقعية مؤقتة، وإرسال الكشوفات التحليلية للمهندس المقيم فور ظهور الحاجة مع تحديد السقف الزمني للرد.",
        "mitigated_prob": 3,
        "mitigated_impact": 3
    },
    {
        "id": "ADM_02",
        "category": "ADMIN_CONTRACTUAL",
        "title_ar": "عوائق تسليم الموقع (تعارضات شبكات الكهرباء والماء والتجاوزات)",
        "title_en": "Site Handover Impediments & Underground Utility Clashes",
        "probability": 4,
        "impact": 4,
        "affected_wbs": "الأعمال الترابية والأساسات وشبكات البنية التحتية",
        "schedule_delay_days": (30, 75, 150),
        "cost_impact_pct": (3, 8, 15),
        "mitigation_ar": "إجراء مسح راداري أرضي (GPR) مشترك مع دوائر البلدية والكهرباء قبل بدء الحفر، وتثبيت محاضر التعارض في محضر تسليم الموقع الأولي.",
        "mitigated_prob": 2,
        "mitigated_impact": 2
    },
    {
        "id": "WRK_01",
        "category": "WORKFORCE_SAFETY",
        "title_ar": "نقص الكوادر التخصصية المعتمدة وتعثر المقاولين الثانويين",
        "title_en": "Shortage of Skilled Labor & Subcontractor Distress",
        "probability": 3,
        "impact": 4,
        "affected_wbs": "أعمال الكهروميكانيك MEP، الواجهات، والإنهاءات الدقيقة",
        "schedule_delay_days": (15, 35, 70),
        "cost_impact_pct": (2, 5, 12),
        "mitigation_ar": "التأهيل الفني المسبق للمقاولين الثانويين مع إلزامهم بضمانات أداء، وتوفير برامج تدريب موقعية للعمالة المحلية.",
        "mitigated_prob": 2,
        "mitigated_impact": 2
    },
    {
        "id": "CLM_01",
        "category": "CLIMATE_ENVIRONMENT",
        "title_ar": "توقف العمل نهاراً بسبب درجات الحرارة القصوى (≥ 50°C) صيفاً",
        "title_en": "Summer Extreme Heat (≥50°C) Daylight Work Stoppages",
        "probability": 5,
        "impact": 3,
        "affected_wbs": "صب الخرسانة، أعمال الهياكل الفولاذية، والإنشاءات المكشوفة",
        "schedule_delay_days": (15, 30, 60),
        "cost_impact_pct": (1, 3, 7),
        "mitigation_ar": "التحول لنظام العمل الليلي (Night Shifts)، استخدام خلطات خرسانية مبردة بالثلج ومثبطات الشك، وتوفير خيام ومبردات للعمال.",
        "mitigated_prob": 2,
        "mitigated_impact": 1
    },
    {
        "id": "CLM_02",
        "category": "CLIMATE_ENVIRONMENT",
        "title_ar": "ارتفاع منسوب المياه الجوفية الكبريتية وصعوبة النزح المائي",
        "title_en": "High Saline/Sulfate Groundwater & Dewatering Complexities",
        "probability": 3,
        "impact": 4,
        "affected_wbs": "أعمال الحفريات العميقة والأساسات والسراديب",
        "schedule_delay_days": (10, 25, 60),
        "cost_impact_pct": (2, 6, 14),
        "mitigation_ar": "استخدام منظومة نزح مائي متطورة (Wellpoint Systems)، واستخدام الأسمنت المقاوم للأملاح (Type V) وعوازل بيتومينية معتمدة.",
        "mitigated_prob": 1,
        "mitigated_impact": 2
    },
    {
        "id": "SOC_01",
        "category": "SOCIAL_SECURITY",
        "title_ar": "النزاعات العشائرية ومطالبات التشغيل المحلي الإلزامية",
        "title_en": "Tribal Disputes & Local Community Hiring Interferences",
        "probability": 3,
        "impact": 4,
        "affected_wbs": "الأعمال الميدانية الخارجية ومرور الآليات الثقيلة",
        "schedule_delay_days": (10, 30, 75),
        "cost_impact_pct": (1, 4, 10),
        "mitigation_ar": "التنسيق مع القيادات المحلية ووجهاء المنطقة مبكراً، تخصيص حصة عادلة للأعمال البسيطة لأبناء المنطقة وتوفير حماية أمنية موقعية رسمية.",
        "mitigated_prob": 1,
        "mitigated_impact": 2
    }
]

def calculate_risk_score(probability: int, impact: int) -> int:
    """حساب درجة الخطورة = الاحتمالية × التأثير (1-25)"""
    return int(probability * impact)

def get_risk_level(score: int) -> Dict[str, str]:
    """تصنيف مستوى الخطر ولونه"""
    if score >= 15:
        return {"level_ar": "حرج جداً (High)", "level_en": "Critical", "color": "#EF4444", "badge": "🔴"}
    elif score >= 8:
        return {"level_ar": "متوسط (Medium)", "level_en": "Moderate", "color": "#F59E0B", "badge": "🟡"}
    else:
        return {"level_ar": "منخفض (Low)", "level_en": "Low", "color": "#10B981", "badge": "🟢"}

def compute_iraqi_stalling_risk_score(
    risk_register: List[Dict[str, Any]],
    unresolved_rfis_count: int = 5,
    pending_change_orders: int = 3,
    cash_flow_deficit_pct: float = 15.0,
    subcontractor_performance_score: float = 70.0
) -> Dict[str, Any]:
    """
    خوارزمية حساب مؤشر خطر التلكؤ العراقي (Iraqi Stalling Risk Score - ISRS)
    تعتمد على الترجيح الرياضي لمخاطر البيئة العراقية والمؤشرات الحقلية التنبؤية.
    """
    category_scores = {k: 0.0 for k in RISK_CATEGORIES}
    category_max = {k: 0.0 for k in RISK_CATEGORIES}

    for risk in risk_register:
        cat = risk.get("category", "ADMIN_CONTRACTUAL")
        if cat not in category_scores:
            cat = "ADMIN_CONTRACTUAL"
        score = risk.get("probability", 3) * risk.get("impact", 3)
        category_scores[cat] += score
        category_max[cat] += 25.0

    normalized_cat_scores = {}
    weighted_sum = 0.0

    for cat_key, cat_meta in RISK_CATEGORIES.items():
        if category_max[cat_key] > 0:
            norm = (category_scores[cat_key] / category_max[cat_key]) * 100.0
        else:
            norm = 20.0
        normalized_cat_scores[cat_key] = norm
        weighted_sum += norm * cat_meta["weight"]

    # Operational & Field Penalties
    rfi_penalty = min(10.0, max(0.0, (unresolved_rfis_count - 3) * 1.5))
    co_penalty = min(12.0, max(0.0, (pending_change_orders - 1) * 2.5))
    cash_penalty = min(15.0, (cash_flow_deficit_pct / 100.0) * 35.0)
    sub_penalty = max(0.0, (80.0 - subcontractor_performance_score) * 0.3)

    operational_penalty = rfi_penalty + co_penalty + cash_penalty + sub_penalty
    raw_isrs = (weighted_sum * 0.65) + (operational_penalty * 1.0)
    final_isrs = min(100.0, max(5.0, raw_isrs))

    if final_isrs >= 65.0:
        status_ar = "مشروع معرض لخطر التلكؤ الحرج (Critical Stalling Risk)"
        status_en = "Critical Stalling Risk"
        status_color = "#DC2626"
        status_icon = "🚨"
        recommendations = [
            "تفعيل المادة (69) من الشروط العامة لمقاولات أعمال الهندسة المدنية للمطالبة بالتمديدات الزمنية فوراً.",
            "عقد اجتماع طارئ مع جهة التعاقد (الوزارة/المحافظة) لحسم سلف الإنجاز المتأخرة وتسوية أوامر الغيار العالقة.",
            "إعادة جدولة المسار الحرج (Re-baselining) مع عزل الأنشطة المعلقة بالتعارضات البلدية والكمارك.",
            "تفعيل خطة الاستيراد البديل وتحويل بعض المواد لمصانع وطنية حاصلة على اعتماد السيطرة النوعية COSQC."
        ]
    elif final_isrs >= 38.0:
        status_ar = "مشروع تحت المراقبة المشددة ومؤشرات التعثر (Watchlist / Moderate Risk)"
        status_en = "Moderate Risk / Watchlist"
        status_color = "#D97706"
        status_icon = "⚠️"
        recommendations = [
            "تسريع إغلاق طلبات المعلومات (RFIs) لتقليل فترات انتظار الكوادر في الموقع.",
            "متابعة جداول التخليص الكمركي في ميناء أم قصر والمنافذ البرية قبل 30 يوماً من موعد الحاجة.",
            "التحول لنظام العمل الليلي لتجنب توقفات ذروة حرارة الصيف والحفاظ على إنتاجية الكوادر.",
            "مراجعة الملاءة المالية للمقاولين الثانويين وضمان توفر دفعات نقدية تشغيلية لتفادي توقفهم."
        ]
    else:
        status_ar = "مشروع ضمن الحدود الآمنة والمستقرة (Healthy / Low Risk)"
        status_en = "Low Risk / Stable"
        status_color = "#059669"
        status_icon = "✅"
        recommendations = [
            "الاستمرار في تحديث سجل المخاطر دورياً كل أسبوعين.",
            "مواصلة ضبط جودة الفحوصات المختبرية ومطابقة مواصفات التقييس والسيطرة النوعية.",
            "الحفاظ على العلاقات المجتمعية الإيجابية مع محيط موقع المشروع."
        ]

    return {
        "isrs_score": round(final_isrs, 1),
        "status_ar": status_ar,
        "status_en": status_en,
        "status_color": status_color,
        "status_icon": status_icon,
        "category_breakdown": {k: round(v, 1) for k, v in normalized_cat_scores.items()},
        "operational_penalty": round(operational_penalty, 1),
        "recommendations": recommendations
    }

def compute_advanced_iraqi_stalling_risk_score_v2(
    risk_register: List[Dict[str, Any]],
    unresolved_rfis_count: int = 5,
    pending_change_orders: int = 3,
    cash_flow_deficit_pct: float = 15.0,
    subcontractor_performance_score: float = 70.0,
    # المؤشرات الخمسة المتقدمة الجديدة:
    unresolved_bim_clashes_count: int = 2,
    material_price_inflation_pct: float = 8.5,
    lab_testing_delay_days: int = 12,
    contractual_disputes_count: int = 1,
    heatwave_stoppage_hours: int = 18
) -> Dict[str, Any]:
    """
    الخوارزمية الموسعة والمطورة لمؤشر التلكؤ العراقي (Advanced ISRS v2.0)
    تدمج المؤشرات التشغيلية الكلاسيكية مع 5 مؤشرات حقلية ورقمية حية:
    1. تعارضات BIM الحرجة غير المحلولة
    2. تضخم وتقلب أسعار المواد الإنشائية
    3. تأخر نتائج الفحوصات المختبرية
    4. النزاعات ومطالبات فيديك المرفوعة
    5. ساعات التوقف الإلزامي لحرارة الصيف (>50°C)
    """
    # 1. حساب المؤشر الأساسي القياسي للمقارنة
    base_res = compute_iraqi_stalling_risk_score(
        risk_register=risk_register,
        unresolved_rfis_count=unresolved_rfis_count,
        pending_change_orders=pending_change_orders,
        cash_flow_deficit_pct=cash_flow_deficit_pct,
        subcontractor_performance_score=subcontractor_performance_score
    )

    # 2. حساب عقوبات المؤشرات الخمسة الجديدة
    # أ. عقوبة تعارضات BIM الحرجة (تأثير مباشر على المسار الحرج)
    bim_penalty = min(12.0, max(0.0, unresolved_bim_clashes_count * 3.5))
    
    # ب. عقوبة تضخم أسعار المواد (حديد، إسمنت، أسفلت)
    inflation_penalty = min(10.0, max(0.0, (material_price_inflation_pct - 3.0) * 0.8))
    
    # ج. عقوبة تأخر نتائج الفحوصات المختبرية من NCCL
    lab_penalty = min(8.0, max(0.0, (lab_testing_delay_days - 5) * 0.8))
    
    # د. عقوبة النزاعات والمطالبات المعلقة (DAB)
    dispute_penalty = min(10.0, max(0.0, contractual_disputes_count * 4.0))
    
    # هـ. عقوبة ساعات التوقف الإلزامي بسبب حرارة الصيف
    heat_penalty = min(8.0, max(0.0, (heatwave_stoppage_hours - 8) * 0.5))

    new_indicators_penalty = bim_penalty + inflation_penalty + lab_penalty + dispute_penalty + heat_penalty
    
    # حساب المؤشر الموسع v2.0
    combined_raw = base_res["isrs_score"] * 0.75 + new_indicators_penalty * 0.90
    final_isrs_v2 = min(100.0, max(5.0, combined_raw))

    # التقييم اللوني والوصفي
    if final_isrs_v2 >= 65.0:
        status_ar = "مشروع معرض لخطر التلكؤ الحرج (Critical Stalling Risk)"
        status_en = "Critical Stalling Risk"
        status_color = "#DC2626"
        status_icon = "🚨"
    elif final_isrs_v2 >= 38.0:
        status_ar = "مشروع تحت المراقبة المشددة ومؤشرات التعثر (Watchlist / Moderate Risk)"
        status_en = "Moderate Risk / Watchlist"
        status_color = "#D97706"
        status_icon = "⚠️"
    else:
        status_ar = "مشروع ضمن الحدود الآمنة والمستقرة (Healthy / Low Risk)"
        status_en = "Low Risk / Stable"
        status_color = "#059669"
        status_icon = "✅"

    # توصيات استباقية مخصصة للمؤشرات الخمسة
    advanced_recs = []
    if unresolved_bim_clashes_count > 0:
        advanced_recs.append(f"🧊 حل {unresolved_bim_clashes_count} تعارض BIM حرج فوراً لتفادي تكسير الخرسانة موقعياً وتأخير المسار الحرج.")
    if material_price_inflation_pct > 5.0:
        advanced_recs.append(f"📈 تفعيل المادة 13.8 من فيديك وتوثيق فروقات أسعار المواد (تضخم {material_price_inflation_pct}%) لتأمين التعويض المالي.")
    if lab_testing_delay_days > 7:
        advanced_recs.append(f"🧪 توثيق تأخر نتائج الفحوصات المختبرية ({lab_testing_delay_days} يوم) كسبب تأخير خارجي يعفي المقاول من الغرامات.")
    if contractual_disputes_count > 0:
        advanced_recs.append(f"⚖️ إحالة النزاعات العالقة ({contractual_disputes_count} نزاع) للجنة فض النزاعات (DAB) لمنع تجميد المستحقات.")
    if heatwave_stoppage_hours > 10:
        advanced_recs.append(f"🛰️ اعتماد نظام الصب الليلي وتجهيز مياه التبريد المثلجة لتفادي توقفات الحرارة ({heatwave_stoppage_hours} ساعة).")

    # إضافة توصيات الأساس إذا كانت القائمة فارغة
    if not advanced_recs:
        advanced_recs = base_res["recommendations"]

    delta_isrs = round(final_isrs_v2 - base_res["isrs_score"], 1)

    return {
        "base_isrs": base_res,
        "isrs_score_v2": round(final_isrs_v2, 1),
        "status_ar_v2": status_ar,
        "status_en_v2": status_en,
        "status_color_v2": status_color,
        "status_icon_v2": status_icon,
        "delta_isrs": delta_isrs,
        "new_indicators_penalties": {
            "bim_clashes_penalty": round(bim_penalty, 1),
            "material_inflation_penalty": round(inflation_penalty, 1),
            "lab_testing_penalty": round(lab_penalty, 1),
            "disputes_penalty": round(dispute_penalty, 1),
            "heatwave_penalty": round(heat_penalty, 1),
            "total_new_penalty": round(new_indicators_penalty, 1)
        },
        "advanced_recommendations": advanced_recs
    }

