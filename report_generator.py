"""
Executive Risk Assessment & Delay Mitigation Report Generator
مولد التقارير التنفيذية الشاملة لتحليل المخاطر وإدارة التلكؤ ومشكلات التنسيق ISO 31000
نسخة محسنة بالكامل لتناسق اتجاه النصوص والقراءة من اليمين لليسار (RTL)
"""

import io
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
import iso31000_coordination

def generate_markdown_report(
    project_meta: Dict[str, Any],
    simulation_results: Dict[str, Any],
    isrs_data: Dict[str, Any],
    risk_register: List[Dict[str, Any]],
    activities: List[Dict[str, Any]],
    coordination_issues: List[Dict[str, Any]] = None
) -> str:
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    curr = project_meta.get('currency_symbol', '$')
    
    dur_p = simulation_results.get('duration_percentiles', {})
    cost_p = simulation_results.get('cost_percentiles', {})
    
    lines = []
    lines.append('# 🏛️ تقرير التقييم الكمي للمخاطر وإدارة التلكؤ والتنسيق الإنشائي')
    lines.append('### نظام تقييم مخاطر بيئة التشييد في العراق مع معيار ISO 31000')
    lines.append('')
    lines.append(f"- **تاريخ إصدار التقرير:** `{now_str}`")
    lines.append(f"- **اسم المشروع:** {project_meta.get('name_ar', 'مشروع إنشائي')}")
    lines.append(f"- **جهة التعاقد / رب العمل:** {project_meta.get('client_type_ar', 'جهة حكومية / خاصة')}")
    lines.append(f"- **الموقع الجغرافي والمحافظة:** {project_meta.get('location_ar', 'العراق')}")
    lines.append(f"- **العملة المعتمدة:** {project_meta.get('currency', 'USD')} ({curr})")
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('### 1. تشخيص مؤشر خطر التلكؤ العراقي (ISRS)')
    lines.append(f"- **درجة الخطر الإجمالية للمشروع:** **{isrs_data.get('isrs_score', 0.0)}%** {isrs_data.get('status_icon', '')}")
    lines.append(f"- **حالة المشروع:** **{isrs_data.get('status_ar', '')}**")
    lines.append(f"- **مجموع نقاط العقوبات الحقلية:** `{isrs_data.get('operational_penalty', 0.0)}` نقطة")
    lines.append('')
    lines.append('#### تفصيل درجات المخاطر حسب القطاعات العراقية:')
    for cat_k, cat_val in isrs_data.get('category_breakdown', {}).items():
        lines.append(f"- **{cat_k}:** `{cat_val}%`")
        
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append(f"### 2. نتائج محاكاة مونت كارلو للوقت والتكلفة ({simulation_results.get('iterations', 0)} دورة)")
    lines.append('')
    lines.append(f"| المؤشر الإحصائي | مدة المشروع (أيام) | الكلفة الإجمالية ({curr}) | التفسير الهندسي |")
    lines.append("| :--- | :---: | :---: | :--- |")
    lines.append(f"| **التقدير الحتمي المرجعي** | **{round(simulation_results.get('deterministic_duration', 0), 1)}** | **{simulation_results.get('deterministic_cost', 0):,.0f}** | الخطة المرجعية دون احتساب المخاطر |")
    lines.append(f"| **مستوى الثقة P10 (المتفائل)** | {round(dur_p.get('P10', 0), 1)} | {cost_p.get('P10', 0):,.0f} | فرصة 10% فقط للإنجاز قبل هذا الموعد |")
    lines.append(f"| **مستوى الثقة P50 (الأكثر واقعية)** | {round(dur_p.get('P50', 0), 1)} | {cost_p.get('P50', 0):,.0f} | الموعد والميزانية الأكثر احتمالية واقعياً |")
    lines.append(f"| **مستوى الثقة P80 (الالتزام الآمن)** | **{round(dur_p.get('P80', 0), 1)}** | **{cost_p.get('P80', 0):,.0f}** | **الموعد والميزانية الآمنة الموصى بها تعاقدياً** |")
    lines.append(f"| **مستوى الثقة P90 (اليقين المرتفع)** | {round(dur_p.get('P90', 0), 1)} | {cost_p.get('P90', 0):,.0f} | للأعمال المعقدة وعالية الحساسية |")
    lines.append('')
    lines.append('#### احتياطيات الطوارئ الموصى بها لتأمين الإنجاز (بنسبة ثقة 80%):')
    lines.append(f"- **احتياطي الطوارئ الزمني الموصى به:** `+{simulation_results.get('contingency_time_days', 0)}` **يوم عمل إضافي**.")
    lines.append(f"- **احتياطي الطوارئ المالي الموصى به:** `+{simulation_results.get('contingency_cost_val', 0):,.0f}` **{curr}** (بنسبة تعادل `{simulation_results.get('contingency_cost_pct', 0)}%` من الكلفة المرجعية).")
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('### 3. تحليل الحساسية وأبرز مسببات التأخير (Tornado Analysis)')
    for idx, item in enumerate(simulation_results.get('tornado_duration', [])[:6], 1):
        corr_val = round(item.get('correlation', 0.0), 3)
        lines.append(f"{idx}. **{item.get('name', '')}** — معامل الارتباط: `{corr_val}`")
        
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('### 4. تقييم ومعالجة مشكلات التنسيق والتعارضات (ISO 31000:2018)')
    if coordination_issues:
        lines.append(f"- **إجمالي مشكلات التنسيق المرصودة:** `{len(coordination_issues)}` مشكلة تعارض وتنسيق.")
        lines.append('')
        for c_idx, c_item in enumerate(coordination_issues, 1):
            sc = c_item.get('likelihood', 1) * c_item.get('consequence', 1)
            lvl = iso31000_coordination.evaluate_coordination_risk_level(sc)
            lines.append(f"#### {c_idx}. [{c_item.get('id')}] {c_item.get('title_ar')}")
            lines.append(f"- **درجة الخطر والأولوية:** `{sc}/25` — {lvl['badge']} **{lvl['level_ar']}**")
            lines.append(f"- **استراتيجية المعالجة المعتمدة:** `{c_item.get('iso_treatment_strategy')}`")
            lines.append(f"- **الجهة المسؤولة عن المتابعة:** {c_item.get('responsible_party')}")
            lines.append(f"- **خطة المعالجة التنفيذية:** {c_item.get('treatment_action_ar')}")
            lines.append('')
    else:
        lines.append("- لم يتم رصد مشكلات تعارض وتنسيق إضافية.")

    lines.append('---')
    lines.append('')
    lines.append('### 5. التوصيات الفنية والتعاقدية الفورية لمعالجة التلكؤ')
    for rec in isrs_data.get('recommendations', []):
        lines.append(f"- 📌 {rec}")
        
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('### 6. مسرد المصطلحات الهندسية والتعاقدية المعتمدة (Glossary)')
    lines.append('| المصطلح (Term) | الاسم الكامل (Full Name) | المعنى والتعريف الهندسي | المجال |')
    lines.append('| :--- | :--- | :--- | :--- |')
    import glossary_data
    for g in glossary_data.GLOSSARY_TERMS:
        lines.append(f"| **{g['term_en']}** | {g['full_en']} | **{g['term_ar']}**: {g['definition_ar']} | {g['category_ar']} |")
        
    lines.append('')
    lines.append('---')
    lines.append('**Designed and developed by Dr Ahmed Louay Ahmed**  ')
    lines.append('*Iraqi Construction Risk Assessment & Decision Support Platform (ICRAT 2.0)*')
    
    return '\n'.join(lines)

