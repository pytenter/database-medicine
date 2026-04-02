<template>
  <div class="dashboard-page">
    <section class="page-card hero-card">
      <div>
        <span class="hero-tag">运营总览</span>
        <h2>{{ greeting }}，{{ auth.user?.full_name || auth.user?.username }}</h2>
        <p>{{ roleText }}</p>
        <p>当前时间：{{ nowText }}</p>
      </div>
      <div class="hero-stats">
        <div v-for="item in topStats" :key="item.label" class="hero-stat">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>
    </section>

    <section class="summary-grid">
      <article v-for="item in summaryCards" :key="item.label" class="page-card summary-card">
        <span>{{ item.label }}</span>
        <h3>{{ item.value }}</h3>
        <p>{{ item.note }}</p>
      </article>
    </section>

    <section class="chart-grid">
      <article class="page-card chart-card">
        <div class="chart-head">
          <div>
            <h4>近十天收入统计</h4>
            <p>按数据库销售订单汇总每日收入</p>
          </div>
          <span class="chart-mark">折线图</span>
        </div>
        <svg viewBox="0 0 760 280" class="chart-svg">
          <line v-for="y in gridLines" :key="`l-${y}`" x1="48" :y1="y" x2="730" :y2="y" class="grid-line" />
          <text v-for="axis in lineAxis" :key="axis.label" x="18" :y="axis.y + 4" class="axis-text">{{ axis.label }}</text>
          <polyline :points="linePoints" class="trend-line" />
          <circle v-for="point in linePointsData" :key="point.x" :cx="point.x" :cy="point.y" r="4.5" class="trend-dot" />
          <text v-for="point in linePointsData" :key="point.label" :x="point.x" y="255" class="axis-text axis-bottom">{{ point.label }}</text>
        </svg>
      </article>

      <article class="page-card chart-card">
        <div class="chart-head">
          <div>
            <h4>近十天订单统计</h4>
            <p>按数据库订单记录统计每日单量</p>
          </div>
          <span class="chart-mark">柱状图</span>
        </div>
        <svg viewBox="0 0 760 280" class="chart-svg">
          <line v-for="y in gridLines" :key="`b-${y}`" x1="48" :y1="y" x2="730" :y2="y" class="grid-line" />
          <text v-for="axis in barAxis" :key="axis.label" x="26" :y="axis.y + 4" class="axis-text">{{ axis.label }}</text>
          <rect v-for="bar in barSeries" :key="bar.label" :x="bar.x" :y="bar.y" width="42" :height="bar.height" rx="8" class="bar-rect" />
          <text v-for="bar in barSeries" :key="`t-${bar.label}`" :x="bar.x + 21" y="255" text-anchor="middle" class="axis-text axis-bottom">{{ bar.label }}</text>
        </svg>
      </article>
    </section>

    <section class="bottom-grid">
      <article class="page-card donut-card">
        <div class="chart-head">
          <div>
            <h4>药品类别统计</h4>
            <p>按库存数量统计各药品类别占比</p>
          </div>
        </div>
        <div class="donut-body">
          <div class="donut-chart" :style="donutStyle">
            <div class="donut-center">
              <strong>库存</strong>
              <span>分类占比</span>
            </div>
          </div>
          <div class="donut-legend">
            <div class="legend-item" v-for="item in categoryStats" :key="item.label">
              <span class="legend-dot" :style="{ background: item.color }"></span>
              <span class="legend-label">{{ item.label }}</span>
              <strong>{{ item.percent }}%</strong>
            </div>
            <div v-if="!categoryStats.length" class="empty-text">暂无分类数据</div>
          </div>
        </div>
      </article>

      <article class="page-card notice-card">
        <div class="chart-head">
          <div>
            <h4>公告信息</h4>
            <p>读取数据库中已发布的系统公告</p>
          </div>
        </div>
        <div class="notice-list">
          <article class="notice-item" v-for="notice in notices" :key="notice.id">
            <h5>{{ notice.title }}</h5>
            <p>{{ notice.content }}</p>
            <time>{{ notice.time }}</time>
          </article>
          <div v-if="!notices.length" class="empty-text">暂无已发布公告</div>
        </div>
      </article>
    </section>

    <section class="page-card access-card">
      <div class="chart-head">
        <div>
          <h4>近七日业务记录</h4>
          <p>按订单、物流和评价记录统计系统活跃度</p>
        </div>
      </div>
      <div class="access-bars">
        <div class="access-col" v-for="item in activityStats" :key="item.label">
          <span class="access-value">{{ item.value }}</span>
          <div class="access-track">
            <div class="access-fill" :style="{ height: `${item.height}%` }"></div>
          </div>
          <small>{{ item.label }}</small>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { getDashboardOverviewApi } from "../api/dashboard";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const overview = ref({
  top_stats: { order_total: 0, total_revenue: 0, store_count: 0, employee_count: 0 },
  summary: { month_order_count: 0, month_revenue: 0, year_order_count: 0, year_revenue: 0 },
  charts: { income_last_10_days: [], orders_last_10_days: [], category_stats: [], activity_last_7_days: [] },
  notices: [],
});

