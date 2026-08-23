"""
Iraqi Contractual Delay Claims & Extension of Time (EOT) Calculator
محرك تحليل المطالبات العقدية، تمديد المدة (المادة 44)، وحساب تكاليف الاستمرار والغرامات التأخيرية
وفق الشروط العامة لمقاولات أعمال الهندسة المدنية العراقية (الجزء الأول والثاني)
"""

from typing import Dict, List, Any

# تصنيفات أسباب التأخير وفق العقد العراقي
DELAY_EVENT_CATEGORIES = {
    "EMPLOYER_RISK": {
        "name_ar": "تأخير معوّض مالياً وزمنياً (Compensable Delay - رب العمل)",
        "desc_ar": "تأخر صرف السلف، تعارضات المخططات، تأخر تسليم الموقع، أوامر الغيار.",
        "type": "COMPENSABLE",
        "contract_article": "المادة (44 / 1) والمادة (52) من الشروط العامة"
    },
    "EXCUSABLE_NON_COMPENSABLE": {
        "name_ar": "تأخير مبرر زمنياً فقط (Excusable Non-Compensable - ظروف قاهرة/طقس)",
        "desc_ar": "الظروف الجوية القاهرة، انقطاع الطرق العام، الكوارث الطبيعية.",
        "type": "EXCUSABLE",
        "contract_article": "المادة (44 / 2) من الشروط العامة (تمديد مدة دون تعويض مالي)"
    },
    "CONTRACTOR_RISK": {
        "name_ar": "تأخير غير مبرر يقع على عاتق المقاول (Non-Excusable Delay)",
        "desc_ar": "نقص الكوادر والمعدات، سوء التخطيط، فشل الفحوصات المختبرية.",
        "type": "NON_EXCUSABLE",
        "contract_article": "المادة (47) - الغرامات التأخيرية وسحب العمل"
    }
}

DEFAULT_DELAY_EVENTS = [
    {
        "id": "DELAY_01",
        "category": "EMPLOYER_RISK",
        "title_ar": "تأخر صرف سلف الإنجاز الدورية رقم 3 و 4 لمدة 65 يوماً",
        "claimed_days": 45,
        "approved_days": 40,
        "delay_type": "COMPENSABLE",
        "responsible": "جهة التعاقد / الدائرة المالية",
        "legal_basis": "المادة (60) - السلف والدفعات، والمادة (44/1)"
    },
    {
        "id": "DELAY_02",
        "category": "EMPLOYER_RISK",
        "title_ar": "تأخر لجان التدقيق في حسم وإقرار أوامر الغيار والتغييرات",
        "claimed_days": 35,
        "approved_days": 30,
        "delay_type": "COMPENSABLE",
        "responsible": "المهندس المقيم ولجان تدقيق الوزارة",
        "legal_basis": "المادة (52) - التغييرات والإضافات"
    },
    {
        "id": "DELAY_03",
        "category": "EXCUSABLE_NON_COMPENSABLE",
        "title_ar": "توقف العمل نهاراً بسبب درجات الحرارة الاستثنائية (≥ 50°C)",
        "claimed_days": 25,
        "approved_days": 20,
        "delay_type": "EXCUSABLE",
        "responsible": "ظروف جوية استثنائية (الأنواء الجوية)",
        "legal_basis": "المادة (44/2) - الظروف المناخية غير المعتادة"
    },
    {
        "id": "DELAY_04",
        "category": "CONTRACTOR_RISK",
        "title_ar": "تأخر توريد وتثبيت أنابيب التبريد لعدم كفاية كادر المقاول الثانوي",
        "claimed_days": 0,
        "approved_days": 0,
        "contractor_delay_days": 18,
        "delay_type": "NON_EXCUSABLE",
        "responsible": "المقاول الرئيسي والمقاول الثانوي",
        "legal_basis": "المادة (47) - الإخفاق في سرعة الإنجاز"
    }
]

def calculate_contractual_eot_claim(
    delay_events: List[Dict[str, Any]],
    contract_original_duration_days: int = 365,
    contract_original_cost: float = 10000000.0,
    daily_overhead_cost: float = 3500.0,
    daily_delay_fine_multiplier: float = 0.10,
    currency_symbol: str = "$"
) -> Dict[str, Any]:
    """حساب أيام التمديد التعاقدية (EOT)، تكاليف استمرار الموقع، والغرامات التأخيرية المترتبة"""
    total_compensable_days = 0
    total_excusable_days = 0
    total_contractor_delay_days = 0

    event_assessments = []

    for ev in delay_events:
        d_type = ev.get("delay_type", "COMPENSABLE")
        appr_days = int(ev.get("approved_days", 0))
        c_delay_days = int(ev.get("contractor_delay_days", 0))

        if d_type == "COMPENSABLE":
            total_compensable_days += appr_days
            prolongation_cost = appr_days * daily_overhead_cost
            event_assessments.append({
                **ev,
                "entitled_extension": f"{appr_days} يوم",
                "financial_compensation": f"{prolongation_cost:,.0f} {currency_symbol}",
                "status_badge": "🟢 معوّض مالياً وزمنياً"
            })
        elif d_type == "EXCUSABLE":
            total_excusable_days += appr_days
            event_assessments.append({
                **ev,
                "entitled_extension": f"{appr_days} يوم",
                "financial_compensation": f"0 {currency_symbol} (تمديد فقط)",
                "status_badge": "🟡 مبرر زمنياً فقط"
            })
        else:  # NON_EXCUSABLE
            total_contractor_delay_days += c_delay_days
            event_assessments.append({
                **ev,
                "entitled_extension": "0 يوم (مرفوض)",
                "financial_compensation": f"— (يخضع للغرامات)",
                "status_badge": "🔴 غير مبرر (على المقاول)"
            })

    # إجمالي أيام التمديد العقدية المستحقة للمقاول (EOT)
    total_entitled_eot_days = total_compensable_days + total_excusable_days

    # إجمالي المطالبة المالية لمصاريف استمرار الموقع (Prolongation Claim)
    total_prolongation_claim = total_compensable_days * daily_overhead_cost

    # حساب الغرامات التأخيرية اليومية الرسمية (العقد العراقي: مبلغ العقد / مدة العقد * نسبة)
    daily_liquidated_damages = 0.0
    if contract_original_duration_days > 0:
        daily_liquidated_damages = (contract_original_cost / contract_original_duration_days) * (daily_delay_fine_multiplier / 100.0)

    # الحد الأقصى القانوني للغرامات التأخيرية (10% من مبلغ العقد)
    max_legal_fine = contract_original_cost * 0.10
    total_liquidated_damages = min(max_legal_fine, total_contractor_delay_days * daily_liquidated_damages)

    # صافي الاستحقاق المالي
    net_contractual_balance = total_prolongation_claim - total_liquidated_damages

    return {
        "total_compensable_days": total_compensable_days,
        "total_excusable_days": total_excusable_days,
        "total_contractor_delay_days": total_contractor_delay_days,
        "total_entitled_eot_days": total_entitled_eot_days,
        "total_prolongation_claim": total_prolongation_claim,
        "daily_liquidated_damages": daily_liquidated_damages,
        "total_liquidated_damages": total_liquidated_damages,
        "net_contractual_balance": net_contractual_balance,
        "event_assessments": event_assessments
    }
