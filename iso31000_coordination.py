"""
ISO 31000 Risk-Based Coordination Classification & Treatment Engine
نظام تصنيف وتقييم ومعالجة مشكلات التنسيق الإنشائي استناداً إلى معيار إدارة المخاطر الدولي ISO 31000:2018
"""

from typing import Dict, List, Any
import numpy as np

# تصنيف مجالات التنسيق الإنشائي (Coordination Domains)
COORDINATION_DOMAINS = {
    "DESIGN_TECHNICAL": {
        "name_ar": "التنسيق التصميمي والفني (BIM & MEP Clashes)",
        "name_en": "Design & Technical Coordination",
        "icon": "📐",
        "description": "تعارض المخططات المعمارية والإنشائية مع مسارات الدكتات والأنابيب والكابلات"
    },
    "STAKEHOLDER_INTERFACES": {
        "name_ar": "تنسيق أصحاب المصلحة والجهات الخارجية (Stakeholders & Utilities)",
        "name_en": "Stakeholder & External Utility Interfaces",
        "icon": "🏛️",
        "description": "التعارض مع دوائر الكهرباء والماء والمجاري والبلديات وموافقات الطرق"
    },
    "SITE_SUBCONTRACTORS": {
        "name_ar": "تنسيق المقاولين الثانويين والحيز الموقعي (Multi-Trade Site Interfaces)",
        "name_en": "Site Space & Trade Subcontractors Coordination",
        "icon": "👷‍♂️",
        "description": "تزامن أعمال المقاولين الثانويين في نفس المساحة وتشارك الرافعات والمعدات"
    },
    "SUPPLY_LOGISTICS": {
        "name_ar": "تنسيق سلاسل الإمداد ومختبرات الفحص (Procurement & QC Coordination)",
        "name_en": "Supply Chain & Lab Testing Coordination",
        "icon": "🚚",
        "description": "تنسيق مواعيد وصول الشحنات مع جاهزية الموقع وجداول فحوصات السيطرة النوعية"
    },
    "INFORMATION_FLOW": {
        "name_ar": "تنسيق تدفق المعلومات واعتماد المخططات (RFIs & Submittals)",
        "name_en": "Information Flow & Approval Lag Coordination",
        "icon": "📑",
        "description": "بطء الإجابة على طلبات المعلومات (RFIs) واعتماد المخططات التنفيذية Shop Drawings"
    }
}

# استراتيجيات المعالجة وفق ISO 31000:2018 (Risk Treatment Strategies)
TREATMENT_STRATEGIES = {
    "AVOID": {
        "name_ar": "تجنب الخطر (Risk Avoidance)",
        "name_en": "Avoid",
        "desc_ar": "تغيير المسار التصميمي أو خطة العمل لتفادي التعارض تماماً (مثل إعادة التوجيه عبر BIM)."
    },
    "MITIGATE": {
        "name_ar": "تخفيف الخطر والحد من آثاره (Risk Mitigation / Reduction)",
        "name_en": "Mitigate",
        "desc_ar": "اتخاذ إجراءات استباقية مثل غرف التنسيق المشتركة وتحديد سقف زمني ملزم للرد على RFIs."
    },
    "SHARE": {
        "name_ar": "مشاركة الخطر / نقله تعاقدياً (Risk Sharing / Transfer)",
        "name_en": "Share",
        "desc_ar": "توزيع المسؤولية عبر اتفاقيات الواجهات المشتركة (Interface Agreements) وضمانات المقاولين."
    },
    "ACCEPT": {
        "name_ar": "قبول الخطر الواعي مع المراقبة (Risk Acceptance with Monitoring)",
        "name_en": "Accept",
        "desc_ar": "قبول التأخير البسيط ضمن حدود السماحية الزمنية مع المراقبة الدورية."
    }
}

