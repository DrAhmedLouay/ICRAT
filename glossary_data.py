"""
================================================================================
قاعدة بيانات معجم المصطلحات الهندسية والتعاقدية (Engineering & Contractual Glossary)
ICRAT 2.0 - Iraq Construction Risk Assessment & Decision Support Tool
المطور: Dr Ahmed Louay Ahmed
================================================================================
"""

from typing import List, Dict, Any

GLOSSARY_CATEGORIES = {
    "ALL": "🌐 كافة المصطلحات (All Terms)",
    "AI_SYSTEM": "🧠 المنظومة والذكاء الاصطناعي (AI & Systems)",
    "BIM_DIGITAL": "🧊 نمذجة البناء والتنسيق (BIM & 4D/5D)",
    "SCHEDULE_QSRA": "⏱️ الجدولة والمحاكاة (Schedule & QSRA)",
    "CONTRACTS_FIDIC": "⚖️ العقود والمطالبات وفيديك (Contracts & Claims)",
    "RISK_GEO": "🛡️ إدارة المخاطر والجيوتقنيك (ISO 31000 & Geo-Risk)"
}

GLOSSARY_TERMS: List[Dict[str, Any]] = [
    # 1. AI & Core System
    {
        "term_en": "ICRAT",
        "full_en": "Iraq Construction Risk Assessment Tool",
        "term_ar": "أداة تقييم مخاطر التشييد في العراق",
        "category": "AI_SYSTEM",
        "definition_ar": "منظومة برمجية متكاملة لتقييم المخاطر الإنشائية، التنبؤ بالتأخيرات الزمنية، وإدارة المطالبات التعاقدية في بيئة المشاريع العراقية.",
        "category_ar": "المنظومة والذكاء الاصطناعي"
    },
    {
        "term_en": "ISRS",
        "full_en": "Iraqi Stalling Risk Score",
        "term_ar": "مؤشر خطر التلكؤ العراقي",
        "category": "AI_SYSTEM",
        "definition_ar": "معادلة رياضية مركبة تقيس احتمالية تعثر وتوقف المشروع الإنشائي في العراق استناداً لمصفوفة المخاطر والعقوبات الحقلية والفضائية.",
        "category_ar": "المنظومة والذكاء الاصطناعي"
    },
    {
        "term_en": "AI Clash Triage",
        "full_en": "Artificial Intelligence Clash Prioritization & Filtering",
        "term_ar": "الفرز الذكي وترتيب أولويات التعارضات",
        "category": "AI_SYSTEM",
        "definition_ar": "استخدام خوارزميات التعلم الآلي لعزل الإنذارات الكاذبة (False Positives) وترتيب التعارضات الحقيقية حسب خطورتها على المسار الحرج.",
        "category_ar": "المنظومة والذكاء الاصطناعي"
    },
    {
        "term_en": "Human-in-the-Loop (HITL)",
        "full_en": "Human-in-the-Loop Expert Validation",
        "term_ar": "مبدأ الخبير في الحلقة",
        "category": "AI_SYSTEM",
        "definition_ar": "منهجية تتيح للمهندس البشري فحص وتعديل واعتماد القرارات الصادرة من الذكاء الاصطناعي مع إعادة تدريب النموذج على القرارات المعتمدة.",
        "category_ar": "المنظومة والذكاء الاصطناعي"
    },
    {
        "term_en": "Explainable AI (SHAP)",
        "full_en": "SHapley Additive exPlanations for Machine Learning",
        "term_ar": "الذكاء الاصطناعي التفسيري",
        "category": "AI_SYSTEM",
        "definition_ar": "تقنية حسابية توضح للمهندس العوامل والخصائص المسؤولة عن رفع أو خفض درجة خطورة التعارض لضمان الشفافية وقبول القرار.",
        "category_ar": "المنظومة والذكاء الاصطناعي"
    },

    # 2. BIM & Digital Twin
    {
        "term_en": "BIM",
        "full_en": "Building Information Modeling",
        "term_ar": "نمذجة معلومات البناء",
        "category": "BIM_DIGITAL",
        "definition_ar": "عملية رقمية شاملة لتوليد وإدارة البيانات الهندسية والفيزيائية والوظيفية للمنشأ طوال دورة حياته وفق معيار ISO 19650.",
        "category_ar": "نمذجة البناء والتنسيق"
    },
    {
        "term_en": "4D BIM",
        "full_en": "4-Dimensional Building Information Modeling (3D + Time)",
        "term_ar": "نمذجة البناء رباعية الأبعاد",
        "category": "BIM_DIGITAL",
        "definition_ar": "ربط العناصر والمجسمات ثلاثية الأبعاد بأنشطة الجدول الزمني (Primavera P6) لمحاكاة تسلسل التنفيذ الموقعي ورصد تداخلات الحيز والوقت.",
        "category_ar": "نمذجة البناء والتنسيق"
    },
    {
        "term_en": "5D BIM",
        "full_en": "5-Dimensional Building Information Modeling (4D + Cost)",
        "term_ar": "نمذجة البناء خماسية الأبعاد",
        "category": "BIM_DIGITAL",
        "definition_ar": "ربط النموذج ثلاثي الأبعاد والجدول الزمني بالتكاليف والموازنة ومسار التدفق النقدي لحساب كلفة إعادة العمل والتعطيل الميداني.",
        "category_ar": "نمذجة البناء والتنسيق"
    },
    {
        "term_en": "IFC",
        "full_en": "Industry Foundation Classes",
        "term_ar": "تنسيق التبادل المفتوح لنماذج البناء",
        "category": "BIM_DIGITAL",
        "definition_ar": "صيغة بيانات دولية محايدة ومفتوحة (ISO 16739) تتيح تبادل نماذج الـ BIM بين برامج التصميم المختلفة دون احتكار برمجي.",
        "category_ar": "نمذجة البناء والتنسيق"
    },
    {
        "term_en": "BCF",
        "full_en": "BIM Collaboration Format",
        "term_ar": "تنسيق تبادل تذاكر التنسيق المفتوح",
        "category": "BIM_DIGITAL",
        "definition_ar": "تنسيق مفتوح (BuildingSMART) لنقل تذاكر التعارضات والملاحظات الهندسية ومسؤوليات الحل مباشرة بين برامج مثل Revit و Navisworks.",
        "category_ar": "نمذجة البناء والتنسيق"
    },
    {
        "term_en": "Clash Detection",
        "full_en": "Automated Spatial Conflict Detection",
        "term_ar": "كشف التعارضات والتداخلات الهندسية",
        "category": "BIM_DIGITAL",
        "definition_ar": "عملية آلية لفحص التداخلات الفراغية بين شبكات ومجسمات التخصصات المختلفة (المعماري، الإنشائي، الكهروميكانيكي MEP).",
        "category_ar": "نمذجة البناء والتنسيق"
    },
    {
        "term_en": "False Positive",
        "full_en": "Non-critical Geometric Overlap",
        "term_ar": "إنذار كاذب / تداخل شكلي مسموح",
        "category": "BIM_DIGITAL",
        "definition_ar": "تداخل هندسي يظهر في تقرير الفحص ولكنه لا يشكل خطراً فعلياً لوقوعه ضمن حدود التفاوتات المعمارية المسموحة أو التداخلات المقبولة.",
        "category_ar": "نمذجة البناء والتنسيق"
    },
    {
        "term_en": "As-Built vs As-Planned",
        "full_en": "Actual Construction State vs Baseline Design",
        "term_ar": "المنفذ الفعلي مقارنة بالمخطط التعاقدي",
        "category": "BIM_DIGITAL",
        "definition_ar": "مقارنة حالة التنفيذ الفعلية في الموقع مع المخططات والجدول الزمني الأصلي المعتمد لاكتشاف الانحرافات والمطالبات.",
        "category_ar": "نمذجة البناء والتنسيق"
    },

    # 3. Schedule & Monte Carlo QSRA
    {
        "term_en": "CPM",
        "full_en": "Critical Path Method",
        "term_ar": "منهجية المسار الحرج",
        "category": "SCHEDULE_QSRA",
        "definition_ar": "طريقة رياضية لتحديد سلسلة الأنشطة الحرجة التي يؤدي أي تأخير في أي نشاط منها إلى تأخير الموعد النهائي لتسليم المشروع بالكامل.",
        "category_ar": "الجدولة والمحاكاة"
    },
    {
        "term_en": "Total Float (TF)",
        "full_en": "Total Float / Slack Time",
        "term_ar": "هامش السماحية الزمني الكلي",
        "category": "SCHEDULE_QSRA",
        "definition_ar": "أقصى مدة زمنية يمكن للنشاط أن يتأخر بها دون أن يتسبب في تأخير الموعد النهائي للمشروع (الأنشطة الحرجة تكون TF = 0).",
        "category_ar": "الجدولة والمحاكاة"
    },
    {
        "term_en": "QSRA / QCRA",
        "full_en": "Quantitative Schedule / Cost Risk Analysis",
        "term_ar": "التحليل الكمي لمخاطر الجدول الزمني والكلفة",
        "category": "SCHEDULE_QSRA",
        "definition_ar": "تطبيق النمذجة الإحصائية لتقدير التوزيع الاحتمالي لمدة وتكلفة المشروع النهائي واحتياطيات الطوارئ المطلوبة.",
        "category_ar": "الجدولة والمحاكاة"
    },
    {
        "term_en": "Monte Carlo Simulation",
        "full_en": "Probabilistic Monte Carlo Iteration Engine",
        "term_ar": "محاكاة مونت كارلو الاحتمالية",
        "category": "SCHEDULE_QSRA",
        "definition_ar": "خوارزمية حاسوبية تُجري آلاف الجولات العشوائية لحساب نطاقات الاحتمال لمدد وتكاليف المشروع عند دمج المخاطر.",
        "category_ar": "الجدولة والمحاكاة"
    },
    {
        "term_en": "Beta-PERT Distribution",
        "full_en": "Program Evaluation and Review Technique Beta Distribution",
        "term_ar": "توزيع بيتا-بيرت الإحصائي",
        "category": "SCHEDULE_QSRA",
        "definition_ar": "دالة توزيع احتمالي تعتمد على ثلاثة تقديرات (متفائل، مرجح، متشائم) وتمنح وزناً واقعياً للقيمة المرجحة في المشاريع الإنشائية.",
        "category_ar": "الجدولة والمحاكاة"
    },
    {
        "term_en": "S-Curve",
        "full_en": "Cumulative Probability Distribution Curve",
        "term_ar": "منحنى التوزيع التراكمي (S-Curve)",
        "category": "SCHEDULE_QSRA",
        "definition_ar": "رسم بياني تراكمي يُظهر احتمالية إنجاز المشروع ضمن موازنة أو مدة معينة عند مختلف مستويات الثقة (P10 إلى P90).",
        "category_ar": "الجدولة والمحاكاة"
    },
    {
        "term_en": "P80 Confidence Level",
        "full_en": "80th Percentile Risk Threshold",
        "term_ar": "مستوى الثقة الإحصائية 80%",
        "category": "SCHEDULE_QSRA",
        "definition_ar": "المعيار التعاقدي الآمن الموصى به دولياً لتسعير العطاءات وتحديد مدة العقد بحيث تكون نسبة النجاح والالتزام 80%.",
        "category_ar": "الجدولة والمحاكاة"
    },
    {
        "term_en": "Time / Cost Contingency",
        "full_en": "Buffer Allocation for Unknown Risks",
        "term_ar": "احتياطي الطوارئ الزمني والمالي",
        "category": "SCHEDULE_QSRA",
        "definition_ar": "مبالغ ومدد إضافية محسوبة إحصائياً تُضاف للموازنة والجدول الزمني للتحوط من المخاطر والأحداث غير المنظورة.",
        "category_ar": "الجدولة والمحاكاة"
    },
    {
        "term_en": "Tornado Diagram",
        "full_en": "Sensitivity Tornado Analysis",
        "term_ar": "مخطط تورنادو لتحليل الحساسية",
        "category": "SCHEDULE_QSRA",
        "definition_ar": "مخطط بياني يرتب الأنشطة والمخاطر تنازلياً وفق معامل ارتباط بيرسون لتحديد أكثر العوامل تحكماً في مسار المشروع.",
        "category_ar": "الجدولة والمحاكاة"
    },

    # 4. Contracts & Claims
    {
        "term_en": "EOT",
        "full_en": "Extension of Time for Completion",
        "term_ar": "تمديد مدة الإنجاز التعاقدية",
        "category": "CONTRACTS_FIDIC",
        "definition_ar": "حق المقاول في زيادة مدة العقد الأصلية دون غرامات نتيجة وقوع أحداث تأخير معوّضة ومبررة ناتجة عن صاحب العمل أو القوة القاهرة.",
        "category_ar": "العقود والمطالبات وفيديك"
    },
    {
        "term_en": "Prolongation Costs",
        "full_en": "Site Overhead & Extended Preliminaries Costs",
        "term_ar": "تكاليف استمرار الموقع والمصاريف الإدارية",
        "category": "CONTRACTS_FIDIC",
        "definition_ar": "التعويض المالي للمقاول عن المصاريف التشغيلية اليومية للكوادر والمعدات وإدارة الموقع خلال فترات التمديد المبررة المعوّضة.",
        "category_ar": "العقود والمطالبات وفيديك"
    },
    {
        "term_en": "Liquidated Damages",
        "full_en": "Pre-agreed Delay Penalties",
        "term_ar": "الغرامات والتعويضات التأخيرية المحددة",
        "category": "CONTRACTS_FIDIC",
        "definition_ar": "مبالغ مالية مقتطعة يومياً من المقاول عند تأخره غير المبرر عن موعد الإنجاز بموجب المادة 47 من الشروط العامة لمقاولات الهندسة المدنية.",
        "category_ar": "العقود والمطالبات وفيديك"
    },
    {
        "term_en": "Force Majeure",
        "full_en": "Exceptional Unforeseen Events",
        "term_ar": "القوة القاهرة والظروف الاستثنائية",
        "category": "CONTRACTS_FIDIC",
        "definition_ar": "أحداث استثنائية خارجة عن إرادة وسيطرة طرفي العقد ولا يمكن تفاديها (مثل: الكوارث الطبيعية، الحروب، وحرارة الصيف الشديدة).",
        "category_ar": "العقود والمطالبات وفيديك"
    },
    {
        "term_en": "FIDIC",
        "full_en": "Fédération Internationale Des Ingénieurs-Conseils",
        "term_ar": "الاتحاد الدولي للمهندسين الاستشاريين",
        "category": "CONTRACTS_FIDIC",
        "definition_ar": "المنظمة الدولية المصدرة لصيغ ونماذج العقود الهندسية القياسية المعتمدة عالمياً (مثل: الكتاب الأحمر والأصفر).",
        "category_ar": "العقود والمطالبات وفيديك"
    },
    {
        "term_en": "DAB / DAAB",
        "full_en": "Dispute Avoidance / Adjudication Board",
        "term_ar": "مجلس فض وتجنب النزاعات الهندسية",
        "category": "CONTRACTS_FIDIC",
        "definition_ar": "هيئة استشارية مستقلة من الخبراء تُشكل لحل الخلافات بين صاحب العمل والمقاول وإصدار قرارات ملزمة قبل اللجوء للتحكيم.",
        "category_ar": "العقود والمطالبات وفيديك"
    },
    {
        "term_en": "RFI",
        "full_en": "Request for Information",
        "term_ar": "طلب معلومات واستيضاح فني",
        "category": "CONTRACTS_FIDIC",
        "definition_ar": "مستند رسمي يرسله المقاول للمهندس المقيم للاستفسار عن غموض في المخططات أو طلب تفاصيل إضافية لتنفيذ الأعمال.",
        "category_ar": "العقود والمطالبات وفيديك"
    },
    {
        "term_en": "Variation Order (V.O.)",
        "full_en": "Change Order / Variation Instruction",
        "term_ar": "أمر التغيير / أمر الغيار العقدي",
        "category": "CONTRACTS_FIDIC",
        "definition_ar": "توجيه خطي صادر من المهندس أو صاحب العمل بتعديل أو إضافة أو حذف جزء من الأعمال وتعديل الكلفة والمدة تبعاً لذلك.",
        "category_ar": "العقود والمطالبات وفيديك"
    },
    {
        "term_en": "Price Escalation",
        "full_en": "Adjustments for Changes in Cost (FIDIC 13.8)",
        "term_ar": "تعديل وتضخم أسعار المواد",
        "category": "CONTRACTS_FIDIC",
        "definition_ar": "آلية تعاقدية لتعويض المقاول عن الارتفاع الكبير في أسعار المواد الأساسية (الحديد، الإسمنت، الوقود) وفق نشرات الأسعار الرسمية.",
        "category_ar": "العقود والمطالبات وفيديك"
    },

    # 5. Risk & Geo-Risk
    {
        "term_en": "ISO 31000:2018",
        "full_en": "International Risk Management Guidelines",
        "term_ar": "المعيار الدولي لإدارة المخاطر",
        "category": "RISK_GEO",
        "definition_ar": "المعيار القياسي الدولي الذي يحدد مبادئ وإطار وعمليات تحديد وتحليل وتقييم ومعالجة المخاطر في المؤسسات والمشاريع.",
        "category_ar": "إدارة المخاطر والجيوتقنيك"
    },
    {
        "term_en": "ALARP",
        "full_en": "As Low As Reasonably Practicable",
        "term_ar": "أدنى مستوى خطر ممكن عملياً",
        "category": "RISK_GEO",
        "definition_ar": "مبدأ هندسي لتحديد النطاق المقبول للمخاطر التي تم تقليصها إلى الحد الذي تكون فيه كلفة التخفيف الإضافي غير متناسبة مع الفائدة.",
        "category_ar": "إدارة المخاطر والجيوتقنيك"
    },
    {
        "term_en": "Wellpoint Dewatering",
        "full_en": "Groundwater Lowering System",
        "term_ar": "منظومة النزح المائي الجوفي",
        "category": "RISK_GEO",
        "definition_ar": "شبكة من الأنابيب والمضخات الماصة تُستخدم لخفض منسوب المياه الجوفية وتجفيف حفر الأساسات في المواقع ذات المنسوب المرتفع.",
        "category_ar": "إدارة المخاطر والجيوتقنيك"
    },
    {
        "term_en": "Gypsiferous Soils",
        "full_en": "Collapsible Gypsum-Rich Soil Formations",
        "term_ar": "التربة الجبسية الانهيارية",
        "category": "RISK_GEO",
        "definition_ar": "تكوينات تربة غنية بكبريتات الكالسيوم (شائعة في صلاح الدين والأنبار ونينوى) تذوب وتهبط فجائياً عند ملامستها للمياه.",
        "category_ar": "إدارة المخاطر والجيوتقنيك"
    }
]

def search_glossary(query: str = "", category: str = "ALL") -> List[Dict[str, Any]]:
    """البحث والفلترة الفورية في معجم المصطلحات"""
    results = []
    q = query.strip().lower()
    for item in GLOSSARY_TERMS:
        if category != "ALL" and item["category"] != category:
            continue
        if q:
            match_en = q in item["term_en"].lower() or q in item["full_en"].lower()
            match_ar = q in item["term_ar"].lower() or q in item["definition_ar"].lower()
            if not (match_en or match_ar):
                continue
        results.append(item)
    return results
