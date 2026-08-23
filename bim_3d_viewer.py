"""
Interactive 3D BIM Model Risk Visualizer & Executive Brief Generator
عارض نماذج البناء ثلاثي الأبعاد الملون بمستويات الخطر ومولد التقرير التنفيذي الموجز
"""

import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Any

def create_3d_bim_risk_model(
    storeys_count: int = 4,
    show_footings: bool = True,
    show_columns: bool = True,
    show_slabs: bool = True,
    show_walls: bool = True,
    show_mep: bool = True,
    has_clashes: bool = True,
    element_summary: Dict[str, int] = None,
    coordination_issues: List[Dict[str, Any]] = None
) -> go.Figure:
    """توليد مجسم ثلاثي الأبعاد هندسي متكامل لعناصر المبنى وتلوينها وتوزيعها حسب الطوابق المستوردة"""
    fig = go.Figure()
    s_count = max(1, min(12, int(storeys_count)))
    storey_height = 3.8

    # شبكة المحاور الإنشائية (Structural Grid)
    grid_coords = [-15, -7.5, 0, 7.5, 15]

    # 1. القواعد والأساسات الخرسانية (Footings at Z=0)
    if show_footings:
        footing_x, footing_y, footing_z = [], [], []
        for x in grid_coords:
            for y in grid_coords:
                footing_x.append(x)
                footing_y.append(y)
                footing_z.append(0)

        fig.add_trace(go.Scatter3d(
            x=footing_x,
            y=footing_y,
            z=footing_z,
            mode='markers',
            marker=dict(size=12, color='#10B981', symbol='square', opacity=0.95),
            name='🟢 الأساسات والقواعد (Footings)',
            hovertemplate="<b>قاعدة خرسانية مسلحة (Footing Pad)</b><br>الموقع: (%{x}, %{y})<br>المنسوب: 0.00م<extra></extra>"
        ))

    # 2. الأعمدة الخرسانية المسلحة (Columns) عبر كافة الطوابق
    if show_columns:
        col_x, col_y, col_z = [], [], []
        for s in range(s_count):
            z_base = s * storey_height
            z_top = (s + 1) * storey_height
            for x in grid_coords:
                for y in grid_coords:
                    col_x.extend([x, x, None])
                    col_y.extend([y, y, None])
                    col_z.extend([z_base, z_top, None])

        fig.add_trace(go.Scatter3d(
            x=col_x,
            y=col_y,
            z=col_z,
            mode='lines',
            line=dict(color='#64748B', width=6),
            name='⚪ الأعمدة الإنشائية (Columns)',
            hovertemplate="<b>عمود خرساني مسلح (Concrete Column)</b><extra></extra>"
        ))

    # 3. البلاطات والأسقف والجسور (Slabs & Beams) لكل طابق
    if show_slabs:
        slab_x, slab_y, slab_z = [], [], []
        for s in range(1, s_count + 1):
            z_slab = s * storey_height
            # محيط البلاطة الخارجية
            slab_x.extend([-16.5, 16.5, 16.5, -16.5, -16.5, None])
            slab_y.extend([-16.5, -16.5, 16.5, 16.5, -16.5, None])
            slab_z.extend([z_slab, z_slab, z_slab, z_slab, z_slab, None])

            # شبكة الجسور الرابطة الداخلية (Beams Grid)
            for x in grid_coords:
                slab_x.extend([x, x, None])
                slab_y.extend([-16.5, 16.5, None])
                slab_z.extend([z_slab, z_slab, None])
            for y in grid_coords:
                slab_x.extend([-16.5, 16.5, None])
                slab_y.extend([y, y, None])
                slab_z.extend([z_slab, z_slab, None])

        fig.add_trace(go.Scatter3d(
            x=slab_x,
            y=slab_y,
            z=slab_z,
            mode='lines',
            line=dict(color='#2563EB', width=4),
            name='🔵 البلاطات والأسقف والجسور (Slabs & Beams)',
            hovertemplate="<b>سقف / جسر خرساني (Floor Slab & Beam)</b><extra></extra>"
        ))

    # 4. الجدران الخارجية والقواطع المعمارية (Walls)
    if show_walls:
        wall_x, wall_y, wall_z = [], [], []
        for s in range(s_count):
            z_b = s * storey_height + 0.3
            z_t = (s + 1) * storey_height - 0.3
            # جدران الواجهة
            for y_pt in [-16.5, 16.5]:
                wall_x.extend([-16.5, 16.5, 16.5, -16.5, -16.5, None])
                wall_y.extend([y_pt, y_pt, y_pt, y_pt, y_pt, None])
                wall_z.extend([z_b, z_b, z_t, z_t, z_b, None])

        fig.add_trace(go.Scatter3d(
            x=wall_x,
            y=wall_y,
            z=wall_z,
            mode='lines',
            line=dict(color='#94A3B8', width=2, dash='solid'),
            name='🧱 الجدران والقواطع (Walls)',
            hovertemplate="<b>جدار بنائي وقاطع معماري (Wall)</b><extra></extra>"
        ))

    # 5. شبكات الكهروميكانيك MEP ودكتات التكييف (HVAC & Pipes)
    if show_mep:
        mep_x, mep_y, mep_z = [], [], []
        for s in range(1, s_count + 1):
            z_mep = s * storey_height - 0.7  # منسوب دكتات التكييف المعلقة تحت السقف
            mep_x.extend([-14, 14, 14, 0, 0, -14, None])
            mep_y.extend([-8, -8, 8, 8, -8, -8, None])
            mep_z.extend([z_mep, z_mep, z_mep, z_mep, z_mep, z_mep, None])

        fig.add_trace(go.Scatter3d(
            x=mep_x,
            y=mep_y,
            z=mep_z,
            mode='lines',
            line=dict(color='#0284C7', width=6),
            name='💨 شبكات التكييف والكهروميكانيك (MEP Ducts)',
            hovertemplate="<b>دكت تكييف رئيسي منسق (HVAC Main Duct)</b><extra></extra>"
        ))

    # 6. نقاط التعارض الحرج والتنسيق الهندسي (Clashes)
    if has_clashes:
        clash_x, clash_y, clash_z = [], [], []
        clash_texts = []
        
        # تعارض في الطابق الأول
        clash_x.append(0)
        clash_y.append(0)
        clash_z.append(1 * storey_height - 0.2)
        clash_texts.append('🔴 تعارض دكت تكييف رئيسي مع جسر خرساني (COORD_01)')

        # تعارض في الطابق الثالث إن وجد
        if s_count >= 3:
            clash_x.append(7.5)
            clash_y.append(-7.5)
            clash_z.append(3 * storey_height - 0.2)
            clash_texts.append('🔴 تعارض خط أنابيب الصرف مع عمود إنشائي (COORD_02)')

        fig.add_trace(go.Scatter3d(
            x=clash_x,
            y=clash_y,
            z=clash_z,
            mode='markers+text',
            text=clash_texts,
            textposition='top center',
            marker=dict(size=11, color='#EF4444', symbol='diamond', line=dict(color='#991B1B', width=2)),
            name='🔴 نقاط التعارض الحرج المكتشفة (Clash Points)',
            hovertemplate="<b>%{text}</b><br>المنسوب: %{z:.1f}م<extra></extra>"
        ))

    max_z = max(15, s_count * storey_height + 4)
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X (متر)', backgroundcolor='#F8FAFC', gridcolor='#E2E8F0', range=[-20, 20]),
            yaxis=dict(title='Y (متر)', backgroundcolor='#F8FAFC', gridcolor='#E2E8F0', range=[-20, 20]),
            zaxis=dict(title='Z الارتفاع (متر)', backgroundcolor='#F8FAFC', gridcolor='#E2E8F0', range=[-1, max_z]),
            camera=dict(eye=dict(x=1.7, y=1.7, z=1.3))
        ),
        margin=dict(l=10, r=10, t=30, b=10),
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