def export_activities_csv(activities: List[Dict[str, Any]]) -> str:
    rows = []
    for a in activities:
        o_d, m_d, p_d = a.get('duration_estimates', (0, 0, 0))
        o_c, m_c, p_c = a.get('cost_estimates', (0, 0, 0))
        rows.append({
            'Activity_ID': a.get('id'),
            'Name_AR': a.get('name_ar'),
            'Name_EN': a.get('name_en'),
            'Duration_O_Days': o_d,
            'Duration_M_Days': m_d,
            'Duration_P_Days': p_d,
            'Cost_O': o_c,
            'Cost_M': m_c,
            'Cost_P': p_c,
            'Predecessors': ', '.join(a.get('predecessors', []))
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def export_risks_csv(risks: List[Dict[str, Any]]) -> str:
    rows = []
    for r in risks:
        rows.append({
            'Risk_ID': r.get('id'),
            'Category': r.get('category'),
            'Title_AR': r.get('title_ar'),
            'Probability_1_5': r.get('probability'),
            'Impact_1_5': r.get('impact'),
            'Risk_Score': r.get('probability', 1) * r.get('impact', 1),
            'Mitigation_Strategy': r.get('mitigation_ar')
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def export_coordination_csv(issues: List[Dict[str, Any]]) -> str:
    rows = []
    for i in issues:
        score = i.get('likelihood', 1) * i.get('consequence', 1)
        rows.append({
            'Issue_ID': i.get('id'),
            'Domain': i.get('domain'),
            'Title_AR': i.get('title_ar'),
            'Likelihood_1_5': i.get('likelihood'),
            'Consequence_1_5': i.get('consequence'),
            'Risk_Score': score,
            'Detectability_1_5': i.get('detectability'),
            'Responsible_Party': i.get('responsible_party'),
            'ISO_Treatment_Strategy': i.get('iso_treatment_strategy'),
            'Treatment_Action': i.get('treatment_action_ar'),
            'Post_Likelihood': i.get('post_treatment_likelihood'),
            'Post_Consequence': i.get('post_treatment_consequence')
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)