const roleMap = {
  system_admin: "系统管理员",
  pharmacy_admin: "药店管理员",
  salesperson: "销售人员",
};
const colorPalette = ["#1f8fff", "#1ed5a4", "#ffb020", "#ff6b6b", "#845ef7", "#12b981"];
const now = new Date();
const greeting = now.getHours() < 12 ? "上午好" : now.getHours() < 18 ? "下午好" : "晚上好";
const nowText = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")} ${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}:${String(now.getSeconds()).padStart(2, "0")}`;
const roleText = computed(() => roleMap[auth.user?.role] || "未知角色");
const gridLines = [52, 95, 138, 181, 224];
const chartBaseY = 222;
const chartHeight = 170;
const startX = 78;
const chartWidth = 682;

const formatMoney = (value) => `¥ ${Number(value || 0).toFixed(2)}`;
const niceMax = (values) => {
  const maxValue = Math.max(...values, 0);
  if (maxValue <= 0) return 4;
  const rough = maxValue / 4;
  const unit = rough <= 10 ? 1 : rough <= 50 ? 5 : rough <= 100 ? 10 : 50;
  return Math.ceil(rough / unit) * unit * 4;
};
const axisFor = (maxValue) => [
  { label: maxValue, y: 52 },
  { label: Math.round(maxValue * 0.75), y: 95 },
  { label: Math.round(maxValue * 0.5), y: 138 },
  { label: Math.round(maxValue * 0.25), y: 181 },
  { label: 0, y: 224 },
];

const loadOverview = async () => {
  const { data } = await getDashboardOverviewApi();
  overview.value = data;
};

const topStats = computed(() => [
  { label: "订单总量", value: overview.value.top_stats.order_total },
  { label: "总收益", value: Number(overview.value.top_stats.total_revenue || 0).toFixed(2) },
  { label: "店铺数量", value: overview.value.top_stats.store_count },
  { label: "员工数量", value: overview.value.top_stats.employee_count },
]);
const summaryCards = computed(() => [
  { label: "本月订单量", value: `${overview.value.summary.month_order_count} 单`, note: "按当月销售订单实时统计" },
  { label: "本月收益", value: formatMoney(overview.value.summary.month_revenue), note: "来自当月数据库销售记录" },
  { label: "本年订单量", value: `${overview.value.summary.year_order_count} 单`, note: "按本年累计订单自动汇总" },
  { label: "本年收益", value: formatMoney(overview.value.summary.year_revenue), note: "按本年累计销售额实时更新" },
]);

const incomeSeries = computed(() => overview.value.charts.income_last_10_days || []);
const orderSeries = computed(() => overview.value.charts.orders_last_10_days || []);
const lineMax = computed(() => niceMax(incomeSeries.value.map((item) => Number(item.value || 0))));
const barMax = computed(() => niceMax(orderSeries.value.map((item) => Number(item.value || 0))));
const lineAxis = computed(() => axisFor(lineMax.value));
const barAxis = computed(() => axisFor(barMax.value));
const linePointsData = computed(() => {
  const stepX = incomeSeries.value.length > 1 ? chartWidth / (incomeSeries.value.length - 1) : 0;
  return incomeSeries.value.map((item, index) => ({
    label: item.label,
    x: startX + stepX * index,
    y: chartBaseY - (Number(item.value || 0) / lineMax.value) * chartHeight,
  }));
});
const linePoints = computed(() => linePointsData.value.map((point) => `${point.x},${point.y}`).join(" "));
const barSeries = computed(() => orderSeries.value.map((item, index) => {
  const height = (Number(item.value || 0) / barMax.value) * chartHeight;
  return { label: item.label, x: 58 + index * 66, y: chartBaseY - height, height };
}));
const categoryStats = computed(() => (overview.value.charts.category_stats || []).map((item, index) => ({ ...item, color: colorPalette[index % colorPalette.length] })));
const donutStyle = computed(() => {
  if (!categoryStats.value.length) return { background: "#eef4f8" };
  let start = 0;
  const parts = categoryStats.value.map((item) => {
    const end = start + Number(item.percent || 0);
    const current = `${item.color} ${start}% ${end}%`;
    start = end;
    return current;
  });
  if (start < 100) parts.push(`#eef4f8 ${start}% 100%`);
  return { background: `conic-gradient(${parts.join(", ")})` };
});
const notices = computed(() => overview.value.notices || []);
const activityStats = computed(() => {
  const source = overview.value.charts.activity_last_7_days || [];
  const maxValue = Math.max(...source.map((item) => Number(item.value || 0)), 1);
  return source.map((item) => ({ ...item, height: Math.max(12, (Number(item.value || 0) / maxValue) * 100) }));
});

onMounted(loadOverview);
</script>

<style scoped>
.dashboard-page { display: grid; gap: 18px; }
.hero-card { display: flex; justify-content: space-between; gap: 24px; padding: 26px 28px; background: linear-gradient(135deg, #ffffff 0%, #f8fffd 52%, #f4fbff 100%); }
.hero-card h2 { margin: 8px 0 10px; font-size: 28px; }
.hero-card p { margin: 4px 0; color: #64748b; }
.hero-tag, .chart-mark { display: inline-flex; padding: 6px 10px; border-radius: 999px; background: #eaf8f2; color: #0c7a5c; font-size: 12px; }
.hero-stats { display: grid; grid-template-columns: repeat(4, minmax(92px, 1fr)); gap: 20px; min-width: 480px; }
.hero-stat span { color: #94a3b8; font-size: 13px; }
.hero-stat strong { display: block; margin-top: 8px; color: #16a36f; font-size: 30px; font-weight: 700; }
.summary-grid, .chart-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.summary-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.summary-card, .chart-card, .donut-card, .notice-card, .access-card { padding: 22px; }
.summary-card h3 { margin: 10px 0 6px; font-size: 30px; color: #334155; }
.summary-card span, .summary-card p, .chart-head p, .notice-item p, .notice-item time, .empty-text, .access-value, .access-col small { color: #64748b; }
.chart-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 14px; }
.chart-head h4 { margin: 0; font-size: 18px; }
.chart-svg { width: 100%; height: auto; }
.grid-line { stroke: #e9eef5; stroke-width: 1; }
.axis-text { fill: #94a3b8; font-size: 12px; }
.axis-bottom { text-anchor: middle; }
.trend-line { fill: none; stroke: #2a9cff; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
.trend-dot { fill: #2a9cff; stroke: #ffffff; stroke-width: 2; }
.bar-rect { fill: #1f8fff; }
.bottom-grid { display: grid; grid-template-columns: 1.05fr 1.45fr; gap: 18px; }
.donut-body { display: grid; grid-template-columns: 240px 1fr; gap: 20px; align-items: center; }
.donut-chart { width: 220px; height: 220px; border-radius: 50%; position: relative; margin: 10px auto 0; }
.donut-chart::before { content: ""; position: absolute; inset: 34px; border-radius: 50%; background: #ffffff; box-shadow: inset 0 0 0 1px #edf2f7; }
.donut-center { position: absolute; inset: 0; display: grid; place-items: center; text-align: center; z-index: 1; }
.donut-center strong { display: block; font-size: 24px; color: #334155; }
.donut-center span { color: #94a3b8; font-size: 13px; }
.donut-legend, .notice-list { display: grid; gap: 16px; }
.legend-item { display: grid; grid-template-columns: 12px 1fr auto; gap: 12px; align-items: center; }
.legend-dot { width: 12px; height: 12px; border-radius: 999px; }
.notice-item { padding: 16px 0; border-bottom: 1px solid #edf2f7; }
.notice-item:last-child { border-bottom: none; }
.notice-item h5 { margin: 0 0 10px; font-size: 16px; color: #334155; }
.access-bars { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 18px; padding-top: 6px; }
.access-col { display: grid; justify-items: center; gap: 10px; }
.access-track { width: 100%; max-width: 72px; height: 150px; border-radius: 18px; background: linear-gradient(180deg, #f2f7fb 0%, #edf3f8 100%); display: flex; align-items: flex-end; padding: 8px; }
.access-fill { width: 100%; border-radius: 14px; background: linear-gradient(180deg, #4ec8ff 0%, #12b981 100%); min-height: 12px; }
@media (max-width: 1400px) { .hero-card, .summary-grid, .chart-grid, .bottom-grid { grid-template-columns: 1fr; } .hero-card { flex-direction: column; } .hero-stats { min-width: 0; grid-template-columns: repeat(2, minmax(0, 1fr)); } .donut-body { grid-template-columns: 1fr; } }
@media (max-width: 900px) { .access-bars { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
</style>
