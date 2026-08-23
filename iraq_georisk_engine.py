"""
================================================================================
محرك الموقع الجغرافي وخريطة العراق المكانية وتحليل المخاطر البيئية (Iraq GIS Geo-Risk Engine)
ICRAT 2.0 - Iraq Construction Risk Assessment Tool
المطور: Dr Ahmed Louay Ahmed
معيار التوافق: ISO 31000 / الشروط العامة لمقاولات أعمال الهندسة المدنية (العراقية)
================================================================================
"""

import os
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components
from typing import Dict, Any, List, Optional, Tuple

_COMP_DIR = os.path.join(os.path.dirname(__file__), "iraq_map_component")
_iraq_map_component = components.declare_component("iraq_map_component", path=_COMP_DIR)

def render_interactive_map(
    selected_gov_key: str = "BAGHDAD",
    project_lat: float = 33.3152,
    project_lon: float = 44.3661,
    initial_map_type: str = "SATELLITE",
    key: str = "iraq_gis_map_component"
) -> Optional[Dict[str, Any]]:
    """عرض خريطة العراق التفاعلية واستقبال الإحداثيات مباشرة عند النقر أو الضغط على زر الاعتماد"""
    return _iraq_map_component(
        govs=IRAQ_GOVERNORATES_DB,
        selected_gov_key=selected_gov_key,
        project_lat=project_lat,
        project_lon=project_lon,
        initial_map_type=initial_map_type,
        key=key,
        default=None
    )

