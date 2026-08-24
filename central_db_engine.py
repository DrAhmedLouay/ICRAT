# -*- coding: utf-8 -*-
"""
===============================================================================
🏗️ ICRAT 2.0 - Central Cloud Database & Multi-User Collaboration Engine
===============================================================================
وحدة إدارة قاعدة البيانات المركزية، العمل التشاركي متعدد المستخدمين،
سجل التدقيق الحي (Audit Trail)، ونظام الصلاحيات والأدوار الهندسية (RBAC).

المؤلف: Dr Ahmed Louay Ahmed
الترخيص: ISO 31000:2018 & Iraqi Standard Construction Contracts Compliant
===============================================================================
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# ----------------- 🔒 ROLES & PERMISSIONS MATRIX -----------------
ROLES_METADATA = {
    "ADMIN": {
        "title_ar": "👑 مدير النظام والـ PMO الرئيسي",
        "badge_color": "#1E3A8A",
        "text_color": "#DBEAFE",
        "description_ar": "صلاحيات كاملة لإدارة المشاريع والمستخدمين والصلاحيات والاعتمادات الرسمية."
    },
    "RISK_MANAGER": {
        "title_ar": "🛡️ مدير المخاطر ومحاكاة QSRA",
        "badge_color": "#7C2D12",
        "text_color": "#FFEDD5",
        "description_ar": "تحديث سجل المخاطر الـ 102، تشغيل محاكاة مونت كارلو، وتحديد تدابير الاستجابة."
    },
    "BIM_COORDINATOR": {
        "title_ar": "📐 منسق النمذجة وتعارضات BIM",
        "badge_color": "#0369A1",
        "text_color": "#E0F2FE",
        "description_ar": "استيراد نماذج IFC وملفات Navisworks، ربط التعارضات بـ ISO 31000 وإصدار تذاكر BCF."
    },
    "PLANNER": {
        "title_ar": "📅 مهندس التخطيط والبريمافيرا (P6)",
        "badge_color": "#15803D",
        "text_color": "#DCFCE7",
        "description_ar": "استيراد جداول Primavera P6 (.xer)، إدارة شبكة الأنشطة والمسار الحرج والفائض الزمني."
    },
    "CONTRACTS_EXPERT": {
        "title_ar": "⚖️ مستشار العقود ومطالبات FIDIC",
        "badge_color": "#4C1D95",
        "text_color": "#F3E8FF",
        "description_ar": "تسجيل أحداث التأخير، متابعة الشروط العامة للمقاولات ومطالبات التمديد EOT."
    },
    "VIEWER": {
        "title_ar": "👁️ استشاري / مدقق / جهة إشرافية",
        "badge_color": "#334155",
        "text_color": "#F1F5F9",
        "description_ar": "معاينة واطلاع فقط على لوحة القيادة ومنحنيات S-Curve والتقارير التنفيذية دون تعديل."
    }
}

PERMISSIONS_MAP = {
    "can_manage_users": ["ADMIN"],
    "can_delete_project": ["ADMIN"],
    "can_save_cloud": ["ADMIN", "RISK_MANAGER", "BIM_COORDINATOR", "PLANNER", "CONTRACTS_EXPERT"],
    "can_edit_risks": ["ADMIN", "RISK_MANAGER"],
    "can_edit_bim": ["ADMIN", "BIM_COORDINATOR"],
    "can_edit_wbs": ["ADMIN", "PLANNER"],
    "can_edit_claims": ["ADMIN", "CONTRACTS_EXPERT"],
    "can_run_simulation": ["ADMIN", "RISK_MANAGER", "PLANNER", "BIM_COORDINATOR"],
    "can_export_reports": ["ADMIN", "RISK_MANAGER", "BIM_COORDINATOR", "PLANNER", "CONTRACTS_EXPERT", "VIEWER"],
    "can_view_all": ["ADMIN", "RISK_MANAGER", "BIM_COORDINATOR", "PLANNER", "CONTRACTS_EXPERT", "VIEWER"]
}

# المستخدمون الافتراضيون للمنصة مع أدوارهم الهندسية
DEFAULT_ACCOUNTS = {
    "admin": {
        "password_hash": "ICRAT2026@Secure",
        "role": "ADMIN",
        "full_name_ar": "مدير النظام والـ PMO",
        "email": "admin@icrat.iq"
    },
    "drahmed": {
        "password_hash": "IraqRisk#2026",
        "role": "ADMIN",
        "full_name_ar": "د. أحمد لؤي أحمد",
        "email": "drahmed@icrat.iq"
    },
    "engineer": {
        "password_hash": "Bim@2026",
        "role": "BIM_COORDINATOR",
        "full_name_ar": "م. أحمد الكعبي (BIM Lead)",
        "email": "bim.lead@icrat.iq"
    },
    "ruba": {
        "password_hash": "Ruba@2026",
        "role": "RISK_MANAGER",
        "full_name_ar": "م. ربى السعدي (Risk Specialist)",
        "email": "ruba.risk@icrat.iq"
    },
    "planner": {
        "password_hash": "Plan@2026",
        "role": "PLANNER",
        "full_name_ar": "م. مهندس التخطيط (P6 Lead)",
        "email": "planner@icrat.iq"
    },
    "contracts": {
        "password_hash": "Fidic@2026",
        "role": "CONTRACTS_EXPERT",
        "full_name_ar": "مستشار العقود وفيديك",
        "email": "contracts@icrat.iq"
    },
    "viewer": {
        "password_hash": "View@2026",
        "role": "VIEWER",
        "full_name_ar": "جهة المتابعة والتدقيق الوزاري",
        "email": "viewer@ministry.iq"
    }
}

# مسار قاعدة البيانات المحلية المركزية
DB_DIR = os.path.join(os.path.dirname(__file__), ".icrat_central_db")
DB_FILE = os.path.join(DB_DIR, "icrat_master_cloud.sqlite3")

def _get_db_connection() -> sqlite3.Connection:
    """إنشاء اتصال آمن بقاعدة البيانات المركزية مع دعم التهيئة التلقائية"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=15.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_central_database():
    """تهيئة جداول قاعدة البيانات المركزية وفهارس الأداء"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    # 1. جدول المشاريع المركزية
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS icrat_cloud_projects (
        project_id TEXT PRIMARY KEY,
        name_ar TEXT NOT NULL,
        governorate TEXT NOT NULL,
        client_ar TEXT,
        contractor_ar TEXT,
        contract_cost REAL DEFAULT 0,
        contract_duration INTEGER DEFAULT 0,
        currency_symbol TEXT DEFAULT '$',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        created_by TEXT NOT NULL,
        updated_by TEXT NOT NULL,
        version_id INTEGER DEFAULT 1,
        activities_count INTEGER DEFAULT 0,
        risks_count INTEGER DEFAULT 0,
        clashes_count INTEGER DEFAULT 0,
        claims_count INTEGER DEFAULT 0,
        snapshot_json TEXT NOT NULL
    )
    """)

    # 2. جدول المستخدمين والصلاحيات (RBAC)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS icrat_users (
        username TEXT PRIMARY KEY,
        password_plain TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name_ar TEXT NOT NULL,
        email TEXT,
        created_at TEXT NOT NULL,
        last_login_at TEXT
    )
    """)

    # 3. جدول سجل التدقيق المباشر (Audit Log)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS icrat_audit_trail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT,
        username TEXT NOT NULL,
        user_role TEXT NOT NULL,
        action_type TEXT NOT NULL,
        description_ar TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # إدخال الحسابات الافتراضية إذا لم تكن موجودة
    for uname, udata in DEFAULT_ACCOUNTS.items():
        cursor.execute("SELECT username FROM icrat_users WHERE username = ?", (uname,))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO icrat_users (username, password_plain, role, full_name_ar, email, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (uname, udata["password_hash"], udata["role"], udata["full_name_ar"], udata["email"], datetime.now().isoformat()))

    conn.commit()
    conn.close()

# تنفيذ التهيئة عند استيراد الملف
init_central_database()

# ----------------- 👤 USER & AUTHENTICATION SERVICES -----------------

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """التحقق من بيانات اعتماد المستخدم واسترجاع ملفه الشخصي وصلاحياته"""
    if not username or not password:
        return None
    
    clean_user = username.strip().lower()
    clean_pass = password.strip()
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM icrat_users WHERE username = ?", (clean_user,))
    row = cursor.fetchone()
    
    if row and row["password_plain"] == clean_pass:
        # تحديث وقت آخر تسجيل دخول
        now_iso = datetime.now().isoformat()
        cursor.execute("UPDATE icrat_users SET last_login_at = ? WHERE username = ?", (now_iso, clean_user))
        conn.commit()
        
        user_dict = dict(row)
        conn.close()
        return user_dict
    
    conn.close()
    return None

def get_user_role_info(role_key: str) -> Dict[str, Any]:
    """استرجاع معلومات ووسوم الدور الهندسي"""
    return ROLES_METADATA.get(role_key, ROLES_METADATA["VIEWER"])

def has_permission(user_role: str, permission_key: str) -> bool:
    """فحص امتلاك المستخدم لصلاحية محددة"""
    allowed_roles = PERMISSIONS_MAP.get(permission_key, ["ADMIN"])
    return user_role in allowed_roles

# ----------------- ☁️ PROJECT CLOUD STORAGE & SYNC SERVICES -----------------

def save_project_to_cloud(
    project_id: str,
    meta: Dict[str, Any],
    activities: List[Dict[str, Any]],
    risks: Optional[List[Dict[str, Any]]] = None,
    coordination_issues: Optional[List[Dict[str, Any]]] = None,
    delay_events: Optional[List[Dict[str, Any]]] = None,
    expert_overrides: Optional[Dict[str, Any]] = None,
    spatial_elements: Optional[List[Dict[str, Any]]] = None,
    user: str = "admin",
    user_role: str = "ADMIN"
) -> Tuple[bool, str]:
    """حفظ ومزامنة حزمة المشروع في قاعدة البيانات المركزية وتوثيق العملية في سجل التدقيق"""
    try:
        clean_id = project_id.strip() if project_id else f"PROJ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        name_ar = meta.get("name_ar", "مشروع هندسي مخصص")
        gov = meta.get("governorate", "BAGHDAD")
        client = meta.get("client_ar", "وزارة الإعمار والإسكان")
        contractor = meta.get("contractor_ar", "شركة المقاولات العامة")
        cost = float(meta.get("contract_original_cost", 10000000.0))
        duration = int(meta.get("contract_original_duration_days", 365))
        curr_sym = meta.get("currency_symbol", "$")
        
        acts = activities or []
        r_list = risks or []
        c_list = coordination_issues or []
        d_list = delay_events or []
        
        now_str = datetime.now().isoformat()
        
        # تجميع حزمة البيانات الشاملة
        full_package = {
            "app_signature": "ICRAT_IRAQ_CONSTRUCTION_RISK_AI_SYSTEM",
            "schema_version": "2.0_2026",
            "exported_at": now_str,
            "exported_by": user,
            "project_meta": dict(meta),
            "activities": [dict(a) for a in acts],
            "risk_register": [dict(r) for r in r_list],
            "coordination_issues": [dict(c) for c in c_list],
            "delay_events": [dict(e) for e in d_list],
            "expert_overrides": dict(expert_overrides or {}),
            "ifc_spatial_elements": [dict(s) for s in (spatial_elements or [])]
        }
        
        snapshot_json = json.dumps(full_package, ensure_ascii=False, indent=2)
        
        conn = _get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT version_id FROM icrat_cloud_projects WHERE project_id = ?", (clean_id,))
        existing = cursor.fetchone()
        
        if existing:
            new_version = existing["version_id"] + 1
            cursor.execute("""
            UPDATE icrat_cloud_projects
            SET name_ar = ?, governorate = ?, client_ar = ?, contractor_ar = ?, contract_cost = ?,
                contract_duration = ?, currency_symbol = ?, updated_at = ?, updated_by = ?,
                version_id = ?, activities_count = ?, risks_count = ?, clashes_count = ?,
                claims_count = ?, snapshot_json = ?
            WHERE project_id = ?
            """, (
                name_ar, gov, client, contractor, cost, duration, curr_sym, now_str, user,
                new_version, len(acts), len(r_list), len(c_list), len(d_list), snapshot_json, clean_id
            ))
            action_desc = f"تحديث ومزامنة المشروع سحابياً (الإصدار v{new_version}) بواسطة {user}"
        else:
            new_version = 1
            cursor.execute("""
            INSERT INTO icrat_cloud_projects (
                project_id, name_ar, governorate, client_ar, contractor_ar, contract_cost,
                contract_duration, currency_symbol, created_at, updated_at, created_by,
                updated_by, version_id, activities_count, risks_count, clashes_count,
                claims_count, snapshot_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                clean_id, name_ar, gov, client, contractor, cost, duration, curr_sym,
                now_str, now_str, user, user, 1, len(acts), len(r_list), len(c_list), len(d_list), snapshot_json
            ))
            action_desc = f"إنشاء ونشر المشروع لأول مرة في السحابة المركزية بواسطة {user}"
            
        cursor.execute("""
        INSERT INTO icrat_audit_trail (project_id, username, user_role, action_type, description_ar, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (clean_id, user, user_role, "CLOUD_SYNC", action_desc, now_str))
        
        conn.commit()
        conn.close()
        return True, f"🎉 تم بنجاح حفظ ومزامنة المشروع '{name_ar}' سحابياً (الإصدار v{new_version})!"
    except Exception as e:
        return False, f"❌ فشل حفظ المشروع سحابياً: {str(e)}"

def load_project_from_cloud(project_id: str) -> Optional[Dict[str, Any]]:
    """استرجاع حزمة المشروع الكاملة من قاعدة البيانات المركزية"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM icrat_cloud_projects WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        full_data = json.loads(row["snapshot_json"])
        full_data["cloud_version_id"] = row["version_id"]
        full_data["last_updated_at"] = row["updated_at"]
        full_data["last_updated_by"] = row["updated_by"]
        return full_data
    except Exception:
        return None

def list_cloud_projects() -> List[Dict[str, Any]]:
    """استعراض قائمة المشاريع المتاحة في السحابة المركزية لجميع أعضاء الفريق"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT project_id, name_ar, governorate, client_ar, contractor_ar, contract_cost,
               contract_duration, currency_symbol, updated_at, updated_by, version_id,
               activities_count, risks_count, clashes_count, claims_count
        FROM icrat_cloud_projects
        ORDER BY updated_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []

def delete_cloud_project(project_id: str, user: str, user_role: str) -> Tuple[bool, str]:
    """حذف مشروع من السحابة المركزية (للمشرفين فقط)"""
    if not has_permission(user_role, "can_delete_project"):
        return False, "⚠️ ليس لديك صلاحية لحذف المشاريع السحابية (مخصصة لمدير النظام فقط)."
        
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM icrat_cloud_projects WHERE project_id = ?", (project_id,))
        
        now_str = datetime.now().isoformat()
        cursor.execute("""
        INSERT INTO icrat_audit_trail (project_id, username, user_role, action_type, description_ar, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (project_id, user, user_role, "PROJECT_DELETE", f"قام {user} بحذف المشروع {project_id} من السحابة المركزية", now_str))
        
        conn.commit()
        conn.close()
        return True, f"✅ تم بنجاح حذف المشروع '{project_id}' من قاعدة البيانات المركزية."
    except Exception as e:
        return False, f"❌ حدث خطأ أثناء الحذف: {str(e)}"

# ----------------- 📜 AUDIT TRAIL LOGGING SERVICES -----------------

def log_audit_event(project_id: str, username: str, user_role: str, action_type: str, description_ar: str):
    """توثيق عملية فورية في سجل التدقيق التشاركي"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        now_str = datetime.now().isoformat()
        cursor.execute("""
        INSERT INTO icrat_audit_trail (project_id, username, user_role, action_type, description_ar, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (project_id, username, user_role, action_type, description_ar, now_str))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_recent_audit_logs(project_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """استرجاع أحدث التعديلات والنشاطات التشاركية لفريق العمل"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        if project_id:
            cursor.execute("""
            SELECT * FROM icrat_audit_trail
            WHERE project_id = ?
            ORDER BY id DESC
            LIMIT ?
            """, (project_id, limit))
        else:
            cursor.execute("""
            SELECT * FROM icrat_audit_trail
            ORDER BY id DESC
            LIMIT ?
            """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []
