"""
Interactive Primavera P6 Gantt Chart & Integrated Cash Flow Visualizer
محرك توليد مخطط جانت الزمني (Gantt Chart) المتطابق مع بريمافيرا P6 مع منحنى التدفق المالي المتزامن
مبني بالاعتماد على px.timeline و go.Scatter لسرعة فائقة واستقرار 100% بدون أي تعليق
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import arabic_reshaper

def ar(text: str) -> str:
    if not text: return ""
    try: return arabic_reshaper.reshape(str(text))
    except Exception: return str(text)

def compute_cpm_schedule(
    activities: List[Dict[str, Any]], 
    project_start_date: str = "2024-01-01"
) -> List[Dict[str, Any]]:
    """حساب شبكة المسار الحرج (CPM) مع اعتماد التواريخ الفعلية المستوردة من ملف P6 مباشرة إن وجدت"""
    if not activities:
        return []

    # 1. التحقق مما إذا كانت الأنشطة تحمل تواريخ معتمدة ومستوردة من ملف بريمافيرا P6
    has_explicit_dates = sum(1 for a in activities if a.get("start_date") and a.get("finish_date")) >= max(1, len(activities) * 0.5)

    if has_explicit_dates:
        schedule_rows = []
        for a in activities:
            aid = a["id"]
            s_str = a.get("start_date", "")
            e_str = a.get("finish_date", "")
            try:
                start_dt = datetime.strptime(str(s_str), "%Y-%m-%d")
            except Exception:
                try:
                    start_dt = datetime.strptime(str(project_start_date), "%Y-%m-%d")
                except Exception:
                    start_dt = datetime(2024, 1, 1)

            try:
                finish_dt = datetime.strptime(str(e_str), "%Y-%m-%d")
            except Exception:
                dur_est = max(1, int(a.get("duration_estimates", (10, 20, 30))[1]))
                finish_dt = start_dt + timedelta(days=dur_est)

            dur = max(1, (finish_dt - start_dt).days)
            cost = float(a.get("cost_estimates", (10000, 20000, 30000))[1])
            total_float = int(a.get("total_float", 0))
            is_crit = (total_float <= 0)

            schedule_rows.append({
                "id": aid,
                "name_ar": a.get("name_ar", aid),
                "name_en": a.get("name_en", aid),
                "duration": dur,
                "cost": cost,
                "es_day": 0,
                "ef_day": dur,
                "ls_day": 0,
                "lf_day": dur,
                "total_float": total_float,
                "is_critical": is_crit,
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "finish_date": finish_dt.strftime("%Y-%m-%d"),
                "start_dt": start_dt,
                "finish_dt": finish_dt
            })
        # ترتيب الأنشطة حسب تاريخ البدء الفعلي
        schedule_rows.sort(key=lambda x: x["start_dt"])
        return schedule_rows

    # 2. في حال كانت أنشطة مخصصة بدون تواريخ، يتم حساب المسار الحرج من تاريخ البداية
    try:
        base_date = datetime.strptime(str(project_start_date), "%Y-%m-%d")
    except Exception:
        base_date = datetime(2024, 1, 1)

    act_map = {}
    for a in activities:
        aid = a["id"]
        dur = max(1, int(a.get("duration_estimates", (10, 20, 30))[1]))
        cost = float(a.get("cost_estimates", (10000, 20000, 30000))[1])
        preds = [p for p in a.get("predecessors", []) if p != aid]
        act_map[aid] = {
            "id": aid,
            "name_ar": a.get("name_ar", aid),
            "name_en": a.get("name_en", aid),
            "duration": dur,
            "cost": cost,
            "predecessors": preds,
            "es": 0,
            "ef": dur,
            "ls": 0,
            "lf": 0,
            "in_degree": 0
        }

    # تنظيف مراجع الأنشطة السابقة
    for aid, a in act_map.items():
        a["predecessors"] = [p for p in a["predecessors"] if p in act_map]

    # بناء خريطة التوابع (Successors Map) ودرجات الدخول
    succ_map = {aid: [] for aid in act_map}
    for aid, a in act_map.items():
        for pid in a["predecessors"]:
            succ_map[pid].append(aid)
            a["in_degree"] += 1

    # الترتيب الطوبولوجي وحساب المسار الأمامي Forward Pass O(V+E)
    in_deg = {aid: act_map[aid]["in_degree"] for aid in act_map}
    queue = [aid for aid, deg in in_deg.items() if deg == 0]
    topo_order = []

    while queue:
        curr = queue.pop(0)
        topo_order.append(curr)
        curr_ef = act_map[curr]["ef"]
        for succ in succ_map[curr]:
            if curr_ef > act_map[succ]["es"]:
                act_map[succ]["es"] = curr_ef
                act_map[succ]["ef"] = curr_ef + act_map[succ]["duration"]
            in_deg[succ] -= 1
            if in_deg[succ] == 0:
                queue.append(succ)

    # معالجة أي أنشطة متبقية أو حلقات
    if len(topo_order) < len(act_map):
        for aid in act_map:
            if aid not in topo_order:
                topo_order.append(aid)

    max_project_day = max((a["ef"] for a in act_map.values()), default=100)

    # تهيئة وحساب المسار العكسي Backward Pass O(V+E)
    for a in act_map.values():
        a["lf"] = max_project_day
        a["ls"] = a["lf"] - a["duration"]

    for aid in reversed(topo_order):
        curr_ls = act_map[aid]["ls"]
        for pid in act_map[aid]["predecessors"]:
            if curr_ls < act_map[pid]["lf"]:
                act_map[pid]["lf"] = curr_ls
                act_map[pid]["ls"] = curr_ls - act_map[pid]["duration"]

    # تجميع النتائج وتوليد التواريخ
    schedule_rows = []
    for aid in topo_order:
        calc_a = act_map[aid]
        total_float = max(0, calc_a["ls"] - calc_a["es"])
        is_critical = (total_float == 0)

        start_dt = base_date + timedelta(days=calc_a["es"])
        finish_dt = base_date + timedelta(days=calc_a["ef"])

        schedule_rows.append({
            "id": aid,
            "name_ar": calc_a["name_ar"],
            "name_en": calc_a["name_en"],
            "duration": calc_a["duration"],
            "cost": calc_a["cost"],
            "es_day": calc_a["es"],
            "ef_day": calc_a["ef"],
            "ls_day": calc_a["ls"],
            "lf_day": calc_a["lf"],
            "total_float": total_float,
            "is_critical": is_critical,
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "finish_date": finish_dt.strftime("%Y-%m-%d"),
            "start_dt": start_dt,
            "finish_dt": finish_dt
        })

    return schedule_rows

def create_p6_gantt_chart(
    activities: List[Dict[str, Any]],
    project_start_date: str = "2024-01-01",
    currency_symbol: str = "$",
    max_display_activities: int = 80
) -> go.Figure:
    """توليد مخطط جانت الزمني الصوري (Primavera P6 Gantt Timeline) فائق السرعة والاستقرار"""
    if not activities:
        fig = go.Figure()
        fig.add_annotation(text="لا توجد أنشطة مسجلة لعرض مخطط جانت", showarrow=False, font=dict(size=14))
        return fig

    sched = compute_cpm_schedule(activities, project_start_date)
    df = pd.DataFrame(sched)

    # إذا كان عدد الأنشطة كبيراً جداً (مثلاً أكثر من 80)، نعرض الأنشطة الحرجة والأطول مدة لضمان سرعة المتصفح
    total_acts = len(df)
    is_truncated = False
    if total_acts > max_display_activities:
        # نرتب حسب الحرجية ثم المدة
        df_crit = df[df["is_critical"] == True]
        df_non_crit = df[df["is_critical"] == False].sort_values(by="duration", ascending=False)
        needed = max_display_activities - len(df_crit)
        if needed > 0:
            df = pd.concat([df_crit, df_non_crit.head(needed)]).sort_values(by="es_day")
        else:
            df = df_crit.head(max_display_activities)
        is_truncated = True

    # صياغة اسم وبطاقة النشاط بدون أي تداخل مع مراعاة الهوامش والاتجاه الطبيعي
    def _clean_gantt_label(r):
        aid = str(r['id'])
        name = str(r.get('name_ar', aid))
        if len(name) > 38:
            name = name[:36] + ".."
        return f"{aid} - {ar(name)}"

    df["task_label"] = df.apply(_clean_gantt_label, axis=1)
    df["type_label"] = df["is_critical"].map({True: ar("مسار حرج (Critical)"), False: ar("نشاط اعتيادي (Normal)")})

    chart_title = ar("مخطط جانت الزمني والمسار الحرج (Primavera P6 Gantt Timeline)")
    if is_truncated:
        chart_title += ar(f" [عرض أهم {len(df)} نشاطاً من أصل {total_acts}]")

    # تحديد التباعد الشهري الأمثل بناءً على طول المشروع
    min_date = df["start_dt"].min()
    max_date = df["finish_dt"].max()
    total_months = max(1, (max_date.year - min_date.year) * 12 + (max_date.month - min_date.month) + 1)
    
    if total_months <= 18:
        x_dtick = "M1"
    elif total_months <= 36:
        x_dtick = "M2"
    else:
        x_dtick = "M3"

    fig = px.timeline(
        df,
        x_start="start_dt",
        x_end="finish_dt",
        y="task_label",
        color="type_label",
        color_discrete_map={ar("مسار حرج (Critical)"): "#DC2626", ar("نشاط اعتيادي (Normal)"): "#2563EB"},
        custom_data=["id", "duration", "start_date", "finish_date", "cost", "total_float", "name_ar"]
    )

    fig.update_yaxes(
        autorange="reversed", 
        automargin=True,
        tickfont=dict(family="Cairo, Segoe UI, Tahoma, sans-serif", size=11, color="#0F172A"),
        title=""
    )
    fig.update_xaxes(
        type="date",
        tickformat="%b %Y", 
        dtick=x_dtick,
        side="top",
        showgrid=True,
        gridcolor="#CBD5E1", 
        gridwidth=1.2,
        showline=True,
        linecolor="#0F172A",
        linewidth=1.8,
        mirror="allticks",
        tickfont=dict(family="Cairo, Segoe UI, Tahoma, sans-serif", size=11, color="#0F172A"),
        title=dict(
            text=ar("مسطرة التواريخ والشهور والسنوات (Primavera P6 Time Scale Ruler)"),
            font=dict(family="Cairo, Segoe UI, sans-serif", size=12, color="#0F172A")
        ),
        rangeslider=dict(
            visible=True,
            thickness=0.065,
            bgcolor="#F8FAFC",
            bordercolor="#94A3B8",
            borderwidth=1
        ),
        automargin=True
    )
    
    chart_height = max(440, min(1400, 130 + len(df) * 42))
    fig.update_layout(
        height=chart_height,
        bargap=0.35,
        font=dict(family="Cairo, Segoe UI, Tahoma, sans-serif", size=11, color="#0F172A"),
        margin=dict(l=310, r=40, t=110, b=55),
        title=dict(
            text=chart_title,
            font=dict(family="Cairo, Segoe UI, sans-serif", size=13, color="#0F172A"),
            x=0.98,
            xanchor="right"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="left",
            x=0.01,
            font=dict(family="Cairo, Segoe UI, sans-serif", size=11)
        )
    )

    fig.update_traces(
        marker=dict(line=dict(width=1.2, color='#0F172A'), opacity=0.92),
        hovertemplate=(
            "<b>%{customdata[0]} - %{customdata[6]}</b><br>" +
            "📅 تاريخ البدء: %{customdata[2]}<br>" +
            "🏁 تاريخ الانتهاء: %{customdata[3]}<br>" +
            "⏱️ المدة الإجمالية: %{customdata[1]} يوم<br>" +
            "⏳ السماحية (Float): %{customdata[5]} يوم<br>" +
            f"💰 الكلفة المباشرة: %{{customdata[4]:,.0f}} {currency_symbol}<br>" +
            "<extra></extra>"
        )
    )

    return fig

def create_p6_cashflow_chart(
    activities: List[Dict[str, Any]],
    project_start_date: str = "2024-01-01",
    currency_symbol: str = "$"
) -> go.Figure:
    """توليد منحنى التدفق النقدي والمصروفات الشهرية المتزامن (Monthly Cash Flow Curve) بكتابة واضحة دون أي تداخل"""
    if not activities:
        fig = go.Figure()
        return fig

    sched = compute_cpm_schedule(activities, project_start_date)
    df = pd.DataFrame(sched)

    min_date = df["start_dt"].min()
    max_date = df["finish_dt"].max()
    months = pd.date_range(start=min_date, end=max_date + timedelta(days=31), freq='MS')
    monthly_costs = np.zeros(len(months))

    for _, row in df.iterrows():
        act_dur = max(1, row["duration"])
        daily_cost = row["cost"] / act_dur
        s_dt = row["start_dt"]
        f_dt = row["finish_dt"]
        for m_idx in range(len(months) - 1):
            m_start = months[m_idx]
            m_end = months[m_idx + 1]
            overlap_start = max(s_dt, m_start)
            overlap_end = min(f_dt, m_end)
            if overlap_end > overlap_start:
                days_in_month = (overlap_end - overlap_start).days
                monthly_costs[m_idx] += days_in_month * daily_cost

    total_months = len(months)
    if total_months <= 18:
        cf_dtick = "M1"
    elif total_months <= 36:
        cf_dtick = "M2"
    else:
        cf_dtick = "M3"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months[:-1],
        y=monthly_costs[:-1],
        mode='lines+markers',
        line=dict(color='#0284C7', width=3.5, shape='spline'),
        marker=dict(size=8, color='#0284C7', line=dict(width=2, color='#FFFFFF')),
        fill='tozeroy',
        fillcolor='rgba(2, 132, 199, 0.14)',
        name=ar(f'المصروفات الشهرية ({currency_symbol}/Month)'),
        hovertemplate="<b>الشهر:</b> %{x|%b %Y}<br><b>التدفق المالي المطلوب:</b> %{y:,.0f} " + currency_symbol + "<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text=ar(f"منحنى التدفق النقدي والمصروفات الشهرية المتزامن ({currency_symbol} / Month)"),
            font=dict(family="Cairo, Segoe UI, sans-serif", size=13, color="#0F172A"),
            x=0.98,
            xanchor="right"
        ),
        height=300,
        font=dict(family="Cairo, Segoe UI, Tahoma, sans-serif", size=11, color="#0F172A"),
        margin=dict(l=110, r=40, t=65, b=45),
        xaxis=dict(
            type="date",
            tickformat="%b %Y",
            dtick=cf_dtick,
            showgrid=True,
            gridcolor="#CBD5E1",
            gridwidth=1.2,
            showline=True,
            linecolor="#0F172A",
            linewidth=1.5,
            mirror="allticks",
            tickfont=dict(family="Cairo, Segoe UI, Tahoma, sans-serif", size=11, color="#0F172A"),
            title=dict(text=ar("مسطرة التواريخ وتوزيع الموازنة بالشهور والسنوات"), font=dict(family="Cairo, Segoe UI, sans-serif", size=11, color="#475569")),
            automargin=True
        ),
        yaxis=dict(
            tickformat=",.0f",
            tickprefix=f"{currency_symbol} ",
            gridcolor="#E2E8F0",
            showline=True,
            linecolor="#94A3B8",
            tickfont=dict(family="Cairo, Segoe UI, Tahoma, sans-serif", size=11, color="#1E293B"),
            title=dict(text=ar(f"المصروفات الشهرية ({currency_symbol})"), font=dict(family="Cairo, Segoe UI, sans-serif", size=11, color="#475569")),
            automargin=True
        )
    )

    return fig

def export_fig_to_png(fig: go.Figure, width: int = 1400, height: int = 800) -> Optional[bytes]:
    """تحويل وتصدير مخطط جانت أو التدفق النقدي إلى ملف صورة عالي الدقة (PNG)"""
    try:
        return fig.to_image(format="png", width=width, height=height, scale=2)
    except Exception as e:
        print(f"Image export error: {e}")
        return None

def generate_p6_schedule_printable_html(
    meta: Dict[str, Any],
    cpm_sched: List[Dict[str, Any]],
    currency_symbol: str = "$"
) -> str:
    """توليد تقرير رسمي متكامل قابل للطباعة والحفظ الفوري كملف PDF للجدول الزمني P6 ومخطط جانت"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_cost = sum(s.get("cost", 0) for s in cpm_sched)
    crit_count = sum(1 for s in cpm_sched if s.get("is_critical"))
    
    if cpm_sched:
        min_start = min(s["start_dt"] for s in cpm_sched).strftime("%Y-%m-%d")
        max_finish = max(s["finish_dt"] for s in cpm_sched).strftime("%Y-%m-%d")
        dur_days = (max(s["finish_dt"] for s in cpm_sched) - min(s["start_dt"] for s in cpm_sched)).days
    else:
        min_start, max_finish, dur_days = "—", "—", 0

    rows_html = ""
    for idx, row in enumerate(cpm_sched, 1):
        crit_badge = '<span style="background:#FEE2E2; color:#DC2626; padding:2px 8px; border-radius:4px; font-weight:700;">🔴 حرج CPM</span>' if row.get("is_critical") else '<span style="background:#EFF6FF; color:#2563EB; padding:2px 8px; border-radius:4px; font-weight:700;">🔵 اعتيادي</span>'
        bg = "#FFFFFF" if idx % 2 == 0 else "#F8FAFC"
        rows_html += f"""
        <tr style="background:{bg}; border-bottom:1px solid #E2E8F0; text-align:center;">
            <td style="padding:8px 10px; font-weight:700; color:#0F172A;">{row.get('id')}</td>
            <td style="padding:8px 10px; text-align:right; font-weight:600; color:#1E293B;">{row.get('name_ar')}</td>
            <td style="padding:8px 10px; color:#475569;">{row.get('start_date')}</td>
            <td style="padding:8px 10px; color:#475569;">{row.get('finish_date')}</td>
            <td style="padding:8px 10px; font-weight:700;">{row.get('duration')} يوم</td>
            <td style="padding:8px 10px; color:#64748B;">{row.get('total_float')} يوم</td>
            <td style="padding:8px 10px;">{crit_badge}</td>
            <td style="padding:8px 10px; font-weight:700; color:#0F172A;">{row.get('cost', 0):,.0f} {currency_symbol}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تقرير الجدول الزمني ومخطط جانت - {meta.get('name_ar')}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif; }}
        body {{ background: #F8FAFC; padding: 24px; color: #0F172A; line-height: 1.6; direction: rtl; }}
        .report-card {{ background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 12px; padding: 28px; max-width: 1000px; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
        .header-box {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0F172A; padding-bottom: 14px; margin-bottom: 20px; }}
        .title-area h2 {{ font-size: 1.35rem; color: #0F172A; font-weight: 800; }}
        .title-area p {{ font-size: 0.85rem; color: #64748B; }}
        .meta-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }}
        .meta-item {{ background: #F1F5F9; padding: 10px 14px; border-radius: 8px; border: 1px solid #E2E8F0; text-align: center; }}
        .meta-label {{ font-size: 0.76rem; color: #64748B; font-weight: 600; display: block; }}
        .meta-val {{ font-size: 1.1rem; color: #0F172A; font-weight: 800; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 0.85rem; }}
        th {{ background: #0F172A; color: #FFFFFF; padding: 10px; font-weight: 700; text-align: center; }}
        .print-btn-bar {{ text-align: left; margin-bottom: 16px; }}
        .btn-print {{ background: #2563EB; color: white; border: none; padding: 8px 18px; border-radius: 8px; font-size: 0.9rem; font-weight: 700; cursor: pointer; }}
        .footer {{ text-align: center; margin-top: 30px; font-size: 0.8rem; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 12px; }}
        
        @media print {{
            body {{ background: white; padding: 0; }}
            .report-card {{ border: none; box-shadow: none; padding: 0; }}
            .print-btn-bar {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="report-card">
        <div class="print-btn-bar">
            <button class="btn-print" onclick="window.print()">🖨️ طباعة / حفظ كـ PDF (Print to PDF)</button>
        </div>

        <div class="header-box">
            <div class="title-area">
                <h2>📋 تقرير شبكة الأنشطة والمسار الحرج (Primavera P6 CPM Schedule)</h2>
                <p>جمهورية العراق • المنصة الهندسية المتكاملة لتقييم المخاطر وإدارة المشاريع (ICRAT 2.0)</p>
            </div>
            <div style="text-align: left; font-size: 0.8rem; color: #64748B;">
                <b>تاريخ التوليد:</b> {now_str}<br>
                <b>رقم المشروع:</b> {meta.get('id', 'PROJ_01')}
            </div>
        </div>

        <div class="meta-grid">
            <div class="meta-item">
                <span class="meta-label">🏗️ اسم المشروع:</span>
                <span class="meta-val" style="font-size:0.95rem;">{meta.get('name_ar', 'مشروع إنشائي')}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">⏱️ مدة المسار الحرج CPM:</span>
                <span class="meta-val" style="color:#2563EB;">{dur_days} يوم</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">🔴 الأنشطة الحرجة:</span>
                <span class="meta-val" style="color:#DC2626;">{crit_count} / {len(cpm_sched)}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">💰 كلفة الأنشطة المباشرة:</span>
                <span class="meta-val" style="color:#059669;">{total_cost:,.0f} {currency_symbol}</span>
            </div>
        </div>

        <h3 style="font-size:1.05rem; color:#0F172A; margin-bottom:8px;">📊 جدول تفاصيل الأنشطة وتواريخ البدء والانتهاء (WBS Schedule Matrix):</h3>
        <table>
            <thead>
                <tr>
                    <th>رمز النشاط</th>
                    <th>اسم النشاط الإنشائي</th>
                    <th>تاريخ البدء</th>
                    <th>تاريخ الانتهاء</th>
                    <th>المدة</th>
                    <th>السماحية</th>
                    <th>المسار</th>
                    <th>الكلفة التقديرية</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <div class="footer">
            Designed and developed by Dr Ahmed Louay Ahmed • تم التوليد آلياً عبر منصة ICRAT 2.0
        </div>
    </div>
</body>
</html>
"""
    return html