# سجل مشكلات التنسيق الافتراضي لبيئة العمل العراقية (ISO 31000 Baseline)
DEFAULT_COORDINATION_ISSUES = [
    {
        "id": "COORD_01",
        "domain": "DESIGN_TECHNICAL",
        "title_ar": "تعارض مسارات دكتات التكييف Chiller مع الجسور الخرسانية الساقطة",
        "title_en": "HVAC Duct vs Structural Drop Beam Clashes",
        "likelihood": 4,   # 1 to 5
        "consequence": 4,  # 1 to 5
        "detectability": 3, # 1 (Easy to detect) to 5 (Hard to detect)
        "responsible_party": "المهندس المصمم + مقاول الكهروميكانيك MEP",
        "iso_treatment_strategy": "AVOID",
        "treatment_action_ar": "إجراء نمذجة ثلاثية الأبعاد (BIM Clash Detection) وعقد ورشة تنسيق هندسي مشتركة قبل صب السقوف لتعديل مناسيب الفتحات.",
        "post_treatment_likelihood": 1,
        "post_treatment_consequence": 2
    },
    {
        "id": "COORD_02",
        "domain": "STAKEHOLDER_INTERFACES",
        "title_ar": "تعارض مسار الحفر مع كابلات الكهرباء ذات الضغط العالي غير الموثقة",
        "title_en": "Uncharted High-Voltage Underground Cable Clash",
        "likelihood": 4,
        "consequence": 5,
        "detectability": 4,
        "responsible_party": "مديرية توزيع كهرباء المحافظة + مساح الموقع",
        "iso_treatment_strategy": "MITIGATE",
        "treatment_action_ar": "إجراء مسح راداري أرضي (GPR) مشترك وحفر خنادق استكشافية يدوية (Trial Pits) بمرافقة ممثل دائرة الكهرباء قبل دخول الحفارات.",
        "post_treatment_likelihood": 2,
        "post_treatment_consequence": 2
    },
    {
        "id": "COORD_03",
        "domain": "SITE_SUBCONTRACTORS",
        "title_ar": "تزامن أعمال تركيب شبكات الإطفاء مع تقطيع الجدران وتزاحم الرافعات",
        "title_en": "Firefighting Piping vs Partition Walling Space Clashes",
        "likelihood": 3,
        "consequence": 3,
        "detectability": 2,
        "responsible_party": "مدير الموقع + مقاولو الباطن",
        "iso_treatment_strategy": "MITIGATE",
        "treatment_action_ar": "إعداد جدول تنسيق مكاني وزمني (Space-Time Matrix) وتوزيع نوبات العمل وتقسيم الزونات الموقعية.",
        "post_treatment_likelihood": 1,
        "post_treatment_consequence": 2
    },
    {
        "id": "COORD_04",
        "domain": "INFORMATION_FLOW",
        "title_ar": "تأخر اعتماد المخططات التنفيذية (Shop Drawings) لشبكات الغازات الطبية",
        "title_en": "Medical Gas Shop Drawing Submittal Approval Lag",
        "likelihood": 4,
        "consequence": 4,
        "detectability": 2,
        "responsible_party": "المهندس المقيم / استشاري المشروع",
        "iso_treatment_strategy": "MITIGATE",
        "treatment_action_ar": "تفعيل اتفاقية مستوى الخدمة (SLA) وتحديد سقف زمني إلزامي (7 أيام كحد أقصى) للرد والمصادقة استناداً للمادة 14 من الشروط العامة.",
        "post_treatment_likelihood": 2,
        "post_treatment_consequence": 2
    },
    {
        "id": "COORD_05",
        "domain": "SUPPLY_LOGISTICS",
        "title_ar": "تزامن وصول شحنات الأنابيب والمعدات مع عدم اكتمال الحفريات الموقعية",
        "title_en": "Material Delivery Arrival without Site Staging Readiness",
        "likelihood": 3,
        "consequence": 3,
        "detectability": 2,
        "responsible_party": "مسؤول المشتريات واللوجستيات + أمين المخزن",
        "iso_treatment_strategy": "SHARE",
        "treatment_action_ar": "إلزام المورد بجدول توريد تدريجي على دفعات (Just-In-Time) مع تأمين ساحة تشوين خارجية مؤقتة مرخصة ومحمية.",
        "post_treatment_likelihood": 1,
        "post_treatment_consequence": 1
    }
]

def calculate_iso31000_risk_score(likelihood: int, consequence: int) -> int:
    """حساب درجة خطر التنسيق = الاحتمالية × العواقب (1 - 25)"""
    return int(likelihood * consequence)

def evaluate_coordination_risk_level(score: int) -> Dict[str, str]:
    """
    تقييم وترتيب مستوى خطورة التعارض وفق معيار ISO 31000:
    - High / Critical (غير مقبول - يتطلب معالجة فورية)
    - Moderate / ALARP (مقبول بشرط اتخاذ إجراءات تخفيف)
    - Low / Acceptable (مقبول مع المراقبة العادية)
    """
    if score >= 15:
        return {
            "level_ar": "حرج وغير مقبول (Critical / Unacceptable)",
            "level_en": "Critical",
            "color": "#DC2626",
            "badge": "🔴",
            "action_priority": "أولوية قصوى: عقد ورشة تنسيق طارئة ووقف العمل بالمنطقة المتأثرة لحين حسم التعارض."
        }
    elif score >= 8:
        return {
            "level_ar": "متوسط - يتطلب معالجة ومراقبة (Moderate / ALARP)",
            "level_en": "Moderate",
            "color": "#D97706",
            "badge": "🟡",
            "action_priority": "أولوية متوسطة: معالجة التعارض عبر مذكرات التنسيق الأسبوعية وتعديل المخطط التنفيذي."
        }
    else:
        return {
            "level_ar": "منخفض ومقبول مع الرصد (Low / Tolerable)",
            "level_en": "Low",
            "color": "#059669",
            "badge": "🟢",
            "action_priority": "أولوية عادية: إدراج الملاحظة ضمن المحضر الدوري دون تأثير على المسار الحرج."
        }

def compute_coordination_summary(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """حساب المؤشرات الإحصائية لمشكلات التنسيق الإنشائي"""
    total = len(issues)
    if total == 0:
        return {
            "total_issues": 0,
            "critical_count": 0,
            "moderate_count": 0,
            "low_count": 0,
            "domain_breakdown": {},
            "strategy_breakdown": {}
        }

    critical = sum(1 for i in issues if i["likelihood"] * i["consequence"] >= 15)
    moderate = sum(1 for i in issues if 8 <= i["likelihood"] * i["consequence"] < 15)
    low = sum(1 for i in issues if i["likelihood"] * i["consequence"] < 8)

    domain_counts = {}
    for d in COORDINATION_DOMAINS:
        domain_counts[d] = sum(1 for i in issues if i.get("domain") == d)

    strategy_counts = {}
    for s in TREATMENT_STRATEGIES:
        strategy_counts[s] = sum(1 for i in issues if i.get("iso_treatment_strategy") == s)

    return {
        "total_issues": total,
        "critical_count": critical,
        "moderate_count": moderate,
        "low_count": low,
        "domain_breakdown": domain_counts,
        "strategy_breakdown": strategy_counts
    }
