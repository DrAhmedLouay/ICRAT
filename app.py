"""
Iraqi Construction Risk Assessment & Decision Support Platform (ICRAT 2.0)
المنصة الهندسية المتكاملة لتقييم المخاطر، إدارة المطالبات التعاقدية، ونمذجة البناء 4D/5D
الإصدار 2.0 المتقدم (Primavera P6, EOT Claims, What-If Simulator, AI Copilot, 3D BIM Risk Viewer)
"""

import os
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import importlib
from datetime import datetime
import arabic_reshaper
import math

import iraqi_risk_db
import simulation_engine
import project_samples
import iso31000_coordination
import report_generator
import ifc_parser
import p6_parser
import eot_claims_engine
import what_if_engine
import contract_copilot
import bim_3d_viewer
import p6_gantt_visualizer
import webgl_bim_viewer
import navisworks_parser
import iraq_georisk_engine
import ai_bim_decision_hub
import glossary_data
import streamlit.components.v1 as components

# تهيئة معالجة النصوص العربية
def ar(text: str) -> str:
    """ربط وتشكيل الحروف العربية مع الحفاظ التام على الاتجاه الطبيعي الصحيح للقراءة دون انعكاس"""
    if not text:
        return ""
    try:
        return arabic_reshaper.reshape(str(text))
    except Exception:
        return str(text)

def render_centered_table(df: pd.DataFrame, max_height: Optional[int] = 480):
    """عرض الجداول بتنسيق HTML فائق الدقة مع تثبيت الهيدر وتمرير عمودي وأفقي سلس وتوسيط الخلايا"""
    scroll_style = f"max-height: {max_height}px; overflow-y: auto; overflow-x: auto;" if max_height else "overflow-x: auto;"
    html = f'<div style="{scroll_style} border: 1px solid #CBD5E1; border-radius: 12px; margin: 14px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.03); position: relative;">'
    html += '<table style="width: 100%; border-collapse: collapse; text-align: center; font-family: Cairo, Segoe UI, sans-serif; font-size: 0.88rem; direction: rtl;">'
    html += '<thead style="position: sticky; top: 0; z-index: 10;"><tr style="background-color: #F1F5F9; border-bottom: 2px solid #94A3B8;">'
    for col in df.columns:
        html += f'<th style="padding: 12px 14px; text-align: center !important; vertical-align: middle; color: #0F172A; font-weight: 800; white-space: nowrap; border-left: 1px solid #E2E8F0; background: #F1F5F9;">{col}</th>'
    html += '</tr></thead><tbody>'
    for idx, row in df.iterrows():
        bg = '#FFFFFF' if idx % 2 == 0 else '#F8FAFC'
        html += f'<tr style="background-color: {bg}; border-bottom: 1px solid #E2E8F0;">'
        for val in row:
            html += f'<td style="padding: 10px 14px; text-align: center !important; vertical-align: middle; color: #334155; white-space: nowrap; border-left: 1px solid #F1F5F9; font-weight: 600;">{val}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_decision_hub_html_grid(df: pd.DataFrame):
    """عرض مصفوفة القرارات الهندسية ISO 31000 بتنسيق HTML/CSS فائق الدقة مع شريط تمرير 2D ورأس ثابت وتفاصيل العناصر المتعارضة (Element ID & Item Name)"""
    parts = []
    parts.append('<div style="max-height: 520px; overflow-y: auto; overflow-x: auto; border: 1px solid #CBD5E1; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.04); direction: rtl; background: #FFFFFF; position: relative; margin: 12px 0;">')
    parts.append('<table style="width: 100%; border-collapse: collapse; font-family: Cairo, Segoe UI, Tahoma, sans-serif; font-size: 0.84rem; direction: rtl; text-align: right;">')
    parts.append('<thead style="position: sticky; top: 0; z-index: 20; background: #0F172A; color: #F8FAFC;">')
    parts.append('<tr style="border-bottom: 2px solid #334155;">')
    parts.append('<th style="padding: 12px 14px; text-align: center; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 85px; border-left: 1px solid #334155;">كود التعارض</th>')
    parts.append('<th style="padding: 12px 14px; text-align: center; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 160px; border-left: 1px solid #334155;">معرف العناصر (Element ID)</th>')
    parts.append('<th style="padding: 12px 14px; text-align: right; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 190px; border-left: 1px solid #334155;">أسماء العناصر المتعارضة (Item Name)</th>')
    parts.append('<th style="padding: 12px 14px; text-align: right; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 170px; border-left: 1px solid #334155;">توصيف التعارض</th>')
    parts.append('<th style="padding: 12px 14px; text-align: center; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 100px; border-left: 1px solid #334155;">مؤشر الأولوية Ψ</th>')
    parts.append('<th style="padding: 12px 14px; text-align: center; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 165px; border-left: 1px solid #334155;">تقييم ISO 31000</th>')
    parts.append('<th style="padding: 12px 14px; text-align: right; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 220px; border-left: 1px solid #334155;">فارق التقييم الذكي (2D نظري ⇄ 4D تنفيذي)</th>')
    parts.append('<th style="padding: 12px 14px; text-align: right; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 190px; border-left: 1px solid #334155;">نشاط P6 المتأثر</th>')
    parts.append('<th style="padding: 12px 14px; text-align: center; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 135px; border-left: 1px solid #334155;">المسار الحرج</th>')
    parts.append('<th style="padding: 12px 14px; text-align: center; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 90px; border-left: 1px solid #334155;">أيام التأخير</th>')
    parts.append('<th style="padding: 12px 14px; text-align: center; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 115px; border-left: 1px solid #334155;">كلفة المعالجة 5D</th>')
    parts.append('<th style="padding: 12px 14px; text-align: right; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 175px; border-left: 1px solid #334155;">العامل التفسيري الأكبر (AI)</th>')
    parts.append('<th style="padding: 12px 14px; text-align: center; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 105px; border-left: 1px solid #334155;">استراتيجية ISO</th>')
    parts.append('<th style="padding: 12px 14px; text-align: right; white-space: nowrap; background: #0F172A; color: #F8FAFC; min-width: 250px;">التوصية الإنشائية</th>')
    parts.append('</tr></thead><tbody>')

    for idx, row in df.iterrows():
        bg = '#FFFFFF' if idx % 2 == 0 else '#F8FAFC'
        
        score_val = float(str(row.get("مؤشر الأولوية Ψ", "0")).replace("/100", "").strip() or 0)
        if score_val >= 70:
            badge_score = f'<span style="background:#FEE2E2; color:#991B1B; padding:3px 8px; border-radius:6px; font-weight:800; font-size:0.82rem;">{row.get("مؤشر الأولوية Ψ")}</span>'
        elif score_val >= 40:
            badge_score = f'<span style="background:#FEF3C7; color:#92400E; padding:3px 8px; border-radius:6px; font-weight:800; font-size:0.82rem;">{row.get("مؤشر الأولوية Ψ")}</span>'
        else:
            badge_score = f'<span style="background:#DCFCE7; color:#166534; padding:3px 8px; border-radius:6px; font-weight:800; font-size:0.82rem;">{row.get("مؤشر الأولوية Ψ")}</span>'
            
        crit_txt = str(row.get("المسار الحرج", ""))
        if "حرج" in crit_txt:
            badge_crit = '<span style="background:#FEF2F2; color:#DC2626; border:1px solid #FECACA; padding:3px 8px; border-radius:6px; font-weight:700; font-size:0.78rem;">🔴 حرج (Float=0)</span>'
        else:
            badge_crit = f'<span style="background:#F0FDF4; color:#166534; border:1px solid #BBF7D0; padding:3px 8px; border-radius:6px; font-weight:700; font-size:0.78rem;">{crit_txt}</span>'

        strat_txt = str(row.get("استراتيجية ISO 31000", "MITIGATE"))
        strat_bg = "#EDE9FE" if strat_txt == "MITIGATE" else ("#FEE2E2" if strat_txt == "AVOID" else "#DCFCE7")
        strat_color = "#5B21B6" if strat_txt == "MITIGATE" else ("#991B1B" if strat_txt == "AVOID" else "#166534")
        badge_strat = f'<span style="background:{strat_bg}; color:{strat_color}; padding:3px 8px; border-radius:6px; font-weight:800; font-size:0.75rem;">{strat_txt}</span>'

        delta_txt = str(row.get("الفارق الذكي (4D Delta)", ""))
        if "تصعيد" in delta_txt or "Float = 0" in delta_txt:
            badge_delta = f'<span style="background:#FEF2F2; color:#DC2626; border:1px solid #FECACA; padding:3px 8px; border-radius:6px; font-size:0.77rem; font-weight:700;">{delta_txt}</span>'
        elif "خفض" in delta_txt or "حماية" in delta_txt:
            badge_delta = f'<span style="background:#F0FDF4; color:#15803D; border:1px solid #BBF7D0; padding:3px 8px; border-radius:6px; font-size:0.77rem; font-weight:700;">{delta_txt}</span>'
        else:
            badge_delta = f'<span style="background:#F8FAFC; color:#475569; border:1px solid #E2E8F0; padding:3px 8px; border-radius:6px; font-size:0.77rem; font-weight:600;">{delta_txt}</span>'

        el_id_badge = f'<span style="font-family:Consolas,SFMono-Regular,monospace; background:#F1F5F9; color:#0F172A; padding:3px 7px; border-radius:6px; font-weight:700; font-size:0.77rem; border:1px solid #CBD5E1; white-space:nowrap;">{row.get("معرف العناصر (Element ID)", "—")}</span>'
        item_name_badge = f'<span style="color:#1E293B; font-weight:600; font-size:0.80rem;">{row.get("أسماء العناصر (Item Name)", "—")}</span>'

        parts.append(f'<tr style="background-color: {bg}; border-bottom: 1px solid #E2E8F0;">')
        parts.append(f'<td style="padding: 10px 12px; text-align: center; font-weight: 700; color: #1E293B; border-left: 1px solid #F1F5F9; white-space: nowrap;">{row.get("كود التعارض")}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: center; border-left: 1px solid #F1F5F9; white-space: nowrap;">{el_id_badge}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: right; border-left: 1px solid #F1F5F9;">{item_name_badge}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: right; color: #475569; border-left: 1px solid #F1F5F9; font-size: 0.81rem; font-weight: 600;">{row.get("توصيف التعارض")}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: center; border-left: 1px solid #F1F5F9; white-space: nowrap;">{badge_score}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: center; color: #475569; border-left: 1px solid #F1F5F9; font-size: 0.8rem; font-weight: 700;">{row.get("تقييم ISO 31000")}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: right; border-left: 1px solid #F1F5F9;">{badge_delta}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: right; color: #1E293B; border-left: 1px solid #F1F5F9; font-weight: 600;">{row.get("نشاط P6 المتأثر")}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: center; border-left: 1px solid #F1F5F9; white-space: nowrap;">{badge_crit}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: center; color: #D97706; font-weight: 700; border-left: 1px solid #F1F5F9; white-space: nowrap;">{row.get("أيام التأخير")}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: center; color: #059669; font-weight: 700; border-left: 1px solid #F1F5F9; white-space: nowrap;">{row.get("كلفة المعالجة 5D")}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: right; color: #64748B; font-size: 0.82rem; border-left: 1px solid #F1F5F9;">{row.get("العامل التفسيري الأكبر (AI)")}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: center; border-left: 1px solid #F1F5F9; white-space: nowrap;">{badge_strat}</td>')
        parts.append(f'<td style="padding: 10px 12px; text-align: right; color: #334155; font-size: 0.83rem; line-height: 1.4;">{row.get("التوصية الإنشائية")}</td>')
        parts.append('</tr>')

    parts.append('</tbody></table></div>')
    st.markdown("".join(parts), unsafe_allow_html=True)

def render_iso31000_matrix_html(issues):
    """عرض مصفوفة التنسيق 5x5 ISO 31000 بتصميم هندسي فائق الوضوح مع مناطق الخطورة الملونة والشارات الحية"""
    grid = {}
    for l in range(1, 6):
        for c in range(1, 6):
            grid[(l, c)] = []
    
    for issue in issues:
        l = max(1, min(5, int(issue.get('likelihood', 1))))
        c = max(1, min(5, int(issue.get('consequence', 1))))
        grid[(l, c)].append(issue)

    l_labels = {5: '5-شبه مؤكد', 4: '4-مرجح', 3: '3-متوسط', 2: '2-محتمل', 1: '1-نادر'}
    c_labels = {1: '1-ضئيل', 2: '2-طفيف', 3: '3-متوسط', 4: '4-كبير', 5: '5-كارثي'}

    html = '<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:14px; padding:16px; box-shadow:0 2px 10px rgba(0,0,0,0.04); margin-bottom:15px; direction:rtl;">'
    html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid #E2E8F0; padding-bottom:8px;">'
    html += '<b style="font-size:1.02rem; color:#0F172A;">🎯 مصفوفة تقييم التعارضات والتنسيق (ISO 31000:2018)</b>'
    html += '<span style="font-size:0.8rem; color:#64748B; font-weight:700;">الاحتمالية × الشدة</span>'
    html += '</div>'
    
    html += '<div style="overflow-x:auto;">'
    html += '<table style="width:100%; border-collapse:separate; border-spacing:6px; font-family:Cairo, sans-serif; text-align:center;">'
    
    html += '<thead><tr>'
    html += '<th style="background:#0F172A; color:#F8FAFC; padding:10px 8px; border-radius:8px; font-size:0.82rem; min-width:110px;">الاحتمالية ↓ / الشدة ←</th>'
    for c in range(1, 6):
        html += f'<th style="background:#F1F5F9; color:#1E293B; padding:10px 8px; border-radius:8px; font-size:0.84rem; font-weight:800; border:1px solid #CBD5E1; min-width:90px;">{c_labels[c]}</th>'
    html += '</tr></thead><tbody>'

    for l in range(5, 0, -1):
        html += f'<tr><td style="background:#F1F5F9; color:#1E293B; padding:10px 8px; border-radius:8px; font-weight:800; font-size:0.84rem; border:1px solid #CBD5E1;">{l_labels[l]}</td>'
        for c in range(1, 6):
            score = l * c
            cell_issues = grid.get((l, c), [])
            count = len(cell_issues)
            
            if score >= 15:
                bg = '#FEF2F2'
                border = '#EF4444'
                badge_bg = '#DC2626'
                txt_col = '#991B1B'
                zone_name = 'حرج غير مقبول'
            elif score >= 8:
                bg = '#FFFBEB'
                border = '#F59E0B'
                badge_bg = '#D97706'
                txt_col = '#92400E'
                zone_name = 'متوسط ALARP'
            else:
                bg = '#F0FDF4'
                border = '#10B981'
                badge_bg = '#059669'
                txt_col = '#166534'
                zone_name = 'مقبول مع الرصد'

            titles_tooltip = '\\n'.join([f"• {iss['id']}: {iss['title_ar']}" for iss in cell_issues])
            tooltip_attr = f'title="{zone_name} (Score: {score})\\n{titles_tooltip}"' if count > 0 else f'title="{zone_name} (Score: {score})"'

            cell_content = f'<div style="font-size:0.72rem; color:{txt_col}; opacity:0.85; font-weight:700;">Score {score}</div>'
            if count > 0:
                cell_content += f'<div style="margin-top:4px;"><span style="background:{badge_bg}; color:white; font-size:0.85rem; font-weight:900; padding:3px 10px; border-radius:18px; box-shadow:0 2px 6px rgba(0,0,0,0.18); display:inline-block;">{count} تعارض</span></div>'
            else:
                cell_content += '<div style="color:#CBD5E1; font-size:0.85rem; margin-top:3px;">—</div>'

            html += f'<td {tooltip_attr} style="background:{bg}; border:2px solid {border}; border-radius:10px; padding:8px 6px; vertical-align:middle; cursor:pointer;">{cell_content}</td>'
        html += '</tr>'

    html += '</tbody></table></div>'

    html += '<div style="display:flex; justify-content:center; gap:16px; margin-top:14px; flex-wrap:wrap; font-size:0.82rem; font-weight:700;">'
    html += '<div style="display:flex; align-items:center; gap:6px;"><span style="width:14px; height:14px; background:#EF4444; border-radius:4px; display:inline-block;"></span> <span style="color:#991B1B;">🔴 حرج غير مقبول (15 - 25): ورشة حسم فورية</span></div>'
    html += '<div style="display:flex; align-items:center; gap:6px;"><span style="width:14px; height:14px; background:#F59E0B; border-radius:4px; display:inline-block;"></span> <span style="color:#92400E;">🟡 متوسط ALARP (8 - 14): خطة تخفيف مسبقة</span></div>'
    html += '<div style="display:flex; align-items:center; gap:6px;"><span style="width:14px; height:14px; background:#10B981; border-radius:4px; display:inline-block;"></span> <span style="color:#166534;">🟢 مقبول (1 - 6): رصد ومتابعة موقعية</span></div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_risk_matrix_html(risks):
    """عرض مصفوفة المخاطر النوعية 5x5 بتصميم هندسي واضح مع الشارات الحية"""
    grid = {}
    for l in range(1, 6):
        for c in range(1, 6):
            grid[(l, c)] = []
    
    for risk in risks:
        p = max(1, min(5, int(risk.get('probability', 1))))
        i = max(1, min(5, int(risk.get('impact', 1))))
        grid[(p, i)].append(risk)

    p_labels = {5: '5-شبه مؤكد', 4: '4-مرجح', 3: '3-متوسط', 2: '2-محتمل', 1: '1-نادر'}
    i_labels = {1: '1-ضئيل', 2: '2-منخفض', 3: '3-متوسط', 4: '4-عالي', 5: '5-كارثي'}

    html = '<div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:14px; padding:16px; box-shadow:0 2px 10px rgba(0,0,0,0.04); margin-bottom:15px; direction:rtl;">'
    html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid #E2E8F0; padding-bottom:8px;">'
    html += '<b style="font-size:1.02rem; color:#0F172A;">🎯 مصفوفة الخطر النوعية للبيئة العراقية (5x5 Matrix)</b>'
    html += '<span style="font-size:0.8rem; color:#64748B; font-weight:700;">الاحتمالية × التأثير</span>'
    html += '</div>'
    
    html += '<div style="overflow-x:auto;">'
    html += '<table style="width:100%; border-collapse:separate; border-spacing:6px; font-family:Cairo, sans-serif; text-align:center;">'
    
    html += '<thead><tr>'
    html += '<th style="background:#0F172A; color:#F8FAFC; padding:10px 8px; border-radius:8px; font-size:0.82rem; min-width:110px;">الاحتمالية ↓ / التأثير ←</th>'
    for i in range(1, 6):
        html += f'<th style="background:#F1F5F9; color:#1E293B; padding:10px 8px; border-radius:8px; font-size:0.84rem; font-weight:800; border:1px solid #CBD5E1; min-width:90px;">{i_labels[i]}</th>'
    html += '</tr></thead><tbody>'

    for p in range(5, 0, -1):
        html += f'<tr><td style="background:#F1F5F9; color:#1E293B; padding:10px 8px; border-radius:8px; font-weight:800; font-size:0.84rem; border:1px solid #CBD5E1;">{p_labels[p]}</td>'
        for i in range(1, 6):
            score = p * i
            cell_risks = grid.get((p, i), [])
            count = len(cell_risks)
            
            if score >= 15:
                bg = '#FEF2F2'
                border = '#EF4444'
                badge_bg = '#DC2626'
                txt_col = '#991B1B'
                zone_name = 'خطر عالي وحرج'
            elif score >= 8:
                bg = '#FFFBEB'
                border = '#F59E0B'
                badge_bg = '#D97706'
                txt_col = '#92400E'
                zone_name = 'خطر متوسط'
            else:
                bg = '#F0FDF4'
                border = '#10B981'
                badge_bg = '#059669'
                txt_col = '#166534'
                zone_name = 'خطر منخفض'

            titles_tooltip = '\\n'.join([f"• {r['id']}: {r['title_ar']}" for r in cell_risks])
            tooltip_attr = f'title="{zone_name} (Score: {score})\\n{titles_tooltip}"' if count > 0 else f'title="{zone_name} (Score: {score})"'

            cell_content = f'<div style="font-size:0.72rem; color:{txt_col}; opacity:0.85; font-weight:700;">Score {score}</div>'
            if count > 0:
                cell_content += f'<div style="margin-top:4px;"><span style="background:{badge_bg}; color:white; font-size:0.85rem; font-weight:900; padding:3px 10px; border-radius:18px; box-shadow:0 2px 6px rgba(0,0,0,0.18); display:inline-block;">{count} مخاطر</span></div>'
            else:
                cell_content += '<div style="color:#CBD5E1; font-size:0.85rem; margin-top:3px;">—</div>'

            html += f'<td {tooltip_attr} style="background:{bg}; border:2px solid {border}; border-radius:10px; padding:8px 6px; vertical-align:middle; cursor:pointer;">{cell_content}</td>'
        html += '</tr>'

    html += '</tbody></table></div>'

    html += '<div style="display:flex; justify-content:center; gap:16px; margin-top:14px; flex-wrap:wrap; font-size:0.82rem; font-weight:700;">'
    html += '<div style="display:flex; align-items:center; gap:6px;"><span style="width:14px; height:14px; background:#EF4444; border-radius:4px; display:inline-block;"></span> <span style="color:#991B1B;">🔴 مخاطر عالية (15 - 25): تتطلب إجراءات طوارئ</span></div>'
    html += '<div style="display:flex; align-items:center; gap:6px;"><span style="width:14px; height:14px; background:#F59E0B; border-radius:4px; display:inline-block;"></span> <span style="color:#92400E;">🟡 مخاطر متوسطة (8 - 14): تخفيف ومتابعة مستمرة</span></div>'
    html += '<div style="display:flex; align-items:center; gap:6px;"><span style="width:14px; height:14px; background:#10B981; border-radius:4px; display:inline-block;"></span> <span style="color:#166534;">🟢 مخاطر منخفضة (1 - 6): مقبولة وضمن السيطرة</span></div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

# إعداد الصفحة
st.set_page_config(
    page_title="ICRAT 2.0 | المنصة الهندسية المتكاملة لتقييم المخاطر والمطالبات",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص المظهر وتنسيقات CSS المتقدمة
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');
    
    :root {
        --primary-blue: #2563EB;
        --navy-dark: #0F172A;
        --navy-light: #1E293B;
        --emerald-green: #10B981;
        --amber-gold: #F59E0B;
        --crimson-red: #EF4444;
        --slate-bg: #F8FAFC;
        --card-border: #E2E8F0;
        --radius-lg: 14px;
        --radius-md: 10px;
    }

    html, body, .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Cairo', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        direction: rtl;
        text-align: right;
        line-height: 1.68 !important;
    }

    p, li {
        margin-bottom: 0.65rem !important;
        line-height: 1.75 !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        color: #334155;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cairo', sans-serif !important;
        font-weight: 800 !important;
        line-height: 1.45 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.75rem !important;
        color: #0F172A;
    }

    /* ضبط القائمة الجانبية الموحدة */
    section[data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
        background: #F8FAFC !important;
        border-left: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] > div {
        direction: rtl !important;
        text-align: right !important;
        padding-top: 1.2rem !important;
    }
    
    /* ضبط التبويبات Tabs وجعلها انسيابية */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl !important;
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: flex-start !important;
        gap: 8px !important;
        border-bottom: 2px solid #E2E8F0 !important;
        padding-bottom: 8px !important;
    }
    .stTabs [data-baseweb="tab"] {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        padding: 8px 14px !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #F1F5F9 !important;
        border-color: #94A3B8 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #EFF6FF, #DBEAFE) !important;
        border-color: #3B82F6 !important;
        color: #1D4ED8 !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
    }

    /* عزل حاويات الرسوم البيانية Plotly */
    .stPlotlyChart, div[data-testid="stPlotlyChart"], .js-plotly-plot, .plotly, svg.main-svg {
        direction: ltr !important;
        text-align: center !important;
        border-radius: 12px !important;
    }

    /* معالجة منزلقات الأرقام Sliders */
    div[data-testid="stSlider"] {
        direction: rtl !important;
        text-align: right !important;
        margin-top: 6px !important;
        margin-bottom: 16px !important;
    }
    div[data-testid="stSlider"] label {
        direction: rtl !important;
        text-align: right !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
        display: block !important;
        margin-bottom: 6px !important;
        line-height: 1.4 !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] {
        direction: ltr !important;
    }
    div[data-testid="stSlider"] [data-testid="stThumbValue"] {
        direction: ltr !important;
        font-family: 'Segoe UI', Tahoma, monospace, sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        color: #1E40AF !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* شارات الأرقام والمصطلحات */
    .val-badge {
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 4px 12px;
        font-weight: 800;
        font-size: 0.88rem;
        direction: ltr !important;
        display: inline-block;
        margin-top: 4px;
        margin-bottom: 8px;
        font-family: 'Segoe UI', Tahoma, sans-serif !important;
        line-height: 1.3 !important;
    }

    .en-badge {
        direction: ltr !important;
        unicode-bidi: isolate !important;
        display: inline-block;
        font-family: 'Segoe UI', Tahoma, sans-serif !important;
        font-weight: 700;
        background: #F1F5F9;
        padding: 2px 8px;
        border-radius: 6px;
        border: 1px solid #CBD5E1;
        font-size: 0.84em;
        margin: 0 4px;
        line-height: 1.3 !important;
    }
    
    .en-subtext {
        direction: ltr !important;
        unicode-bidi: isolate !important;
        display: block;
        font-family: 'Segoe UI', Tahoma, sans-serif !important;
        font-size: 0.78rem;
        color: #64748B;
        text-align: left;
        margin-top: 3px;
        line-height: 1.3 !important;
    }

    /* الهيدر وبطاقات المؤشرات المتطورة */
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        border-right: 6px solid #3B82F6;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        direction: rtl;
        text-align: right;
    }
    
    .kpi-card {
        background: #FFFFFF;
        padding: 18px 16px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
        text-align: center;
        direction: rtl;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.08);
        border-color: #CBD5E1;
    }
    .kpi-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #64748B;
        margin-bottom: 6px;
        line-height: 1.4 !important;
    }
    .kpi-value {
        font-size: 1.78rem;
        font-weight: 900;
        color: #0F172A;
        direction: ltr !important;
        display: block;
        margin: 4px 0;
        line-height: 1.2 !important;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #059669;
        font-weight: 700;
        margin-top: 4px;
        line-height: 1.3 !important;
    }

    /* حقول الإدخال المحسنة */
    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextArea"] label {
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        margin-bottom: 6px !important;
        direction: rtl !important;
        text-align: right !important;
        color: #1E293B !important;
    }

    input, textarea, select {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    div[data-testid="stNumberInput"] input {
        direction: ltr !important;
        text-align: center !important;
        font-family: 'Segoe UI', Tahoma, monospace, sans-serif !important;
        font-weight: 700 !important;
    }

    /* شريط المعلومات التنفيذي للواجهة العصرية المضيئة */
    .modern-topbar {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 14px;
        padding: 14px 22px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 6px 24px rgba(0,0,0,0.15);
        direction: rtl;
    }
    .topbar-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9rem;
    }
    .topbar-label {
        color: #94A3B8;
        font-weight: 600;
    }
    .topbar-val {
        color: #F8FAFC;
        font-weight: 800;
        font-family: 'Cairo', sans-serif;
    }
    .mode-badge-modern {
        background: linear-gradient(135deg, #2563EB 0%, #0284C7 100%);
        color: white;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 800;
        box-shadow: 0 2px 8px rgba(37,99,235,0.3);
    }
    .mode-badge-classic {
        background: #475569;
        color: white;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 800;
    }

    /* شريط سير العمل الهندسي الموجه (Workflow Breadcrumb Bar) */
    .workflow-bar {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 10px 16px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        direction: rtl;
    }
    .workflow-step {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.82rem;
        font-weight: 700;
        color: #64748B;
        padding: 4px 8px;
        border-radius: 6px;
    }
    .workflow-step.active {
        color: #1D4ED8;
        background: #EFF6FF;
        font-weight: 800;
    }
    .workflow-arrow {
        color: #CBD5E1;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

def load_clean_project_state(
    meta: dict,
    activities: list,
    risks: list = None,
    coordination_issues: list = None,
    delay_events: list = None,
    spatial_elements: list = None,
    ifc_bytes: bytes = None,
    ifc_filename: str = "model.ifc",
    source: str = "CUSTOM",
    success_msg: str = "🎉 تم بنجاح تفعيل المشروع وتصفية كافة البيانات السابقة!"
):
    """تفريغ وإعادة تهيئة كاملة لحالة الجلسة لضمان عزل تام للمشروع المستورد ومنع أي تداخل للبيانات السابقة"""
    st.session_state.project_source = source
    st.session_state.custom_project_meta = dict(meta)
    
    # 1. إحلال كامل للأنشطة دون أي بقايا سابقة
    st.session_state.activities = [dict(a) for a in activities]
    
    # 2. إحلال أو إعادة تعيين سجل المخاطر المعتمد
    if risks is not None:
        st.session_state.risk_register = [dict(r) for r in risks]
    else:
        st.session_state.risk_register = [dict(r) for r in iraqi_risk_db.DEFAULT_IRAQI_RISK_REGISTER]
        
    # 3. إحلال مشكلات التنسيق
    if coordination_issues is not None:
        st.session_state.coordination_issues = [dict(c) for c in coordination_issues]
    else:
        st.session_state.coordination_issues = [dict(c) for c in iso31000_coordination.DEFAULT_COORDINATION_ISSUES]
        
    # 4. إحلال أحداث التأخير والمطالبات
    if delay_events is not None:
        st.session_state.delay_events = [dict(e) for e in delay_events]
    else:
        st.session_state.delay_events = [dict(e) for e in eot_claims_engine.DEFAULT_DELAY_EVENTS]

    # 5. إحلال العناصر المكانية وملف الـ IFC للعارض ثلاثي الأبعاد WebGL
    if spatial_elements is not None:
        st.session_state.ifc_spatial_elements = [dict(s) for s in spatial_elements]
    else:
        st.session_state.ifc_spatial_elements = []

    if ifc_bytes is not None:
        st.session_state.uploaded_ifc_bytes = ifc_bytes
        st.session_state.uploaded_ifc_filename = ifc_filename
    else:
        st.session_state.uploaded_ifc_bytes = None
        st.session_state.uploaded_ifc_filename = "model.ifc"

    # 6. تصفية مفاتيح المنزلقات لإعادة بنائها نظيفة من قيم المشروع الجديد عند إعادة التشغيل
    for k in ["slider_rfis", "slider_co", "slider_cash", "slider_sub"]:
        st.session_state.pop(k, None)
    
    st.session_state.last_import_msg = success_msg

def process_universal_json_upload(data: Any, filename: str) -> Dict[str, Any]:
    """
    محلل ذكي ومتكيف لجميع ملفات JSON:
    1. ملفات النسخ الاحتياطي الكاملة (Full Project Backup)
    2. تذاكر التنسيق المفتوح (OpenBIM BCF 2.1 JSON)
    3. جداول الأنشطة والـ WBS الجزئية (Activities / Tasks / WBS JSON)
    4. سجلات المخاطر (Risks JSON)
    5. مطالبات وأحداث التأخير (Delay Events JSON)
    """
    clean_name = filename.replace(".json", "").replace("_", " ") if filename else "مشروع مخصص"

    # الحالة الأولى: إذا كان الملف مصفوفة / قائمة من العناصر List
    if isinstance(data, list):
        if not data:
            return {"success": False, "error": "ملف JSON فارغ لا يحتوي على أي بيانات!"}
        
        sample = data[0] if isinstance(data[0], dict) else {}
        
        # 1. هل هي قائمة تذاكر تنسيق BCF أو تعارضات؟
        if any(k in sample for k in ["topic", "clash_id", "guid", "topic_type", "creation_date"]):
            issues = []
            for idx, item in enumerate(data, start=1):
                if isinstance(item, dict):
                    priority = str(item.get("priority", "Normal")).upper()
                    c_val = 5 if priority in ["CRITICAL", "HIGH", "MAJOR"] else (3 if priority in ["NORMAL", "MEDIUM"] else 2)
                    issues.append({
                        "id": str(item.get("id", item.get("clash_id", f"BCF_{idx:03d}"))),
                        "guid": str(item.get("guid", f"guid_{idx}")),
                        "title_ar": str(item.get("title_ar", item.get("title", f"تذكرة BCF {idx}"))),
                        "title_en": str(item.get("title", item.get("title_en", f"BCF Topic {idx}"))),
                        "discipline": "MEP_STR",
                        "discipline_ar": "تنسيق OpenBIM BCF",
                        "likelihood": 4,
                        "consequence": c_val,
                        "risk_score": 4 * c_val,
                        "status_navis": str(item.get("status", "Active")),
                        "status_desc": f"حالة BCF: {item.get('status', 'Open')}",
                        "penetration_depth_mm": float(item.get("penetration_depth_mm", 60.0)),
                        "mitigation_ar": str(item.get("mitigation_ar", item.get("description", "تعديل المخططات التنفيذية وإعادة التوجيه في نموذج الـ BIM")))
                    })
            return {
                "success": True,
                "type": "BCF_TOPICS",
                "title": f"📋 تذاكر تنسيق OpenBIM BCF ({len(issues)} تذكرة)",
                "coordination_issues": issues,
                "msg": f"تم استخراج {len(issues)} تذكرة تنسيق هندسي بنجاح من ملف BCF JSON."
            }

        # 2. هل هي قائمة مخاطر؟
        elif any(k in sample for k in ["probability", "impact", "risk_id", "risk_code", "category_ar"]):
            risks_list = []
            for idx, r in enumerate(data, start=1):
                if isinstance(r, dict):
                    p = int(r.get("probability", r.get("p", 3)))
                    imp = int(r.get("impact", r.get("i", 3)))
                    risks_list.append({
                        "id": str(r.get("id", f"R_{idx:02d}")),
                        "code": str(r.get("code", f"R{idx:02d}")),
                        "category_ar": str(r.get("category_ar", "مخاطر تنفيذية")),
                        "name_ar": str(r.get("name_ar", r.get("name", f"بند خطر {idx}"))),
                        "description_ar": str(r.get("description_ar", "")),
                        "probability": p,
                        "impact": imp,
                        "score": p * imp,
                        "fidic_clause": str(r.get("fidic_clause", "17.3")),
                        "mitigation_ar": str(r.get("mitigation_ar", "متابعة مستمرة وإجراءات تخفيف"))
                    })
            return {
                "success": True,
                "type": "RISKS_LIST",
                "title": f"⚠️ سجل مخاطر ({len(risks_list)} خطر)",
                "risks": risks_list,
                "msg": f"تم استخراج {len(risks_list)} بند خطر بنجاح."
            }

        # 3. الافتراضي: قائمة أنشطة WBS
        else:
            acts = []
            for idx, a in enumerate(data, start=1):
                if isinstance(a, dict):
                    dur = float(a.get("duration", a.get("opt_duration", a.get("days", 10.0))))
                    cst = float(a.get("cost", a.get("cost_impact", a.get("budget", 50000.0))))
                    crit = bool(a.get("critical", False) or a.get("is_critical", False))
                    tf = int(a.get("total_float", 0 if crit else 10))
                    acts.append({
                        "id": str(a.get("id", f"ACT_{idx:02d}")),
                        "name": str(a.get("name", a.get("name_ar", f"Activity {idx}"))),
                        "name_ar": str(a.get("name_ar", a.get("name", f"نشاط {idx}"))),
                        "duration": max(1.0, dur),
                        "cost": max(1000.0, cst),
                        "critical": crit,
                        "total_float": tf
                    })
            meta = {
                "id": "CUSTOM_JSON_LIST",
                "name_ar": clean_name,
                "contract_original_cost": sum(a["cost"] for a in acts) if acts else 10000000.0,
                "contract_original_duration_days": int(sum(a["duration"] for a in acts)) if acts else 365,
                "location_ar": "العراق",
                "type_ar": "مشروع تشييد مستورد من JSON"
            }
            return {
                "success": True,
                "type": "ACTIVITIES_LIST",
                "title": f"📊 جدول أنشطة WBS ({len(acts)} نشاط)",
                "meta": meta,
                "activities": acts,
                "msg": f"تم استخراج {len(acts)} نشاط بنجاح وإنشاء بيانات المشروع تلقائياً."
            }

    # الحالة الثانية: إذا كان الملف قاموساً Dictionary
    elif isinstance(data, dict):
        # 1. فحص النسخة الكاملة أو المحتوية على أنشطة
        if "activities" in data or "meta" in data or "tasks" in data or "wbs" in data:
            raw_acts = data.get("activities", data.get("tasks", data.get("wbs", [])))
            acts = []
            for idx, a in enumerate(raw_acts, start=1):
                if isinstance(a, dict):
                    dur = float(a.get("duration", a.get("opt_duration", a.get("days", 10.0))))
                    cst = float(a.get("cost", a.get("cost_impact", a.get("budget", 50000.0))))
                    crit = bool(a.get("critical", False) or a.get("is_critical", False))
                    tf = int(a.get("total_float", 0 if crit else 10))
                    acts.append({
                        "id": str(a.get("id", f"ACT_{idx:02d}")),
                        "name": str(a.get("name", a.get("name_ar", f"Activity {idx}"))),
                        "name_ar": str(a.get("name_ar", a.get("name", f"نشاط {idx}"))),
                        "duration": max(1.0, dur),
                        "cost": max(1000.0, cst),
                        "critical": crit,
                        "total_float": tf
                    })
            
            raw_meta = data.get("meta", {})
            calc_cost = sum(a["cost"] for a in acts) if acts else 10000000.0
            calc_dur = int(sum(a["duration"] for a in acts)) if acts else 365
            
            meta = {
                "id": str(raw_meta.get("id", "CUSTOM_JSON_PROJ")),
                "name_ar": str(raw_meta.get("name_ar", clean_name)),
                "contract_original_cost": float(raw_meta.get("contract_original_cost", calc_cost)),
                "contract_original_duration_days": int(raw_meta.get("contract_original_duration_days", calc_dur)),
                "location_ar": str(raw_meta.get("location_ar", "العراق")),
                "type_ar": str(raw_meta.get("type_ar", "مشروع متكامل مستورد"))
            }
            return {
                "success": True,
                "type": "FULL_PROJECT",
                "title": f"🏗️ مشروع متكامل: '{meta['name_ar']}' ({len(acts)} نشاط)",
                "meta": meta,
                "activities": acts,
                "risks": data.get("risks", data.get("risk_register")),
                "coordination_issues": data.get("coordination_issues", data.get("clashes")),
                "delay_events": data.get("delay_events", data.get("claims")),
                "msg": f"نسخة متكاملة صالحة ({len(acts)} نشاط، {len(data.get('risks', []) or [])} مخاطر)."
            }

        # 2. فحص ملف OpenBIM BCF 2.1
        elif any(k in data for k in ["topics", "bcf_version", "project", "markup"]):
            raw_topics = data.get("topics", [])
            issues = []
            for idx, t in enumerate(raw_topics, start=1):
                guid = t.get("guid", f"bcf_guid_{idx}")
                title = t.get("title", f"تذكرة BCF {idx}")
                priority = str(t.get("priority", "Normal")).upper()
                c_val = 5 if priority in ["CRITICAL", "HIGH", "MAJOR"] else (3 if priority in ["NORMAL", "MEDIUM"] else 2)
                issues.append({
                    "id": f"BCF_{idx:03d}",
                    "guid": guid,
                    "title_ar": f"تذكرة BCF: {title}",
                    "title_en": title,
                    "discipline": "MEP_STR",
                    "discipline_ar": "تنسيق OpenBIM BCF",
                    "likelihood": 4,
                    "consequence": c_val,
                    "risk_score": 4 * c_val,
                    "status_navis": t.get("status", "Open"),
                    "status_desc": f"حالة BCF: {t.get('status', 'Open')}",
                    "penetration_depth_mm": 65.0,
                    "mitigation_ar": t.get("description", "تعديل المخططات التنفيذية وتوجيه المسار في BIM")
                })
            return {
                "success": True,
                "type": "BCF_TOPICS",
                "title": f"📋 ملف تذاكر OpenBIM BCF 2.1 ({len(issues)} تذكرة)",
                "coordination_issues": issues,
                "msg": f"تم استخراج {len(issues)} تذكرة تنسيق بنجاح من ملف OpenBIM BCF."
            }

        # 3. فحص سجل المخاطر
        elif "risks" in data or "risk_register" in data:
            raw_risks = data.get("risks", data.get("risk_register", []))
            return {
                "success": True,
                "type": "RISKS_LIST",
                "title": f"⚠️ سجل مخاطر ({len(raw_risks)} خطر)",
                "risks": raw_risks,
                "msg": f"تم استخراج {len(raw_risks)} خطر بنجاح."
            }

        # 4. فحص التعارضات المباشرة
        elif "coordination_issues" in data or "clashes" in data:
            raw_clashes = data.get("coordination_issues", data.get("clashes", []))
            return {
                "success": True,
                "type": "BCF_TOPICS",
                "title": f"🧩 تعارضات وتنسيق ({len(raw_clashes)} تعارض)",
                "coordination_issues": raw_clashes,
                "msg": f"تم استخراج {len(raw_clashes)} تعارض بنجاح."
            }

    return {
        "success": False,
        "error": "لم يتم التعرف على بنية ملف JSON المرفوع. يرجى التأكد من احتوائه على أنشطة (activities/tasks)، تذاكر (topics/BCF)، أو سجل مخاطر (risks)."
    }

# ----------------- SESSION STATE INITIALIZATION -----------------
# 🎯 معالجة التقاط الإحداثيات المباشرة من نقرة الخريطة التفاعلية مع البقاء بنفس التبويب
if "map_lat" in st.query_params and "map_lon" in st.query_params:
    try:
        q_lat = float(st.query_params["map_lat"])
        q_lon = float(st.query_params["map_lon"])
        q_gov, _ = iraq_georisk_engine.find_nearest_governorate(q_lat, q_lon)
        st.session_state["_pending_map_lat"] = q_lat
        st.session_state["_pending_map_lon"] = q_lon
        st.session_state["_pending_gov_key"] = q_gov
        if "custom_project_meta" not in st.session_state:
            st.session_state.custom_project_meta = {}
        st.session_state.custom_project_meta["latitude"] = q_lat
        st.session_state.custom_project_meta["longitude"] = q_lon
        st.session_state.custom_project_meta["governorate"] = q_gov
        
        # 🎯 ضمان البقاء في نفس الشاشة (تبويب الاستيراد والموقع المكاني)
        st.session_state.active_nav_tab = "🏢 استيراد (P6 / IFC / JSON)"
        st.session_state["pills_nav_tab"] = "🏢 استيراد (P6 / IFC / JSON)"
        st.session_state["modern_hub_selector"] = "🧊 4. الهندسة الرقمية ونمذجة البناء (4D/5D BIM)"
        st.session_state["modern_subtools_🧊 4. الهندسة الرقمية ونمذجة البناء (4D/5D BIM)"] = "🏢 استيراد (P6 / IFC / JSON)"
        st.session_state["_prev_sel_gov"] = q_gov
        st.session_state["gis_gov_selector"] = q_gov
        
        st.session_state.last_import_msg = f"🎯 تم بنجاح التقاط وتحديث إحداثيات الموقع مباشرة من الخريطة: ({q_lat:.4f}° N, {q_lon:.4f}° E) — أقرب محافظة: {iraq_georisk_engine.IRAQ_GOVERNORATES_DB[q_gov]['name_ar']}"
        st.query_params.clear()
    except Exception as e:
        pass

# ----------------- 🔒 SECURITY & ACCESS CONTROL GATEWAY -----------------
AUTHORIZED_CREDENTIALS = {
    "admin": "ICRAT2026@Secure",
    "drahmed": "IraqRisk#2026",
    "engineer": "Bim@2026",
    "ruba": "Ruba@2026"
}

def render_login_portal():
    """بوابة الأمان والتحقق الرقمي المدمجة لحماية المنصة على الإنترنت"""
    st.markdown("""
    <div style="max-width: 500px; margin: 30px auto 16px auto; background: #FFFFFF; border-radius: 18px; padding: 28px 32px; box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08); border: 1px solid #E2E8F0; text-align: center; direction: rtl;">
        <div style="font-size: 2.8rem; margin-bottom: 6px;">🏛️</div>
        <h2 style="color: #0F172A; font-weight: 800; font-size: 1.35rem; margin-bottom: 4px;">منصة تقييم المخاطر الإنشائية (ICRAT 2.0)</h2>
        <div style="color: #2563EB; font-size: 0.86rem; margin-bottom: 6px; font-weight: 700;">🔒 بوابة الدخول المعتمدة للمهندسين والمشرفين</div>
        <div style="font-size: 0.78rem; color: #64748B; margin-bottom: 16px; font-weight: 600; font-family: 'Segoe UI', Tahoma, sans-serif; direction: ltr;">Iraqi Construction Risk Assessment & Decision Support Platform</div>
        <div style="background: #F8FAFC; border-radius: 10px; padding: 10px 14px; border: 1px solid #E2E8F0; font-size: 0.82rem; color: #475569; margin-bottom: 12px; line-height: 1.5;">
            هذه المنصة محمية بنظام التحقق الرقمي المشفر. يرجى إدخال بيانات الاعتماد المصرح بها للوصول إلى أدوات ومحركات المشروع.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_pad1, col_form, col_pad2 = st.columns([1, 1.8, 1])
    with col_form:
        with st.form("security_login_form", clear_on_submit=False):
            u_input = st.text_input("👤 اسم المستخدم (Username):", placeholder="أدخل اسم المستخدم المصرح به...")
            p_input = st.text_input("🔑 كلمة المرور (Password):", type="password", placeholder="أدخل كلمة المرور...")
            submit_btn = st.form_submit_button("🚀 تسجيل الدخول إلى المنصة", use_container_width=True, type="primary")

            if submit_btn:
                u_val = u_input.strip()
                p_val = p_input.strip()
                u_key = u_val.lower()
                if u_key in AUTHORIZED_CREDENTIALS and AUTHORIZED_CREDENTIALS[u_key] == p_val:
                    st.session_state["authenticated"] = True
                    st.session_state["logged_user"] = u_val
                    st.success(f"✅ تم التحقق بنجاح! مرحباً بك {u_val}")
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة! يرجى التحقق وإعادة المحاولة.")

    st.markdown("""
    <div style="text-align: center; margin-top: 28px; padding-top: 16px; border-top: 1px solid #E2E8F0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; direction: ltr;">
        <div style="font-size: 0.88rem; font-weight: 700; color: #1E293B; margin-bottom: 4px; letter-spacing: 0.2px;">
            Iraqi Construction Risk Assessment & Decision Support Platform
        </div>
        <div style="font-size: 0.82rem; font-weight: 600; color: #2563EB;">
            Designed and Developed by Dr Ahmed Louay Ahmed
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not st.session_state.get("authenticated", False):
    render_login_portal()

if "ifc_spatial_elements" not in st.session_state:
    st.session_state.ifc_spatial_elements = []
if "uploaded_ifc_bytes" not in st.session_state:
    st.session_state.uploaded_ifc_bytes = None
if "uploaded_ifc_filename" not in st.session_state:
    st.session_state.uploaded_ifc_filename = "model.ifc"
if "project_source" not in st.session_state:
    st.session_state.project_source = "SAMPLE"

if "selected_sample_key" not in st.session_state:
    st.session_state.selected_sample_key = "HOSPITAL_BAGHDAD"

if "custom_project_meta" not in st.session_state:
    st.session_state.custom_project_meta = {
        "id": "CUSTOM_PROJ_01",
        "name_ar": "مشروع إنشائي جديد (مخصص)",
        "name_en": "New Custom Construction Project",
        "client_type_ar": "الجهة المستفيدة / صاحب العمل",
        "location_ar": "بغداد - العراق",
        "governorate": "BAGHDAD",
        "latitude": 33.3152,
        "longitude": 44.3661,
        "currency": "USD",
        "currency_symbol": "$",
        "contract_original_cost": 12500000.0,
        "contract_original_duration_days": 450,
        "daily_overhead_usd": 3500.0,
        "unresolved_rfis": 4,
        "pending_change_orders": 2,
        "cash_flow_deficit_pct": 15.0,
        "subcontractor_performance": 75.0
    }

if "risk_register" not in st.session_state:
    st.session_state.risk_register = [dict(r) for r in iraqi_risk_db.DEFAULT_IRAQI_RISK_REGISTER]

if "activities" not in st.session_state:
    sample = project_samples.SAMPLE_PROJECTS[st.session_state.selected_sample_key]
    st.session_state.activities = [dict(a) for a in sample["activities"]]

if "coordination_issues" not in st.session_state:
    st.session_state.coordination_issues = [dict(c) for c in iso31000_coordination.DEFAULT_COORDINATION_ISSUES]

if "delay_events" not in st.session_state:
    st.session_state.delay_events = [dict(e) for e in eot_claims_engine.DEFAULT_DELAY_EVENTS]

if "last_import_msg" not in st.session_state:
    st.session_state.last_import_msg = None

# تهيئة متغيرات المؤشرات الخمسة المتقدمة
if "unresolved_bim_clashes_count" not in st.session_state:
    st.session_state.unresolved_bim_clashes_count = 2

if "material_price_inflation_pct" not in st.session_state:
    st.session_state.material_price_inflation_pct = 8.5

if "lab_testing_delay_days" not in st.session_state:
    st.session_state.lab_testing_delay_days = 12

if "contractual_disputes_count" not in st.session_state:
    st.session_state.contractual_disputes_count = 1

if "heatwave_stoppage_hours" not in st.session_state:
    st.session_state.heatwave_stoppage_hours = 18

if "isrs_eval_mode" not in st.session_state:
    st.session_state.isrs_eval_mode = "COMPARE"

# ----------------- SIDEBAR -----------------
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "icrat_bim_logo.jpg")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.image("https://img.icons8.com/isometric/512/crane.png", width=65)

    st.markdown(f"""
    <div style="background: #F8FAFC; border-radius: 10px; padding: 8px 12px; border: 1px solid #E2E8F0; margin-top: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; direction: rtl;">
        <div>
            <div style="font-size: 0.72rem; color: #64748B; font-weight: 600;">المستخدم النشط:</div>
            <div style="font-size: 0.85rem; color: #0F172A; font-weight: 800;">👤 {st.session_state.get('logged_user', 'Admin')}</div>
        </div>
        <span style="background: #DCFCE7; color: #166534; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 700; border: 1px solid #BBF7D0;">🟢 مصرح</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔒 تسجيل الخروج (Lock)", key="btn_auth_logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state.pop("logged_user", None)
        st.rerun()

    st.markdown("### ⚙️ لوحة التحكم والإعدادات")
    st.markdown("<div class='en-subtext'>ICRAT 2.0 • Advanced Risk & Claims Engine</div>", unsafe_allow_html=True)
    
    st.markdown("##### 🎨 نمط واجهة المنصة (UI Layout)")
    if "ui_layout_mode" not in st.session_state:
        st.session_state.ui_layout_mode = "MODERN"
        
    ui_choice = st.radio(
        "اختر نمط العرض والتنقل:",
        options=[
            "🌟 الواجهة العصرية الذكية (Executive Studio)",
            "🏛️ الواجهة الكلاسيكية (Classic 12-Tabs)"
        ],
        index=0 if st.session_state.ui_layout_mode == "MODERN" else 1,
        key="radio_ui_mode_choice"
    )
    st.session_state.ui_layout_mode = "MODERN" if "🌟" in ui_choice else "CLASSIC"
    st.divider()

    st.markdown("##### 🎛️ نظام تقييم مؤشر التلكؤ (ISRS Mode)")
    isrs_mode_choice = st.radio(
        "اختر نمط حساب مؤشر التلكؤ:",
        options=[
            "📊 وضع المقارنة المزدوجة المباشرة (Side-by-Side)",
            "🌟 المؤشر المطور الموسع (Advanced ISRS v2.0)",
            "🏛️ المؤشر القياسي الأساسي (Standard ISRS)"
        ],
        index=0 if st.session_state.isrs_eval_mode == "COMPARE" else (1 if st.session_state.isrs_eval_mode == "ADVANCED" else 2),
        key="radio_isrs_eval_mode_choice"
    )
    if "📊" in isrs_mode_choice:
        st.session_state.isrs_eval_mode = "COMPARE"
    elif "🌟" in isrs_mode_choice:
        st.session_state.isrs_eval_mode = "ADVANCED"
    else:
        st.session_state.isrs_eval_mode = "STANDARD"
    st.divider()

    mode_options = ["نماذج مشاريع عراقية جاهزة", "المشروع المخصص / المستورد"]
    current_mode_index = 0 if st.session_state.project_source == "SAMPLE" else 1

    proj_mode = st.radio(
        "نوع المشروع النشط:",
        options=mode_options,
        index=current_mode_index,
        key="radio_proj_mode"
    )

    if proj_mode == "نماذج مشاريع عراقية جاهزة":
        st.session_state.project_source = "SAMPLE"
        sample_options = {
            "HOSPITAL_BAGHDAD": "🏥 مستشفى تعليمي 400 سرير (بغداد)",
            "SEWER_BASRA": "🌊 شبكات مجاري ومحطة معالجة (البصرة)",
            "HOUSING_NAJAF": "🏘️ مجمع سكني 1200 وحدة (النجف)",
            "HIGHWAY_NINEVEH": "🛣️ تأهيل طريق وجسور رابطة (نينوى)"
        }
        chosen_sample = st.selectbox(
            "اختر النموذج المرجعي:",
            options=list(sample_options.keys()),
            format_func=lambda k: sample_options[k],
            index=list(sample_options.keys()).index(st.session_state.selected_sample_key)
        )
        if chosen_sample != st.session_state.selected_sample_key:
            st.session_state.selected_sample_key = chosen_sample
            sample_data = project_samples.SAMPLE_PROJECTS[chosen_sample]
            load_clean_project_state(
                meta=sample_data,
                activities=sample_data["activities"],
                source="SAMPLE",
                success_msg=f"تم تفعيل النموذج المرجعي: {sample_data['name_ar']}"
            )
            st.rerun()

        active_meta = project_samples.SAMPLE_PROJECTS[st.session_state.selected_sample_key]
    else:
        st.session_state.project_source = "CUSTOM"
        active_meta = st.session_state.custom_project_meta

        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E3A8A, #2563EB); color: #FFFFFF; border-radius: 10px; padding: 12px 14px; margin-top: 6px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(37,99,235,0.25); text-align: right; direction: rtl;">
            <div style="font-weight: 800; font-size: 0.95rem; display: flex; align-items: center; justify-content: space-between;">
                <span>🏢 مركز إعداد المشروع والموقع واستيراد النماذج</span>
                <span style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px; font-size: 0.72rem;">نشط ⚡</span>
            </div>
            <div style="font-size: 0.78rem; color: #DBEAFE; margin-top: 5px; line-height: 1.4;">
                إعداد الموقع المكاني على خريطة العراق، بيانات العقد، واستيراد P6 و BIM IFC.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗺️ فتح مركز الإعداد والموقع واستيراد النماذج", type="primary", use_container_width=True, key="sb_btn_open_import_hub"):
            st.session_state.active_nav_tab = "🏢 استيراد (P6 / IFC / JSON)"
            st.session_state["modern_hub_selector"] = "🧊 4. الهندسة الرقمية ونمذجة البناء (4D/5D BIM)"
            st.session_state["pills_nav_tab"] = "🏢 استيراد (P6 / IFC / JSON)"
            st.rerun()

        if st.button("🧹 تصفية والبدء بمشروع فارغ جديد (تصفير شامل)", type="secondary", use_container_width=True):
            clean_blank_meta = {
                "id": "NEW_CUSTOM_01",
                "name_ar": "مشروع مخصص جديد (فارغ)",
                "name_en": "New Clean Custom Project",
                "client_type_ar": "الجهة المستفيدة / صاحب العمل",
                "location_ar": "العراق",
                "currency": "USD",
                "currency_symbol": "$",
                "contract_original_cost": 0.0,
                "contract_original_duration_days": 0,
                "daily_overhead_usd": 0.0,
                "unresolved_rfis": 0,
                "pending_change_orders": 0,
                "cash_flow_deficit_pct": 0.0,
                "subcontractor_performance": 100.0
            }
            load_clean_project_state(
                meta=clean_blank_meta,
                activities=[],
                risks=[],
                coordination_issues=[],
                delay_events=[],
                source="CUSTOM",
                success_msg="🧹 تم بنجاح تصفير كافة الأرقام والمبالغ والمدد والبدء بمشروع فارغ تماماً!"
            )
            st.rerun()

    # 📥 قسم استيراد Primavera P6 و BIM IFC و JSON و Navisworks في القائمة الجانبية
    with st.expander("📥 استيراد مشروع (P6 / IFC / JSON / Navisworks)", expanded=False):
        st.markdown("<div style='font-size:0.8rem; color:#64748B; margin-bottom:6px;'>استيراد مباشر وسريع لملفات المشروع:</div>", unsafe_allow_html=True)
        sb_import_type = st.radio(
            "اختر صيغة الملف:",
            options=["1️⃣ جدول Primavera P6 (.xer)", "2️⃣ نموذج BIM (.ifc)", "3️⃣ تعارضات Navisworks (.xml / .csv)", "4️⃣ نسخة احتياطية (.json)"],
            key="sb_import_type_radio"
        )
        
        if "1️⃣" in sb_import_type:
            sb_up_p6 = st.file_uploader("ملف جدول P6 (.xer):", type=["xer"], key="sb_p6_uploader")
            if sb_up_p6 is not None:
                sb_p6_res = p6_parser.parse_p6_file_bytes(sb_up_p6.getvalue(), sb_up_p6.name)
                if sb_p6_res.get("success"):
                    st.success(f"✅ تم تحليل الجدول: ({sb_p6_res['activities_count']} نشاط)")
                    if st.button("🚀 تفعيل جدول بريمافيرا P6", type="primary", key="sb_btn_apply_p6", use_container_width=True):
                        load_clean_project_state(
                            meta=sb_p6_res["project_meta"],
                            activities=sb_p6_res["activities"],
                            source="CUSTOM",
                            success_msg=f"🎉 تم بنجاح استيراد وتفعيل جدول بريمافيرا P6: '{sb_p6_res['project_meta']['name_ar']}'!"
                        )
                        st.rerun()

        elif "2️⃣" in sb_import_type:
            sb_up_ifc = st.file_uploader("ملف نموذج BIM (.ifc):", type=["ifc"], key="sb_ifc_uploader")
            if sb_up_ifc is not None:
                sb_ifc_res = ifc_parser.parse_ifc_file_bytes(sb_up_ifc.getvalue(), sb_up_ifc.name)
                if sb_ifc_res.get("success"):
                    st.success(f"✅ تم تحليل نموذج IFC: ({sb_ifc_res['total_elements']} عنصر / {sb_ifc_res['storey_count']} طوابق)")
                    if st.button("🚀 تفعيل نموذج BIM IFC", type="primary", key="sb_btn_apply_ifc", use_container_width=True):
                        load_clean_project_state(
                            meta=sb_ifc_res["project_meta"],
                            activities=sb_ifc_res["activities"],
                            coordination_issues=sb_ifc_res.get("coordination_issues"),
                            spatial_elements=sb_ifc_res.get("spatial_elements", []),
                            ifc_bytes=sb_up_ifc.getvalue(),
                            ifc_filename=sb_up_ifc.name,
                            source="CUSTOM",
                            success_msg=f"🎉 تم بنجاح استيراد وتفعيل نموذج الـ IFC: '{sb_ifc_res['project_meta']['name_ar']}'!"
                        )
                        st.rerun()

        elif "3️⃣" in sb_import_type:
            sb_up_navis = st.file_uploader("تقرير تعارضات Navisworks (.xml, .csv):", type=["xml", "csv"], key="sb_navis_uploader")
            if sb_up_navis is not None:
                sb_navis_res = navisworks_parser.parse_navisworks_clash_bytes(sb_up_navis.getvalue(), sb_up_navis.name)
                if sb_navis_res.get("success"):
                    st.success(f"✅ تم بنجاح قراءة وتحليل كافة الـ {sb_navis_res['total_clashes']:,} تعارض بالكامل ({sb_navis_res['critical_clashes_count']:,} حرج)!")
                    if st.button("🚀 دمج وتفعيل تعارضات Navisworks", type="primary", key="sb_btn_apply_navis", use_container_width=True):
                        st.session_state.coordination_issues = sb_navis_res["coordination_issues"]
                        st.session_state.last_import_msg = f"🎉 تم بنجاح استيراد وتفعيل كافة الـ {sb_navis_res['total_clashes']:,} تعارض بالكامل وتحديث مصفوفة ISO 31000!"
                        st.rerun()

        else:
            sb_up_json = st.file_uploader("ملف JSON (نسخة كاملة / BCF / أنشطة / مخاطر):", type=["json"], key="sb_json_uploader")
            if sb_up_json is not None:
                try:
                    data = json.loads(sb_up_json.getvalue().decode('utf-8'))
                    res = process_universal_json_upload(data, sb_up_json.name)
                    if res["success"]:
                        st.success(f"✅ {res['title']}")
                        st.markdown(f"<div style='font-size:0.78rem; color:#475569; margin-bottom:6px;'>💡 {res['msg']}</div>", unsafe_allow_html=True)
                        if st.button("🚀 تفعيل واستيراد البيانات الآن", type="primary", key="sb_btn_apply_json", use_container_width=True):
                            if res["type"] in ["FULL_PROJECT", "ACTIVITIES_LIST"]:
                                load_clean_project_state(
                                    meta=res.get("meta", {}),
                                    activities=res.get("activities", []),
                                    risks=res.get("risks"),
                                    coordination_issues=res.get("coordination_issues"),
                                    delay_events=res.get("delay_events"),
                                    source="CUSTOM",
                                    success_msg=f"🎉 تم بنجاح تفعيل {res['title']} وتحديث كامل مؤشرات المنصة!"
                                )
                            elif res["type"] == "BCF_TOPICS":
                                st.session_state.coordination_issues = res["coordination_issues"]
                                st.session_state.last_import_msg = f"🎉 تم بنجاح استيراد وتفعيل {len(res['coordination_issues'])} تذكرة تنسيق BCF وتحديث مصفوفة ISO 31000!"
                            elif res["type"] == "RISKS_LIST":
                                st.session_state.risk_register = res["risks"]
                                st.session_state.last_import_msg = f"🎉 تم بنجاح استيراد وتحديث {len(res['risks'])} بند خطر في سجل المخاطر!"
                            st.rerun()
                    else:
                        st.error(res["error"])
                except Exception as e:
                    st.error(f"خطأ في قراءة ملف JSON: {e}")

    st.markdown("---")
    st.markdown("#### 🎲 بارامترات محاكاة مونت كارلو")
    
    sim_iterations = st.slider(
        "عدد دورات المحاكاة الإحصائية",
        min_value=500,
        max_value=5000,
        value=2500,
        step=500,
        help="عدد التكرارات العشوائية لمونت كارلو"
    )
    st.markdown(f"<div style='text-align:left;'><span class='val-badge'>القيمة المختارة: {sim_iterations:,.0f} دورة</span></div>", unsafe_allow_html=True)

    confidence_options = ["P70", "P75", "P80", "P85", "P90", "P95"]
    target_confidence = st.selectbox(
        "مستوى الثقة المستهدف للإنجاز (Target P-Value)",
        options=confidence_options,
        index=2,
        help="تحديد مستوى الأمان الزمني والمالي المطلوب"
    )
    conf_desc = {
        "P70": "نسبة ثقة 70% (معتدل)",
        "P75": "نسبة ثقة 75% (متوازن)",
        "P80": "نسبة ثقة 80% (موصى بها تعاقدياً)",
        "P85": "نسبة ثقة 85% (أمان متقدم)",
        "P90": "نسبة ثقة 90% (يقين مرتفع)",
        "P95": "نسبة ثقة 95% (أقصى تحفظ)"
    }
    st.markdown(f"<div style='text-align:left;'><span class='val-badge'>{target_confidence} — {conf_desc.get(target_confidence, '')}</span></div>", unsafe_allow_html=True)

    schedule_cost_corr = st.slider(
        "معامل ارتباط التأخير الزمني بتضخم التكلفة (ρ)",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05,
        help="درجة تأثير تأخير الجدول الزمني على زيادة المصاريف غير المباشرة"
    )
    st.divider()

    with st.expander("📖 معجم المصطلحات الهندسية (Glossary)", expanded=False):
        g_search_side = st.text_input("🔍 ابحث عن أي مصطلح:", placeholder="ابحث بالعربية أو الإنجليزية...", key="sidebar_g_search")
        g_cat_side = st.selectbox(
            "تصفية حسب المجال:",
            options=list(glossary_data.GLOSSARY_CATEGORIES.keys()),
            format_func=lambda x: glossary_data.GLOSSARY_CATEGORIES[x],
            key="sidebar_g_cat"
        )
        g_results_side = glossary_data.search_glossary(query=g_search_side, category=g_cat_side)
        st.markdown(f"<div style='font-size:0.75rem; color:#64748B; margin-bottom:8px;'>عدد المصطلحات المطابقة: <b>{len(g_results_side)}</b></div>", unsafe_allow_html=True)
        for item in g_results_side[:10]:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:8px 10px; margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="color:#2563EB; font-size:0.85rem;">{item['term_en']}</b>
                    <span style="font-size:0.7rem; background:#F1F5F9; color:#475569; padding:2px 6px; border-radius:4px;">{item['category_ar']}</span>
                </div>
                <div style="font-size:0.8rem; font-weight:700; color:#0F172A; margin:2px 0;">{item['term_ar']}</div>
                <div style="font-size:0.75rem; color:#475569; line-height:1.4;">{item['definition_ar']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.markdown(f"""
    **📌 ملخص المشروع النشط:**
    - **المشروع:** {active_meta.get('name_ar', '')}
    - **الموقع:** {active_meta.get('location_ar', '')}
    - **العملة:** {active_meta.get('currency', 'USD')} ({active_meta.get('currency_symbol', '$')})
    - **الأنشطة:** {len(st.session_state.activities)} نشاط
    - **المخاطر:** {len(st.session_state.risk_register)} خطر
    - **مشكلات التنسيق:** {len(st.session_state.coordination_issues)} تعارض
    """)
    
    st.markdown("""
    <div style="text-align:center; font-size:0.78rem; color:#64748B; border-top:1px solid #CBD5E1; padding-top:14px; margin-top:20px; direction:ltr;">
        Designed and developed by<br/>
        <b style="color:#1E3A8A; font-size:0.85rem;">Dr Ahmed Louay Ahmed</b>
    </div>
    """, unsafe_allow_html=True)

# ----------------- MAIN HEADER -----------------
col_hdr_1, col_hdr_2 = st.columns([3.5, 1.2])
with col_hdr_1:
    st.markdown(f"""
    <div class="main-header">
        <h2 style="margin:0; font-size:1.55rem; color:#F8FAFC;">🏗️ ICRAT 2.0 | المنصة الهندسية المتكاملة لتقييم المخاطر والمطالبات</h2>
        <p style="margin:8px 0 0 0; color:#94A3B8; font-size:0.92rem; line-height:1.6;">
            محاكاة مونت كارلو <span class='en-badge'>QSRA/QCRA</span> • التنسيق <span class='en-badge'>ISO 31000</span> • مطالبات التمديد <span class='en-badge'>EOT</span> • استيراد <span class='en-badge'>Primavera P6 & BIM</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_hdr_2:
    st.markdown(f"""
    <div style="background:#F1F5F9; border-radius:12px; padding:16px 14px; text-align:center; border:1px solid #CBD5E1; direction:rtl;">
        <span style="font-size:0.8rem; color:#64748B; font-weight:700;">المشروع المفعّل حالياً:</span><br/>
        <b style="font-size:0.95rem; color:#1E293B; line-height:1.5; display:block; margin-top:4px;">{active_meta['name_ar']}</b>
    </div>
    """, unsafe_allow_html=True)

# إشعار نجاح الاستيراد إن وجد
if st.session_state.last_import_msg:
    st.success(st.session_state.last_import_msg)
    st.session_state.last_import_msg = None

# ----------------- CACHED ENGINES FOR ZERO LATENCY -----------------
@st.cache_data(show_spinner=False)
def run_cached_monte_carlo(activities, risks, iterations, schedule_cost_correlation, daily_overhead_rate, random_seed=42):
    sim = simulation_engine.MonteCarloSimulator(
        activities=activities,
        risks=risks,
        iterations=iterations,
        schedule_cost_correlation=schedule_cost_correlation,
        daily_overhead_rate=daily_overhead_rate,
        random_seed=random_seed
    )
    return sim.run_simulation()

@st.cache_data(show_spinner=False)
def get_cached_eot_claims(delay_events, duration_days, cost, overhead, fine_mult, curr_sym):
    return eot_claims_engine.calculate_contractual_eot_claim(
        delay_events=delay_events,
        contract_original_duration_days=duration_days,
        contract_original_cost=cost,
        daily_overhead_cost=overhead,
        daily_delay_fine_multiplier=fine_mult,
        currency_symbol=curr_sym
    )

@st.cache_data(show_spinner=False)
def run_cached_whatif(base_activities, base_risks, base_meta, levers, iterations=1500, random_seed=42):
    return what_if_engine.simulate_mitigation_scenario(
        base_activities=base_activities,
        base_risks=base_risks,
        base_meta=base_meta,
        levers=levers,
        iterations=iterations,
        random_seed=random_seed
    )

@st.cache_data(show_spinner=False)
def get_cached_3d_bim(storeys_count, show_footings, show_columns, show_slabs, show_walls, show_mep, has_clashes):
    return bim_3d_viewer.create_3d_bim_risk_model(
        storeys_count=storeys_count,
        show_footings=show_footings,
        show_columns=show_columns,
        show_slabs=show_slabs,
        show_walls=show_walls,
        show_mep=show_mep,
        has_clashes=has_clashes
    )

@st.cache_data(show_spinner=False)
def get_cached_ai_bim_decision_hub(clashes, activities):
    return ai_bim_decision_hub.project_clash_schedule_risk_network(
        clashes=clashes,
        activities=activities
    )

@st.cache_data(show_spinner=False)
def get_cached_coordination_summary(clashes):
    return iso31000_coordination.compute_coordination_summary(clashes)

@st.cache_data(show_spinner=False)
def get_cached_isrs_v2(risk_register, curr_rfis, curr_co, curr_cash_def, curr_sub_perf, curr_bim_clashes, curr_inflation, curr_lab_delay, curr_disputes, curr_heat_stoppage):
    return iraqi_risk_db.compute_advanced_iraqi_stalling_risk_score_v2(
        risk_register=risk_register,
        unresolved_rfis_count=curr_rfis,
        pending_change_orders=curr_co,
        cash_flow_deficit_pct=curr_cash_def,
        subcontractor_performance_score=curr_sub_perf,
        unresolved_bim_clashes_count=curr_bim_clashes,
        material_price_inflation_pct=curr_inflation,
        lab_testing_delay_days=curr_lab_delay,
        contractual_disputes_count=curr_disputes,
        heatwave_stoppage_hours=curr_heat_stoppage
    )

# ----------------- SIMULATION & ISRS RUNNER -----------------
curr_rfis = st.session_state.get("slider_rfis", active_meta.get("unresolved_rfis", 4))
curr_co = st.session_state.get("slider_co", active_meta.get("pending_change_orders", 2))
curr_cash_def = st.session_state.get("slider_cash", active_meta.get("cash_flow_deficit_pct", 15.0))
curr_sub_perf = st.session_state.get("slider_sub", active_meta.get("subcontractor_performance", 75.0))

curr_bim_clashes = st.session_state.get("slider_bim_clashes", st.session_state.get("unresolved_bim_clashes_count", 2))
curr_inflation = st.session_state.get("slider_inflation", st.session_state.get("material_price_inflation_pct", 8.5))
curr_lab_delay = st.session_state.get("slider_lab_delay", st.session_state.get("lab_testing_delay_days", 12))
curr_disputes = st.session_state.get("slider_disputes", st.session_state.get("contractual_disputes_count", 1))
curr_heat_stoppage = st.session_state.get("slider_heat_stoppage", st.session_state.get("heatwave_stoppage_hours", 18))

if len(st.session_state.activities) > 0:
    isrs_v2_result = get_cached_isrs_v2(
        risk_register=st.session_state.risk_register,
        curr_rfis=curr_rfis,
        curr_co=curr_co,
        curr_cash_def=curr_cash_def,
        curr_sub_perf=curr_sub_perf,
        curr_bim_clashes=curr_bim_clashes,
        curr_inflation=curr_inflation,
        curr_lab_delay=curr_lab_delay,
        curr_disputes=curr_disputes,
        curr_heat_stoppage=curr_heat_stoppage
    )
    eval_mode = st.session_state.get("isrs_eval_mode", "COMPARE")
    if eval_mode == "ADVANCED":
        isrs_result = {
            "isrs_score": isrs_v2_result["isrs_score_v2"],
            "status_ar": isrs_v2_result["status_ar_v2"],
            "status_en": isrs_v2_result["status_en_v2"],
            "status_color": isrs_v2_result["status_color_v2"],
            "status_icon": isrs_v2_result["status_icon_v2"],
            "category_breakdown": isrs_v2_result["base_isrs"]["category_breakdown"],
            "operational_penalty": isrs_v2_result["new_indicators_penalties"]["total_new_penalty"],
            "recommendations": isrs_v2_result["advanced_recommendations"]
        }
    else:
        isrs_result = isrs_v2_result["base_isrs"]

    sim_res = run_cached_monte_carlo(
        activities=st.session_state.activities,
        risks=st.session_state.risk_register,
        iterations=sim_iterations,
        schedule_cost_correlation=schedule_cost_corr,
        daily_overhead_rate=active_meta.get("daily_overhead_usd", 3000.0),
        random_seed=42
    )
else:
    # حالة التصفير الشامل عند عدم وجود أنشطة
    isrs_result = {
        "isrs_score": 0.0,
        "status_ar": "مشروع جديد قيد التخطيط وإدخال الأنشطة",
        "status_color": "#64748B",
        "status_icon": "⚪",
        "category_breakdown": {c: 0.0 for c in iraqi_risk_db.RISK_CATEGORIES},
        "recommendations": ["ابدأ بإدخال أنشطة المشروع أو استيراد جدول Primavera P6 / نموذج IFC."]
    }
    isrs_v2_result = {
        "base_isrs": isrs_result,
        "isrs_score_v2": 0.0,
        "status_ar_v2": isrs_result["status_ar"],
        "status_en_v2": "New Project",
        "status_color_v2": "#64748B",
        "status_icon_v2": "⚪",
        "delta_isrs": 0.0,
        "new_indicators_penalties": {
            "bim_clashes_penalty": 0.0,
            "material_inflation_penalty": 0.0,
            "lab_testing_penalty": 0.0,
            "disputes_penalty": 0.0,
            "heatwave_penalty": 0.0,
            "total_new_penalty": 0.0
        },
        "advanced_recommendations": isrs_result["recommendations"]
    }
    sim_res = {
        "iterations": sim_iterations,
        "total_durations": np.zeros(sim_iterations),
        "total_costs": np.zeros(sim_iterations),
        "duration_percentiles": {p: 0.0 for p in ["P10", "P20", "P30", "P40", "P50", "P60", "P70", "P75", "P80", "P85", "P90", "P95"]},
        "cost_percentiles": {p: 0.0 for p in ["P10", "P20", "P30", "P40", "P50", "P60", "P70", "P75", "P80", "P85", "P90", "P95"]},
        "deterministic_duration": 0.0,
        "deterministic_cost": 0.0,
        "tornado_duration": [],
        "tornado_cost": [],
        "activity_duration_results": {},
        "risk_delay_impacts": {}
    }

curr_sym = active_meta.get("currency_symbol", "$")
target_p_dur = sim_res["duration_percentiles"].get(target_confidence, sim_res["duration_percentiles"]["P80"])
target_p_cost = sim_res["cost_percentiles"].get(target_confidence, sim_res["cost_percentiles"]["P80"])
target_time_contingency = max(0.0, target_p_dur - sim_res["duration_percentiles"]["P50"])
target_cost_contingency = max(0.0, target_p_cost - sim_res["cost_percentiles"]["P50"])
target_cost_contingency_pct = (target_cost_contingency / sim_res["cost_percentiles"]["P50"]) * 100.0 if sim_res["cost_percentiles"]["P50"] > 0 else 0.0

# حساب المطالبات التعاقدية والتنسيق الهندسي (مخزن مؤقتاً بالكامل 0ms)
eot_calc_res = get_cached_eot_claims(
    delay_events=st.session_state.delay_events,
    duration_days=int(active_meta.get("contract_original_duration_days", 450)),
    cost=float(active_meta.get("contract_original_cost", 12500000.0)),
    overhead=float(active_meta.get("daily_overhead_usd", 3500.0)),
    fine_mult=0.10,
    curr_sym=curr_sym
)
coord_summary = iso31000_coordination.compute_coordination_summary(st.session_state.coordination_issues)

# ----------------- DUAL-MODE NAVIGATION ENGINE (MODERN EXECUTIVE STUDIO vs CLASSIC) -----------------
TAB_OPTIONS = [
    "📊 لوحة القيادة",
    "📈 منحنيات S-Curve",
    "🌪️ تحليل الحساسية",
    "🧩 التنسيق (ISO 31000)",
    "⚖️ المطالبات والتمديد (EOT)",
    "🔮 مقارن السيناريوهات (What-If)",
    "🤖 المستشار الذكي والمخاطبات",
    "🧊 عارض BIM 3D التفاعلي",
    "📅 مخطط جانت وبريمافيرا (Gantt)",
    "🛡️ مصفوفة المخاطر",
    "🏢 استيراد (P6 / IFC / JSON)",
    "📄 التقرير والتصدير"
]

MODERN_HUBS = {
    "🏢 1. المشروع والتوأم الرقمي (Project & Digital Twin)": [
        "📊 لوحة القيادة",
        "🏢 استيراد (P6 / IFC / JSON)",
        "🧊 عارض BIM 3D التفاعلي"
    ],
    "🧠 2. محطة قرارات التنسيق الذكية (AI Decision & ISO 31000)": [
        "🧩 التنسيق (ISO 31000)",
        "🛡️ مصفوفة المخاطر"
    ],
    "⏱️ 3. الجدولة ومحاكاة المخاطر (Schedule & Monte Carlo)": [
        "📅 مخطط جانت وبريمافيرا (Gantt)",
        "📈 منحنيات S-Curve",
        "🌪️ تحليل الحساسية",
        "🔮 مقارن السيناريوهات (What-If)"
    ],
    "⚖️ 4. العقود والمطالبات والتقارير (Contracts, Claims & Reports)": [
        "⚖️ المطالبات والتمديد (EOT)",
        "🤖 المستشار الذكي والمخاطبات",
        "📄 التقرير والتصدير"
    ]
}

if "active_nav_tab" not in st.session_state:
    st.session_state.active_nav_tab = "📊 لوحة القيادة"

layout_mode = st.session_state.get("ui_layout_mode", "MODERN")

if layout_mode == "MODERN":
    # 1. شريط المعلومات التنفيذي السريع (Executive Topbar)
    gov_meta_key = active_meta.get('governorate', 'BAGHDAD')
    geo_prof_top = iraq_georisk_engine.get_governorate_profile(gov_meta_key)

    st.markdown(f"""
    <div class="modern-topbar">
        <div class="topbar-item">
            <span class="topbar-label">🏗️ المشروع:</span>
            <span class="topbar-val">{active_meta.get('name_ar', 'مشروع إنشائي')}</span>
        </div>
        <div class="topbar-item">
            <span class="topbar-label">📍 الموقع الجغرافي:</span>
            <span class="topbar-val">{geo_prof_top['name_ar']} ({geo_prof_top['lat']:.2f}°, {geo_prof_top['lon']:.2f}°)</span>
        </div>
        <div class="topbar-item">
            <span class="topbar-label">💰 موازنة العقد:</span>
            <span class="topbar-val">{active_meta.get('contract_original_cost', 0):,.0f} {curr_sym}</span>
        </div>
        <div class="topbar-item">
            <span class="topbar-label">⏱️ المدة التعاقدية:</span>
            <span class="topbar-val">{active_meta.get('contract_original_duration_days', 0):,} يوم</span>
        </div>
        <div class="topbar-item">
            <span class="topbar-label">🛡️ مؤشر السلامة ISRS:</span>
            <span class="topbar-val" style="color:{isrs_result['status_color']};">{isrs_result['status_icon']} {isrs_result['isrs_score']:.1f}/100</span>
        </div>
        <div>
            <span class="mode-badge-modern">🌟 نمط الاستوديو العصري</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1.1 شريط سير العمل الهندسي الموجه (Workflow Breadcrumb Bar)
    active_wf_step = 3
    if st.session_state.active_nav_tab == "🏢 استيراد (P6 / IFC / JSON)":
        active_wf_step = 1
    elif st.session_state.active_nav_tab in ["🧊 عارض BIM 3D التفاعلي", "📅 مخطط جانت وبريمافيرا (Gantt)", "🧩 التنسيق (ISO 31000)"]:
        active_wf_step = 2
    elif st.session_state.active_nav_tab in ["📊 لوحة القيادة", "📈 منحنيات S-Curve", "🌪️ تحليل الحساسية", "🛡️ مصفوفة المخاطر", "🔮 مقارن السيناريوهات (What-If)"]:
        active_wf_step = 3
    elif st.session_state.active_nav_tab in ["⚖️ المطالبات والتمديد (EOT)", "🤖 المستشار الذكي والمخاطبات"]:
        active_wf_step = 4
    elif st.session_state.active_nav_tab == "📄 التقرير والتصدير":
        active_wf_step = 5

    st.markdown(f"""
    <div class="workflow-bar">
        <div class="workflow-step {'active' if active_wf_step == 1 else ''}">
            <span>1️⃣</span> <span>🗺️ الإعداد والموقع المكاني</span>
        </div>
        <span class="workflow-arrow">◀</span>
        <div class="workflow-step {'active' if active_wf_step == 2 else ''}">
            <span>2️⃣</span> <span>🏗️ النماذج و 3D BIM/P6</span>
        </div>
        <span class="workflow-arrow">◀</span>
        <div class="workflow-step {'active' if active_wf_step == 3 else ''}">
            <span>3️⃣</span> <span>🎲 محاكاة المخاطر QSRA</span>
        </div>
        <span class="workflow-arrow">◀</span>
        <div class="workflow-step {'active' if active_wf_step == 4 else ''}">
            <span>4️⃣</span> <span>⚖️ المطالبات وقرارات FIDIC</span>
        </div>
        <span class="workflow-arrow">◀</span>
        <div class="workflow-step {'active' if active_wf_step == 5 else ''}">
            <span>5️⃣</span> <span>📄 التقرير التنفيذي والتصدير</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. تحديد المحور النشط
    current_hub = "📊 1. مركز القيادة والتقارير التنفيذية"
    for hub_name, tools in MODERN_HUBS.items():
        if st.session_state.active_nav_tab in tools:
            current_hub = hub_name
            break

    selected_hub = st.segmented_control(
        "اختر المحور التشغيلي:",
        options=list(MODERN_HUBS.keys()),
        default=current_hub,
        key="modern_hub_selector",
        label_visibility="collapsed"
    )
    if not selected_hub:
        selected_hub = current_hub

    # 3. الأدوات داخل المحور
    hub_tools = MODERN_HUBS[selected_hub]
    sub_default = st.session_state.active_nav_tab if st.session_state.active_nav_tab in hub_tools else hub_tools[0]
    
    selected_tab = st.pills(
        "اختر الأداة المتخصصة:",
        options=hub_tools,
        default=sub_default,
        key=f"modern_subtools_{selected_hub}",
        label_visibility="collapsed"
    )
    if not selected_tab:
        selected_tab = hub_tools[0]
    st.session_state.active_nav_tab = selected_tab

else:
    # النمط الكلاسيكي الأصلي
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <span style="font-size:0.85rem; color:#64748B; font-weight:700;">تنقل بين شاشات وأدوات المنصة (الواجهة الكلاسيكية):</span>
        <span class="mode-badge-classic">🏛️ الواجهة الكلاسيكية 12-Tabs</span>
    </div>
    """, unsafe_allow_html=True)
    
    selected_tab = st.pills(
        "تنقل بين شاشات وأدوات المنصة:",
        options=TAB_OPTIONS,
        default=st.session_state.active_nav_tab,
        key="pills_nav_tab",
        label_visibility="collapsed"
    )
    if not selected_tab:
        selected_tab = "📊 لوحة القيادة"
    st.session_state.active_nav_tab = selected_tab

# ----------------- TAB 1: DASHBOARD & ISRS -----------------
if selected_tab == "📊 لوحة القيادة":
    if len(st.session_state.activities) == 0:
        st.info("💡 **المشروع مصفّر وخالٍ من أي بيانات سابقة.** للبدء في تشغيل المحاكاة واستخراج مؤشرات الأداء، يرجى إضافة أنشطة من تبويب **📋 هيكل الأنشطة (WBS)** أو استيراد جدول **Primavera P6** أو نموذج **BIM IFC** من تبويب **🏢 استيراد**.")

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        dur_display = f"{target_p_dur:,.0f}" if target_p_dur > 0 else "0"
        det_dur_display = f"{sim_res['deterministic_duration']:.0f}" if sim_res['deterministic_duration'] > 0 else "0"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">⏱️ مدة الإنجاز الآمنة بمستوى <span class='en-badge'>{target_confidence}</span></div>
            <div class="kpi-value">{dur_display} <span style="font-size:1rem; color:#64748B;">يوم</span></div>
            <div class="kpi-sub">المدة الحتمية المرجعية: {det_dur_display} يوم</div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi2:
        cont_d_display = f"+{target_time_contingency:,.1f}" if target_time_contingency > 0 else "0.0"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">🛡️ احتياطي الطوارئ الزمني الموصى به</div>
            <div class="kpi-value" style="color:#2563EB;">{cont_d_display} <span style="font-size:1rem; color:#64748B;">يوم</span></div>
            <div class="kpi-sub">تأمين الالتزام بمستوى ثقة {target_confidence}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi3:
        cost_display = f"{target_p_cost:,.0f}" if target_p_cost > 0 else "0"
        det_cost_display = f"{sim_res['deterministic_cost']:,.0f}" if sim_res['deterministic_cost'] > 0 else "0"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">💵 الميزانية الآمنة بمستوى <span class='en-badge'>{target_confidence}</span></div>
            <div class="kpi-value">{cost_display} <span style="font-size:1rem; color:#64748B;">{curr_sym}</span></div>
            <div class="kpi-sub">الكلفة الحتمية المرجعية: {det_cost_display} {curr_sym}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpi4:
        cont_c_display = f"+{target_cost_contingency:,.0f}" if target_cost_contingency > 0 else "0"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">💰 احتياطي الطوارئ المالي الموصى به</div>
            <div class="kpi-value" style="color:#D97706;">{cont_c_display} <span style="font-size:1rem; color:#64748B;">{curr_sym}</span></div>
            <div class="kpi-sub">يعادل {target_cost_contingency_pct:.1f}% من الميزانية المرجعية</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    eval_mode = st.session_state.get("isrs_eval_mode", "COMPARE")

    if eval_mode == "COMPARE":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 14px 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
            <div style="color: #FFFFFF; font-size: 1.05rem; font-weight: 700;">
                📊 وضع المقارنة المزدوجة المباشرة (Side-by-Side ISRS Comparison)
            </div>
            <div style="background: #3B82F6; color: #FFFFFF; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">
                مقارنة فورية لنفس المشروع
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_comp_g1, col_comp_g2, col_comp_rad = st.columns([1.5, 1.5, 2.0])

        with col_comp_g1:
            st.markdown("##### 🏛️ المؤشر القياسي الأساسي (Standard)")
            b_score = isrs_v2_result["base_isrs"]["isrs_score"]
            b_color = isrs_v2_result["base_isrs"]["status_color"]
            fig_g_base = go.Figure(go.Indicator(
                mode="gauge+number",
                value=b_score,
                domain={'x': [0.08, 0.92], 'y': [0.12, 0.95]},
                number={'suffix': "%", 'font': {'size': 30, 'family': 'Segoe UI, Tahoma, sans-serif', 'color': b_color}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                    'bar': {'color': b_color, 'thickness': 0.35},
                    'bgcolor': "white",
                    'steps': [
                        {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.2)'},
                        {'range': [35, 65], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [65, 100], 'color': 'rgba(239, 68, 68, 0.25)'}
                    ]
                }
            ))
            fig_g_base.update_layout(height=210, margin=dict(l=10, r=10, t=10, b=10), font=dict(family='Cairo, sans-serif'))
            st.plotly_chart(fig_g_base, use_container_width=True, key="plot_gauge_base_compare")
            st.markdown(f"<div style='text-align:center; font-size:0.85rem; font-weight:700; color:{b_color};'>{isrs_v2_result['base_isrs']['status_icon']} {isrs_v2_result['base_isrs']['status_ar']}</div>", unsafe_allow_html=True)

        with col_comp_g2:
            st.markdown("##### 🌟 المؤشر المطور الموسع (Advanced v2.0)")
            v2_score = isrs_v2_result["isrs_score_v2"]
            v2_color = isrs_v2_result["status_color_v2"]
            fig_g_v2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=v2_score,
                domain={'x': [0.08, 0.92], 'y': [0.12, 0.95]},
                number={'suffix': "%", 'font': {'size': 30, 'family': 'Segoe UI, Tahoma, sans-serif', 'color': v2_color}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                    'bar': {'color': v2_color, 'thickness': 0.35},
                    'bgcolor': "white",
                    'steps': [
                        {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.2)'},
                        {'range': [35, 65], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [65, 100], 'color': 'rgba(239, 68, 68, 0.25)'}
                    ]
                }
            ))
            fig_g_v2.update_layout(height=210, margin=dict(l=10, r=10, t=10, b=10), font=dict(family='Cairo, sans-serif'))
            st.plotly_chart(fig_g_v2, use_container_width=True, key="plot_gauge_v2_compare")
            st.markdown(f"<div style='text-align:center; font-size:0.85rem; font-weight:700; color:{v2_color};'>{isrs_v2_result['status_icon_v2']} {isrs_v2_result['status_ar_v2']}</div>", unsafe_allow_html=True)

        with col_comp_rad:
            st.markdown("##### 🕸️ مقارنة توزيع المخاطر (Standard vs Advanced)")
            categories = list(iraqi_risk_db.RISK_CATEGORIES.keys())
            cat_names = [ar(iraqi_risk_db.RISK_CATEGORIES[c]["name_ar"]) for c in categories]
            cat_vals_base = [isrs_v2_result["base_isrs"]["category_breakdown"].get(c, 0.0) for c in categories]
            
            # مضاعف تقديري للمؤشرات المتقدمة في الرادار
            cat_vals_adv = [min(100.0, v * 1.15 + (isrs_v2_result['new_indicators_penalties']['total_new_penalty'] * 0.4)) for v in cat_vals_base]

            fig_comp_radar = go.Figure()
            fig_comp_radar.add_trace(go.Scatterpolar(
                r=cat_vals_base + [cat_vals_base[0]],
                theta=cat_names + [cat_names[0]],
                fill='toself',
                fillcolor='rgba(59, 130, 246, 0.20)',
                line=dict(color='#2563EB', width=2),
                name=ar('التقييم الأساسي')
            ))
            fig_comp_radar.add_trace(go.Scatterpolar(
                r=cat_vals_adv + [cat_vals_adv[0]],
                theta=cat_names + [cat_names[0]],
                fill='toself',
                fillcolor='rgba(217, 119, 6, 0.20)',
                line=dict(color='#D97706', width=2, dash='dot'),
                name=ar('الموسع v2.0')
            ))
            fig_comp_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix='%')),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                height=260,
                font=dict(family='Cairo, sans-serif', size=10),
                margin=dict(l=40, r=40, t=10, b=10)
            )
            st.plotly_chart(fig_comp_radar, use_container_width=True, key="plot_radar_compare")

        # بطاقة تفصيل الفارق التحليلي
        delta_color = "#DC2626" if isrs_v2_result["delta_isrs"] > 0 else "#059669"
        delta_sign = "+" if isrs_v2_result["delta_isrs"] > 0 else ""
        st.markdown(f"""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:14px; margin-top:8px; display:flex; justify-content:space-around; align-items:center; text-align:center;">
            <div>
                <div style="font-size:0.8rem; color:#64748B;">التقييم الأساسي</div>
                <div style="font-size:1.3rem; font-weight:800; color:{b_color};">{b_score:.1f}%</div>
            </div>
            <div style="font-size:1.5rem; color:#94A3B8;">➔</div>
            <div>
                <div style="font-size:0.8rem; color:#64748B;">التقييم الموسع v2.0</div>
                <div style="font-size:1.3rem; font-weight:800; color:{v2_color};">{v2_score:.1f}%</div>
            </div>
            <div style="font-size:1.5rem; color:#94A3B8;">=</div>
            <div>
                <div style="font-size:0.8rem; color:#64748B;">فارق الأثر التنبؤي (Δ)</div>
                <div style="font-size:1.3rem; font-weight:900; color:{delta_color};">{delta_sign}{isrs_v2_result['delta_isrs']:.1f}%</div>
            </div>
            <div>
                <div style="font-size:0.8rem; color:#64748B;">إجمالي عقوبات المؤشرات الـ 5</div>
                <div style="font-size:1.3rem; font-weight:800; color:#7C3AED;">+{isrs_v2_result['new_indicators_penalties']['total_new_penalty']:.1f} نقطة</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # العرض القياسي أو المطور المنفرد
        col_gauge, col_radar = st.columns([1.8, 2.2])

        with col_gauge:
            st.markdown("### 🚨 مؤشر خطر التلكؤ العراقي (ISRS)")
            st.markdown(f"<div class='en-subtext'>{'Advanced ISRS v2.0 Engine' if eval_mode == 'ADVANCED' else 'Standard ISRS Engine'}</div>", unsafe_allow_html=True)
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=isrs_result["isrs_score"],
                domain={'x': [0.08, 0.92], 'y': [0.12, 0.95]},
                number={'suffix': "%", 'font': {'size': 38, 'family': 'Segoe UI, Tahoma, sans-serif', 'color': isrs_result["status_color"]}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                    'bar': {'color': isrs_result["status_color"], 'thickness': 0.35},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#E2E8F0",
                    'steps': [
                        {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.2)'},
                        {'range': [35, 65], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [65, 100], 'color': 'rgba(239, 68, 68, 0.25)'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.8,
                        'value': 65
                    }
                }
            ))
            fig_gauge.update_layout(
                height=270, 
                margin=dict(l=15, r=15, t=20, b=15), 
                font=dict(family='Cairo, sans-serif')
            )
            st.plotly_chart(fig_gauge, use_container_width=True, key="plot_single_isrs_gauge")

            st.markdown(f"""
            <div style="background:{isrs_result['status_color']}15; border:1px solid {isrs_result['status_color']}40; border-radius:10px; padding:12px; text-align:center; margin-top:-10px;">
                <b style="color:{isrs_result['status_color']}; font-size:1.05rem;">{isrs_result['status_icon']} {isrs_result['status_ar']}</b>
            </div>
            """, unsafe_allow_html=True)

        with col_radar:
            st.markdown("### 🕸️ توزيع شدة المخاطر على القطاعات العراقية")
            st.markdown("<div class='en-subtext'>Risk Breakdown by Iraqi Construction Domains</div>", unsafe_allow_html=True)
            
            categories = list(iraqi_risk_db.RISK_CATEGORIES.keys())
            cat_names = [ar(iraqi_risk_db.RISK_CATEGORIES[c]["name_ar"]) for c in categories]
            cat_values = [isrs_result["category_breakdown"].get(c, 0.0) for c in categories]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=cat_values + [cat_values[0]],
                theta=cat_names + [cat_names[0]],
                fill='toself',
                fillcolor='rgba(59, 130, 246, 0.25)',
                line=dict(color='#2563EB', width=2),
                name=ar('درجة الخطر')
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix='%')),
                showlegend=False,
                height=300,
                font=dict(family='Cairo, sans-serif', size=11),
                margin=dict(l=50, r=50, t=25, b=25)
            )
            st.plotly_chart(fig_radar, use_container_width=True, key="plot_single_isrs_radar")

    st.markdown("---")

    # لوحة المؤشرات التشغيلية الكلاسيكية
    st.markdown("### 🎛️ 1. المؤشرات التشغيلية الحقلية الأساسية (Classic Operational Telemetry)")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        new_rfis = st.slider("طلبات المعلومات العالقة (RFIs)", min_value=0, max_value=30, value=curr_rfis, key="slider_rfis")
        st.markdown(f"<div style='text-align:left;'><span class='val-badge'>{new_rfis} طلبات عالقة</span></div>", unsafe_allow_html=True)
    with col_f2:
        new_co = st.slider("أوامر الغيار قيد المصادقة", min_value=0, max_value=15, value=curr_co, key="slider_co")
        st.markdown(f"<div style='text-align:left;'><span class='val-badge'>{new_co} أوامر غيار</span></div>", unsafe_allow_html=True)
    with col_f3:
        new_cash = st.slider("عجز التدفق النقدي / السلف %", min_value=0, max_value=60, value=int(curr_cash_def), key="slider_cash")
        st.markdown(f"<div style='text-align:left;'><span class='val-badge'>{new_cash}% عجز سلف</span></div>", unsafe_allow_html=True)
    with col_f4:
        new_sub = st.slider("تقييم أداء المقاولين الثانويين", min_value=30, max_value=100, value=int(curr_sub_perf), key="slider_sub")
        st.markdown(f"<div style='text-align:left;'><span class='val-badge'>{new_sub} / 100 درجة</span></div>", unsafe_allow_html=True)

    # لوحة المؤشرات الخمسة المتقدمة (ISRS v2.0 Telemetry Suite)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:10px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-weight:700; color:#166534;">📡 2. المؤشرات الحقلية والفضائية الخمسة المتقدمة (Advanced Live Telemetry Feed)</span>
        <span style="font-size:0.75rem; background:#DCFCE7; color:#15803D; padding:3px 8px; border-radius:6px; font-weight:700;">ISRS v2.0 Suite</span>
    </div>
    """, unsafe_allow_html=True)

    col_adv1, col_adv2, col_adv3, col_adv4, col_adv5 = st.columns(5)
    with col_adv1:
        new_bim_c = st.slider("🧊 تعارضات BIM الحرجة:", 0, 15, int(curr_bim_clashes), key="slider_bim_clashes")
        st.markdown(f"<div style='font-size:0.75rem; color:#475569;'>عقوبة: <b>+{isrs_v2_result['new_indicators_penalties']['bim_clashes_penalty']}</b> نقطة</div>", unsafe_allow_html=True)
    with col_adv2:
        new_inf = st.slider("📈 تضخم أسعار المواد %:", 0.0, 30.0, float(curr_inflation), step=0.5, key="slider_inflation")
        st.markdown(f"<div style='font-size:0.75rem; color:#475569;'>عقوبة: <b>+{isrs_v2_result['new_indicators_penalties']['material_inflation_penalty']}</b> نقطة</div>", unsafe_allow_html=True)
    with col_adv3:
        new_lab = st.slider("🧪 تأخر فحص المختبر (أيام):", 0, 40, int(curr_lab_delay), key="slider_lab_delay")
        st.markdown(f"<div style='font-size:0.75rem; color:#475569;'>عقوبة: <b>+{isrs_v2_result['new_indicators_penalties']['lab_testing_penalty']}</b> نقطة</div>", unsafe_allow_html=True)
    with col_adv4:
        new_disp = st.slider("⚖️ النزاعات ومطالبات DAB:", 0, 10, int(curr_disputes), key="slider_disputes")
        st.markdown(f"<div style='font-size:0.75rem; color:#475569;'>عقوبة: <b>+{isrs_v2_result['new_indicators_penalties']['disputes_penalty']}</b> نقطة</div>", unsafe_allow_html=True)
    with col_adv5:
        new_heat = st.slider("🛰️ توقف حرارة الصيف (ساعة):", 0, 50, int(curr_heat_stoppage), key="slider_heat_stoppage")
        st.markdown(f"<div style='font-size:0.75rem; color:#475569;'>عقوبة: <b>+{isrs_v2_result['new_indicators_penalties']['heatwave_penalty']}</b> نقطة</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📌 التوصيات الفنية والتعاقدية الاستباقية لمعالجة التلكؤ")
    recs_to_show = isrs_v2_result["advanced_recommendations"] if eval_mode in ["COMPARE", "ADVANCED"] else isrs_result["recommendations"]
    for rec in recs_to_show:
        st.info(f"📌 **إجراء تعاقدي موصى به:** {rec}")

# ----------------- TAB 2: S-CURVES -----------------
elif selected_tab == "📈 منحنيات S-Curve":
    st.markdown("### 📈 منحنيات التوزيع التراكمي (S-Curves) ومستويات الثقة الإحصائية")
    st.markdown("<div class='en-subtext'>Quantitative Schedule & Cost Probability Distributions (QSRA / QCRA)</div>", unsafe_allow_html=True)
    
    if len(st.session_state.activities) == 0:
        st.info("💡 لا توجد أنشطة مسجلة حالياً لعرض منحنيات S-Curve. يرجى إضافة أنشطة من تبويب WBS أو استيراد جدول زمني.")
    else:
        col_scurve_time, col_scurve_cost = st.columns(2)

        with col_scurve_time:
            st.markdown("#### ⏳ منحنى S-Curve للجدول الزمني (مدة المشروع)")
            durations = np.sort(sim_res["total_durations"])
            probs = np.linspace(0, 100, len(durations))

            fig_dur = go.Figure()
            fig_dur.add_trace(go.Scatter(x=durations, y=probs, mode='lines', line=dict(color='#2563EB', width=3), name='S-Curve'))
            
            p50_d = sim_res["duration_percentiles"]["P50"]
            p80_d = sim_res["duration_percentiles"]["P80"]
            p90_d = sim_res["duration_percentiles"]["P90"]

            fig_dur.add_vline(x=p50_d, line_dash="dash", line_color="#10B981", annotation_text=f"P50: {p50_d:.0f}d")
            fig_dur.add_vline(x=p80_d, line_dash="dash", line_color="#F59E0B", annotation_text=f"P80: {p80_d:.0f}d")
            fig_dur.add_vline(x=p90_d, line_dash="dash", line_color="#EF4444", annotation_text=f"P90: {p90_d:.0f}d")

            fig_dur.update_layout(
                xaxis_title=ar("مدة المشروع الكلية (أيام العمل)"),
                yaxis_title=ar("احتمالية الإنجاز التراكمية (%)"),
                height=370,
                font=dict(family='Cairo, sans-serif'),
                hovermode="x unified"
            )
            st.plotly_chart(fig_dur, use_container_width=True, key="plot_scurve_duration")

        with col_scurve_cost:
            st.markdown(f"#### 💰 منحنى S-Curve للتكلفة الكلية للمشروع ({curr_sym})")
            costs = np.sort(sim_res["total_costs"])
            
            fig_cost = go.Figure()
            fig_cost.add_trace(go.Scatter(x=costs, y=probs, mode='lines', line=dict(color='#D97706', width=3), name='Cost S-Curve'))
            
            p50_c = sim_res["cost_percentiles"]["P50"]
            p80_c = sim_res["cost_percentiles"]["P80"]
            p90_c = sim_res["cost_percentiles"]["P90"]

            fig_cost.add_vline(x=p50_c, line_dash="dash", line_color="#10B981", annotation_text=f"P50: {p50_c:,.0f}")
            fig_cost.add_vline(x=p80_c, line_dash="dash", line_color="#F59E0B", annotation_text=f"P80: {p80_c:,.0f}")
            fig_cost.add_vline(x=p90_c, line_dash="dash", line_color="#EF4444", annotation_text=f"P90: {p90_c:,.0f}")

            fig_cost.update_layout(
                xaxis_title=ar(f"الكلفة التراكمية الإجمالية ({curr_sym})"),
                yaxis_title=ar("احتمالية عدم تجاوز الميزانية (%)"),
                height=370,
                font=dict(family='Cairo, sans-serif'),
                hovermode="x unified"
            )
            st.plotly_chart(fig_cost, use_container_width=True, key="plot_scurve_cost")

        st.markdown("#### 📑 جدول نسب الثقة والتوزيع الإحصائي التفصيلي")
        p_data = []
        for p_key in ["P10", "P20", "P30", "P40", "P50", "P60", "P70", "P75", "P80", "P85", "P90", "P95"]:
            d_val = sim_res["duration_percentiles"].get(p_key, 0)
            c_val = sim_res["cost_percentiles"].get(p_key, 0)
            p_data.append({
                "مستوى الثقة": p_key,
                "الاحتمالية": f"{p_key[1:]}%",
                "مدة المشروع (يوم)": f"{d_val:,.1f}",
                "الفرق عن التقدير الحتمي (يوم)": f"{d_val - sim_res['deterministic_duration']:+,.1f}",
                f"التكلفة المتوقعة ({curr_sym})": f"{c_val:,.0f}",
                "الفرق عن الكلفة المرجعية": f"{c_val - sim_res['deterministic_cost']:+,.0f}"
            })
        render_centered_table(pd.DataFrame(p_data))

# ----------------- TAB 3: TORNADO -----------------
elif selected_tab == "🌪️ تحليل الحساسية":
    st.markdown("### 🌪️ تحليل الحساسية ومخطط تورنادو (Tornado Sensitivity Analysis)")
    st.markdown("<div class='en-subtext'>Spearman Rank Correlation - Schedule & Cost Critical Drivers</div>", unsafe_allow_html=True)
    
    col_t_ctrl1, col_t_ctrl2 = st.columns([2, 1])
    with col_t_ctrl1:
        tornado_choice = st.radio(
            "🎯 اختر نوع تحليل الحساسية ومخطط تورنادو:",
            options=["⏱️ حساسية مدة الإنجاز والجدول الزمني (Schedule Duration)", "💰 حساسية التكلفة الكلية للمشروع (Project Cost)"],
            horizontal=True,
            key="tornado_mode_choice"
        )

    is_cost_mode = "التكلفة" in tornado_choice
    tornado_items = sim_res.get("tornado_cost" if is_cost_mode else "tornado_duration", [])
    
    if tornado_items:
        df_tornado = pd.DataFrame(tornado_items)
        df_tornado["name_ar_reshaped"] = df_tornado["name"].apply(ar)
        df_tornado["type_ar_reshaped"] = df_tornado["type"].map({
            "activity": ar("نشاط إنشائي"),
            "risk": ar("خطر عراقي")
        })
        df_tornado = df_tornado.sort_values(by="correlation", ascending=True)

        chart_title_txt = "مخطط تورنادو: العوامل الأكثر حساسية وتأثيراً على التكلفة الكلية" if is_cost_mode else "مخطط تورنادو: العوامل الأكثر حساسية وتأثيراً على مدة المشروع"
        fig_tornado = px.bar(
            df_tornado,
            x="correlation",
            y="name_ar_reshaped",
            orientation="h",
            color="type_ar_reshaped",
            color_discrete_map={ar("نشاط إنشائي"): "#3B82F6", ar("خطر عراقي"): "#EF4444"},
            title=ar(chart_title_txt)
        )
        
        fig_tornado.update_yaxes(
            automargin=True,
            title="",
            tickfont=dict(family="Cairo, Segoe UI, Tahoma, sans-serif", size=12, color="#0F172A")
        )
        fig_tornado.update_xaxes(
            title=ar("معامل الارتباط الترتيبي بالحساسية (Spearman Rank Correlation - ρ)"),
            gridcolor="#E2E8F0",
            automargin=True
        )
        
        chart_height = max(420, min(850, 80 + len(df_tornado) * 40))
        fig_tornado.update_layout(
            height=chart_height, 
            font=dict(family='Cairo, Segoe UI, Tahoma, sans-serif', size=12),
            margin=dict(l=320, r=40, t=60, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_tornado.update_traces(
            hovertemplate="<b>%{y}</b><br>🎯 معامل الارتباط بالحساسية (Spearman ρ): <b>%{x:.3f}</b><extra></extra>"
        )
        st.plotly_chart(fig_tornado, use_container_width=True, key="plot_tornado_sensitivity")

        st.markdown("---")
        st.markdown("#### 📋 جدول ترتيب العوامل والمخاطر الأكثر حساسية (Sensitivity Drivers Ranking):")
        df_table_tornado = pd.DataFrame(tornado_items).sort_values(by="correlation", key=abs, ascending=False)
        table_rows = []
        for idx, row in df_table_tornado.iterrows():
            table_rows.append({
                "المرتبة": len(table_rows) + 1,
                "العامل / النشاط الإنشائي": row.get("name"),
                "التصنيف": "🔴 خطر عراقي" if row.get("type") == "risk" else "🔵 نشاط إنشائي",
                "معامل الارتباط (Spearman ρ)": f"{row.get('correlation'):.3f}",
                "شدة التأثير النسبي": f"{abs(row.get('correlation', 0)) * 100:.1f}%"
            })
        render_centered_table(pd.DataFrame(table_rows))
    else:
        st.info("💡 لا توجد بيانات كافية حالياً لتحليل الحساسية ومخطط تورنادو. يرجى إضافة أنشطة ومخاطر للمشروع.")

# ----------------- TAB 4: ISO 31000 COORDINATION ISSUES -----------------
elif selected_tab == "🧩 التنسيق (ISO 31000)":
    st.markdown("### 🧩 نظام تصنيف وتقييم ومعالجة مشكلات التنسيق (ISO 31000:2018)")
    st.markdown("<div class='en-subtext'>Construction Coordination Risk Identification, Analysis, Evaluation & Treatment</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:18px 20px; margin-bottom:18px; direction:rtl; text-align:right;">
        <div style="font-weight:800; font-size:0.98rem; color:#1E293B; margin-bottom:12px;">
            📐 <b>المنهجية المعتمدة وفق معيار إدارة المخاطر الدولي (ISO 31000:2018):</b>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:12px;">
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:4px solid #3B82F6; border-radius:8px; padding:12px 14px;">
                <div style="font-weight:800; font-size:0.92rem; color:#1E40AF; margin-bottom:6px;">
                    1️⃣ تحديد الخطر <span class='en-badge'>Identification</span>
                </div>
                <div style="font-size:0.84rem; color:#475569; line-height:1.55;">
                    رصد وتوصيف التعارضات التصميمية والموقعية وتنسيق الجهات والدوائر الخدمية.
                </div>
            </div>
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:4px solid #0284C7; border-radius:8px; padding:12px 14px;">
                <div style="font-weight:800; font-size:0.92rem; color:#0369A1; margin-bottom:6px;">
                    2️⃣ تحليل الخطر <span class='en-badge'>Analysis</span>
                </div>
                <div style="font-size:0.84rem; color:#475569; line-height:1.55;">
                    تقدير احتمالية الوقوع وشدة العواقب وتأثيرها وقابلية الاكتشاف المبكر.
                </div>
            </div>
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:4px solid #D97706; border-radius:8px; padding:12px 14px;">
                <div style="font-weight:800; font-size:0.92rem; color:#B45309; margin-bottom:6px;">
                    3️⃣ تقييم الخطر <span class='en-badge'>Evaluation</span>
                </div>
                <div style="font-size:0.84rem; color:#475569; line-height:1.55;">
                    مواءمة مستوى الخطر وتحديد الأولويات (حرج غير مقبول / متوسط ALARP / مقبول).
                </div>
            </div>
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-top:4px solid #10B981; border-radius:8px; padding:12px 14px;">
                <div style="font-weight:800; font-size:0.92rem; color:#047857; margin-bottom:6px;">
                    4️⃣ معالجة الخطر <span class='en-badge'>Treatment</span>
                </div>
                <div style="font-size:0.84rem; color:#475569; line-height:1.55;">
                    تطبيق استراتيجيات (التجنب Avoid، التخفيف Mitigate، المشاركة Share، والقبول Accept).
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📥 استيراد وتحديث التعارضات مباشرة من تقرير Navisworks Clash Detective (.xml / .csv)", expanded=False):
        col_t4_nv1, col_t4_nv2 = st.columns([2.5, 1.2])
        with col_t4_nv1:
            up_t4_navis = st.file_uploader("اختر ملف تقرير تعارضات Navisworks (.xml / .csv):", type=["xml", "csv"], key="tab4_navis_uploader")
        with col_t4_nv2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if up_t4_navis is not None:
                res_t4 = navisworks_parser.parse_navisworks_clash_bytes(up_t4_navis.getvalue(), up_t4_navis.name)
                if res_t4.get("success"):
                    st.success(f"✅ تم بنجاح قراءة وتحليل كافة الـ {res_t4['total_clashes']:,} تعارض بالكامل ({res_t4['critical_clashes_count']:,} حرج)!")
                    if st.button("🚀 تحديث مصفوفة ISO 31000", type="primary", key="btn_apply_tab4_navis", use_container_width=True):
                        st.session_state.coordination_issues = res_t4["coordination_issues"]
                        st.session_state.last_import_msg = f"🎉 تم بنجاح استيراد وتفعيل كافة الـ {res_t4['total_clashes']:,} تعارض بالكامل في مصفوفة القرارات!"
                        st.rerun()
                else:
                    st.error(res_t4.get("error", "فشل تحليل الملف"))

    # استدعاء محرك الذكاء الاصطناعي والربط الزمني الفراغي 4D/5D مع التخزين المؤقت للسرعة الفائقة
    ai_hub_res = get_cached_ai_bim_decision_hub(
        clashes=st.session_state.coordination_issues,
        activities=st.session_state.activities
    )
    coord_summary = get_cached_coordination_summary(st.session_state.coordination_issues)

    # 1. شريط الإنذار المبكر ومؤشرات الأداء الذكية (Early Warning KPI Strip)
    col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
    with col_c1:
        st.markdown(f"""
        <div class="kpi-card" style="padding:12px;">
            <div class="kpi-title" style="font-size:0.78rem;">📌 إجمالي التعارضات</div>
            <div class="kpi-value" style="font-size:1.4rem;">{ai_hub_res['total_clashes']} <span style="font-size:0.75rem; color:#64748B;">تعارض</span></div>
            <div class="kpi-sub">مرصودة في النماذج</div>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown(f"""
        <div class="kpi-card" style="padding:12px;">
            <div class="kpi-title" style="font-size:0.78rem;">🛡️ تصفية الضوضاء AI</div>
            <div class="kpi-value" style="font-size:1.4rem; color:#0284C7;">{ai_hub_res['noise_filtered_pct']}%</div>
            <div class="kpi-sub">{ai_hub_res['noise_filtered_count']} تفاوت مسموح مصفى</div>
        </div>
        """, unsafe_allow_html=True)

    with col_c3:
        st.markdown(f"""
        <div class="kpi-card" style="padding:12px;">
            <div class="kpi-title" style="font-size:0.78rem;">🚨 تهديد المسار الحرج P6</div>
            <div class="kpi-value" style="font-size:1.4rem; color:#DC2626;">{ai_hub_res['critical_clashes_count']} <span style="font-size:0.75rem; color:#64748B;">تعارض</span></div>
            <div class="kpi-sub">يمس أنشطة حرجة (Float=0)</div>
        </div>
        """, unsafe_allow_html=True)

    with col_c4:
        st.markdown(f"""
        <div class="kpi-card" style="padding:12px;">
            <div class="kpi-title" style="font-size:0.78rem;">⏳ التأخير التنبؤي المتوقع</div>
            <div class="kpi-value" style="font-size:1.4rem; color:#D97706;">+{ai_hub_res['total_critical_path_delay_days']} <span style="font-size:0.75rem; color:#64748B;">يوم</span></div>
            <div class="kpi-sub">أثر مباشر قبل الحسم</div>
        </div>
        """, unsafe_allow_html=True)

    with col_c5:
        st.markdown(f"""
        <div class="kpi-card" style="padding:12px;">
            <div class="kpi-title" style="font-size:0.78rem;">💰 كلفة إعادة العمل 5D</div>
            <div class="kpi-value" style="font-size:1.4rem; color:#7C3AED;">{ai_hub_res['total_projected_rework_cost_usd']:,.0f} <span style="font-size:0.75rem; color:#64748B;">{curr_sym}</span></div>
            <div class="kpi-sub">توفير مضمون بالحسم المبكر</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. مصفوفة ISO 31000 وتوزيع المجالات
    col_ch1, col_ch2 = st.columns([1.65, 1.35])

    with col_ch1:
        render_iso31000_matrix_html(st.session_state.coordination_issues)

    with col_ch2:
        st.markdown("#### 📊 توزيع التعارضات حسب مجالات التنسيق (ISO 31000)")
        
        domain_mapping = {
            "DESIGN_TECHNICAL": "📐 التصميم ونمذجة BIM",
            "STAKEHOLDER_INTERFACES": "🏛️ أصحاب المصلحة والخدمات",
            "SITE_SUBCONTRACTORS": "👷‍♂️ مقاولو الموقع والتنفيذ",
            "SUPPLY_LOGISTICS": "🚚 سلاسل التوريد والفحص",
            "INFORMATION_FLOW": "📑 تدفق المخططات و RFIs"
        }
        
        domain_labels = [domain_mapping.get(d, iso31000_coordination.COORDINATION_DOMAINS[d]["name_ar"]) for d in iso31000_coordination.COORDINATION_DOMAINS]
        domain_vals = [coord_summary["domain_breakdown"].get(d, 0) for d in iso31000_coordination.COORDINATION_DOMAINS]
        domain_colors = ["#2563EB", "#0284C7", "#D97706", "#059669", "#7C3AED"]

        fig_dom = go.Figure(go.Bar(
            x=domain_vals,
            y=domain_labels,
            orientation='h',
            marker=dict(
                color=domain_colors,
                line=dict(color='#CBD5E1', width=1)
            ),
            text=[f"  <b>{v}</b> تعارض" if v > 0 else " 0" for v in domain_vals],
            textposition='auto',
            textfont=dict(family='Cairo, sans-serif', size=12, color='#0F172A'),
            hovertemplate='<b>%{y}</b><br>عدد مشكلات التنسيق: <b>%{x}</b><extra></extra>'
        ))

        fig_dom.update_layout(
            height=320,
            font=dict(family='Cairo, sans-serif', size=12),
            margin=dict(l=185, r=30, t=20, b=25),
            plot_bgcolor='rgba(248, 250, 252, 0.6)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title=dict(text='عدد المشكلات والتعارضات المرصودة', font=dict(family='Cairo, sans-serif', size=12, color='#475569')),
                gridcolor='#E2E8F0',
                zeroline=False,
                automargin=True,
                tickfont=dict(family='Segoe UI, Tahoma, sans-serif', size=11)
            ),
            yaxis=dict(
                autorange='reversed',
                automargin=True,
                tickfont=dict(family='Cairo, sans-serif', size=12, color='#0F172A')
            ),
            showlegend=False
        )
        st.plotly_chart(fig_dom, use_container_width=True, key="plot_iso31000_domains")

        st.markdown("""
        <div style="background:#F8FAFC; border-radius:10px; padding:12px; border:1px solid #E2E8F0; font-size:0.82rem; color:#475569; line-height:1.6; text-align:right; direction:rtl;">
            💡 <b>إرشاد تحليلي:</b> يوضح المخطط تركز مشكلات التنسيق بين التخصصات المعمارية والإنشائية ومسارات الكهروميكانيك (MEP) والواجهات الموقعية لتحديد أولويات المعالجة التعاقدية.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 💡 بطاقة التفسير المفاهيمي الذكية للفرق بين الحصر النظري 2D والفرز التنفيذي 4D (المقترح الثاني)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%); border: 1px solid #BFDBFE; border-radius: 12px; padding: 14px 18px; margin: 12px 0 18px 0; box-shadow: 0 2px 8px rgba(37,99,235,0.05); direction: rtl;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid #DBEAFE; padding-bottom: 6px;">
            <span style="font-weight: 800; font-size: 0.95rem; color: #1E40AF;">💡 دليل فهم المصفوفتين (الفرق بين الحصر النظري 2D والفرز التنفيذي الذكي 4D/5D):</span>
            <span style="font-size: 0.75rem; background: #DBEAFE; color: #1E40AF; padding: 2px 8px; border-radius: 6px; font-weight: 700;">ISO 31000 + Bitaraf Model 2024</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 0.82rem; color: #334155; line-height: 1.5;">
            <div style="background: #FFFFFF; border-radius: 8px; padding: 10px 12px; border: 1px solid #E2E8F0;">
                <b style="color: #0F172A;">1️⃣ المصفوفة العليا (2D BIM Compliance):</b><br/>
                حصر هندسي نظري مجرد (الاحتمالية × الشدة). يضع معظم التعارضات في المنطقة الحمراء (حرجة/كبيرة) بسبب نوع العنصر فقط دون معرفة موعد تنفيذه في الموقع.
            </div>
            <div style="background: #FFFFFF; border-radius: 8px; padding: 10px 12px; border: 1px solid #E2E8F0;">
                <b style="color: #0284C7;">2️⃣ مصفوفة القرارات الذكية (4D/5D AI-Triage):</b><br/>
                فرز تنفيذي ديناميكي يدمج جدول <b>Primavera P6</b>؛ فالتعارض الذي يمتلك سماحية زمنية (Float) يُخفض خطره إلى <b>خطر متوسط (ALARP)</b> لعدم مساسه بالمسار الحرج اليوم، مما يوفر جهود الموقع ويركز على الطوارئ الحقيقية.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. جدول محطة دعم القرار الذكية وتحديد الأولويات والتفسير (Decision Hub Prioritization Table)
    st.markdown("#### 🧠 مصفوفة القرارات الذكية وتحديد الأولويات والتفسير (AI-BIM Decision Hub & Triage Matrix)")
    st.markdown("<div style='font-size:0.85rem; color:#64748B; margin-bottom:12px;'>ترتيب الأولويات متعدد المعايير (نموذج Bitaraf 2024)، الربط بجدول P6، التفسير بالذكاء الاصطناعي، واستراتيجيات ISO 31000:</div>", unsafe_allow_html=True)

    hub_rows = []
    for ac in ai_hub_res["analyzed_clashes"]:
        top_shap = ac["shap_explanation"][0] if ac["shap_explanation"] else {"factor": "عام", "impact_pct": 20}
        hub_rows.append({
            "كود التعارض": ac["clash_id"],
            "معرف العناصر (Element ID)": ac.get("element_ids_formatted", f"{ac.get('element_id_1', '13178084')} ⚔️ {ac.get('element_id_2', '25046673')}"),
            "أسماء العناصر (Item Name)": ac.get("item_names_formatted", f"{ac.get('item1_name', 'MEP_Duct')} ⚔️ {ac.get('item2_name', 'STR_Beam')}"),
            "توصيف التعارض": ac["title_ar"],
            "مؤشر الأولوية Ψ": f"{ac['priority_score']:.1f}/100",
            "درجة_الخطورة": ac["priority_score"],
            "تقييم ISO 31000": ac["iso_level_ar"],
            "الفارق الذكي (4D Delta)": ac.get("delta_explanation", "حماية المسار الحرج"),
            "نشاط P6 المتأثر": ac["p6_activity_name"],
            "المسار الحرج": "🔴 حرج (Float=0)" if ac["is_critical_p6"] else f"🟢 سماحية {ac['total_float_days']} يوم",
            "أيام التأخير": f"+{ac['estimated_delay_days']} يوم",
            "كلفة المعالجة 5D": f"{ac['estimated_rework_cost_usd']:,.0f} {curr_sym}",
            "العامل التفسيري الأكبر (AI)": f"{top_shap['factor']} ({top_shap['impact_pct']}%)",
            "استراتيجية ISO 31000": ac["suggested_iso_strategy"],
            "التوصية الإنشائية": ac["treatment_recommendation_ar"]
        })
    hub_columns = [
        "كود التعارض", "معرف العناصر (Element ID)", "أسماء العناصر (Item Name)", "توصيف التعارض", "مؤشر الأولوية Ψ", "درجة_الخطورة",
        "تقييم ISO 31000", "الفارق الذكي (4D Delta)", "نشاط P6 المتأثر", "المسار الحرج", "أيام التأخير",
        "كلفة المعالجة 5D", "العامل التفسيري الأكبر (AI)", "استراتيجية ISO 31000", "التوصية الإنشائية"
    ]
    df_hub_full = pd.DataFrame(hub_rows, columns=hub_columns) if hub_rows else pd.DataFrame(columns=hub_columns)

    if df_hub_full.empty:
        st.info("💡 لا توجد تعارضات مسجلة حالياً في مصفوفة التنسيق. يرجى استيراد تقرير تعارضات Navisworks (.xml / .csv) من الصندوق أعلاه لعرض مصفوفة القرارات الذكية.")
    else:
        # شريط التحكم والتصفية الذكية
        col_t1, col_t2, col_t3 = st.columns([1.8, 1.2, 1.0])
        with col_t1:
            t_search_kw = st.text_input("🔍 بحث فوري (كود، معرف Element ID، اسم Item، نشاط، فارق):", placeholder="ابحث برقم العنصر 13178084، الاسم، الكود، النشاط...", key="triage_search_kw")
        with col_t2:
            raw_iso_opts = list(df_hub_full["تقييم ISO 31000"].dropna().unique()) if "تقييم ISO 31000" in df_hub_full.columns else []
            t_iso_options = ["الكل"] + sorted(raw_iso_opts)
            t_selected_iso = st.selectbox("🎯 تصفية بمستوى خطر ISO:", options=t_iso_options, key="triage_iso_filter")
        with col_t3:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            t_only_crit = st.checkbox("🚨 مسار حرج فقط (Float = 0)", value=False, key="triage_only_crit")

        # تطبيق الفلاتر
        df_hub_filtered = df_hub_full.copy()
        if t_search_kw:
            q = t_search_kw.strip().lower()
            df_hub_filtered = df_hub_filtered[
                df_hub_filtered["كود التعارض"].astype(str).str.lower().str.contains(q) |
                df_hub_filtered["معرف العناصر (Element ID)"].astype(str).str.lower().str.contains(q) |
                df_hub_filtered["أسماء العناصر (Item Name)"].astype(str).str.lower().str.contains(q) |
                df_hub_filtered["توصيف التعارض"].astype(str).str.lower().str.contains(q) |
                df_hub_filtered["نشاط P6 المتأثر"].astype(str).str.lower().str.contains(q) |
                df_hub_filtered["الفارق الذكي (4D Delta)"].astype(str).str.lower().str.contains(q) |
                df_hub_filtered["استراتيجية ISO 31000"].astype(str).str.lower().str.contains(q) |
                df_hub_filtered["التوصية الإنشائية"].astype(str).str.lower().str.contains(q)
            ]
        if t_selected_iso != "الكل":
            df_hub_filtered = df_hub_filtered[df_hub_filtered["تقييم ISO 31000"] == t_selected_iso]
        if t_only_crit:
            df_hub_filtered = df_hub_filtered[df_hub_filtered["المسار الحرج"].astype(str).str.contains("حرج")]

        col_pag1, col_pag2 = st.columns([2.2, 1.2])
        with col_pag1:
            st.markdown(f"<div style='font-size:0.83rem; color:#475569; padding-top:8px; font-weight:600;'>النتائج المعروضة: <b style='color:#0284C7;'>{len(df_hub_filtered)}</b> من أصل <b>{len(df_hub_full)}</b> تعارض</div>", unsafe_allow_html=True)
        with col_pag2:
            t_page_size = st.selectbox("📄 عدد التعارضات بالصفحة:", options=[50, 100, 200, "الكل"], index=0, key="triage_page_sz")

        display_df = df_hub_filtered.drop(columns=["درجة_الخطورة"], errors="ignore")
        if t_page_size != "الكل" and len(display_df) > int(t_page_size):
            psize = int(t_page_size)
            total_pages = max(1, math.ceil(len(display_df) / psize))
            col_pg_btn1, col_pg_btn2 = st.columns([1.2, 2.8])
            with col_pg_btn1:
                cur_page = st.number_input(f"📑 رقم الصفحة (من {total_pages}):", min_value=1, max_value=total_pages, value=1, step=1, key="triage_cur_pg")
            with col_pg_btn2:
                st.markdown(f"<div style='font-size:0.80rem; color:#64748B; padding-top:28px;'>عرض التعارضات من {(cur_page-1)*psize + 1} إلى {min(cur_page*psize, len(display_df))}</div>", unsafe_allow_html=True)
            start_i = (cur_page - 1) * psize
            end_i = start_i + psize
            display_df = display_df.iloc[start_i:end_i]

        render_decision_hub_html_grid(display_df)

    # 4. لوحة فحص وتصحيح الخبراء التفاعلية وتصدير تذاكر BCF (Human-in-the-Loop & BCF Export)
    st.markdown("<br>", unsafe_allow_html=True)
    col_fb1, col_fb2 = st.columns([1.5, 1.0])

    with col_fb1:
        st.markdown("##### ✍️ استوديو فحص وتصحيح الخبير في الحلقة (Human-in-the-Loop Studio):")
        col_s_box, col_s_in = st.columns([1.4, 1.1])
        with col_s_box:
            clash_options = [c["id"] for c in st.session_state.coordination_issues[:2000]]
            sel_c_id_select = st.selectbox("1️⃣ اختر كود التعارض من القائمة السريعة:", options=clash_options, key="hitl_clash_sel") if clash_options else ""
        with col_s_in:
            manual_c_id = st.text_input("أو ابحث برقم الكود مباشرة:", placeholder="مثال: NV_045...", key="hitl_manual_cid")
            
        sel_c_id = manual_c_id.strip() if manual_c_id.strip() else sel_c_id_select
        if sel_c_id:
            sel_clash_data = next((c for c in st.session_state.coordination_issues if c["id"].lower() == sel_c_id.lower()), None)
            sel_analyzed = next((ac for ac in ai_hub_res["analyzed_clashes"] if ac["clash_id"].lower() == sel_c_id.lower()), None)
            
            if sel_clash_data and sel_analyzed:
                st.markdown(f"""
                <div style="background:#F1F5F9; border-radius:10px; padding:10px 14px; border:1px solid #CBD5E1; margin-bottom:12px; font-size:0.84rem;">
                    <b>🤖 تقييم الذكاء الاصطناعي الأولي:</b> {sel_analyzed['iso_level_ar']} • مؤشر الأولوية: <b>{sel_analyzed['priority_score']:.1f}/100</b> • الكلفة التقديرية: <b>{sel_analyzed['estimated_rework_cost_usd']:,.0f} {curr_sym}</b>
                </div>
                """, unsafe_allow_html=True)
                
                col_e1, col_e2, col_e3 = st.columns(3)
                with col_e1:
                    new_l = st.slider("الاحتمالية المحدثة:", 1, 5, int(sel_clash_data.get("likelihood", 3)), key=f"hitl_l_{sel_c_id}")
                with col_e2:
                    new_c = st.slider("العواقب المحدثة:", 1, 5, int(sel_clash_data.get("consequence", 3)), key=f"hitl_c_{sel_c_id}")
                with col_e3:
                    strat_options = ["AVOID", "MITIGATE", "TRANSFER", "ACCEPT"]
                    strat_idx = strat_options.index(sel_clash_data.get("iso_treatment_strategy", "MITIGATE")) if sel_clash_data.get("iso_treatment_strategy") in strat_options else 1
                    new_strat = st.selectbox("استراتيجية المعالجة المعتمدة:", strat_options, index=strat_idx, key=f"hitl_st_{sel_c_id}")
                
                if st.button("💾 اعتماد وتثبيت قرار الخبير وتحديث منظومة المحاكاة فوراً", type="primary", key="btn_save_hitl", use_container_width=True):
                    sel_clash_data["likelihood"] = new_l
                    sel_clash_data["consequence"] = new_c
                    sel_clash_data["iso_treatment_strategy"] = new_strat
                    st.session_state.last_import_msg = f"✅ تم بنجاح تثبيت تصحيح الخبير للتعارض {sel_c_id} وإعادة معايرة محرك القرارات الذكي!"
                    st.rerun()

    with col_fb2:
        st.markdown("##### 📤 تصدير تقرير التنسيق المفتوح (OpenBIM BCF 2.1):")
        st.markdown("<div style='font-size:0.8rem; color:#64748B; margin-bottom:10px;'>تصدير مخرجات القرارات ومصفوفة ISO 31000 بتنسيق BCF المعتمد للفتح في Autodesk Revit و Navisworks:</div>", unsafe_allow_html=True)
        bcf_json_payload = ai_bim_decision_hub.export_clash_triage_to_bcf_json(
            analyzed_clashes=ai_hub_res["analyzed_clashes"],
            project_name=active_meta.get("name_ar", "CBI Tower Project")
        )
        st.download_button(
            label="📥 تنزيل تذاكر التنسيق الذكية (BCF 2.1 JSON)",
            data=bcf_json_payload,
            file_name=f"ICRAT_BCF_{active_meta.get('id', 'Project')}_Clash_Triage.json",
            mime="application/json",
            use_container_width=True,
            key="btn_download_bcf_tab4"
        )

