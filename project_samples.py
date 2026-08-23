"""
Realistic Iraqi Construction Project Case Studies (نماذج مشاريع عراقية واقعية)
"""

SAMPLE_PROJECTS = {
    "HOSPITAL_BAGHDAD": {
        "id": "HOSPITAL_BAGHDAD",
        "name_ar": "مشروع إنشاء مستشفى تعليمي سعة 400 سرير (بغداد)",
        "name_en": "400-Bed Teaching Hospital Project - Baghdad",
        "client_type_ar": "وزارة الصحة / وزارة الإعمار والإسكان",
        "location_ar": "بغداد - الرصافة",
        "governorate": "BAGHDAD",
        "latitude": 33.3152,
        "longitude": 44.3661,
        "currency": "USD",
        "currency_symbol": "$",
        "daily_overhead_usd": 4500.0,
        "unresolved_rfis": 8,
        "pending_change_orders": 4,
        "cash_flow_deficit_pct": 22.0,
        "subcontractor_performance": 65.0,
        "activities": [
            {
                "id": "ACT_01",
                "name_ar": "الحفريات العميقة والنزح المائي والأساسات الحصيرة (Raft)",
                "name_en": "Deep Excavation, Dewatering & Raft Foundation",
                "duration_estimates": (45, 60, 95),  # O, M, P (Days)
                "cost_estimates": (3500000, 4200000, 5800000),  # O, M, P (USD)
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": []
            },
            {
                "id": "ACT_02",
                "name_ar": "الهيكل الخرساني الشامل والأعمدة والجسور",
                "name_en": "Concrete Superstructure & Slabs",
                "duration_estimates": (120, 160, 240),
                "cost_estimates": (12000000, 14500000, 18500000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_01"]
            },
            {
                "id": "ACT_03",
                "name_ar": "شبكات الكهروميكانيك MEP والتكييف المركزي Chiller",
                "name_en": "MEP & HVAC Central Chillers Installation",
                "duration_estimates": (90, 130, 200),
                "cost_estimates": (8500000, 10200000, 13800000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_02"]
            },
            {
                "id": "ACT_04",
                "name_ar": "استيراد وتركيب شبكات الغازات الطبية وغرف العمليات الكبسولية",
                "name_en": "Medical Gases & Modular Operating Theatres",
                "duration_estimates": (60, 90, 160),
                "cost_estimates": (6000000, 7500000, 11000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_03"]
            },
            {
                "id": "ACT_05",
                "name_ar": "الإنهاءات المعمارية والأرضيات المقاومة للبكتيريا والواجهات",
                "name_en": "Architectural Finishes, Antibacterial Vinyl & Cladding",
                "duration_estimates": (75, 100, 150),
                "cost_estimates": (5000000, 6200000, 8000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_03"]
            },
            {
                "id": "ACT_06",
                "name_ar": "توريد وتركيب أجهزة الرنين MRI والمفراس CT والمصاعد الطبية",
                "name_en": "Heavy Medical Imaging (MRI/CT) & Bed Elevators",
                "duration_estimates": (45, 75, 135),
                "cost_estimates": (11000000, 13500000, 17000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_04", "ACT_05"]
            },
            {
                "id": "ACT_07",
                "name_ar": "الفحص والتشغيل التجريبي والتسليم الابتدائي",
                "name_en": "Testing, Commissioning & Initial Handover",
                "duration_estimates": (30, 45, 75),
                "cost_estimates": (1000000, 1400000, 2100000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_06"]
            }
        ]
    },
    "SEWER_BASRA": {
        "id": "SEWER_BASRA",
        "name_ar": "مشروع شبكات مجاري ومحطة معالجة مياه الصرف (البصرة)",
        "name_en": "Sewerage Network & Central Treatment Plant - Basra",
        "client_type_ar": "محافظة البصرة / مديرية مجاري البصرة",
        "location_ar": "البصرة - شط العرب والقرنة",
        "governorate": "BASRA",
        "latitude": 30.5081,
        "longitude": 47.7835,
        "currency": "IQD",
        "currency_symbol": "د.ع",
        "daily_overhead_usd": 3800.0,
        "unresolved_rfis": 11,
        "pending_change_orders": 5,
        "cash_flow_deficit_pct": 28.0,
        "subcontractor_performance": 58.0,
        "activities": [
            {
                "id": "ACT_01",
                "name_ar": "مسوحات الرادار الأرضي (GPR) وتحويل تعارضات الكهرباء والماء",
                "name_en": "GPR Surveys & Utility Clash Relocation",
                "duration_estimates": (30, 50, 90),
                "cost_estimates": (1200000000, 1600000000, 2400000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": []
            },
            {
                "id": "ACT_02",
                "name_ar": "الحفريات العميقة وتثبيت الستائر اللوحية (Sheet Piling) ومد الأنابيب GRP",
                "name_en": "Deep Trenching, Sheet Piling & GRP Trunk Lines",
                "duration_estimates": (110, 150, 230),
                "cost_estimates": (14000000000, 17500000000, 23000000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_01"]
            },
            {
                "id": "ACT_03",
                "name_ar": "تنفيذ محطات الرفع الغاطسة (PS) والأعمال الكهروميكانيكية",
                "name_en": "Submersible Pumping Stations Civil & Mechanical",
                "duration_estimates": (80, 110, 170),
                "cost_estimates": (6500000000, 8200000000, 11000000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_02"]
            },
            {
                "id": "ACT_04",
                "name_ar": "أحواض التهوية والترسيب بمحطة المعالجة المركزية (WWTP)",
                "name_en": "Aeration & Clarifier Basins at Treatment Plant",
                "duration_estimates": (90, 130, 195),
                "cost_estimates": (9000000000, 11500000000, 15500000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_01"]
            },
            {
                "id": "ACT_05",
                "name_ar": "توريد وتركيب منظومات التحكم الآلي SCADA والمولدات التوربينية",
                "name_en": "SCADA Automation, Telemetry & Backup Generators",
                "duration_estimates": (45, 70, 120),
                "cost_estimates": (4000000000, 5200000000, 7200000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_03", "ACT_04"]
            },
            {
                "id": "ACT_06",
                "name_ar": "الفحص الهيدروليكي وإعادة إكساء الشوارع بالأسفلت والتسليم",
                "name_en": "Hydrostatic Testing, Road Re-asphalting & Commissioning",
                "duration_estimates": (35, 55, 90),
                "cost_estimates": (2500000000, 3400000000, 4800000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_05"]
            }
        ]
    },
    "HOUSING_NAJAF": {
        "id": "HOUSING_NAJAF",
        "name_ar": "مشروع مجمع سكني استثماري 1200 وحدة (النجف الأشرف)",
        "name_en": "1,200-Unit Residential Complex - Najaf",
        "client_type_ar": "هيئة استثمار النجف / القطاع الخاص المستثمر",
        "location_ar": "النجف الأشرف",
        "governorate": "NAJAF",
        "latitude": 32.0259,
        "longitude": 44.3462,
        "currency": "USD",
        "currency_symbol": "$",
        "daily_overhead_usd": 3200.0,
        "unresolved_rfis": 4,
        "pending_change_orders": 2,
        "cash_flow_deficit_pct": 12.0,
        "subcontractor_performance": 78.0,
        "activities": [
            {
                "id": "ACT_01",
                "name_ar": "تسوية الموقع والتربة والأساسات السطحية والعزل",
                "name_en": "Site Grading, Earthworks & Raft Foundations",
                "duration_estimates": (40, 55, 80),
                "cost_estimates": (3000000, 3800000, 5000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": []
            },
            {
                "id": "ACT_02",
                "name_ar": "تنفيذ الهياكل الخرسانية بنظام القوالب النفقية (Tunnel Form)",
                "name_en": "Monolithic Concrete Structure with Tunnel Forms",
                "duration_estimates": (110, 140, 190),
                "cost_estimates": (15000000, 18000000, 22500000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_01"]
            },
            {
                "id": "ACT_03",
                "name_ar": "التأسيسات الصحية والكهربائية والغاز المركزي للأبراج",
                "name_en": "Plumbing, Electrical & Central Gas Internal Networks",
                "duration_estimates": (70, 95, 140),
                "cost_estimates": (5500000, 6800000, 9000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_02"]
            },
            {
                "id": "ACT_04",
                "name_ar": "الإنهاءات الداخلية (سيراميك، أبواب، دهان) والواجهات الخارجية",
                "name_en": "Internal Architectural Finishes & External Façades",
                "duration_estimates": (80, 110, 160),
                "cost_estimates": (7000000, 8500000, 11000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_03"]
            },
            {
                "id": "ACT_05",
                "name_ar": "البنية التحتية للمجمع (طرق داخلية، محولات كهرباء، حدائق)",
                "name_en": "Site Infrastructure, Transformers, Landscaping & Roads",
                "duration_estimates": (50, 70, 105),
                "cost_estimates": (3500000, 4400000, 5800000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_02"]
            },
            {
                "id": "ACT_06",
                "name_ar": "الفحص النهائي وإصدار شهادات الإشغال والتسليم للمستفيدين",
                "name_en": "Final Inspection, Occupancy Certification & Delivery",
                "duration_estimates": (25, 40, 65),
                "cost_estimates": (400000, 600000, 900000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_04", "ACT_05"]
            }
        ]
    },
    "HIGHWAY_NINEVEH": {
        "id": "HIGHWAY_NINEVEH",
        "name_ar": "مشروع تأهيل طريق رئيسي وجسور رابطة (نينوى / صلاح الدين)",
        "name_en": "Highway Rehabilitation & Bridge Reconstruction - Nineveh",
        "client_type_ar": "دائرة الطرق والجسور / صندوق إعادة الإعمار",
        "location_ar": "نينوى - الموصل إلى الشرقاط",
        "governorate": "NINEVEH",
        "latitude": 36.3489,
        "longitude": 43.1577,
        "currency": "IQD",
        "currency_symbol": "د.ع",
        "daily_overhead_usd": 3000.0,
        "unresolved_rfis": 6,
        "pending_change_orders": 3,
        "cash_flow_deficit_pct": 18.0,
        "subcontractor_performance": 72.0,
        "activities": [
            {
                "id": "ACT_01",
                "name_ar": "المسح الميداني وتطهير المقاطع من المخلفات الحربية (UXO Clearance)",
                "name_en": "UXO Survey, Demining & Traffic Diversions",
                "duration_estimates": (25, 40, 75),
                "cost_estimates": (800000000, 1100000000, 1600000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": []
            },
            {
                "id": "ACT_02",
                "name_ar": "قشط الأسفلت المتضرر وتثبيت طبقات التعلية الترابية والأساس الحصوي",
                "name_en": "Milling Damaged Asphalt, Subgrade & Subbase Stabilization",
                "duration_estimates": (60, 85, 130),
                "cost_estimates": (6000000000, 7800000000, 10500000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_01"]
            },
            {
                "id": "ACT_03",
                "name_ar": "إعادة صب وتثبيت الروافد الخرسانية مسبقة الجهد للجسور المتضررة",
                "name_en": "Prestressed Concrete Bridge Girders Casting & Erection",
                "duration_estimates": (70, 100, 160),
                "cost_estimates": (7500000000, 9500000000, 13000000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_01"]
            },
            {
                "id": "ACT_04",
                "name_ar": "فرش طبقات الأسفلت الرابطة والسطحية المحسنة بالبوليمر (SMA)",
                "name_en": "Polymer Modified Asphalt Binder & Wearing Course (SMA)",
                "duration_estimates": (45, 65, 100),
                "cost_estimates": (5500000000, 7000000000, 9200000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_02", "ACT_03"]
            },
            {
                "id": "ACT_05",
                "name_ar": "مفاصل التمدد للجسور، الحواجز الخرسانية والتأثيث والتخطيط الحراري",
                "name_en": "Bridge Expansion Joints, Guardrails, Road Signage & Thermoplastic",
                "duration_estimates": (20, 35, 55),
                "cost_estimates": (1500000000, 2100000000, 2900000000),
                "dist_type": "PERT",
                "cost_dist_type": "PERT",
                "predecessors": ["ACT_04"]
            }
        ]
    }
}