def create_raw_ifc_3d_model(
    spatial_elements: List[Dict[str, Any]],
    visible_categories: List[str] = None
) -> go.Figure:
    """توليد عارض المجسم الهندسي الأصلي الحقيقي المستخرج من ملف الـ IFC المرفوع"""
    fig = go.Figure()
    if not spatial_elements:
        fig.add_annotation(
            text="لم يتم العثور على إحداثيات مكانية في ملف الـ IFC المرفوع",
            showarrow=False,
            font=dict(size=14, color="#64748B")
        )
        return fig

    # تجميع العناصر حسب التخصص
    categories = {}
    for el in spatial_elements:
        cat = el.get("category_ar", "أخرى")
        if visible_categories is not None and cat not in visible_categories:
            continue
        if cat not in categories:
            categories[cat] = {
                "x": [], "y": [], "z": [], "names": [], "ids": [],
                "color": el.get("color", "#64748B"),
                "symbol": el.get("symbol", "circle"),
                "size": el.get("size", 7)
            }
        categories[cat]["x"].append(el["x"])
        categories[cat]["y"].append(el["y"])
        categories[cat]["z"].append(el["z"])
        categories[cat]["names"].append(el["name"])
        categories[cat]["ids"].append(el["id"])

    # 1. رسم مناسيب وبلاطات الطوابق تلقائياً لتأطير المبنى هندسياً
    all_x = [el["x"] for el in spatial_elements if el.get("x") is not None]
    all_y = [el["y"] for el in spatial_elements if el.get("y") is not None]
    all_z = [el["z"] for el in spatial_elements if el.get("z") is not None]

    if all_x and all_y and all_z:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        min_z, max_z = min(all_z), max(all_z)

        # استخراج مناسيب الطوابق الفريدة المكتشفة
        z_rounded = sorted(list(set(round(z, 0) for z in all_z)))
        if len(z_rounded) > 12:
            # تقليص إلى 8-10 مستويات رئيسية
            step = max(1, len(z_rounded) // 8)
            z_levels = z_rounded[::step]
        else:
            z_levels = z_rounded

        floor_x, floor_y, floor_z = [], [], []
        for z_lvl in z_levels:
            floor_x.extend([min_x, max_x, max_x, min_x, min_x, None])
            floor_y.extend([min_y, min_y, max_y, max_y, min_y, None])
            floor_z.extend([z_lvl, z_lvl, z_lvl, z_lvl, z_lvl, None])

        fig.add_trace(go.Scatter3d(
            x=floor_x,
            y=floor_y,
            z=floor_z,
            mode='lines',
            line=dict(color='#3B82F6', width=3, dash='solid'),
            name='🔵 حدود ومناسيب الأسقف (Storey Slabs)',
            hoverinfo='skip'
        ))

    # 2. رسم العناصر الهندسية المكتشفة مصنفة حسب التخصص
    VALID_SCATTER3D_SYMBOLS = {'circle', 'circle-open', 'cross', 'diamond', 'diamond-open', 'square', 'square-open', 'x'}
    def _safe_sym(s):
        if s in VALID_SCATTER3D_SYMBOLS:
            return s
        m = {'triangle-up': 'diamond', 'triangle-down': 'diamond-open', 'star': 'cross'}
        return m.get(s, 'circle')

    for cat_name, data in categories.items():
        fig.add_trace(go.Scatter3d(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            mode='markers',
            marker=dict(
                size=data["size"],
                color=data["color"],
                symbol=_safe_sym(data.get("symbol", "circle")),
                opacity=0.85
            ),
            name=f"{cat_name} ({len(data['x'])} عنصر)",
            customdata=list(zip(data["names"], data["ids"], [cat_name] * len(data["x"]))),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" +
                "🏷️ الكود: %{customdata[1]}<br>" +
                "📁 التصنيف: %{customdata[2]}<br>" +
                "📍 الإحداثيات: X=%{x:.2f}, Y=%{y:.2f}, Z=%{z:.2f}م<br>" +
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X (متر)', backgroundcolor='#F8FAFC', gridcolor='#E2E8F0'),
            yaxis=dict(title='Y (متر)', backgroundcolor='#F8FAFC', gridcolor='#E2E8F0'),
            zaxis=dict(title='Z الارتفاع (متر)', backgroundcolor='#F8FAFC', gridcolor='#E2E8F0'),
            camera=dict(eye=dict(x=1.7, y=1.7, z=1.3))
        ),
        margin=dict(l=10, r=10, t=30, b=10),
        height=540,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

def generate_executive_brief_html(
    project_meta: Dict[str, Any],
    sim_results: Dict[str, Any],
    isrs_data: Dict[str, Any],
    eot_data: Dict[str, Any],
    coordination_summary: Dict[str, Any]
) -> str:
    """توليد وثيقة التقرير التنفيذي الرسمي المخصص للطباعة والعرض الوزاري (Executive Two-Pager)"""
    p_name = project_meta.get("name_ar", "المشروع الإنشائي")
    client = project_meta.get("client_type_ar", "وزارة الإعمار والإسكان")
    curr_sym = project_meta.get("currency_symbol", "$")
    
    p80_dur = sim_results["duration_percentiles"].get("P80", 0)
    p80_cost = sim_results["cost_percentiles"].get("P80", 0)
    time_cont = max(0.0, p80_dur - sim_results["duration_percentiles"].get("P50", p80_dur))
    cost_cont = max(0.0, p80_cost - sim_results["cost_percentiles"].get("P50", p80_cost))

    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
    <meta charset="utf-8"/>
    <title>التقرير التنفيذي الشامل لإدارة المخاطر والتنسيق | {p_name}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
        body {{
            font-family: 'Cairo', sans-serif;
            direction: rtl;
            text-align: right;
            color: #0F172A;
            background: #FFFFFF;
            padding: 30px;
            line-height: 1.6;
        }}
        .header-box {{
            border-bottom: 3px solid #1E3A8A;
            padding-bottom: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .title-main {{ font-size: 22px; font-weight: 900; color: #1E3A8A; margin: 0; }}
        .title-sub {{ font-size: 14px; color: #64748B; margin-top: 4px; }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}
        .kpi-cell {{
            background: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        .kpi-val {{ font-size: 20px; font-weight: 900; color: #1E293B; }}
        .section-title {{
            font-size: 16px;
            font-weight: 800;
            color: #1E3A8A;
            border-right: 4px solid #3B82F6;
            padding-right: 8px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
            font-size: 13px;
        }}
        th, td {{
            border: 1px solid #CBD5E1;
            padding: 8px 10px;
            text-align: center;
        }}
        th {{ background: #F1F5F9; font-weight: 700; color: #1E293B; }}
        .signature-box {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #E2E8F0;
            text-align: center;
        }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
    </head>
    <body>
        <div class="header-box">
            <div>
                <h1 class="title-main">جمهورية العراق | {client}</h1>
                <div class="title-sub">التقرير التنفيذي الموحد للتقييم الكمي للمخاطر وتنسيق المشاريع (ISO 31000:2018)</div>
            </div>
            <div style="text-align:left; font-size:12px; color:#475569;">
                <b>رمز المشروع:</b> {project_meta.get('id', 'PROJ')}<br/>
                <b>تاريخ التقرير:</b> 2026/08/19 م
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-cell">
                <div style="font-size:12px; color:#64748B;">مدة الإنجاز الآمنة (P80)</div>
                <div class="kpi-val">{p80_dur:,.0f} يوم</div>
                <div style="font-size:11px; color:#2563EB;">احتياطي زمني: +{time_cont:,.0f} يوم</div>
            </div>
            <div class="kpi-cell">
                <div style="font-size:12px; color:#64748B;">الميزانية الآمنة (P80)</div>
                <div class="kpi-val">{p80_cost:,.0f} {curr_sym}</div>
                <div style="font-size:11px; color:#D97706;">احتياطي مالي: +{cost_cont:,.0f} {curr_sym}</div>
            </div>
            <div class="kpi-cell">
                <div style="font-size:12px; color:#64748B;">مؤشر خطر التلكؤ (ISRS)</div>
                <div class="kpi-val" style="color:{isrs_data['status_color']};">{isrs_data['isrs_score']}%</div>
                <div style="font-size:11px;">{isrs_data['status_ar']}</div>
            </div>
            <div class="kpi-cell">
                <div style="font-size:12px; color:#64748B;">مشكلات التنسيق (ISO 31000)</div>
                <div class="kpi-val">{coordination_summary['total_issues']} تعارض</div>
                <div style="font-size:11px; color:#DC2626;">منها {coordination_summary['critical_count']} حرج</div>
            </div>
        </div>

        <div class="section-title">⚖️ الموقف التعاقدي والمطالبات المستحقة (المادة 44 من الشروط العامة)</div>
        <p style="font-size:13px; margin:4px 0 10px 0;">
            إجمالي التمديد الزمني المستحق للمقاول: <b>{eot_data.get('total_entitled_eot_days', 0)} يوماً</b> • إجمالي مصاريف الاستمرار المعوضة: <b>{eot_data.get('total_prolongation_claim', 0):,.0f} {curr_sym}</b> • صافي الرصيد التعاقدي: <b>{eot_data.get('net_contractual_balance', 0):,.0f} {curr_sym}</b>.
        </p>

        <div class="section-title">📌 التوصيات الفنية والقرارات الواجبة فوراً</div>
        <ul style="font-size:13px; margin-top:4px;">
            {''.join([f"<li>{r}</li>" for r in isrs_data.get('recommendations', [])])}
            <li>عقد ورشة التنسيق الهندسي بالموقع لحسم التعارضات المكتشفة وتعديل المخططات التنفيذية قبل موعد الصب.</li>
            <li>إطلاق دفعات السلف الإنجازية العالقة لتجنب تراكم مطالبات التمديد وتكاليف استمرار الموقع.</li>
        </ul>

        <div class="signature-box">
            <div>
                <b>مهندس التنسيق والنمذجة BIM</b><br/><br/>
                التوقيع: ............................
            </div>
            <div>
                <b>دائرة المهندس المقيم</b><br/><br/>
                التوقيع: ............................
            </div>
            <div>
                <b>مصادقة رب العمل / المدير العام</b><br/><br/>
                التوقيع: ............................
            </div>
        </div>

        <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #CBD5E1; text-align: center; font-size: 12px; color: #475569; direction: ltr;">
            <b>Designed and developed by <span style="color: #2563EB;">Dr Ahmed Louay Ahmed</span></b> • ICRAT 2.0 Platform
        </div>
    </body>
    </html>
    """
    return html