# قاعدة بيانات المخاطر المكانية والجيوتقنية والمناخية لمحافظات العراق الـ 18
IRAQ_GOVERNORATES_DB: Dict[str, Dict[str, Any]] = {
    "BAGHDAD": {
        "name_ar": "بغداد",
        "name_en": "Baghdad",
        "region": "CENTRAL",
        "region_ar": "الفرات الأوسط / العاصمة",
        "lat": 33.3152,
        "lon": 44.3661,
        "soil_type_ar": "تربة طميية رسوبية (Alluvial Clay/Silt)",
        "groundwater_depth_m": 2.5,
        "salinity_sulfate_risk": "متوسط (Moderate)",
        "salinity_badge": "🟡 متوسط",
        "dewatering_risk": "متوسط (يتطلب نزح مائي عند الحفر أسفل 2.5م)",
        "foundation_recommendation_ar": "أساسات حصيرة خرسانية مع إسمنت مقاوم للأملاح (SRC) أو ركائز حفر",
        "summer_heat_index": 82, # مؤشر الإجهاد الحراري صيفاً (0-100)
        "sandstorm_days_year": 18,
        "flood_vulnerability": "متوسطة (طفح شبكات المجاري)",
        "traffic_closure_risk": "مرتفع (زيارة الإمام الكاظم، مناسبات رسمية، ازدحامات يومية)",
        "quarry_source_ar": "مقالع النباعي والتاجي والصويرة (35 - 70 كم)",
        "port_distance_km": 540, # عن ميناء أم قصر
        "uxo_risk_ar": "منخفض / يتطلب كشف خدمات تحت الأرض مزدحمة",
        "overall_geo_risk_score": 68
    },
    "BASRA": {
        "name_ar": "البصرة",
        "name_en": "Basra",
        "region": "SOUTH",
        "region_ar": "المنطقة الجنوبية الساحلية",
        "lat": 30.5081,
        "lon": 47.7835,
        "soil_type_ar": "تربة سبخة رخوة عالية الرطوبة والملوحة (Saline Sabkha & Mud)",
        "groundwater_depth_m": 1.2,
        "salinity_sulfate_risk": "حرج وشديد العدوانية (Critical Aggressive Sulfates)",
        "salinity_badge": "🔴 حرج جداً",
        "dewatering_risk": "حرج ومستمر (Continuous Wellpoint Dewatering System)",
        "foundation_recommendation_ar": "ركائز خرسانية عميقة مسبقة الصب أو مدقوقة مع عزل مائي ثقيل ومقاوم للأملاح",
        "summer_heat_index": 96, # رطوبة وحرارة تتجاوز 52 مئوية
        "sandstorm_days_year": 22,
        "flood_vulnerability": "مرتفعة (مد وجزر مياه شط العرب ومياه الأمطار)",
        "traffic_closure_risk": "متوسط / طقس صيفي قاهر يمنع الصب نهاراً",
        "quarry_source_ar": "مقالع الدبدبة وأم قصر وسنام (40 - 80 كم)",
        "port_distance_km": 45, # ملاصق لميناء أم قصر وخور الزبير
        "uxo_risk_ar": "متوسط في المناطق المفتوحة والشريط الحدودي",
        "overall_geo_risk_score": 88
    },
    "NINEVEH": {
        "name_ar": "نينوى (الموصل)",
        "name_en": "Nineveh (Mosul)",
        "region": "NORTH",
        "region_ar": "المنطقة الشمالية المتموجة",
        "lat": 36.3489,
        "lon": 43.1577,
        "soil_type_ar": "تربة حصوية حجرية جيرية مع مناطق طينية (Gravelly Limestone)",
        "groundwater_depth_m": 8.0,
        "salinity_sulfate_risk": "منخفض إلى متوسط (Low to Moderate)",
        "salinity_badge": "🟢 منخفض",
        "dewatering_risk": "منخفض",
        "foundation_recommendation_ar": "قواعد شريطية أو منفردة على تربة قوية مع فحص تجاويف الصخور الجيرية",
        "summer_heat_index": 65,
        "sandstorm_days_year": 12,
        "flood_vulnerability": "متوسطة (سيول الوديان المحاذية)",
        "traffic_closure_risk": "منخفض",
        "quarry_source_ar": "مقالع بادوش وحاوي الكنيسة والكوير (15 - 40 كم)",
        "port_distance_km": 920,
        "uxo_risk_ar": "مرتفع في المناطق القديمة (يتطلب مسح أمني وخلو مخلفات UXO)",
        "overall_geo_risk_score": 72
    },
    "ERBIL": {
        "name_ar": "أربيل",
        "name_en": "Erbil",
        "region": "KURDISTAN",
        "region_ar": "إقليم كردستان الشمالي",
        "lat": 36.1911,
        "lon": 44.0091,
        "soil_type_ar": "تربة طينية متماسكة وصخرية جبلية (Rocky & Stiff Clay)",
        "groundwater_depth_m": 15.0,
        "salinity_sulfate_risk": "منخفض جداً (Very Low)",
        "salinity_badge": "🟢 منخفض",
        "dewatering_risk": "منعدم / منخفض جداً",
        "foundation_recommendation_ar": "قواعد خرسانية مباشرة مع دراسة ثبات المنحدرات (Slope Stability)",
        "summer_heat_index": 55,
        "sandstorm_days_year": 6,
        "flood_vulnerability": "منخفضة إلى متوسطة في الوديان",
        "traffic_closure_risk": "منخفض",
        "quarry_source_ar": "مقالع هولير وكركوك ومحمور (20 - 45 كم)",
        "port_distance_km": 870,
        "uxo_risk_ar": "منخفض جداً ومستقر",
        "overall_geo_risk_score": 45
    },
    "SULAIMANIYAH": {
        "name_ar": "السليمانية",
        "name_en": "Sulaymaniyah",
        "region": "KURDISTAN",
        "region_ar": "المنطقة الجبلية الشرقية",
        "lat": 35.5570,
        "lon": 45.4359,
        "soil_type_ar": "تكوينات صخرية جبلية وترب رسوبية جبلية",
        "groundwater_depth_m": 18.0,
        "salinity_sulfate_risk": "منخفض جداً",
        "salinity_badge": "🟢 منخفض",
        "dewatering_risk": "منخفض",
        "foundation_recommendation_ar": "تأسيس صخري مع تدعيم جدران السند والاحتياط الزلزالي",
        "summer_heat_index": 50,
        "sandstorm_days_year": 5,
        "flood_vulnerability": "سيول جبلية وثلوج شتوية تعيق العمل",
        "traffic_closure_risk": "منخفض",
        "quarry_source_ar": "مقالع بازيان وطاسلوجة (15 - 35 كم)",
        "port_distance_km": 790,
        "uxo_risk_ar": "منخفض في المراكز الحضرية",
        "overall_geo_risk_score": 42
    },
    "DUHOK": {
        "name_ar": "دهوك",
        "name_en": "Duhok",
        "region": "KURDISTAN",
        "region_ar": "المنطقة الجبلية الشمالية الحدودية",
        "lat": 36.8679,
        "lon": 42.9886,
        "soil_type_ar": "صخور كلسية وترب جبلية منحدرة",
        "groundwater_depth_m": 20.0,
        "salinity_sulfate_risk": "منخفض",
        "salinity_badge": "🟢 منخفض",
        "dewatering_risk": "منخفض",
        "foundation_recommendation_ar": "قواعد على صخور صلبة مع جدران ساندة للتربة",
        "summer_heat_index": 48,
        "sandstorm_days_year": 4,
        "flood_vulnerability": "ثلوج شتوية وانخفاض درجات الحرارة لما دون الصفر",
        "traffic_closure_risk": "منخفض",
        "quarry_source_ar": "مقالع زاخو وفايدة (20 - 40 كم)",
        "port_distance_km": 990,
        "uxo_risk_ar": "منخفض في المدن",
        "overall_geo_risk_score": 44
    },
    "KIRKUK": {
        "name_ar": "كركوك",
        "name_en": "Kirkuk",
        "region": "NORTH_CENTRAL",
        "region_ar": "المنطقة المتموجة النفطية",
        "lat": 35.4681,
        "lon": 44.3922,
        "soil_type_ar": "تربة طميية وحصوية مع تكوينات نفطية هيدروكربونية",
        "groundwater_depth_m": 6.0,
        "salinity_sulfate_risk": "متوسط",
        "salinity_badge": "🟡 متوسط",
        "dewatering_risk": "متوسط",
        "foundation_recommendation_ar": "قواعد حصيرة أو ركائز مع عزل هيدروكربوني للمياه",
        "summer_heat_index": 75,
        "sandstorm_days_year": 14,
        "flood_vulnerability": "متوسطة",
        "traffic_closure_risk": "منخفض إلى متوسط",
        "quarry_source_ar": "مقالع التون كوبري وداقوق (25 - 50 كم)",
        "port_distance_km": 680,
        "uxo_risk_ar": "متوسط في أطراف المحافظة",
        "overall_geo_risk_score": 62
    },
    "ANBAR": {
        "name_ar": "الأنبار (الرمادي / الفلوجة)",
        "name_en": "Al-Anbar",
        "region": "WEST",
        "region_ar": "الهضبة الغربية والصحراوية",
        "lat": 33.4233,
        "lon": 43.2974,
        "soil_type_ar": "تربة رملية جبسية معرضة للهبوط بالماء (Gypiferous Sand & Silt)",
        "groundwater_depth_m": 7.5,
        "salinity_sulfate_risk": "مرتفع بسبب الجبس والكبريتات (Gypiferous Soil)",
        "salinity_badge": "🟠 مرتفع جبسي",
        "dewatering_risk": "منخفض (لكن حساس جداً لتسرب المياه)",
        "foundation_recommendation_ar": "استبدال التربة الجبسية أو الدمك الديناميكي واستخدام خرسانة عازلة محكمة",
        "summer_heat_index": 85,
        "sandstorm_days_year": 28,
        "flood_vulnerability": "سيول وادي حوران والوديان الصحراوية",
        "traffic_closure_risk": "منخفض",
        "quarry_source_ar": "مقالع الحبانية والصقلاوية والرمادي (15 - 45 كم)",
        "port_distance_km": 620,
        "uxo_risk_ar": "مرتفع في المناطق المفتوحة وغير المطورة (يتطلب كشف مسحي)",
        "overall_geo_risk_score": 75
    },
    "KARBALA": {
        "name_ar": "كربلاء المقدسة",
        "name_en": "Karbala",
        "region": "EUPHRATES",
        "region_ar": "منطقة الفرات الأوسط",
        "lat": 32.6160,
        "lon": 44.0249,
        "soil_type_ar": "تربة رملية طينية رسوبية تتدرج لهضبة جبسية غرباً",
        "groundwater_depth_m": 3.0,
        "salinity_sulfate_risk": "متوسط إلى مرتفع",
        "salinity_badge": "🟡 متوسط-مرتفع",
        "dewatering_risk": "مرتفع في مركز المدينة القديمة والبحيرة",
        "foundation_recommendation_ar": "أساسات حصيرة خرسانية مع تدعيم الجوانب ونزح مائي",
        "summer_heat_index": 84,
        "sandstorm_days_year": 20,
        "flood_vulnerability": "متوسطة",
        "traffic_closure_risk": "حرج جداً 🔴 (الزيارة الأربعينية وعاشوراء تغلق الطرق 15-20 يوماً سنوياً)",
        "quarry_source_ar": "مقالع الإخيضر وعين التمر (30 - 65 كم)",
        "port_distance_km": 460,
        "uxo_risk_ar": "منخفض جداً",
        "overall_geo_risk_score": 82
    },
    "NAJAF": {
        "name_ar": "النجف الأشرف",
        "name_en": "Najaf",
        "region": "EUPHRATES",
        "region_ar": "منطقة الفرات الأوسط والهضبة",
        "lat": 32.0259,
        "lon": 44.3462,
        "soil_type_ar": "تربة رملية جبسية وهضبة صخرية رملية جافة",
        "groundwater_depth_m": 5.5,
        "salinity_sulfate_risk": "مرتفع للجبس",
        "salinity_badge": "🟠 مرتفع جبسي",
        "dewatering_risk": "منخفض في الهضبة / مرتفع قرب بحر النجف",
        "foundation_recommendation_ar": "أساسات حصيرة مع فحص عمق الطبقات الجبسية وعزل القواعد",
        "summer_heat_index": 88,
        "sandstorm_days_year": 24,
        "flood_vulnerability": "سيول الهضبة الغربية باتجاه بحر النجف",
        "traffic_closure_risk": "حرج جداً 🔴 (الزيارات المليونية وقطوعات النقل والمواد)",
        "quarry_source_ar": "مقالع الرهيمة وبحر النجف (20 - 45 كم)",
        "port_distance_km": 420,
        "uxo_risk_ar": "منخفض جداً",
        "overall_geo_risk_score": 79
    },
    "BABIL": {
        "name_ar": "بابل (الحلة)",
        "name_en": "Babil (Hillah)",
        "region": "EUPHRATES",
        "region_ar": "حوض الفرات الأوسط الزراعي",
        "lat": 32.4847,
        "lon": 44.4312,
        "soil_type_ar": "تربة طميية رسوبية زراعية ثقيلة وعالية التماسك",
        "groundwater_depth_m": 2.0,
        "salinity_sulfate_risk": "متوسط إلى مرتفع",
        "salinity_badge": "🟡 متوسط",
        "dewatering_risk": "مرتفع لوجود جداول الري المتفرعة",
        "foundation_recommendation_ar": "أساسات حصيرة مع نزح مائي دقيق واستخدام إسمنت مقاوم",
        "summer_heat_index": 82,
        "sandstorm_days_year": 16,
        "flood_vulnerability": "ارتفاع مناسيب قنوات الري",
        "traffic_closure_risk": "مرتفع خلال مواسم مرور الزائرين نحو كربلاء",
        "quarry_source_ar": "مقالع الصويرة وجنوب بغداد (40 - 80 كم)",
        "port_distance_km": 470,
        "uxo_risk_ar": "منخفض",
        "overall_geo_risk_score": 67
    },
    "WASIT": {
        "name_ar": "واسط (الكوت)",
        "name_en": "Wasit (Kut)",
        "region": "TIGRIS",
        "region_ar": "حوض دجلة الأوسط الشرقي",
        "lat": 32.5085,
        "lon": 45.8197,
        "soil_type_ar": "تربة طينية رسوبية زراعية",
        "groundwater_depth_m": 2.2,
        "salinity_sulfate_risk": "متوسط إلى مرتفع",
        "salinity_badge": "🟡 متوسط",
        "dewatering_risk": "مرتفع قرب مجرى نهر دجلة والغراف",
        "foundation_recommendation_ar": "أساسات حصيرة مسلحة مع عزل مائي وإسمنت SRC",
        "summer_heat_index": 85,
        "sandstorm_days_year": 18,
        "flood_vulnerability": "سيول قادمة من الحدود الشرقية",
        "traffic_closure_risk": "متوسط",
        "quarry_source_ar": "مقالع الصويرة وجباب وزرباطية (35 - 75 كم)",
        "port_distance_km": 390,
        "uxo_risk_ar": "متوسط في الشريط الحدودي الشرقي",
        "overall_geo_risk_score": 65
    },
    "DHI_QAR": {
        "name_ar": "ذي قار (الناصرية)",
        "name_en": "Dhi Qar (Nasiriyah)",
        "region": "SOUTH",
        "region_ar": "المنطقة الجنوبية وأهوار الفرات",
        "lat": 31.0579,
        "lon": 46.2573,
        "soil_type_ar": "تربة رسوبية طميية رخوة عالية الملوحة ورطوبة الأهوار",
        "groundwater_depth_m": 1.5,
        "salinity_sulfate_risk": "مرتفع جداً (High Sulfates)",
        "salinity_badge": "🔴 مرتفع جداً",
        "dewatering_risk": "حرج ويتطلب مضخات نزح مستمرة",
        "foundation_recommendation_ar": "ركائز حفر خرسانية أو حصيرة معالجة بالمواد المانعة لتسرب الأملاح",
        "summer_heat_index": 92,
        "sandstorm_days_year": 24,
        "flood_vulnerability": "ارتفاع مناسيب المياه وتوسع مناطق الأهوار",
        "traffic_closure_risk": "متوسط",
        "quarry_source_ar": "مقالع البصرة وغرب الناصرية (50 - 100 كم)",
        "port_distance_km": 180,
        "uxo_risk_ar": "متوسط",
        "overall_geo_risk_score": 81
    },
    "MAYSAN": {
        "name_ar": "ميسان (العمارة)",
        "name_en": "Maysan (Amara)",
        "region": "SOUTH",
        "region_ar": "المنطقة الجنوبية وحوض أهوار دجلة",
        "lat": 31.8449,
        "lon": 47.1448,
        "soil_type_ar": "تربة طميية رخوة مشبعة بالمياه ونطاقات سبخة",
        "groundwater_depth_m": 1.4,
        "salinity_sulfate_risk": "مرتفع جداً",
        "salinity_badge": "🔴 مرتفع جداً",
        "dewatering_risk": "حرج ومستمر",
        "foundation_recommendation_ar": "ركائز أو استبدال تربة عميق مع إسمنت فائق المقاومة للأملاح",
        "summer_heat_index": 90,
        "sandstorm_days_year": 22,
        "flood_vulnerability": "سيول موسمية من المرتفعات الشرقية ومياه الأهوار",
        "traffic_closure_risk": "متوسط",
        "quarry_source_ar": "مقالع الطيب وعلي الغربي (45 - 80 كم)",
        "port_distance_km": 190,
        "uxo_risk_ar": "مرتفع في الشريط الحدودي ومناطق الطيب",
        "overall_geo_risk_score": 83
    },
    "MUTHANNA": {
        "name_ar": "المثنى (السماوة)",
        "name_en": "Al-Muthanna (Samawah)",
        "region": "SOUTH_WEST",
        "region_ar": "المنطقة الجنوبية الغربية والصحراوية",
        "lat": 31.3255,
        "lon": 45.2818,
        "soil_type_ar": "تربة رملية جبسية وصخور كلسية ملحية (بحيرة ساوة)",
        "groundwater_depth_m": 4.0,
        "salinity_sulfate_risk": "مرتفع كبريتياً وجبسياً",
        "salinity_badge": "🟠 مرتفع",
        "dewatering_risk": "متوسط",
        "foundation_recommendation_ar": "أساسات حصيرة مع عزل كيميائي للخرسانة ضد الأملاح الجبسية",
        "summer_heat_index": 89,
        "sandstorm_days_year": 26,
        "flood_vulnerability": "سيول الوديان الجنوبية باتجاه الفرات",
        "traffic_closure_risk": "منخفض",
        "quarry_source_ar": "مقالع النجمة وبصية والبطحاء (30 - 70 كم)",
        "port_distance_km": 280,
        "uxo_risk_ar": "متوسط في البادية الجنوبية",
        "overall_geo_risk_score": 76
    },
    "QADISIYYAH": {
        "name_ar": "الديوانية (القادسية)",
        "name_en": "Al-Qadisiyyah (Diwaniyah)",
        "region": "EUPHRATES",
        "region_ar": "حوض الفرات الأوسط الرسوبي",
        "lat": 31.9922,
        "lon": 44.9250,
        "soil_type_ar": "تربة طميية رسوبية زراعية مع مناطق ملحية",
        "groundwater_depth_m": 2.1,
        "salinity_sulfate_risk": "متوسط إلى مرتفع",
        "salinity_badge": "🟡 متوسط",
        "dewatering_risk": "مرتفع في المناطق الحضرية",
        "foundation_recommendation_ar": "أساسات حصيرة خرسانية مع عزل مائي وإسمنت SRC",
        "summer_heat_index": 86,
        "sandstorm_days_year": 20,
        "flood_vulnerability": "متوسطة",
        "traffic_closure_risk": "متوسط (طريق مرور الزائرين)",
        "quarry_source_ar": "مقالع غرب الفرات والنجف (40 - 75 كم)",
        "port_distance_km": 340,
        "uxo_risk_ar": "منخفض",
        "overall_geo_risk_score": 70
    },
    "DIYALA": {
        "name_ar": "ديالى (بعقوبة)",
        "name_en": "Diyala (Baqubah)",
        "region": "EAST_CENTRAL",
        "region_ar": "حوض نهر ديالى والمنطقة الشرقية",
        "lat": 33.7438,
        "lon": 44.6462,
        "soil_type_ar": "تربة طينية رسوبية وحصوية متدرجة شرقاً",
        "groundwater_depth_m": 3.5,
        "salinity_sulfate_risk": "متوسط",
        "salinity_badge": "🟡 متوسط",
        "dewatering_risk": "متوسط",
        "foundation_recommendation_ar": "قواعد منفردة أو شريطية أو حصيرة حسب دراسة التربة",
        "summer_heat_index": 78,
        "sandstorm_days_year": 16,
        "flood_vulnerability": "سيول الوديان الشرقية القادمة من حمرين والحدود",
        "traffic_closure_risk": "متوسط",
        "quarry_source_ar": "مقالع حمرين والصور وقره تبه (25 - 60 كم)",
        "port_distance_km": 590,
        "uxo_risk_ar": "متوسط في بعض بساتين وقواطع حمرين",
        "overall_geo_risk_score": 66
    },
    "SALAH_AL_DIN": {
        "name_ar": "صلاح الدين (تكريت / سامراء)",
        "name_en": "Salah al-Din (Tikrit/Samarra)",
        "region": "NORTH_CENTRAL",
        "region_ar": "حوض دجلة الشمالي الأوسط",
        "lat": 34.6060,
        "lon": 43.6793,
        "soil_type_ar": "تربة حصوية ورملية جافة مع تكوينات طينية رسوبية",
        "groundwater_depth_m": 5.0,
        "salinity_sulfate_risk": "متوسط",
        "salinity_badge": "🟡 متوسط",
        "dewatering_risk": "متوسط قرب دجلة والثرثار",
        "foundation_recommendation_ar": "قواعد شريطية أو حصيرة مع مراعاة فحص الجبس في المناطق الغربية",
        "summer_heat_index": 78,
        "sandstorm_days_year": 20,
        "flood_vulnerability": "متوسطة",
        "traffic_closure_risk": "مرتفع في محيط سامراء خلال الزيارات الدينية",
        "quarry_source_ar": "مقالع مكحول والدور وسامراء (20 - 50 كم)",
        "port_distance_km": 670,
        "uxo_risk_ar": "متوسط (يتطلب مسح أمني وخلو مخلفات)",
        "overall_geo_risk_score": 71
    }
}

def get_governorate_profile(gov_key_or_name: str) -> Dict[str, Any]:
    """استرجاع الملف الجيوتقني والمكاني للمحافظة"""
    k = str(gov_key_or_name).upper().strip()
    if k in IRAQ_GOVERNORATES_DB:
        return IRAQ_GOVERNORATES_DB[k]
    
    # البحث بالاسم العربي
    for key, data in IRAQ_GOVERNORATES_DB.items():
        if data["name_ar"] in gov_key_or_name or gov_key_or_name in data["name_ar"]:
            return data
            
    # افتراضي: بغداد
    return IRAQ_GOVERNORATES_DB["BAGHDAD"]

def find_nearest_governorate(lat: float, lon: float) -> Tuple[str, float]:
    """
    تحديد أقرب محافظة عراقية للإحداثيات المعطاة وحساب المسافة بالكيلومتر
    """
    min_dist = float("inf")
    best_key = "BAGHDAD"
    import math
    R = 6371.0  # نصف قطر الأرض بالكيلومتر
    for k, data in IRAQ_GOVERNORATES_DB.items():
        dlat = math.radians(data["lat"] - lat)
        dlon = math.radians(data["lon"] - lon)
        a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(data["lat"])) * math.sin(dlon / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        dist_km = R * c
        if dist_km < min_dist:
            min_dist = dist_km
            best_key = k
    return best_key, min_dist

def generate_leaflet_map_html(
    selected_gov_key: str = "BAGHDAD",
    project_lat: float = 33.3152,
    project_lon: float = 44.3661,
    project_name: str = "مشروع إنشائي عراقي",
    initial_map_type: str = "SATELLITE",
    height_px: int = 540
) -> str:
    """
    توليد خريطة Leaflet تفاعلية تتيح النقر في أي مكان في العراق وتحريك الماوس وسحب النجمة لتحديد الموقع
    """
    import json
    govs_json = json.dumps(IRAQ_GOVERNORATES_DB, ensure_ascii=False)
    prof = get_governorate_profile(selected_gov_key)
    
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خريطة العراق المكانية التفاعلية</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        body {{ background: transparent; overflow: hidden; }}
        #map {{ width: 100%; height: {height_px}px; border-radius: 12px; z-index: 1; border: 1px solid #CBD5E1; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        
        /* Floating Info HUD */
        .info-hud {{
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 1000;
            background: rgba(15, 23, 42, 0.90);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            color: #FFFFFF;
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.35);
            border: 1px solid rgba(255,255,255,0.18);
            min-width: 280px;
            max-width: 330px;
            direction: rtl;
            text-align: right;
            transition: all 0.3s ease;
        }}
        .info-hud-title {{
            font-size: 0.95rem;
            font-weight: 800;
            color: #60A5FA;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            padding-bottom: 6px;
        }}
        .hud-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.82rem;
            margin-bottom: 5px;
        }}
        .hud-lbl {{ color: #94A3B8; font-weight: 600; }}
        .hud-val {{ color: #F8FAFC; font-weight: 700; }}
        .hud-badge-click {{
            background: linear-gradient(135deg, #2563EB, #1D4ED8);
            color: #FFFFFF;
            font-size: 0.76rem;
            font-weight: 700;
            padding: 5px 8px;
            border-radius: 6px;
            text-align: center;
            margin-top: 8px;
            border: 1px solid rgba(255,255,255,0.25);
            animation: pulse-border 2s infinite;
        }}
        @keyframes pulse-border {{
            0% {{ box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.6); }}
            70% {{ box-shadow: 0 0 0 8px rgba(59, 130, 246, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }}
        }}

        /* Custom Project Pin Marker */
        .project-pin-icon {{
            background: #2563EB;
            border: 3px solid #FFFFFF;
            border-radius: 50%;
            width: 34px !important;
            height: 34px !important;
            box-shadow: 0 0 22px rgba(37, 99, 235, 0.95);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #FFFFFF;
            font-weight: 900;
            font-size: 16px;
            cursor: grab;
        }}
        .project-pin-icon:active {{ cursor: grabbing; }}
        .gov-dot-icon {{
            border: 2px solid #FFFFFF;
            border-radius: 50%;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }}
        .leaflet-popup-content-wrapper {{
            border-radius: 10px;
            padding: 4px;
            font-family: 'Cairo', sans-serif;
            direction: rtl;
            text-align: right;
            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
        }}
        .leaflet-popup-content {{
            font-size: 0.85rem;
            line-height: 1.6;
            margin: 10px 14px;
        }}
        .hud-apply-btn {{
            width: 100%;
            background: linear-gradient(135deg, #10B981, #059669);
            color: #FFFFFF;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            padding: 7px 10px;
            font-size: 0.82rem;
            font-weight: 800;
            cursor: pointer;
            margin-top: 8px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
        }}
        .hud-apply-btn:hover {{
            background: linear-gradient(135deg, #059669, #047857);
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(16, 185, 129, 0.5);
        }}
        .hud-apply-btn:active {{
            transform: translateY(1px);
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    
    <div class="info-hud" id="hudBox">
        <div class="info-hud-title">
            <span>🎯 الموقع المحدد بالماوس</span>
            <span style="font-size:0.75rem; background:#1E3A8A; color:#93C5FD; padding:2px 6px; border-radius:4px; font-weight:700;" id="hudLiveTag">مباشر</span>
        </div>
        <div class="hud-row">
            <span class="hud-lbl">🌐 خط العرض (Lat):</span>
            <span class="hud-val" id="hudLat">{project_lat:.4f}° N</span>
        </div>
        <div class="hud-row">
            <span class="hud-lbl">🌐 خط الطول (Lon):</span>
            <span class="hud-val" id="hudLon">{project_lon:.4f}° E</span>
        </div>
        <div class="hud-row">
            <span class="hud-lbl">🏛️ أقرب محافظة:</span>
            <span class="hud-val" style="color:#FBBF24;" id="hudGov">{prof['name_ar']}</span>
        </div>
        <div class="hud-row">
            <span class="hud-lbl">💧 المياه الجوفية:</span>
            <span class="hud-val" id="hudWater">{prof['groundwater_depth_m']} م</span>
        </div>
        <button id="hudSyncBtn" class="hud-apply-btn" onclick="applyAndCopyCoords()">
            ⚡ اعتماد ونسخ الإحداثيات المحددة
        </button>
        <div id="hudNotice" style="display:none; background:#065F46; color:#A7F3D0; font-size:0.75rem; padding:4px 6px; border-radius:4px; margin-top:6px; text-align:center; font-weight:700;"></div>
        <div class="hud-badge-click">
            👆 انقر بالماوس في أي مكان بالعراق أو اسحب النجمة لتحديد الموقع
        </div>
    </div>

    <script>
        var GOVERNORATES = {govs_json};
        var currentLat = {project_lat};
        var currentLon = {project_lon};
        
        // 1. تعريف طبقات الخرائط
        var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            maxZoom: 19,
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS'
        }});

        var streetsLayer = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap'
        }});

        var topoLayer = L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 17,
            attribution: 'Map data: &copy; OpenStreetMap, SRTM'
        }});

        // 2. إنشاء الخريطة
        var initLayer = ('{initial_map_type}' === 'SATELLITE') ? satelliteLayer : streetsLayer;
        var map = L.map('map', {{
            center: [currentLat, currentLon],
            zoom: 6,
            layers: [initLayer]
        }});

        // 3. أداة التبديل بين الطبقات
        var baseMaps = {{
            "🛰️ أقمار صناعية (Satellite)": satelliteLayer,
            "🗺️ شوارع قياسية (OpenStreetMap)": streetsLayer,
            "⛰️ تضاريس وطبوغرافيا (Topography)": topoLayer
        }};
        L.control.layers(baseMaps, null, {{ position: 'topleft' }}).addTo(map);
        L.control.scale({{ metric: true, imperial: false, position: 'bottomleft' }}).addTo(map);

        // 4. دالة حساب أقرب محافظة في المتصفح
        function calculateNearestGov(lat, lon) {{
            var minD = Infinity;
            var bestK = 'BAGHDAD';
            var R = 6371.0;
            for (var k in GOVERNORATES) {{
                var g = GOVERNORATES[k];
                var dlat = (g.lat - lat) * Math.PI / 180.0;
                var dlon = (g.lon - lon) * Math.PI / 180.0;
                var a = Math.sin(dlat/2)*Math.sin(dlat/2) + 
                        Math.cos(lat*Math.PI/180.0) * Math.cos(g.lat*Math.PI/180.0) * 
                        Math.sin(dlon/2)*Math.sin(dlon/2);
                var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                var dist = R * c;
                if (dist < minD) {{
                    minD = dist;
                    bestK = k;
                }}
            }}
            return {{ key: bestK, data: GOVERNORATES[bestK], distKm: dist }};
        }}

        // 5. إضافة نقاط المحافظات الـ 18
        for (var k in GOVERNORATES) {{
            var g = GOVERNORATES[k];
            var dotColor = g.overall_geo_risk_score >= 80 ? '#EF4444' : (g.overall_geo_risk_score >= 65 ? '#F59E0B' : '#10B981');
            
            var govIcon = L.divIcon({{
                className: 'gov-dot-icon',
                html: '<div style=\"background:' + dotColor + '; width:12px; height:12px; border-radius:50%;\"></div>',
                iconSize: [12, 12],
                iconAnchor: [6, 6]
            }});

            var marker = L.marker([g.lat, g.lon], {{ icon: govIcon }}).addTo(map);
            marker.bindTooltip('<b>📍 ' + g.name_ar + '</b><br>المخاطر: ' + g.overall_geo_risk_score + '/100', {{
                direction: 'top'
            }});
        }}

        // 6. علامة المشروع الميدانية القابلة للسحب والنقر
        var projectPinIcon = L.divIcon({{
            className: 'project-pin-icon',
            html: '🎯',
            iconSize: [34, 34],
            iconAnchor: [17, 17]
        }});

        var projectMarker = L.marker([currentLat, currentLon], {{
            icon: projectPinIcon,
            draggable: true,
            zIndexOffset: 1000
        }}).addTo(map);

        var radarCircle = L.circle([currentLat, currentLon], {{
            radius: 12000,
            color: '#3B82F6',
            weight: 2,
            fillColor: '#60A5FA',
            fillOpacity: 0.2
        }}).addTo(map);

        function setNativeValue(element, value) {{
            var valueSetter = Object.getOwnPropertyDescriptor(element, 'value').set;
            var prototype = Object.getPrototypeOf(element);
            var prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;
            if (valueSetter && valueSetter !== prototypeValueSetter) {{
                prototypeValueSetter.call(element, value);
            }} else if (valueSetter) {{
                valueSetter.call(element, value);
            }} else {{
                element.value = value;
            }}
        }}

        function syncParentInputs(lat, lon) {{
            try {{
                if (window.parent && window.parent.document) {{
                    var numInputs = window.parent.document.querySelectorAll('input[type=\"number\"]');
                    for (var i = 0; i < numInputs.length; i++) {{
                        var inp = numInputs[i];
                        var pBox = inp.closest('[data-testid=\"stNumberInput\"]');
                        var txt = (inp.getAttribute('aria-label') || '') + ' ' + (pBox ? pBox.innerText : '');
                        if (txt.includes('العرض') || txt.includes('Lat') || txt.includes('°N')) {{
                            setNativeValue(inp, lat.toFixed(4));
                            inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                        if (txt.includes('الطول') || txt.includes('Lon') || txt.includes('°E')) {{
                            setNativeValue(inp, lon.toFixed(4));
                            inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }}
                }}
            }} catch (err) {{
                console.log('Sync to parent DOM:', err);
            }}
        }}

        function applyAndCopyCoords() {{
            var txt = currentLat.toFixed(4) + ", " + currentLon.toFixed(4);
            var nearest = calculateNearestGov(currentLat, currentLon);
            
            // 1. محاولة مزامنة حقول الإدخال مباشرة في الـ Parent DOM
            syncParentInputs(currentLat, currentLon);
            
            // 2. نسخ الإحداثيات للحافظة
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(txt);
            }}
            
            // 3. إظهار إشعار التأكيد في الـ HUD
            var notice = document.getElementById('hudNotice');
            if (notice) {{
                notice.style.display = 'block';
                notice.innerHTML = '✅ تم تحديد الإحداثيات وتغيير المحافظة إلى: ' + nearest.data.name_ar + '<br>(' + txt + ')';
                setTimeout(function() {{
                    notice.style.display = 'none';
                }}, 5000);
            }}
        }}

        function updateProjectPosition(lat, lon) {{
            currentLat = lat;
            currentLon = lon;
            projectMarker.setLatLng([lat, lon]);
            radarCircle.setLatLng([lat, lon]);
            
            var nearest = calculateNearestGov(lat, lon);
            
            document.getElementById('hudLat').innerText = lat.toFixed(4) + '° N';
            document.getElementById('hudLon').innerText = lon.toFixed(4) + '° E';
            document.getElementById('hudGov').innerText = nearest.data.name_ar + ' (' + nearest.distKm.toFixed(1) + ' كم)';
            document.getElementById('hudWater').innerText = nearest.data.groundwater_depth_m + ' م (' + nearest.data.salinity_badge + ')';
            
            projectMarker.bindPopup(
                '<div style=\"font-weight:800; font-size:0.95rem; color:#1E40AF; margin-bottom:4px;\">🎯 موقع المشروع المحدد</div>' +
                '<b>المحافظة الأقرب:</b> ' + nearest.data.name_ar + '<br>' +
                '<b>الإحداثيات:</b> ' + lat.toFixed(4) + '° N, ' + lon.toFixed(4) + '° E<br>' +
                '<b>طبيعة التربة:</b> ' + nearest.data.soil_type_ar + '<br>' +
                '<button onclick=\"applyAndCopyCoords()\" style=\"margin-top:8px; width:100%; background:#10B981; color:#fff; border:none; border-radius:6px; padding:6px 12px; font-weight:800; font-size:0.85rem; cursor:pointer;\">⚡ اعتماد هذا الموقع</button>'
            ).openPopup();
        }}

        // النقر بالماوس على أي مكان في الخريطة لنقل النجمة فوراً
        map.on('click', function(e) {{
            updateProjectPosition(e.latlng.lat, e.latlng.lng);
        }});

        // سحب النجمة بالماوس
        projectMarker.on('dragend', function(e) {{
            var pos = projectMarker.getLatLng();
            updateProjectPosition(pos.lat, pos.lng);
        }});

        // تهيئة الـ Popup المبدئي
        updateProjectPosition(currentLat, currentLon);
    </script>
</body>
</html>"""
    return html

def create_iraq_gis_map(
    selected_gov_key: str = "BAGHDAD",
    project_lat: float = 33.3152,
    project_lon: float = 44.3661,
    project_name: str = "مشروع إنشائي عراقي",
    map_type: str = "SATELLITE"
) -> go.Figure:
    """
    توليد خريطة العراق المكانية التفاعلية مع دعم نمط الأقمار الصناعية (Satellite) والنمط القياسي (Standard OpenStreetMap)
    """
    fig = go.Figure()
    is_satellite = (map_type == "SATELLITE")
    
    # 1. نقاط ومراكز محافظات العراق الـ 18
    for k, data in IRAQ_GOVERNORATES_DB.items():
        score = data["overall_geo_risk_score"]
        is_selected = (k == selected_gov_key)
        
        if score >= 80:
            c = "#EF4444" # أحمر - مخاطر جغرافية حرجة
        elif score >= 65:
            c = "#F59E0B" # برتقالي - مخاطر متوسطة مرتفعة
        else:
            c = "#10B981" # أخضر - مستقر
            
        m_size = 14 if is_selected else 8
        text_color = "#FFFFFF" if is_satellite else "#0F172A"
        
        hover_info = (
            f"<b>📍 محافظة {data['name_ar']} ({data['name_en']})</b><br>"
            f"🏛️ الإقليم: {data['region_ar']}<br>"
            f"💧 المياه الجوفية: {data['groundwater_depth_m']} م ({data['salinity_badge']})<br>"
            f"🌡️ الإجهاد الحراري: {data['summer_heat_index']}%<br>"
            f"🌪️ العواصف الترابية: {data['sandstorm_days_year']} يوم/سنة<br>"
            f"📊 مؤشر الخطورة المكانية: <b>{score}/100</b>"
        )
        
        fig.add_trace(go.Scattermapbox(
            lat=[data["lat"]],
            lon=[data["lon"]],
            mode="markers+text",
            text=[data["name_ar"]],
            textposition="top center",
            textfont=dict(family="Cairo, Segoe UI, sans-serif", size=10, color=text_color, weight="bold"),
            marker=dict(
                size=m_size,
                color=c,
                opacity=0.9
            ),
            hoverinfo="text",
            hovertext=[hover_info],
            name=f"محافظة {data['name_ar']}",
            showlegend=False
        ))
    
    # 2. علامة موقع المشروع الفعلي المختار (Target Project Pin)
    proj_hover = (
        f"<b>🎯 موقع المشروع المعتمد: {project_name}</b><br>"
        f"🌐 خط العرض (Lat): {project_lat:.4f}° N<br>"
        f"🌐 خط الطول (Lon): {project_lon:.4f}° E<br>"
        f"📌 المحافظة المحددة: {get_governorate_profile(selected_gov_key)['name_ar']}"
    )
    
    fig.add_trace(go.Scattermapbox(
        lat=[project_lat],
        lon=[project_lon],
        mode="markers+text",
        text=["🎯 موقع المشروع"],
        textposition="bottom center",
        textfont=dict(family="Cairo, Segoe UI, sans-serif", size=13, color="#FACC15" if is_satellite else "#1E40AF", weight="bold"),
        marker=dict(
            size=22,
            color="#3B82F6",
            opacity=1.0
        ),
        hoverinfo="text",
        hovertext=[proj_hover],
        name="موقع المشروع الفعلي (Site Location)",
        showlegend=True
    ))

    # إعدادات نوع الخريطة (Satellite vs Standard)
    if is_satellite:
        fig.update_layout(
            mapbox=dict(
                style="white-bg",
                center=dict(lat=project_lat if selected_gov_key != "BAGHDAD" else 33.2, lon=project_lon if selected_gov_key != "BAGHDAD" else 44.0),
                zoom=5.5,
                layers=[{
                    "below": "traces",
                    "sourcetype": "raster",
                    "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]
                }]
            )
        )
    else:
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(lat=project_lat if selected_gov_key != "BAGHDAD" else 33.2, lon=project_lon if selected_gov_key != "BAGHDAD" else 44.0),
                zoom=5.5
            )
        )

    map_title = "🛰️ خريطة الأقمار الصناعية للموقع (Satellite Imagery GIS)" if is_satellite else "🗺️ الخريطة الطبوغرافية القياسية للموقع (Standard Street Map GIS)"

    fig.update_layout(
        height=480,
        margin=dict(l=0, r=0, t=35, b=0),
        font=dict(family="Cairo, Segoe UI, sans-serif", size=11),
        title=dict(
            text=map_title,
            font=dict(family="Cairo, Segoe UI, sans-serif", size=13, color="#0F172A"),
            x=0.98,
            xanchor="right"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.85)"
        )
    )

    return fig

def generate_spatial_iso_risks(gov_key: str) -> List[Dict[str, Any]]:
    """توليد بنود مخاطر مكانية تلقائية مخصصة للمحافظة وفق ISO 31000"""
    data = get_governorate_profile(gov_key)
    gov_ar = data["name_ar"]
    risks = []
    
    # 1. خطر المياه الجوفية والتربة
    if data["groundwater_depth_m"] <= 2.0 or "حرج" in data["salinity_sulfate_risk"]:
        risks.append({
            "id": f"GEO_{gov_key}_01",
            "title_ar": f"ارتفاع منسوب المياه الجوفية والأملاح الكبريتية العدوانية في {gov_ar}",
            "title_en": f"High Saline Groundwater & Sulfate Attack ({data['name_en']})",
            "category": "TECHNICAL_DESIGN",
            "probability": 5,
            "impact": 5,
            "schedule_delay_days": (10, 20, 45),
            "cost_impact_usd": 35000.0,
            "mitigation_ar": f"تطبيق منظومة نزح مائي مستمرة (Wellpoint Dewatering) واعتماد إسمنت SRC فائق المقاومة مع عزل مائي مزدوج"
        })
    elif "جبس" in data["soil_type_ar"]:
        risks.append({
            "id": f"GEO_{gov_key}_01",
            "title_ar": f"قابلية ذوبان وهبوط التربة الجبسية عند تشبعها بالماء في {gov_ar}",
            "title_en": f"Gypiferous Soil Collapse & Dissolution ({data['name_en']})",
            "category": "TECHNICAL_DESIGN",
            "probability": 4,
            "impact": 5,
            "schedule_delay_days": (8, 15, 30),
            "cost_impact_usd": 28000.0,
            "mitigation_ar": "استبدال التربة الجبسية بطبقات سبيس حصوية مدموكة وتأمين تصريف مياه الأمطار بعيداً عن القواعد"
        })
        
    # 2. خطر الإجهاد الحراري الصيفي
    if data["summer_heat_index"] >= 80:
        risks.append({
            "id": f"GEO_{gov_key}_02",
            "title_ar": f"تراجع إنتاجية العمالة وحظر الصب النهاري بسبب حرارة صيف {gov_ar} (>50°C)",
            "title_en": f"Extreme Summer Heat Disruption (>50°C in {data['name_en']})",
            "category": "FORCE_MAJEURE_WEATHER",
            "probability": 5,
            "impact": 4,
            "schedule_delay_days": (12, 22, 40),
            "cost_impact_usd": 18000.0,
            "mitigation_ar": "اعتماد نوبات عمل ليلية (Night Shifts) واستخدام مياه مثلجة لتبريد الخرسانة الجاهزة"
        })
        
    # 3. خطر قطوعات الطرق والزيارات المليونية
    if "حرج" in data["traffic_closure_risk"]:
        risks.append({
            "id": f"GEO_{gov_key}_03",
            "title_ar": f"قطوعات النقل وتوقف توريد المواد خلال مواسم الزيارات المليونية في {gov_ar}",
            "title_en": f"Mega-Pilgrimage Transport Lockdown ({data['name_en']})",
            "category": "POLITICAL_SECURITY",
            "probability": 5,
            "impact": 4,
            "schedule_delay_days": (10, 15, 25),
            "cost_impact_usd": 12000.0,
            "mitigation_ar": "التخزين المسبق للمواد الإنشائية في الموقع قبل 10 أيام من بدء الزيارة وتوثيق التعليق كأمر تمديد مدة EOT تعاقدي"
        })
        
    return risks
