"""
Monte Carlo Quantitative Schedule & Cost Risk Analysis (QSRA & QCRA) Engine
محرك محاكاة مونت كارلو للتحليل الكمي للوقت والتكلفة مع تثبيت العشوائية (Deterministic Random Seed)
لضمان استقرار ودقة الأرقام عند التنقل بين الشاشات والتبويبات
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Any, Tuple

def sample_distribution(
    dist_type: str, 
    o: float, 
    m: float, 
    p: float, 
    size: int = 1, 
    rng: np.random.RandomState = None
) -> np.ndarray:
    """توليد عينات إحصائية متطابقة وثابتة وفق نوع التوزيع المطلوب (Beta-PERT, Triangular, Normal, Uniform)"""
    if rng is None:
        rng = np.random.RandomState(42)

    o, m, p = float(o), float(m), float(p)
    if o > m: o = m
    if p < m: p = m
    if o == p:
        return np.full(size, m)

    dist_type = dist_type.upper()
    if dist_type in ["PERT", "BETA_PERT", "BETA-PERT"]:
        range_val = p - o
        if range_val <= 0:
            return np.full(size, m)
        alpha = 1.0 + 4.0 * (m - o) / range_val
        beta = 1.0 + 4.0 * (p - m) / range_val
        samples = stats.beta.rvs(alpha, beta, size=size, random_state=rng)
        return o + samples * range_val

    elif dist_type in ["TRIANGULAR", "TRIANG"]:
        c = (m - o) / (p - o) if (p - o) > 0 else 0.5
        return stats.triang.rvs(c, loc=o, scale=(p - o), size=size, random_state=rng)

    elif dist_type == "NORMAL":
        mean = m
        std = (p - o) / 6.0 if (p - o) > 0 else 1.0
        samples = rng.normal(mean, std, size=size)
        return np.clip(samples, o, p)

    elif dist_type == "UNIFORM":
        return rng.uniform(o, p, size=size)

    else:
        # الافتراضي PERT
        range_val = p - o
        if range_val <= 0:
            return np.full(size, m)
        alpha = 1.0 + 4.0 * (m - o) / range_val
        beta = 1.0 + 4.0 * (p - m) / range_val
        samples = stats.beta.rvs(alpha, beta, size=size, random_state=rng)
        return o + samples * range_val

class MonteCarloSimulator:
    def __init__(
        self,
        activities: List[Dict[str, Any]],
        risks: List[Dict[str, Any]],
        iterations: int = 2500,
        schedule_cost_correlation: float = 0.75,
        daily_overhead_rate: float = 2500.0,
        random_seed: int = 42
    ):
        self.activities = activities
        self.risks = risks
        self.iterations = max(500, min(iterations, 10000))
        self.schedule_cost_correlation = max(0.0, min(schedule_cost_correlation, 1.0))
        self.daily_overhead_rate = daily_overhead_rate
        self.random_seed = random_seed

    def _topological_sort(self) -> List[str]:
        """ترتيب الأنشطة وفق شبكة التتابع المنطقية (Precedence Network)"""
        adj = {}
        in_degree = {}
        for act in self.activities:
            aid = act["id"]
            adj[aid] = []
            in_degree[aid] = 0

        for act in self.activities:
            aid = act["id"]
            for pred in act.get("predecessors", []):
                if pred in adj:
                    adj[pred].append(aid)
                    in_degree[aid] += 1

        queue = [aid for aid, deg in in_degree.items() if deg == 0]
        sorted_order = []
        while queue:
            curr = queue.pop(0)
            sorted_order.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_order) < len(self.activities):
            sorted_order = [act["id"] for act in self.activities]
        return sorted_order

    def run_simulation(self) -> Dict[str, Any]:
        """تشغيل محاكاة مونت كارلو الكاملة للوقت والتكلفة (QSRA & QCRA) مع استقرار تام للنتائج"""
        if not self.activities:
            return {
                "iterations": self.iterations,
                "total_durations": np.zeros(self.iterations),
                "total_costs": np.zeros(self.iterations),
                "duration_percentiles": {p: 0.0 for p in ["P10", "P20", "P30", "P40", "P50", "P60", "P70", "P75", "P80", "P85", "P90", "P95"]},
                "cost_percentiles": {p: 0.0 for p in ["P10", "P20", "P30", "P40", "P50", "P60", "P70", "P75", "P80", "P85", "P90", "P95"]},
                "deterministic_duration": 0.0,
                "deterministic_cost": 0.0,
                "tornado_duration": [],
                "tornado_cost": [],
                "activity_duration_results": {},
                "risk_delay_impacts": {}
            }

        rng = np.random.RandomState(self.random_seed)
        n = self.iterations
        act_dict = {act["id"]: act for act in self.activities}
        sorted_ids = self._topological_sort()

        # الخطوة 1: توليد مدد وتكاليف الأنشطة
        sampled_durations = {}
        sampled_direct_costs = {}

        for aid in sorted_ids:
            act = act_dict[aid]
            o_d, m_d, p_d = act.get("duration_estimates", (10, 20, 30))
            dist_d = act.get("dist_type", "PERT")
            sampled_durations[aid] = sample_distribution(dist_d, o_d, m_d, p_d, size=n, rng=rng)

            o_c, m_c, p_c = act.get("cost_estimates", (10000, 20000, 30000))
            dist_c = act.get("cost_dist_type", "PERT")
            sampled_direct_costs[aid] = sample_distribution(dist_c, o_c, m_c, p_c, size=n, rng=rng)

        # الخطوة 2: محاكاة تأثير أحداث المخاطر
        risk_delay_samples = np.zeros(n)
        risk_cost_samples = np.zeros(n)
        risk_individual_impacts = {}

        for r in self.risks:
            rid = r.get("id", "UNK")
            prob = r.get("probability", 3) / 5.0
            occurred = rng.binomial(1, prob, size=n)

            o_sd, m_sd, p_sd = r.get("schedule_delay_days", (10, 30, 60))
            delays = sample_distribution("PERT", o_sd, m_sd, p_sd, size=n, rng=rng) * occurred
            risk_delay_samples += delays
            risk_individual_impacts[rid] = delays

            o_cp, m_cp, p_cp = r.get("cost_impact_pct", (2, 5, 10))
            cost_pcts = sample_distribution("PERT", o_cp, m_cp, p_cp, size=n, rng=rng) / 100.0
            base_cost = sum([act.get("cost_estimates", (0, 0, 0))[1] for act in self.activities])
            costs = (cost_pcts * base_cost) * occurred
            risk_cost_samples += costs

        # الخطوة 3: حساب المسار الحرج والشبكة المنطقية (CPM Network Calculation)
        ef_matrix = np.zeros((len(sorted_ids), n))
        es_matrix = np.zeros((len(sorted_ids), n))
        id_to_idx = {aid: idx for idx, aid in enumerate(sorted_ids)}

        for aid in sorted_ids:
            idx = id_to_idx[aid]
            act = act_dict[aid]
            preds = act.get("predecessors", [])
            
            if not preds:
                es = np.zeros(n)
            else:
                pred_indices = [id_to_idx[p] for p in preds if p in id_to_idx]
                if pred_indices:
                    es = np.max(ef_matrix[pred_indices, :], axis=0)
                else:
                    es = np.zeros(n)

            es_matrix[idx, :] = es
            ef_matrix[idx, :] = es + sampled_durations[aid]

        project_cpm_durations = np.max(ef_matrix, axis=0)
        total_durations = project_cpm_durations + (risk_delay_samples * 0.45)

        # الخطوة 4: حساب التكاليف المباشرة وغير المباشرة
        total_direct_costs = np.sum(list(sampled_direct_costs.values()), axis=0)
        delay_days = np.maximum(0, total_durations - np.median(total_durations) * 0.85)
        indirect_overhead = delay_days * self.daily_overhead_rate * self.schedule_cost_correlation
        total_costs = total_direct_costs + indirect_overhead + risk_cost_samples

        # الخطوة 5: حساب النسب المئوية ومستويات الثقة (P-Values)
        percentiles = [10, 20, 30, 40, 50, 60, 70, 75, 80, 85, 90, 95]
        duration_p = {f"P{p}": float(np.percentile(total_durations, p)) for p in percentiles}
        cost_p = {f"P{p}": float(np.percentile(total_costs, p)) for p in percentiles}

        det_dur = sum([act.get("duration_estimates", (10, 20, 30))[1] for act in self.activities])
        det_cost = sum([act.get("cost_estimates", (10000, 20000, 30000))[1] for act in self.activities])

        p80_duration = duration_p["P80"]
        p80_cost = cost_p["P80"]
        contingency_time_days = max(0.0, p80_duration - duration_p["P50"])
        contingency_cost_val = max(0.0, p80_cost - cost_p["P50"])
        contingency_cost_pct = (contingency_cost_val / cost_p["P50"]) * 100.0 if cost_p["P50"] > 0 else 0.0

        # الخطوة 6: تحليل الحساسية ومخطط تورنادو (Spearman Rank Correlation)
        tornado_duration = []
        for aid in sorted_ids:
            act_name = act_dict[aid].get("name_ar", aid)
            corr, _ = stats.spearmanr(sampled_durations[aid], total_durations)
            if np.isnan(corr): corr = 0.0
            tornado_duration.append({
                "id": aid,
                "name": f"[نشاط] {act_name}",
                "correlation": float(corr),
                "type": "activity"
            })

        for r in self.risks:
            rid = r.get("id", "UNK")
            rtitle = r.get("title_ar", rid)
            if rid in risk_individual_impacts:
                corr, _ = stats.spearmanr(risk_individual_impacts[rid], total_durations)
                if np.isnan(corr): corr = 0.0
                tornado_duration.append({
                    "id": rid,
                    "name": f"[خطر] {rtitle[:35]}...",
                    "correlation": float(corr),
                    "type": "risk"
                })

        tornado_duration.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "iterations": n,
            "total_durations": total_durations.tolist(),
            "total_costs": total_costs.tolist(),
            "duration_percentiles": duration_p,
            "cost_percentiles": cost_p,
            "deterministic_duration": det_dur,
            "deterministic_cost": det_cost,
            "contingency_time_days": round(contingency_time_days, 1),
            "contingency_cost_val": round(contingency_cost_val, 2),
            "contingency_cost_pct": round(contingency_cost_pct, 1),
            "tornado_duration": tornado_duration[:12]
        }