# ----------------- TAB 5: CONTRACTUAL DELAY CLAIMS & EOT [NEW] -----------------
elif selected_tab == "⚖️ المطالبات والتمديد (EOT)":
    st.markdown("### ⚖️ حاسبة المطالبات التعاقدية والتمديد الزمني (EOT & Prolongation Claims)")
    st.markdown("<div class='en-subtext'>Iraqi General Conditions of Contract (Article 44 & 47) • Extension of Time & Delay Fines</div>", unsafe_allow_html=True)

    eot_calc_res = get_cached_eot_claims(
        delay_events=st.session_state.delay_events,
        duration_days=int(active_meta.get("contract_original_duration_days", 450)),
        cost=float(active_meta.get("contract_original_cost", 12500000.0)),
        overhead=float(active_meta.get("daily_overhead_usd", 3500.0)),
        fine_mult=0.10,
        curr_sym=curr_sym
    )

    col_eot1, col_eot2, col_eot3, col_eot4 = st.columns(4)
    with col_eot1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">⏳ التمديد الزمني المستحق (EOT)</div>
            <div class="kpi-value" style="color:#2563EB;">+{eot_calc_res['total_entitled_eot_days']} <span style="font-size:1rem; color:#64748B;">يوم</span></div>
            <div class="kpi-sub">المادة (44) من الشروط العامة</div>
        </div>
        """, unsafe_allow_html=True)

    with col_eot2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">💵 مطالبة تكاليف استمرار الموقع</div>
            <div class="kpi-value" style="color:#059669;">+{eot_calc_res['total_prolongation_claim']:,.0f} <span style="font-size:1rem; color:#64748B;">{curr_sym}</span></div>
            <div class="kpi-sub">عن {eot_calc_res['total_compensable_days']} يوم تأخير معوّض</div>
        </div>
        """, unsafe_allow_html=True)

    with col_eot3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">⚠️ الغرامات التأخيرية المحسوبة</div>
            <div class="kpi-value" style="color:#DC2626;">-{eot_calc_res['total_liquidated_damages']:,.0f} <span style="font-size:1rem; color:#64748B;">{curr_sym}</span></div>
            <div class="kpi-sub">عن {eot_calc_res['total_contractor_delay_days']} يوم غير مبرر (م47)</div>
        </div>
        """, unsafe_allow_html=True)

    with col_eot4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">💰 صافي الرصيد المالي للمطالبة</div>
            <div class="kpi-value" style="color:#D97706;">{eot_calc_res['net_contractual_balance']:+,.0f} <span style="font-size:1rem; color:#64748B;">{curr_sym}</span></div>
            <div class="kpi-sub">الاستحقاق المالي الصافي للمقاول</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📋 سجل أحداث وتوقفات المشروع المسجلة رسمياً (Delay Events Register)")
    
    eot_table_rows = []
    for ev in eot_calc_res["event_assessments"]:
        eot_table_rows.append({
            "كود الحدث": ev.get("id"),
            "توصيف التوقف / التأخير": ev.get("title_ar"),
            "التصنيف التعاقدي": ev.get("status_badge"),
            "الأيام المطالب بها": f"{ev.get('claimed_days', 0)} يوم",
            "التمديد المصادق عليه": ev.get("entitled_extension"),
            "التعويض المالي": ev.get("financial_compensation"),
            "السند القانوني العراقي": ev.get("legal_basis", "")
        })
    render_centered_table(pd.DataFrame(eot_table_rows))

    with st.expander("➕ إضافة حدث تأخير أو مطالبة جديدة لسجل المشروع", expanded=False):
        with st.form("add_delay_event_form"):
            col_de1, col_de2 = st.columns(2)
            with col_de1:
                new_de_id = st.text_input("كود حدث التأخير:", value=f"DELAY_{len(st.session_state.delay_events)+1:02d}")
                new_de_title = st.text_input("عنوان وتوصيف حدث التأخير:", placeholder="مثال: تأخر تسليم موقع محطة التحويل الثانوية")
                new_de_cat = st.selectbox(
                    "التصنيف القانوني والتعاقدي للتأخير:",
                    options=list(eot_claims_engine.DELAY_EVENT_CATEGORIES.keys()),
                    format_func=lambda k: f"{eot_claims_engine.DELAY_EVENT_CATEGORIES[k]['name_ar']}"
                )
            with col_de2:
                new_de_claimed = st.number_input("عدد الأيام المطالب بها رسمياً:", min_value=1, value=30, step=1)
                new_de_approved = st.number_input("عدد الأيام المصادق عليها من المهندس المقيم:", min_value=0, value=25, step=1)
                new_de_legal = st.text_input("المادة العقدية والسند القانوني:", value="المادة (44) والمادة (52) من الشروط العامة")

            submit_de = st.form_submit_button("💾 إضافة وتوثيق حدث التأخير", use_container_width=True)
            if submit_de:
                d_type = eot_claims_engine.DELAY_EVENT_CATEGORIES[new_de_cat]["type"]
                st.session_state.delay_events.append({
                    "id": new_de_id,
                    "category": new_de_cat,
                    "title_ar": new_de_title or "حدث تأخير جديد",
                    "claimed_days": int(new_de_claimed),
                    "approved_days": int(new_de_approved) if d_type != "NON_EXCUSABLE" else 0,
                    "contractor_delay_days": int(new_de_claimed) if d_type == "NON_EXCUSABLE" else 0,
                    "delay_type": d_type,
                    "responsible": "جهة التعاقد / المقاول",
                    "legal_basis": new_de_legal
                })
                st.success(f"تمت إضافة حدث التأخير ({new_de_title}) وحساب المطالبات بنجاح!")
                st.rerun()

# ----------------- TAB 6: WHAT-IF MITIGATION COMPARATOR [NEW] -----------------
elif selected_tab == "🔮 مقارن السيناريوهات (What-If)":
    st.markdown("### 🔮 محاكي ومقارن السيناريوهات التفاعلي (What-If Mitigation Simulator)")
    st.markdown("<div class='en-subtext'>Interactive Scenario Analysis: Pre-Mitigation Baseline vs. Post-Mitigation Optimized</div>", unsafe_allow_html=True)
    
    st.markdown("#### 🎛️ تفعيل وتجربة رافعات المعالجة الهندسية والتعاقدية (Mitigation Levers):")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        lev_cash = st.checkbox("💵 تأمين السيولة وصرف سلف الإنجاز", value=True, help="يخفض عجز السلف ومخاطر التمويل بنسبة 80%")
        lev_bim = st.checkbox("🧩 حسم تعارضات BIM الموقعية مسبقاً", value=True, help="يحل التعارضات ويقلل طلبات المعلومات RFIs بنسبة 70%")
    with col_l2:
        lev_co = st.checkbox("⚡ تسريع لجان مصادقة أوامر الغيار", value=True, help="تقليص الدورة المستندية لأوامر التغيير")
        lev_sub = st.checkbox("🤝 تأهيل وفرض ضمانات المقاولين الثانويين", value=True, help="رفع كفاءة الإنجاز إلى 95%")
    with col_l3:
        lev_cust = st.checkbox("🚢 التخليص الكمركي المسبق في المنافذ", value=True, help="تفادي غرامات الأرضيات وتأخر الاستيراد")

    whatif_res = run_cached_whatif(
        base_activities=st.session_state.activities,
        base_risks=st.session_state.risk_register,
        base_meta=active_meta,
        levers={
            "lever_cash_flow": lev_cash,
            "lever_bim_coordination": lev_bim,
            "lever_fast_change_orders": lev_co,
            "lever_subcontractor": lev_sub,
            "lever_customs": lev_cust
        },
        iterations=1500,
        random_seed=42
    )

    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:4px solid #3B82F6;">
            <div class="kpi-title">⏱️ الأيام الزمنية التي تم إنقاذها</div>
            <div class="kpi-value" style="color:#2563EB;">+{whatif_res['days_saved']:,.0f} <span style="font-size:1rem; color:#64748B;">يوم</span></div>
            <div class="kpi-sub">توفير {whatif_res['days_saved_pct']:.1f}% من مدة المشروع الكلية</div>
        </div>
        """, unsafe_allow_html=True)

    with col_w2:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:4px solid #10B981;">
            <div class="kpi-title">💰 الوفر المالي المحقق من المعالجة</div>
            <div class="kpi-value" style="color:#059669;">+{whatif_res['cost_saved']:,.0f} <span style="font-size:1rem; color:#64748B;">{curr_sym}</span></div>
            <div class="kpi-sub">تقليل تضخم التكاليف والمصاريف الإدارية</div>
        </div>
        """, unsafe_allow_html=True)

    with col_w3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:4px solid #F59E0B;">
            <div class="kpi-title">🚨 تراجع مؤشر خطر التلكؤ (ISRS)</div>
            <div class="kpi-value" style="color:#D97706;">-{whatif_res['isrs_reduction']:.1f}%</div>
            <div class="kpi-sub">من {whatif_res['base_isrs']:.1f}% ➔ إلى {whatif_res['mit_isrs']:.1f}% (منطقة آمنة)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📊 مقارنة بصرية بين السيناريو الراهن والسيناريو المعالج:")
    
    col_wc1, col_wc2 = st.columns(2)
    with col_wc1:
        fig_w_dur = go.Figure()
        fig_w_dur.add_trace(go.Bar(
            x=[ar("الوضع الراهن (Pre-Mitigation)"), ar("الوضع المعالج (Post-Mitigation)")],
            y=[whatif_res["base_p80_duration"], whatif_res["mit_p80_duration"]],
            marker_color=["#EF4444", "#10B981"],
            text=[f"{whatif_res['base_p80_duration']:.0f} يوم", f"{whatif_res['mit_p80_duration']:.0f} يوم"],
            textposition="auto"
        ))
        fig_w_dur.update_layout(
            title=ar("مقارنة مدة الإنجاز P80 (أيام)"),
            height=320,
            font=dict(family="Cairo, sans-serif"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_w_dur, use_container_width=True, key="plot_whatif_durations")

    with col_wc2:
        fig_w_isrs = go.Figure()
        fig_w_isrs.add_trace(go.Bar(
            x=[ar("مؤشر التلكؤ الراهن"), ar("مؤشر التلكؤ المعالج")],
            y=[whatif_res["base_isrs"], whatif_res["mit_isrs"]],
            marker_color=["#DC2626", "#059669"],
            text=[f"{whatif_res['base_isrs']:.1f}%", f"{whatif_res['mit_isrs']:.1f}%"],
            textposition="auto"
        ))
        fig_w_isrs.update_layout(
            title=ar("مقارنة مؤشر خطر التلكؤ العراقي (ISRS)"),
            height=320,
            font=dict(family="Cairo, sans-serif"),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_w_isrs, use_container_width=True, key="plot_whatif_isrs")

# ----------------- TAB 7: AI CONTRACT COPILOT [NEW] -----------------
elif selected_tab == "🤖 المستشار الذكي والمخاطبات":
    st.markdown("### 🤖 المستشار الذكي للعقود وصانع المخاطبات الرسمية (AI Contract Copilot)")
    st.markdown("<div class='en-subtext'>Iraqi Construction Legal & Contractual Advisory • Automated Formal Letter Drafting</div>", unsafe_allow_html=True)
    
    col_cp1, col_cp2 = st.columns([1.5, 2.5])
    
    with col_cp1:
        st.markdown("#### 📝 اختر نوع الكتاب الرسمي المراد توليده:")
        letter_choice = st.radio(
            "نوع المخاطبة الرسمية:",
            [
                "1. كتاب طلب تمديد مدة العقد والمطالبة بالتعويض (EOT Claim)",
                "2. كتاب طلب حسم تعارض تنسيقي موقعي (BIM RFI)",
                "3. محضر اجتماع ورشة التنسيق ISO 31000 الرسمي"
            ]
        )

        st.markdown("---")
        st.markdown("#### 📚 استعراض المواد القانونية العراقية المعتمدة:")
        selected_art_key = st.selectbox(
            "اختر المادة العقدية للاطلاع:",
            options=list(contract_copilot.IRAQI_CONTRACT_ARTICLES.keys()),
            format_func=lambda k: contract_copilot.IRAQI_CONTRACT_ARTICLES[k]["article"]
        )
        art_info = contract_copilot.IRAQI_CONTRACT_ARTICLES[selected_art_key]
        st.info(f"📌 **{art_info['article']}**\n\n{art_info['summary_ar']}\n\n*النص العريض:* {art_info['legal_text']}")

    with col_cp2:
        st.markdown("#### 📄 مسودة الكتاب الرسمي المولد (جاهز للنسخ والطباعة):")
        
        if "1. كتاب طلب تمديد" in letter_choice:
            drafted_letter = contract_copilot.generate_official_eot_letter(
                project_name=active_meta.get("name_ar", "المشروع الإنشائي"),
                contract_ref=active_meta.get("id", "IRQ_PROJ_2026"),
                client_name=active_meta.get("client_type_ar", "الجهة المستفيدة / صاحب العمل"),
                contractor_name="شركة المقاولات العامة المنفذة",
                claimed_days=eot_calc_res.get("total_entitled_eot_days", 45),
                reasons_list=[ev.get("title_ar") for ev in st.session_state.delay_events if ev.get("delay_type") != "NON_EXCUSABLE"],
                prolongation_cost_str=f"{eot_calc_res.get('total_prolongation_claim', 0):,.0f} {curr_sym}"
            )
        elif "2. كتاب طلب حسم تعارض" in letter_choice:
            first_coord = st.session_state.coordination_issues[0] if st.session_state.coordination_issues else {"id": "COORD_01", "title_ar": "تعارض خط الأنابيب مع الأساسات", "treatment_action_ar": "تعديل المسار"}
            drafted_letter = contract_copilot.generate_coordination_rfi_letter(
                project_name=active_meta.get("name_ar", "المشروع الإنشائي"),
                contract_ref=active_meta.get("id", "IRQ_PROJ_2026"),
                client_name=active_meta.get("client_type_ar", "دائرة المهندس المقيم"),
                issue_code=first_coord.get("id"),
                issue_desc=first_coord.get("title_ar"),
                proposed_solution=first_coord.get("treatment_action_ar")
            )
        else:
            drafted_letter = contract_copilot.generate_coordination_meeting_minutes(
                project_name=active_meta.get("name_ar", "المشروع الإنشائي"),
                issues_summary=st.session_state.coordination_issues[:4]
            )

        st.text_area("نص الكتاب الرسمي:", value=drafted_letter, height=430)
        st.download_button(
            label="📥 تنزيل نص الكتاب الرسمي (.txt)",
            data=drafted_letter,
            file_name=f"Official_Letter_{active_meta.get('id', 'PROJ')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ----------------- TAB 8: 3D BIM RISK VIEWER [NEW] -----------------
elif selected_tab == "🧊 عارض BIM 3D التفاعلي":
    st.markdown("### 🧊 عارض نماذج البناء ثلاثي الأبعاد الملون بالمخاطر (3D BIM Risk Viewer)")
    st.markdown("<div class='en-subtext'>Interactive 3D Multi-Storey BIM Visualization with Spatial Risk & Clash Tagging</div>", unsafe_allow_html=True)
    
    elem_summary = active_meta.get("element_summary", {})
    if elem_summary:
        st.markdown(f"""
        <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:10px; padding:12px 18px; margin-bottom:14px; direction:rtl;">
            <span style="font-weight:700; color:#166534; font-size:0.95rem;">🏢 نموذج BIM المفعّل حالياً: {active_meta.get('name_ar')}</span>
            <div style="font-size:0.82rem; color:#475569; margin-top:3px;">
                تم حصر <b>{active_meta.get('total_elements', 0)}</b> عنصراً هندسياً موزعة على <b>{active_meta.get('storeys_count', 4)}</b> طوابق إنشائية.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        with col_b1:
            st.markdown(f"""
            <div class="kpi-card" style="padding:10px;">
                <div class="kpi-title" style="font-size:0.75rem;">🟢 الأساسات والقواعد</div>
                <div class="kpi-value" style="font-size:1.25rem; color:#059669;">{elem_summary.get('الأساسات والقواعد (Footings)', 0)} <span style="font-size:0.75rem; color:#64748B;">عنصر</span></div>
            </div>
            """, unsafe_allow_html=True)
        with col_b2:
            st.markdown(f"""
            <div class="kpi-card" style="padding:10px;">
                <div class="kpi-title" style="font-size:0.75rem;">⚪ الأعمدة الخرسانية</div>
                <div class="kpi-value" style="font-size:1.25rem; color:#475569;">{elem_summary.get('الأعمدة الخرسانية (Columns)', 0)} <span style="font-size:0.75rem; color:#64748B;">عمود</span></div>
            </div>
            """, unsafe_allow_html=True)
        with col_b3:
            st.markdown(f"""
            <div class="kpi-card" style="padding:10px;">
                <div class="kpi-title" style="font-size:0.75rem;">🔵 الجسور والأسقف</div>
                <div class="kpi-value" style="font-size:1.25rem; color:#2563EB;">{elem_summary.get('الجسور والأعتاب (Beams)', 0) + elem_summary.get('البلاطات والأسقف (Slabs)', 0)} <span style="font-size:0.75rem; color:#64748B;">عنصر</span></div>
            </div>
            """, unsafe_allow_html=True)
        with col_b4:
            st.markdown(f"""
            <div class="kpi-card" style="padding:10px;">
                <div class="kpi-title" style="font-size:0.75rem;">💨 شبكات MEP والتكييف</div>
                <div class="kpi-value" style="font-size:1.25rem; color:#D97706;">{elem_summary.get('دكتات التكييف (Ducts)', 0) + elem_summary.get('شبكات الأنابيب (Pipes)', 0)} <span style="font-size:0.75rem; color:#64748B;">مسار</span></div>
            </div>
            """, unsafe_allow_html=True)

    viewer_mode = st.radio(
        "🖥️ اختر نمط العرض ثلاثي الأبعاد:",
        options=[
            "🧊 1. عارض المجسمات المصمتة الحقيقي (WebGL 3D Solid BIM Model Viewer)",
            "🎨 2. النموذج التوليدي المعزز بطبقات المخاطر والتعارضات (Parametric Risk-Augmented Model)",
            "📍 3. سحابة النقاط والمواقع الفراغية لعناصر الـ IFC (Spatial Coordinates Point Cloud)"
        ],
        index=0,
        horizontal=True,
        key="bim_viewer_mode_choice"
    )

    if "🧊 1." in viewer_mode:
        st.markdown("<div style='margin-bottom:8px; font-size:0.85rem; color:#475569;'>💡 <b>عارض BIM WebGL تفاعلي كامل:</b> يدعم التحريك بالماوس، الدوران 360°، وضع الشفافية (X-Ray)، الهيكل الشبكي (Wireframe)، وإظهار خصائص أي عنصر بالنقر عليه المباشر.</div>", unsafe_allow_html=True)
        webgl_html = webgl_bim_viewer.render_webgl_ifc_viewer_html(
            spatial_elements=st.session_state.get("ifc_spatial_elements"),
            storeys_count=int(active_meta.get("storeys_count", 8)),
            element_summary=active_meta.get("element_summary"),
            coordination_issues=st.session_state.get("coordination_issues"),
            height=680
        )
        components.html(webgl_html, height=700)

    elif "🎨 2." in viewer_mode:
        # النمط 2: النموذج التوليدي المعزز بطبقات المخاطر
        col_3d_ctrl1, col_3d_ctrl2 = st.columns([1.1, 2.9])
        with col_3d_ctrl1:
            st.markdown("**🎮 أدوات التحكم بالنموذج التوليدي 3D:**")
            default_s = int(active_meta.get("storeys_count", 8 if active_meta.get("is_ifc_model") else 4))
            storeys_num = st.slider("عدد الطوابق المعروضة:", min_value=1, max_value=max(12, default_s), value=min(10, default_s), key="bim_storeys_slider")
            
            st.markdown("**🏗️ طبقات العناصر الهندسية (BIM Layers):**")
            lay_footing = st.checkbox("🟢 الأساسات والقواعد (Footings)", value=True, key="chk_lay_footing")
            lay_columns = st.checkbox("⚪ الأعمدة الخرسانية (Columns)", value=True, key="chk_lay_columns")
            lay_slabs = st.checkbox("🔵 البلاطات والجسور (Slabs & Beams)", value=True, key="chk_lay_slabs")
            lay_walls = st.checkbox("🧱 الجدران والقواطع (Walls)", value=True, key="chk_lay_walls")
            lay_mep = st.checkbox("💨 دكتات التكييف MEP (HVAC)", value=True, key="chk_lay_mep")
            show_clash_pts = st.checkbox("🔴 إبراز نقاط التعارض الحرج", value=True, key="chk_lay_clashes")

            st.markdown("""
            <div style="background:#F8FAFC; border-radius:8px; padding:10px; font-size:0.8rem; color:#475569; border:1px solid #CBD5E1; margin-top:10px;">
                <b>دليل التلوين ثلاثي الأبعاد:</b><br/>
                • 🟢 <b>الأخضر:</b> قواعد وسقوف سليمة<br/>
                • ⚪ <b>الرمادي:</b> أعمدة وهيكل خرساني<br/>
                • 🔵 <b>الأزرق:</b> بلاطات وجسور الطوابق<br/>
                • 🧱 <b>الرصاصي:</b> جدران وقواطع معمارية<br/>
                • 💨 <b>السماوي:</b> دكتات تكييف منسقة<br/>
                • 🔴 <b>الأحمر:</b> تعارضات حرجة (Clashes)
            </div>
            """, unsafe_allow_html=True)

        with col_3d_ctrl2:
            fig_3d = get_cached_3d_bim(
                storeys_count=storeys_num,
                show_footings=lay_footing,
                show_columns=lay_columns,
                show_slabs=lay_slabs,
                show_walls=lay_walls,
                show_mep=lay_mep,
                has_clashes=show_clash_pts
            )
            st.plotly_chart(fig_3d, use_container_width=True, key="plot_3d_bim_scatter")

    else:
        # النمط 3: سحابة النقاط والمواقع الفراغية
        if st.session_state.ifc_spatial_elements:
            col_raw_ctrl1, col_raw_ctrl2 = st.columns([1.1, 2.9])
            available_cats = sorted(list(set(el.get("category_ar", "أخرى") for el in st.session_state.ifc_spatial_elements)))
            
            with col_raw_ctrl1:
                st.markdown("**🎮 تخصصات وعناصر المودل الأصلي:**")
                selected_raw_cats = st.multiselect(
                    "اختر التخصصات المعروضة في المودل:",
                    options=available_cats,
                    default=available_cats,
                    key="raw_ifc_multisel_cats"
                )
                st.markdown(f"""
                <div style="background:#F8FAFC; border-radius:8px; padding:10px; font-size:0.8rem; color:#475569; border:1px solid #CBD5E1; margin-top:10px;">
                    <b>بيانات المودل الحقيقي:</b><br/>
                    • إجمالي العناصر المكانية: <b>{len(st.session_state.ifc_spatial_elements):,}</b> عنصر<br/>
                    • التخصصات المكتشفة: <b>{len(available_cats)}</b> تصنيف<br/>
                    • الدقة: <b>إحداثيات حقيقية من ملف الـ IFC</b>
                </div>
                """, unsafe_allow_html=True)

            with col_raw_ctrl2:
                fig_raw = bim_3d_viewer.create_raw_ifc_3d_model(st.session_state.ifc_spatial_elements, selected_raw_cats)
                st.plotly_chart(fig_raw, use_container_width=True, key="plot_3d_raw_scatter")
        else:
            st.info("💡 **سحابة النقاط والمواقع الفراغية:** يرجى رفع وتفعيل ملف نموذج الـ IFC من الصندوق أدناه لاستخراج الإحداثيات الهندسية وعرضها مباشرة.")

    # جدول تفاصيل العناصر المستوردة من الـ IFC
    if elem_summary:
        st.markdown("---")
        st.markdown("#### 📋 جدول حصر وتصنيف عناصر نموذج البناء المستورد (BIM Element Quantities):")
        el_rows = []
        for cat_name, cnt in elem_summary.items():
            el_rows.append({
                "التصنيف الإنشائي والمعماري": cat_name,
                "عدد العناصر في المودل": f"{cnt:,} عنصر",
                "الحالة الفنية": "✅ تم التحليل والربط بالـ WBS" if cnt > 0 else "⚪ غير متوفر في المودل"
            })
        render_centered_table(pd.DataFrame(el_rows))

    with st.expander("📥 استيراد نموذج IFC جديد وتفعيله مباشرة في العارض", expanded=not bool(elem_summary)):
        uploaded_ifc_direct = st.file_uploader("اختر ملف نموذج BIM (.ifc):", type=["ifc"], key="ifc_direct_uploader")
        if uploaded_ifc_direct is not None:
            ifc_res_d = ifc_parser.parse_ifc_file_bytes(uploaded_ifc_direct.getvalue(), uploaded_ifc_direct.name)
            if ifc_res_d.get("success"):
                st.success(f"🎉 تم تحليل نموذج IFC بنجاح: ({ifc_res_d['total_elements']} عنصر هندسي / {ifc_res_d['storey_count']} طوابق)")
                if st.button("🚀 تفعيل وعرض النموذج ثلاثي الأبعاد الآن", type="primary", key="btn_apply_ifc_direct", use_container_width=True):
                    load_clean_project_state(
                        meta=ifc_res_d["project_meta"],
                        activities=ifc_res_d["activities"],
                        coordination_issues=ifc_res_d.get("coordination_issues"),
                        spatial_elements=ifc_res_d.get("spatial_elements", []),
                        ifc_bytes=uploaded_ifc_direct.getvalue(),
                        ifc_filename=uploaded_ifc_direct.name,
                        source="CUSTOM",
                        success_msg=f"🎉 تم بنجاح تفعيل نموذج BIM: '{ifc_res_d['project_meta']['name_ar']}' (حصر {ifc_res_d['total_elements']} عنصر / {ifc_res_d['storey_count']} طوابق) وتحديث العارض!"
                    )
                    st.session_state.active_nav_tab = "🧊 عارض BIM 3D التفاعلي"
                    st.rerun()

# ----------------- TAB 9: WBS ACTIVITIES & P6 GANTT -----------------
elif selected_tab == "📅 مخطط جانت وبريمافيرا (Gantt)":
    st.markdown("### 📅 مخطط جانت الزمني والتدفق المالي المتزامن (Primavera P6 Gantt & Cash Flow)")
    st.markdown("<div class='en-subtext'>Interactive Gantt Timeline, CPM Critical Path & Synchronized Monthly Budget Distribution</div>", unsafe_allow_html=True)
    
    if st.session_state.activities:
        # استخراج تاريخ بداية المشروع الفعلي من بيانات ملف P6 أو أقرب نشاط
        valid_starts = [a["start_date"] for a in st.session_state.activities if a.get("start_date")]
        default_start_str = active_meta.get("project_start_date") or (min(valid_starts) if valid_starts else "2024-01-01")
        try:
            default_start_dt = datetime.strptime(str(default_start_str), "%Y-%m-%d")
        except Exception:
            default_start_dt = datetime(2024, 1, 1)

        col_g1, col_g2, col_g3, col_g4 = st.columns([1.5, 1.2, 1.2, 1.2])
        with col_g1:
            p_start_date = st.date_input(
                "📅 تاريخ بداية المشروع:",
                value=default_start_dt,
                key=f"gantt_start_date_{active_meta.get('id', 'proj')}"
            )
        
        cpm_sched = p6_gantt_visualizer.compute_cpm_schedule(st.session_state.activities, str(p_start_date))
        critical_count = sum(1 for s in cpm_sched if s["is_critical"])
        
        if cpm_sched:
            min_start = min(s["start_dt"] for s in cpm_sched)
            max_finish = max(s["finish_dt"] for s in cpm_sched)
            cpm_project_duration = max(1, (max_finish - min_start).days)
        else:
            cpm_project_duration = 0
            
        total_direct_cost = sum(s["cost"] for s in cpm_sched)

        with col_g2:
            st.markdown(f"""
            <div class="kpi-card" style="padding:10px; min-height:85px;">
                <div class="kpi-title" style="font-size:0.78rem;">⏳ مدة المسار الحرج CPM</div>
                <div class="kpi-value" style="font-size:1.3rem; color:#2563EB;">{cpm_project_duration} <span style="font-size:0.8rem; color:#64748B;">يوم</span></div>
            </div>
            """, unsafe_allow_html=True)

        with col_g3:
            st.markdown(f"""
            <div class="kpi-card" style="padding:10px; min-height:85px;">
                <div class="kpi-title" style="font-size:0.78rem;">🔴 الأنشطة الحرجة</div>
                <div class="kpi-value" style="font-size:1.3rem; color:#DC2626;">{critical_count} <span style="font-size:0.8rem; color:#64748B;">أنشطة</span></div>
            </div>
            """, unsafe_allow_html=True)

        with col_g4:
            st.markdown(f"""
            <div class="kpi-card" style="padding:10px; min-height:85px;">
                <div class="kpi-title" style="font-size:0.78rem;">💰 كلفة الأنشطة المباشرة</div>
                <div class="kpi-value" style="font-size:1.3rem; color:#D97706;">{total_direct_cost:,.0f} <span style="font-size:0.8rem; color:#64748B;">{curr_sym}</span></div>
            </div>
            """, unsafe_allow_html=True)

        chart_config = {
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f"P6_Gantt_{active_meta.get('id', 'proj')}",
                'height': 800,
                'width': 1400,
                'scale': 2
            },
            'displayModeBar': True
        }

        fig_p6_gantt = p6_gantt_visualizer.create_p6_gantt_chart(
            activities=st.session_state.activities,
            project_start_date=str(p_start_date),
            currency_symbol=curr_sym
        )
        st.plotly_chart(fig_p6_gantt, use_container_width=True, config=chart_config, key="plot_p6_gantt_chart")

        fig_p6_cashflow = p6_gantt_visualizer.create_p6_cashflow_chart(
            activities=st.session_state.activities,
            project_start_date=str(p_start_date),
            currency_symbol=curr_sym
        )
        st.plotly_chart(fig_p6_cashflow, use_container_width=True, config=chart_config, key="plot_p6_cashflow_chart")

        # 📤 شريط أزرار التصدير للصور والـ PDF
        st.markdown("##### 📤 خيارات تصدير الجدول الزمني والمخططات (Export Options):")
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            gantt_png_bytes = p6_gantt_visualizer.export_fig_to_png(fig_p6_gantt)
            if gantt_png_bytes:
                st.download_button(
                    label="🖼️ تنزيل مخطط جانت كصورة (PNG)",
                    data=gantt_png_bytes,
                    file_name=f"P6_Gantt_Timeline_{active_meta.get('id', 'Proj')}.png",
                    mime="image/png",
                    use_container_width=True
                )
            else:
                st.info("💡 يمكنك حفظ الصورة بالنقر على أيقونة الكاميرا 📷 أعلى المخطط.")
                
        with col_exp2:
            cashflow_png_bytes = p6_gantt_visualizer.export_fig_to_png(fig_p6_cashflow)
            if cashflow_png_bytes:
                st.download_button(
                    label="📊 تنزيل التدفق المالي كصورة (PNG)",
                    data=cashflow_png_bytes,
                    file_name=f"P6_Cash_Flow_{active_meta.get('id', 'Proj')}.png",
                    mime="image/png",
                    use_container_width=True
                )

        with col_exp3:
            p6_pdf_html = p6_gantt_visualizer.generate_p6_schedule_printable_html(
                meta=active_meta,
                cpm_sched=cpm_sched,
                currency_symbol=curr_sym
            )
            st.download_button(
                label="📄 تنزيل تقرير P6 للطباعة / PDF",
                data=p6_pdf_html,
                file_name=f"P6_Schedule_Report_{active_meta.get('id', 'Proj')}.html",
                mime="text/html",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("#### 📋 جدول تفاصيل هيكل تجزئة العمل والأنشطة (WBS Table)")
        
        # 🔍 شريط البحث والفلترة الذكي
        col_srch1, col_srch2, col_srch3 = st.columns([2.2, 1.3, 1.3])
        with col_srch1:
            wbs_search = st.text_input(
                "🔍 بحث سريع في الأنشطة:",
                placeholder="اكتب رمز النشاط أو اسمه بالعربية أو الإنجليزية...",
                key="wbs_search_query"
            )
        with col_srch2:
            wbs_path_filter = st.selectbox(
                "تصفية نوع المسار:",
                options=["جميع الأنشطة (All)", "🔴 المسار الحرج فقط (Critical)", "🔵 المسار الاعتيادي (Normal)"],
                key="wbs_path_filter_sel"
            )
        with col_srch3:
            wbs_sort_order = st.selectbox(
                "ترتيب الجدول حسب:",
                options=["الترتيب الافتراضي (الشبكي)", "الأطول مدة زمنية", "الأعلى تكلفة مباشرة", "أقرب تاريخ بدء"],
                key="wbs_sort_order_sel"
            )

        # تطبيق الفلترة
        filtered_sched = list(cpm_sched)
        if wbs_search:
            q = wbs_search.strip().lower()
            filtered_sched = [
                s for s in filtered_sched 
                if q in str(s.get("id", "")).lower() 
                or q in str(s.get("name_ar", "")).lower() 
                or q in str(s.get("name_en", "")).lower()
            ]

        if "المسار الحرج فقط" in wbs_path_filter:
            filtered_sched = [s for s in filtered_sched if s.get("is_critical")]
        elif "المسار الاعتيادي" in wbs_path_filter:
            filtered_sched = [s for s in filtered_sched if not s.get("is_critical")]

        # تطبيق الترتيب
        if wbs_sort_order == "الأطول مدة زمنية":
            filtered_sched.sort(key=lambda x: x.get("duration", 0), reverse=True)
        elif wbs_sort_order == "الأعلى تكلفة مباشرة":
            filtered_sched.sort(key=lambda x: x.get("cost", 0), reverse=True)
        elif wbs_sort_order == "أقرب تاريخ بدء":
            filtered_sched.sort(key=lambda x: x.get("start_dt"))

        st.markdown(
            f"<div style='margin-bottom:8px; font-size:0.85rem; color:#64748B;'>📊 عرض <b>{len(filtered_sched)}</b> من أصل <b>{len(cpm_sched)}</b> نشاط</div>",
            unsafe_allow_html=True
        )

        if filtered_sched:
            wbs_rows = []
            for a in filtered_sched:
                wbs_rows.append({
                    "رمز النشاط": a.get("id"),
                    "اسم النشاط الإنشائي": a.get("name_ar"),
                    "تاريخ البدء": a.get("start_date"),
                    "تاريخ الانتهاء": a.get("finish_date"),
                    "المدة (يوم)": a.get("duration"),
                    "السماحية (Float)": f"{a.get('total_float')} يوم",
                    "المسار": "🔴 حرج (Critical)" if a.get("is_critical") else "🔵 اعتيادي",
                    f"الكلفة المباشرة ({curr_sym})": f"{a.get('cost'):,.0f} {curr_sym}"
                })
            render_centered_table(pd.DataFrame(wbs_rows))
        else:
            st.warning(f"⚠️ لم يتم العثور على أي نشاط يطابق معايير البحث: '{wbs_search}'")
    else:
        st.info("💡 لا توجد أنشطة مسجلة حالياً لعرض مخطط جانت. يرجى إضافة أنشطة من النموذج أدناه أو استيراد جدول Primavera P6 / IFC.")

    st.markdown("---")
    st.markdown("#### ➕ إضافة نشاط إنشائي جديد (Add New Activity)")
    with st.expander("فتح نموذج إضافة نشاط جديد", expanded=False):
        with st.form("add_activity_form"):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                new_act_id = st.text_input("رمز النشاط (Activity ID):", value=f"ACT_{len(st.session_state.activities)+1:02d}")
                new_act_name_ar = st.text_input("اسم النشاط (بالعربية):", placeholder="مثال: أعمال صب الأساسات الحصيرة")
                new_act_name_en = st.text_input("اسم النشاط (بالإنجليزية):", placeholder="e.g. Concrete Raft Foundation")
                new_act_dist = st.selectbox("نوع التوزيع الاحتمالي:", ["PERT", "TRIANGULAR", "NORMAL", "UNIFORM"], index=0)

            with col_a2:
                st.markdown("**تقديرات المدة الزمنية (أيام):**")
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d1:
                    new_opt_d = st.number_input("متفائل (O):", min_value=1, value=15, step=1)
                with col_d2:
                    new_ml_d = st.number_input("الأرجح (M):", min_value=1, value=25, step=1)
                with col_d3:
                    new_pess_d = st.number_input("متشائم (P):", min_value=1, value=45, step=1)

                st.markdown(f"**تقديرات التكلفة المباشرة ({curr_sym}):**")
                col_c1, col_c2, col_c3 = st.columns(3)
                with col_c1:
                    new_opt_c = st.number_input("كلفة متفائلة:", min_value=0, value=500000, step=50000)
                with col_c2:
                    new_ml_c = st.number_input("كلفة الأرجح:", min_value=0, value=750000, step=50000)
                with col_c3:
                    new_pess_c = st.number_input("كلفة متشائمة:", min_value=0, value=1100000, step=50000)

            existing_ids = [a["id"] for a in st.session_state.activities]
            selected_preds = st.multiselect("الأنشطة السابقة:", options=existing_ids)

            submit_act = st.form_submit_button("💾 حفظ وإضافة النشاط للمشروع", use_container_width=True)

            if submit_act:
                if not new_act_name_ar:
                    st.error("يرجى إدخال اسم النشاط بالعربية!")
                elif new_opt_d > new_ml_d or new_pess_d < new_ml_d:
                    st.error("خطأ في التقديرات الزمنية: يجب أن يكون المتفائل ≤ الأرجح ≤ المتشائم!")
                elif new_act_id in existing_ids:
                    st.error("رمز النشاط مستخدم بالفعل! يرجى اختيار رمز آخر.")
                else:
                    new_activity_dict = {
                        "id": new_act_id,
                        "name_ar": new_act_name_ar,
                        "name_en": new_act_name_en or new_act_name_ar,
                        "duration_estimates": (int(new_opt_d), int(new_ml_d), int(new_pess_d)),
                        "cost_estimates": (float(new_opt_c), float(new_ml_c), float(new_pess_c)),
                        "dist_type": new_act_dist,
                        "cost_dist_type": new_act_dist,
                        "predecessors": selected_preds
                    }
                    st.session_state.activities.append(new_activity_dict)
                    st.success(f"تمت إضافة النشاط ({new_act_name_ar}) بنجاح وإعادة تشغيل المحاكاة!")
                    st.rerun()

    st.markdown("---")
    st.markdown("#### 🗑️ حذف وإدارة أنشطة المشروع (Delete Activities)")
    
    if st.session_state.activities:
        col_del1, col_del2 = st.columns(2)
        
        with col_del1:
            with st.expander("🗑️ حذف نشاط فردي محدد", expanded=True):
                act_to_del = st.selectbox(
                    "اختر النشاط المراد حذفه:",
                    options=existing_ids,
                    format_func=lambda x: f"{x} - {next((a['name_ar'] for a in st.session_state.activities if a['id']==x), '')}",
                    key="sb_act_single_del"
                )
                if st.button("🗑️ تأكيد حذف هذا النشاط", type="secondary", use_container_width=True, key="btn_confirm_single_del"):
                    st.session_state.activities = [a for a in st.session_state.activities if a["id"] != act_to_del]
                    for a in st.session_state.activities:
                        if act_to_del in a.get("predecessors", []):
                            a["predecessors"].remove(act_to_del)
                    st.success(f"تم بنجاح حذف النشاط ({act_to_del}) وتحديث شبكة الأنشطة!")
                    st.rerun()

        with col_del2:
            with st.expander("🗑️ حذف جماعي أو تفريغ كامل الأنشطة", expanded=True):
                bulk_acts_to_del = st.multiselect(
                    "اختر مجموعة أنشطة لحذفها معاً:",
                    options=existing_ids,
                    format_func=lambda x: f"{x} - {next((a['name_ar'] for a in st.session_state.activities if a['id']==x), '')}",
                    key="ms_act_bulk_del"
                )
                if st.button("🗑️ حذف الأنشطة المحددة", type="secondary", use_container_width=True, disabled=len(bulk_acts_to_del)==0):
                    st.session_state.activities = [a for a in st.session_state.activities if a["id"] not in bulk_acts_to_del]
                    for a in st.session_state.activities:
                        a["predecessors"] = [p for p in a.get("predecessors", []) if p not in bulk_acts_to_del]
                    st.success(f"تم بنجاح حذف {len(bulk_acts_to_del)} نشاطاً من المشروع!")
                    st.rerun()

                st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
                if st.button("⚠️ تفريغ ومسح كافة أنشطة WBS", type="secondary", use_container_width=True, key="btn_clear_all_wbs"):
                    st.session_state.activities = []
                    st.success("تم مسح وتفريغ كافة أنشطة المشروع بنجاح!")
                    st.rerun()
    else:
        st.info("💡 لا توجد أنشطة مسجلة حالياً في المشروع. يمكنك إضافة أنشطة جديدة من النموذج أعلاه أو استيراد جدول بريمافيرا / IFC.")

# ----------------- TAB 10: RISKS MANAGEMENT -----------------
elif selected_tab == "🛡️ مصفوفة المخاطر":
    st.markdown("### 🛡️ مصفوفة وسجل المخاطر المخصص للبيئة العراقية")
    st.markdown("<div class='en-subtext'>Iraqi Construction Risk Register & 5x5 Qualitative Matrix</div>", unsafe_allow_html=True)
    
    col_mat, col_stats = st.columns([1.65, 1.35])
    with col_mat:
        render_risk_matrix_html(st.session_state.risk_register)

    with col_stats:
        st.markdown("#### 📊 ملخص المخاطر المسجلة")
        high_cnt = sum(1 for r in st.session_state.risk_register if r["probability"] * r["impact"] >= 15)
        med_cnt = sum(1 for r in st.session_state.risk_register if 8 <= r["probability"] * r["impact"] < 15)
        low_cnt = sum(1 for r in st.session_state.risk_register if r["probability"] * r["impact"] < 8)

        st.markdown(f"""
        <div style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:10px; padding:12px 16px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; direction:rtl;">
            <span style="font-weight:700; color:#991B1B; font-size:0.92rem;">🔴 مخاطر عالية وحرجة (Score ≥ 15)</span>
            <b style="font-size:1.25rem; color:#DC2626; font-family:'Segoe UI', Tahoma, sans-serif; direction:ltr;">{high_cnt} مخاطر</b>
        </div>
        <div style="background:#FFFBEB; border:1px solid #FCD34D; border-radius:10px; padding:12px 16px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; direction:rtl;">
            <span style="font-weight:700; color:#92400E; font-size:0.92rem;">🟡 مخاطر متوسطة (Score 8 - 14)</span>
            <b style="font-size:1.25rem; color:#D97706; font-family:'Segoe UI', Tahoma, sans-serif; direction:ltr;">{med_cnt} مخاطر</b>
        </div>
        <div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:10px; padding:12px 16px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; direction:rtl;">
            <span style="font-weight:700; color:#166534; font-size:0.92rem;">🟢 مخاطر منخفضة (Score < 8)</span>
            <b style="font-size:1.25rem; color:#059669; font-family:'Segoe UI', Tahoma, sans-serif; direction:ltr;">{low_cnt} مخاطر</b>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📋 تفاصيل سجل المخاطر وخطط المعالجة الموقعية")
    risk_rows = []
    for r in st.session_state.risk_register:
        score = r["probability"] * r["impact"]
        lvl = iraqi_risk_db.get_risk_level(score)
        risk_rows.append({
            "كود الخطر": r["id"],
            "القطاع العراقي": iraqi_risk_db.RISK_CATEGORIES.get(r["category"], {}).get("name_ar", r["category"]),
            "عنوان الخطر": r["title_ar"],
            "الاحتمالية": r["probability"],
            "التأثير": r["impact"],
            "درجة الخطورة": score,
            "المستوى": f"{lvl['badge']} {lvl['level_ar']}",
            "تأخير متوقع": f"{r.get('schedule_delay_days', (0,0,0))[1]} يوم",
            "إجراء المعالجة الموصى به": r.get("mitigation_ar", "")
        })
    render_centered_table(pd.DataFrame(risk_rows))

# ----------------- TAB 11: IMPORT / EXPORT & GIS LOCATION -----------------
elif selected_tab == "🏢 استيراد (P6 / IFC / JSON)":
    st.markdown("### 🏢 مركز إعداد المشروع والموقع المكاني واستيراد النماذج المتعددة")
    st.markdown("<div class='en-subtext'>Project Setup, Interactive GIS Site Mapping (Satellite / Standard), Primavera P6, BIM IFC & Navisworks Ingestion Hub</div>", unsafe_allow_html=True)
    
    tab_setup_gis, tab_setup_meta, tab_setup_import = st.tabs([
        "🗺️ 1. الموقع المكاني وخريطة العراق (GIS Map)",
        "📝 2. البيانات التعاقدية للمشروع (Metadata)",
        "📥 3. استيراد النماذج والجداول (P6 / IFC / Navisworks / JSON)"
    ])

    # ------------------ SUB-TAB 1: GIS LOCATION & SATELLITE MAP ------------------
    with tab_setup_gis:
        st.markdown("#### 🗺️ تحديد موقع المشروع تفاعلياً بالماوس وتحليل المخاطر الجيوتقنية والمناخية")
        st.info("💡 **طريقة الاستخدام:** يمكنك تحريك زر الماوس والنقر في أي مكان داخل خريطة العراق أو سحب النجمة 🎯، وسيتم تحديث الإحداثيات وتعبئة الحقول وتحليل خواص التربة والمياه الجوفية والمناخ فوراً.")
        
        gov_keys = list(iraq_georisk_engine.IRAQ_GOVERNORATES_DB.keys())
        curr_gov = active_meta.get("governorate", "BAGHDAD")
        if curr_gov not in gov_keys:
            curr_gov = "BAGHDAD"

        # تطبيق أي إحداثيات أو محافظة قيد الانتظار (قبل استدعاء الـ Widgets)
        if "_pending_map_lat" in st.session_state and "_pending_map_lon" in st.session_state:
            p_lat = float(st.session_state.pop("_pending_map_lat"))
            p_lon = float(st.session_state.pop("_pending_map_lon"))
            st.session_state["gis_in_lat"] = p_lat
            st.session_state["gis_in_lon"] = p_lon
            p_gov, _ = iraq_georisk_engine.find_nearest_governorate(p_lat, p_lon)
            st.session_state["gis_gov_selector"] = p_gov
            st.session_state["_prev_sel_gov"] = p_gov
            curr_gov = p_gov

        if "_pending_gov_key" in st.session_state:
            p_gov = st.session_state.pop("_pending_gov_key")
            st.session_state["gis_gov_selector"] = p_gov
            st.session_state["_prev_sel_gov"] = p_gov
            curr_gov = p_gov

        # تهيئة حالة الإحداثيات في Session State
        if "gis_in_lat" not in st.session_state:
            st.session_state["gis_in_lat"] = float(active_meta.get("latitude") or iraq_georisk_engine.IRAQ_GOVERNORATES_DB[curr_gov]["lat"])
        if "gis_in_lon" not in st.session_state:
            st.session_state["gis_in_lon"] = float(active_meta.get("longitude") or iraq_georisk_engine.IRAQ_GOVERNORATES_DB[curr_gov]["lon"])

        col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1.6, 1.3, 1.0, 1.0])
        with col_ctrl1:
            gov_idx = gov_keys.index(curr_gov) if curr_gov in gov_keys else 0
            sel_gov = st.selectbox(
                "اختر المحافظة كمركز افتراضي:",
                options=gov_keys,
                format_func=lambda k: f"📍 {iraq_georisk_engine.IRAQ_GOVERNORATES_DB[k]['name_ar']} ({iraq_georisk_engine.IRAQ_GOVERNORATES_DB[k]['region_ar']})",
                index=gov_idx,
                key="gis_gov_selector"
            )
            # إذا قام المستخدم بتغيير القائمة المنسدلة يدوياً
            if sel_gov != st.session_state.get("_prev_sel_gov", curr_gov):
                st.session_state["_prev_sel_gov"] = sel_gov
                c_lat = float(iraq_georisk_engine.IRAQ_GOVERNORATES_DB[sel_gov]["lat"])
                c_lon = float(iraq_georisk_engine.IRAQ_GOVERNORATES_DB[sel_gov]["lon"])
                st.session_state["_pending_map_lat"] = c_lat
                st.session_state["_pending_map_lon"] = c_lon
                st.session_state["_pending_gov_key"] = sel_gov
                st.session_state.custom_project_meta["governorate"] = sel_gov
                st.session_state.custom_project_meta["latitude"] = c_lat
                st.session_state.custom_project_meta["longitude"] = c_lon
                st.rerun()
        
        with col_ctrl2:
            sel_map_style = st.radio(
                "الطبقة الافتراضية للخريطة:",
                options=["🛰️ أقمار صناعية (Satellite)", "🗺️ شوارع قياسية (OpenStreetMap)"],
                index=0,
                horizontal=True,
                key="gis_map_style_choice"
            )
            map_type_code = "SATELLITE" if "🛰️" in sel_map_style else "STANDARD"

        with col_ctrl3:
            in_lat = st.number_input("خط العرض (°N):", key="gis_in_lat", format="%.4f", step=0.005)

        with col_ctrl4:
            in_lon = st.number_input("خط الطول (°E):", key="gis_in_lon", format="%.4f", step=0.005)

        # الكشف التلقائي عن أقرب محافظة للإحداثيات الحالية
        detected_gov_key, dist_to_center = iraq_georisk_engine.find_nearest_governorate(in_lat, in_lon)
        prof = iraq_georisk_engine.get_governorate_profile(detected_gov_key)

        col_act_btn1, col_act_btn2 = st.columns([1.5, 1.0])
        with col_act_btn1:
            if st.button("📍 تطبيق وتثبيت الموقع الجغرافي المختار على المشروع", type="primary", use_container_width=True, key="btn_apply_gis_loc"):
                st.session_state.custom_project_meta.update({
                    "governorate": detected_gov_key,
                    "latitude": float(in_lat),
                    "longitude": float(in_lon)
                })
                st.session_state["_prev_sel_gov"] = detected_gov_key
                st.session_state["_pending_gov_key"] = detected_gov_key
                st.session_state.last_import_msg = f"🎉 تم بنجاح تثبيت موقع المشروع الميداني: {prof['name_ar']} ({in_lat:.4f}° N, {in_lon:.4f}° E)"
                st.rerun()
        with col_act_btn2:
            if st.button("🔄 محاذاة الإحداثيات لمركز " + iraq_georisk_engine.IRAQ_GOVERNORATES_DB[sel_gov]["name_ar"], type="secondary", use_container_width=True, key="btn_reset_center"):
                c_lat = float(iraq_georisk_engine.IRAQ_GOVERNORATES_DB[sel_gov]["lat"])
                c_lon = float(iraq_georisk_engine.IRAQ_GOVERNORATES_DB[sel_gov]["lon"])
                st.session_state["_pending_map_lat"] = c_lat
                st.session_state["_pending_map_lon"] = c_lon
                st.session_state["_pending_gov_key"] = sel_gov
                st.session_state.custom_project_meta["governorate"] = sel_gov
                st.session_state.custom_project_meta["latitude"] = c_lat
                st.session_state.custom_project_meta["longitude"] = c_lon
                st.session_state["_prev_sel_gov"] = sel_gov
                st.rerun()

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        # أزرار الانتقال السريع لمحافظات العراق الـ 18 (دائماً ظاهرة ونشطة لتغيير المحافظة والإحداثيات بنقرة واحدة)
        st.markdown("<div style='font-size:0.85rem; font-weight:800; color:#1E40AF; margin-bottom:4px;'>📌 اختيار سريع لمحافظات العراق الـ 18 (تحديث فوري لاسم المحافظة وخط العرض والطول):</div>", unsafe_allow_html=True)
        gov_cols = st.columns(6)
        for i, (g_k, g_v) in enumerate(iraq_georisk_engine.IRAQ_GOVERNORATES_DB.items()):
            col_i = gov_cols[i % 6]
            with col_i:
                is_active = (g_k == detected_gov_key)
                btn_label = f"⭐ {g_v['name_ar']}" if is_active else f"📍 {g_v['name_ar']}"
                btn_type = "primary" if is_active else "secondary"
                if st.button(btn_label, key=f"quick_gov_{g_k}", use_container_width=True, type=btn_type):
                    st.session_state["_pending_map_lat"] = float(g_v["lat"])
                    st.session_state["_pending_map_lon"] = float(g_v["lon"])
                    st.session_state["_pending_gov_key"] = g_k
                    st.session_state.custom_project_meta["governorate"] = g_k
                    st.session_state.custom_project_meta["latitude"] = float(g_v["lat"])
                    st.session_state.custom_project_meta["longitude"] = float(g_v["lon"])
                    st.session_state["_prev_sel_gov"] = g_k
                    st.session_state.last_import_msg = f"🎯 تم اختيار محافظة {g_v['name_ar']} وتحديث الإحداثيات ({float(g_v['lat']):.4f}° N, {float(g_v['lon']):.4f}° E)"
                    st.rerun()

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        
        col_gis_left, col_gis_right = st.columns([1.65, 1.0])
        with col_gis_left:
            # خريطة العراق التفاعلية بالأقمار الصناعية مع التقاط النقرات وأزرار الاعتماد الفورية
            map_response = iraq_georisk_engine.render_interactive_map(
                selected_gov_key=detected_gov_key,
                project_lat=in_lat,
                project_lon=in_lon,
                initial_map_type=map_type_code,
                key="iraq_interactive_leaflet_map"
            )
            
            # التقاط ضغط أزرار الاعتماد «اعتماد الإحداثيات فوراً في الحقول» أو «اعتماد هذا الموقع»
            if map_response and isinstance(map_response, dict) and "lat" in map_response and "lon" in map_response:
                c_lat = round(float(map_response["lat"]), 4)
                c_lon = round(float(map_response["lon"]), 4)
                curr_lat = round(float(st.session_state.get("gis_in_lat", in_lat)), 4)
                curr_lon = round(float(st.session_state.get("gis_in_lon", in_lon)), 4)
                map_ts = map_response.get("timestamp")
                if abs(c_lat - curr_lat) > 0.0001 or abs(c_lon - curr_lon) > 0.0001 or map_ts != st.session_state.get("_last_map_ts"):
                    st.session_state["_last_map_ts"] = map_ts
                    nearest_k = map_response.get("govKey") or iraq_georisk_engine.find_nearest_governorate(c_lat, c_lon)[0]
                    st.session_state["_pending_map_lat"] = c_lat
                    st.session_state["_pending_map_lon"] = c_lon
                    st.session_state["_pending_gov_key"] = nearest_k
                    st.session_state.custom_project_meta["latitude"] = c_lat
                    st.session_state.custom_project_meta["longitude"] = c_lon
                    st.session_state.custom_project_meta["governorate"] = nearest_k
                    st.session_state["_prev_sel_gov"] = nearest_k
                    st.session_state.last_import_msg = f"🎯 تم بنجاح اعتماد إحداثيات الموقع وتحديث الحقول: ({c_lat:.4f}° N, {c_lon:.4f}° E) — أقرب محافظة: {iraq_georisk_engine.IRAQ_GOVERNORATES_DB[nearest_k]['name_ar']}"
                    st.rerun()



        with col_gis_right:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:12px; padding:18px; box-shadow:0 3px 12px rgba(0,0,0,0.05); direction:rtl; text-align:right;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #E2E8F0; padding-bottom:10px; margin-bottom:12px;">
                    <div>
                        <span style="font-weight:800; font-size:1.1rem; color:#0F172A;">📍 محافظة {prof['name_ar']}</span>
                        <div style="font-size:0.75rem; color:#64748B;">المسافة من المركز: {dist_to_center:.1f} كم</div>
                    </div>
                    <span style="background:#EFF6FF; color:#1E40AF; padding:3px 10px; border-radius:6px; font-size:0.8rem; font-weight:700;">{prof['region_ar']}</span>
                </div>
                <div style="margin-bottom:12px; background:#FEF2F2; border:1px solid #FCA5A5; border-radius:8px; padding:8px 12px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.85rem; color:#991B1B; font-weight:700;">مؤشر الخطورة المكانية:</span>
                    <b style="font-size:1.15rem; color:#DC2626;">{prof['overall_geo_risk_score']}/100</b>
                </div>
                <div style="font-size:0.86rem; line-height:1.75; color:#1E293B;">
                    <b>💧 المياه الجوفية:</b> {prof['groundwater_depth_m']} م ({prof['salinity_badge']})<br>
                    <b>🧱 طبيعة التربة:</b> {prof['soil_type_ar']}<br>
                    <b>🌡️ الإجهاد الحراري صيفاً:</b> {prof['summer_heat_index']}% (تأثير >50°C)<br>
                    <b>🌪️ العواصف الترابية:</b> {prof['sandstorm_days_year']} يوم/سنة<br>
                    <b>🚧 مخاطر القطوعات المرورية:</b> {prof['traffic_closure_risk']}<br>
                    <b>⛏️ مصادر المقالع والحصى:</b> {prof['quarry_source_ar']}<br>
                    <b>🚢 البعد عن ميناء أم قصر:</b> {prof['port_distance_km']} كم<br>
                    <b>🏗️ التوصية الإنشائية:</b> <span style="color:#0284C7; font-weight:700;">{prof['foundation_recommendation_ar']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("⚡ حقن وتحديث المخاطر المكانية في مصفوفة ISO 31000", type="primary", use_container_width=True, key="btn_inject_geo_risks_tab11"):
                injected_risks = iraq_georisk_engine.generate_spatial_iso_risks(detected_gov_key)
                existing_ids = [r["id"] for r in st.session_state.risk_register]
                added_cnt = 0
                for ir in injected_risks:
                    if ir["id"] not in existing_ids:
                        st.session_state.risk_register.append(ir)
                        added_cnt += 1
                if added_cnt > 0:
                    st.session_state.last_import_msg = f"🎉 تم بنجاح حقن {added_cnt} مخاطر جيوتقنية ومناخية خاصة بـ {prof['name_ar']} في مصفوفة المخاطر ومحاكي مونت كارلو!"
                else:
                    st.session_state.last_import_msg = f"💡 المخاطر المكانية لمحافظة {prof['name_ar']} مسجلة ومفعلة بالفعل في مصفوفة المخاطر!"
                st.rerun()

    # ------------------ SUB-TAB 2: CONTRACTUAL METADATA ------------------
    with tab_setup_meta:
        st.markdown("#### 📝 إدخال وتعديل البيانات التعاقدية والإدارية للمشروع")
        with st.form("custom_project_meta_form_full"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                p_name_ar = st.text_input("اسم المشروع (بالعربية):", value=st.session_state.custom_project_meta.get("name_ar", "مشروع إنشائي جديد"))
                p_client_ar = st.text_input("الجهة المستفيدة / رب العمل:", value=st.session_state.custom_project_meta.get("client_type_ar", "الجهة المستفيدة / صاحب العمل"))
                p_location_ar = st.text_input("العنوان والموقع الإنشائي الميداني:", value=st.session_state.custom_project_meta.get("location_ar", "بغداد - العراق"))
                p_currency = st.selectbox("عملة المشروع المعتمدة:", ["USD", "IQD"], index=0 if st.session_state.custom_project_meta.get("currency") == "USD" else 1)

            with col_m2:
                p_cost = st.number_input("مبلغ العقد الإجمالي المعتمد:", min_value=0.0, value=float(st.session_state.custom_project_meta.get("contract_original_cost", 0.0)), step=100000.0)
                p_duration = st.number_input("مدة العقد الأصلية المعتمدة (أيام العمل):", min_value=0, value=int(st.session_state.custom_project_meta.get("contract_original_duration_days", 0)), step=10)
                p_overhead = st.number_input("المصاريف الإدارية اليومية غير المباشرة للموقع ($/يوم):", min_value=0.0, value=float(st.session_state.custom_project_meta.get("daily_overhead_usd", 0.0)), step=100.0)
                p_id = st.text_input("رمز أو رقم العقد الرسمي:", value=st.session_state.custom_project_meta.get("id", "PROJ_IRQ_2026"))

            submit_meta = st.form_submit_button("💾 حفظ وتحديث بيانات المشروع التعاقدية", type="primary", use_container_width=True)
            if submit_meta:
                st.session_state.custom_project_meta.update({
                    "id": p_id,
                    "name_ar": p_name_ar,
                    "name_en": p_name_ar,
                    "client_type_ar": p_client_ar,
                    "location_ar": p_location_ar,
                    "currency": p_currency,
                    "currency_symbol": "$" if p_currency == "USD" else "د.ع",
                    "contract_original_cost": float(p_cost),
                    "contract_original_duration_days": int(p_duration),
                    "daily_overhead_usd": float(p_overhead)
                })
                st.session_state.project_source = "CUSTOM"
                st.session_state.last_import_msg = f"🎉 تم بنجاح حفظ وتحديث بيانات المشروع: '{p_name_ar}'!"
                st.rerun()

    # ------------------ SUB-TAB 3: MULTI-SOURCE INGESTION HUB ------------------
    with tab_setup_import:
        st.markdown("#### 📥 مركز استيراد الجداول والنماذج والتعارضات والنسخ الاحتياطي:")
        st.markdown("<div style='font-size:0.85rem; color:#64748B; margin-bottom:16px;'>استيراد وتحديث كافة مصادر البيانات الهندسية في مسار متناسق موحد أفقياً:</div>", unsafe_allow_html=True)
        
        col_imp_p6, col_imp_ifc, col_imp_navis, col_imp_json = st.columns(4)

        with col_imp_p6:
            st.markdown("""
            <div style="background:linear-gradient(135deg, #1E40AF, #1D4ED8); color:#FFFFFF; border-radius:10px 10px 0 0; padding:10px 12px; text-align:center; font-weight:800; font-size:0.95rem;">
                1️⃣ جدول بريمافيرا (P6 XER)
            </div>
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 10px 10px; padding:12px; height:84px; font-size:0.82rem; color:#475569; line-height:1.5; text-align:right; margin-bottom:12px;">
                استيراد شبكة الأنشطة والمدد الأصلية والعلاقات المنطقية من ملف <code>.xer</code> مع تصفية البيانات القديمة.
            </div>
            """, unsafe_allow_html=True)
            uploaded_p6 = st.file_uploader("اختر ملف بريمافيرا (.xer):", type=["xer"], key="p6_file_uploader")
            if uploaded_p6 is not None:
                p6_res = p6_parser.parse_p6_file_bytes(uploaded_p6.getvalue(), uploaded_p6.name)
                if p6_res.get("success"):
                    st.success(f"تمت قراءة جدول بريمافيرا: ({p6_res['activities_count']} نشاط)")
                    if st.button("🚀 تفعيل جدول بريمافيرا", type="primary", key="btn_apply_p6", use_container_width=True):
                        load_clean_project_state(
                            meta=p6_res["project_meta"],
                            activities=p6_res["activities"],
                            source="CUSTOM",
                            success_msg=f"🎉 تم بنجاح استيراد وتفعيل جدول بريمافيرا P6: '{p6_res['project_meta']['name_ar']}' وتصفية البيانات السابقة!"
                        )
                        st.rerun()

        with col_imp_ifc:
            st.markdown("""
            <div style="background:linear-gradient(135deg, #0284C7, #0369A1); color:#FFFFFF; border-radius:10px 10px 0 0; padding:10px 12px; text-align:center; font-weight:800; font-size:0.95rem;">
                2️⃣ نموذج البناء (BIM IFC)
            </div>
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 10px 10px; padding:12px; height:84px; font-size:0.82rem; color:#475569; line-height:1.5; text-align:right; margin-bottom:12px;">
                حصر العناصر وتوليد أنشطة WBS وتعادل التنسيق ISO 31000 من ملف <code>.ifc</code> الهندسي.
            </div>
            """, unsafe_allow_html=True)
            uploaded_ifc = st.file_uploader("اختر ملف نموذج BIM (.ifc):", type=["ifc"], key="ifc_file_uploader_tab")
            if uploaded_ifc is not None:
                ifc_res = ifc_parser.parse_ifc_file_bytes(uploaded_ifc.getvalue(), uploaded_ifc.name)
                if ifc_res.get("success"):
                    st.success(f"تم تحليل نموذج IFC: ({ifc_res['total_elements']} عنصر)")
                    if st.button("🚀 تفعيل بيانات نموذج IFC", type="primary", key="btn_apply_ifc", use_container_width=True):
                        load_clean_project_state(
                            meta=ifc_res["project_meta"],
                            activities=ifc_res["activities"],
                            coordination_issues=ifc_res.get("coordination_issues"),
                            spatial_elements=ifc_res.get("spatial_elements", []),
                            ifc_bytes=uploaded_ifc.getvalue(),
                            ifc_filename=uploaded_ifc.name,
                            source="CUSTOM",
                            success_msg=f"🎉 تم بنجاح استيراد وتفعيل نموذج IFC: '{ifc_res['project_meta']['name_ar']}' وتصفية البيانات السابقة!"
                        )
                        st.rerun()

        with col_imp_navis:
            st.markdown("""
            <div style="background:linear-gradient(135deg, #D97706, #B45309); color:#FFFFFF; border-radius:10px 10px 0 0; padding:10px 12px; text-align:center; font-weight:800; font-size:0.95rem;">
                3️⃣ تعارضات نافيسووركس
            </div>
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 10px 10px; padding:12px; height:84px; font-size:0.82rem; color:#475569; line-height:1.5; text-align:right; margin-bottom:12px;">
                استيراد تقارير Clash Detective وترجمتها آلياً لمخاطر وتأخيرات تعاقدية ISO 31000.
            </div>
            """, unsafe_allow_html=True)
            uploaded_navis = st.file_uploader("اختر تقرير تعارضات (.xml / .csv):", type=["xml", "csv"], key="navis_file_uploader_tab")
            if uploaded_navis is not None:
                navis_res = navisworks_parser.parse_navisworks_clash_bytes(uploaded_navis.getvalue(), uploaded_navis.name)
                if navis_res.get("success"):
                    st.success(f"✅ تم بنجاح قراءة وتحليل كافة الـ {navis_res['total_clashes']:,} تعارض بالكامل ({navis_res['critical_clashes_count']:,} حرج)!")
                    if st.button("🚀 دمج تعارضات Navisworks", type="primary", key="btn_apply_navis_tab11", use_container_width=True):
                        st.session_state.coordination_issues = navis_res["coordination_issues"]
                        st.session_state.last_import_msg = f"🎉 تم بنجاح استيراد وتفعيل كافة الـ {navis_res['total_clashes']:,} تعارض بالكامل في مصفوفة ISO 31000!"
                        st.rerun()

        with col_imp_json:
            st.markdown("""
            <div style="background:linear-gradient(135deg, #059669, #047857); color:#FFFFFF; border-radius:10px 10px 0 0; padding:10px 12px; text-align:center; font-weight:800; font-size:0.95rem;">
                4️⃣ استيراد واستعادة JSON الذكي
            </div>
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-top:none; border-radius:0 0 10px 10px; padding:12px; height:84px; font-size:0.82rem; color:#475569; line-height:1.5; text-align:right; margin-bottom:12px;">
                استعادة كامل بيانات المشروع، أو استيراد تذاكر OpenBIM BCF، أو جداول الأنشطة وسجلات المخاطر بصيغة <code>.json</code>.
            </div>
            """, unsafe_allow_html=True)
            uploaded_json = st.file_uploader("اختر ملف JSON (.json):", type=["json"], key="json_file_uploader_tab")
            if uploaded_json is not None:
                try:
                    loaded_data = json.load(uploaded_json)
                    res_tab = process_universal_json_upload(loaded_data, uploaded_json.name)
                    if res_tab["success"]:
                        st.success(f"✅ {res_tab['title']}")
                        st.markdown(f"<div style='font-size:0.82rem; color:#475569; margin-bottom:6px;'>💡 {res_tab['msg']}</div>", unsafe_allow_html=True)
                        if st.button("🚀 استعادة وتفعيل بيانات JSON", type="primary", key="btn_apply_json_tab11", use_container_width=True):
                            if res_tab["type"] in ["FULL_PROJECT", "ACTIVITIES_LIST"]:
                                load_clean_project_state(
                                    meta=res_tab.get("meta", st.session_state.custom_project_meta),
                                    activities=res_tab.get("activities", []),
                                    risks=res_tab.get("risks"),
                                    coordination_issues=res_tab.get("coordination_issues"),
                                    delay_events=res_tab.get("delay_events"),
                                    source="CUSTOM",
                                    success_msg=f"🎉 تم بنجاح استيراد وتفعيل {res_tab['title']} وتحديث مخرجات المنصة!"
                                )
                            elif res_tab["type"] == "BCF_TOPICS":
                                st.session_state.coordination_issues = res_tab["coordination_issues"]
                                st.session_state.last_import_msg = f"🎉 تم بنجاح استيراد وتفعيل {len(res_tab['coordination_issues'])} تذكرة تنسيق BCF وتحديث مصفوفة ISO 31000!"
                            elif res_tab["type"] == "RISKS_LIST":
                                st.session_state.risk_register = res_tab["risks"]
                                st.session_state.last_import_msg = f"🎉 تم بنجاح استيراد وتحديث {len(res_tab['risks'])} بند خطر في سجل المخاطر!"
                            st.rerun()
                    else:
                        st.error(res_tab["error"])
                except Exception as e:
                    st.error(f"خطأ في قراءة ملف JSON: {e}")

            # زر تنزيل النسخة الاحتياطية أسفل البطاقة
            full_proj_dump = {
                "meta": active_meta,
                "activities": st.session_state.activities,
                "risks": st.session_state.risk_register,
                "coordination_issues": st.session_state.coordination_issues,
                "delay_events": st.session_state.delay_events
            }
            dump_json = json.dumps(full_proj_dump, ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 تنزيل نسخة JSON الحالية",
                data=dump_json,
                file_name=f"Project_{active_meta.get('id', 'Custom')}_Backup.json",
                mime="application/json",
                use_container_width=True,
                key="btn_download_json_hub"
            )

# ----------------- TAB 12: EXECUTIVE REPORTING & PDF -----------------
elif selected_tab == "📄 التقرير والتصدير":
    st.markdown("### 📄 التقارير التنفيذية الرسمية والتصدير (Executive Reports & PDF Brief)")
    st.markdown("<div class='en-subtext'>Official Executive Briefing, Multi-Page Markdown Report & CSV Datasets</div>", unsafe_allow_html=True)
    
    # حساب بيانات المطالبات والتنسيق للتقرير
    eot_calc_res = get_cached_eot_claims(
        delay_events=st.session_state.delay_events,
        duration_days=int(active_meta.get("contract_original_duration_days", 450)),
        cost=float(active_meta.get("contract_original_cost", 12500000.0)),
        overhead=float(active_meta.get("daily_overhead_usd", 3500.0)),
        fine_mult=0.10,
        curr_sym=curr_sym
    )
    coord_summary = iso31000_coordination.compute_coordination_summary(st.session_state.coordination_issues)

    col_rep1, col_rep2, col_rep3, col_rep4 = st.columns(4)
    
    exec_brief_html = bim_3d_viewer.generate_executive_brief_html(
        project_meta=active_meta,
        sim_results=sim_res,
        isrs_data=isrs_result,
        eot_data=eot_calc_res,
        coordination_summary=coord_summary
    )

    with col_rep1:
        st.download_button(
            label="🏛️ تنزيل الإيجاز التنفيذي (HTML / PDF)",
            data=exec_brief_html,
            file_name=f"Executive_Brief_{active_meta.get('id', 'PROJ')}.html",
            mime="text/html",
            use_container_width=True
        )

    report_md = report_generator.generate_markdown_report(
        project_meta=active_meta,
        simulation_results=sim_res,
        isrs_data=isrs_result,
        risk_register=st.session_state.risk_register,
        activities=st.session_state.activities,
        coordination_issues=st.session_state.coordination_issues
    )

    with col_rep2:
        st.download_button(
            label="📥 تحميل التقرير الكامل (MD)",
            data=report_md,
            file_name=f"ICRAT_Report_{active_meta.get('id', 'PROJ')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col_rep3:
        activities_csv = report_generator.export_activities_csv(st.session_state.activities)
        st.download_button(
            label="📊 جدول الأنشطة (CSV)",
            data=activities_csv,
            file_name=f"WBS_Activities_{active_meta.get('id', 'PROJ')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_rep4:
        coord_csv = report_generator.export_coordination_csv(st.session_state.coordination_issues)
        st.download_button(
            label="🧩 سجل التنسيق ISO 31000 (CSV)",
            data=coord_csv,
            file_name=f"ISO31000_Coordination_{active_meta.get('id', 'PROJ')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown("#### 👁️ معاينة الإيجاز التنفيذي المخصص للطباعة والعرض الوزاري:")
    st.components.v1.html(exec_brief_html, height=520, scrolling=True)

    st.markdown("---")
    st.markdown("### 📚 معجم المصطلحات الهندسية والتعاقدية المعتمدة (ICRAT Glossary)")
    st.markdown("<div class='en-subtext'>Standardized Engineering, BIM, QSRA, and FIDIC Terminologies & Definitions</div>", unsafe_allow_html=True)

    col_g_search, col_g_cat = st.columns([2, 1])
    with col_g_search:
        search_query_tab12 = st.text_input("🔍 ابحث في معجم المصطلحات (بالعربية أو الإنجليزية):", placeholder="مثال: EOT, BIM, Float, فيديك, المسار الحرج...", key="tab12_glossary_search")
    with col_g_cat:
        cat_filter_tab12 = st.selectbox(
            "تصفية حسب المجال الهندسي:",
            options=list(glossary_data.GLOSSARY_CATEGORIES.keys()),
            format_func=lambda x: glossary_data.GLOSSARY_CATEGORIES[x],
            key="tab12_glossary_cat"
        )

    glossary_items = glossary_data.search_glossary(query=search_query_tab12, category=cat_filter_tab12)
    st.markdown(f"<div style='font-size:0.85rem; color:#475569; margin-bottom:14px;'>إجمالي المصطلحات المطابقة: <b>{len(glossary_items)}</b> مصطلح</div>", unsafe_allow_html=True)

    # عرض بطاقات المصطلحات
    for g_item in glossary_items:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 18px; margin-bottom:10px; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>
                    <span style="font-size:1.1rem; font-weight:800; color:#1D4ED8; font-family:'Segoe UI', Tahoma, sans-serif;">{g_item['term_en']}</span>
                    <span style="font-size:0.85rem; color:#64748B; margin-right:8px;">({g_item['full_en']})</span>
                </div>
                <span style="background:#EFF6FF; color:#1E40AF; border:1px solid #BFDBFE; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:20px;">
                    {g_item['category_ar']}
                </span>
            </div>
            <div style="font-size:0.95rem; font-weight:700; color:#0F172A; margin:6px 0 4px 0;">
                🏷️ {g_item['term_ar']}
            </div>
            <div style="font-size:0.85rem; color:#334155; line-height:1.6;">
                {g_item['definition_ar']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----------------- GLOBAL FOOTER (ALL PAGES) -----------------
st.markdown("""
<div style="text-align:center; padding: 28px 10px 35px 10px; margin-top: 40px; border-top: 2px solid #E2E8F0; direction: ltr;">
    <div style="font-size: 1.05rem; font-weight: 700; color: #1E293B; letter-spacing: 0.3px; margin-bottom: 6px;">
        Designed and developed by <span style="color: #2563EB;">Dr Ahmed Louay Ahmed</span>
    </div>
    <div style="font-size: 0.82rem; color: #64748B; direction: rtl;">
        Iraqi Construction Risk Assessment & Decision Support Platform (ICRAT 2.0) • متوافق مع معيار إدارة المخاطر الدولي ISO 31000:2018 والشروط العامة لمقاولات أعمال الهندسة المدنية
    </div>
</div>
""", unsafe_allow_html=True)
