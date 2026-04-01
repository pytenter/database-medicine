<template>
  <div class="dashboard-page">
    <section class="page-card hero-card">
      <div class="hero-left">
        <div class="hero-avatar">
          <div class="avatar-core">药</div>
        </div>
        <div class="hero-copy">
          <span class="hero-tag">运营总览</span>
          <h3>{{ greeting }}，{{ auth.user?.full_name || auth.user?.username }}</h3>
          <p>{{ roleText }}</p>
          <p>当前时间：{{ nowText }}</p>
        </div>
      </div>
      <div class="hero-stats">
        <div class="hero-stat" v-for="item in topStats" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>
    </section>

    <section class="summary-grid">
      <article class="page-card summary-card" v-for="item in summaryCards" :key="item.label">
        <div class="summary-icon">↗</div>
        <div>
          <span>{{ item.label }}</span>
          <h4>{{ item.value }}</h4>
          <p>{{ item.note }}</p>
        </div>
      </article>
    </section>

    <section class="chart-grid">
      <article class="page-card chart-card wide-card">
        <div class="chart-head">
          <div>
            <h4>近十天收入统计</h4>
            <p>观察销售额变化趋势</p>
          </div>
          <span class="chart-mark">折线图</span>
        </div>
        <div class="line-chart-wrap">
          <svg viewBox="0 0 760 280" class="chart-svg">
            <g>
              <line v-for="y in gridLines" :key="`line-${y}`" x1="48" :y1="y" x2="730" :y2="y" class="grid-line" />
            </g>
            <g>
              <text v-for="axis in lineAxis" :key="`axis-${axis.label}`" x="18" :y="axis.y + 4" class="axis-text">{{ axis.label }}</text>
            </g>
            <polyline :points="linePoints" class="trend-line" />
            <g>
              <circle v-for="point in lineSeriesPoints" :key="`point-${point.x}`" :cx="point.x" :cy="point.y" r="4.5" class="trend-dot" />
            </g>
            <g>
              <text v-for="item in dayLabels" :key="`day-${item.day}`" :x="item.x" y="255" class="axis-text axis-bottom">{{ item.day }}</text>
            </g>
          </svg>
        </div>
      </article>

      <article class="page-card chart-card wide-card">
        <div class="chart-head">
          <div>
            <h4>近十天工单统计</h4>
            <p>展示每日订单处理数量</p>
          </div>
          <span class="chart-mark">柱状图</span>
        </div>
        <div class="bar-chart-wrap">
          <svg viewBox="0 0 760 280" class="chart-svg">
            <g>
              <line v-for="y in gridLines" :key="`bar-line-${y}`" x1="48" :y1="y" x2="730" :y2="y" class="grid-line" />
            </g>
            <g>
              <text v-for="axis in barAxis" :key="`bar-axis-${axis.label}`" x="26" :y="axis.y + 4" class="axis-text">{{ axis.label }}</text>
            </g>
            <g>
              <rect v-for="bar in barSeries" :key="`bar-${bar.day}`" :x="bar.x" :y="bar.y" width="42" :height="bar.height" rx="8" class="bar-rect" />
              <text v-for="bar in barSeries" :key="`bar-label-${bar.day}`" :x="bar.x + 21" y="255" text-anchor="middle" class="axis-text axis-bottom">{{ bar.day }}</text>
            </g>
          </svg>
        </div>
      </article>
    </section>

    <section class="bottom-grid">
      <article class="page-card donut-card">
        <div class="chart-head">
          <div>
            <h4>药品类别统计</h4>
            <p>按当前库存构成估算占比</p>
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
          </div>
        </div>
      </article>

      <article class="page-card notice-card">
        <div class="chart-head">
          <div>
            <h4>公告信息</h4>
            <p>用于展示门店通知与业务提醒</p>
          </div>
        </div>
        <div class="notice-list">
          <article class="notice-item" v-for="notice in notices" :key="notice.title">
            <h5>{{ notice.title }}</h5>
            <p>{{ notice.content }}</p>
            <time>{{ notice.time }}</time>
          </article>
        </div>
      </article>
    </section>

    <section class="page-card access-card">
      <div class="chart-head">
        <div>
          <h4>近七日系统访问记录</h4>
          <p>用于模拟后台访问热度变化</p>
        </div>
      </div>
      <div class="access-bars">
        <div class="access-col" v-for="item in accessStats" :key="item.day">
          <span class="access-value">{{ item.value }}</span>
          <div class="access-track">
            <div class="access-fill" :style="{ height: `${item.value * 9}%` }"></div>
          </div>
          <small>{{ item.day }}</small>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from "vue";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();

const roleMap = {
  system_admin: "系统管理员",
  pharmacy_admin: "药店管理员",
  salesperson: "销售人员",
};

const now = new Date();
const hour = now.getHours();
const greeting = hour < 12 ? "上午好" : hour < 18 ? "下午好" : "晚上好";
const nowText = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")} ${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}:${String(now.getSeconds()).padStart(2, "0")}`;
const roleText = computed(() => roleMap[auth.user?.role] || "未知角色");

const topStats = [
  { label: "订单总量", value: "10" },
  { label: "总收益", value: "1044.4" },
  { label: "店铺数量", value: "2" },
  { label: "员工数量", value: "2" },
];

const summaryCards = [
  { label: "本月订单量", value: "4 单", note: "较上月提升 12%" },
  { label: "本月收益", value: "321.3 元", note: "客单价保持稳定" },
  { label: "本年订单量", value: "10 单", note: "已覆盖全部门店" },
  { label: "本年收益", value: "1044.4 元", note: "库存周转正常" },
];

const lineValues = [8, 12, 11, 10, 9, 14, 252, 248, 10, 70];
const barValues = [0, 0, 0, 0, 0, 0, 2, 0, 0, 2];

const chartWidth = 682;
const startX = 78;
const stepX = chartWidth / (lineValues.length - 1);
const chartBaseY = 222;
const chartHeight = 170;
const lineMax = 300;
const barMax = 2;

const lineSeriesPoints = lineValues.map((value, index) => ({
  x: startX + stepX * index,
  y: chartBaseY - (value / lineMax) * chartHeight,
}));

const linePoints = lineSeriesPoints.map((point) => `${point.x},${point.y}`).join(" ");

const dayLabels = lineSeriesPoints.map((point, index) => ({
  day: index + 1,
  x: point.x,
}));

const gridLines = [52, 95, 138, 181, 224];
const lineAxis = [
  { label: "300", y: 52 },
  { label: "225", y: 95 },
  { label: "150", y: 138 },
  { label: "75", y: 181 },
  { label: "0", y: 224 },
];
const barAxis = [
  { label: "2", y: 52 },
  { label: "1", y: 138 },
  { label: "0", y: 224 },
];

const barSeries = barValues.map((value, index) => {
  const height = (value / barMax) * chartHeight;
  return {
    day: index + 1,
    x: 58 + index * 66,
    y: chartBaseY - height,
    height,
  };
});

const categoryStats = [
  { label: "感冒药", percent: 69, color: "#1f8fff" },
  { label: "抗生素", percent: 21, color: "#1ed5a4" },
  { label: "维生素", percent: 10, color: "#ffb020" },
];

const donutStyle = computed(() => ({
  background: `conic-gradient(${categoryStats[0].color} 0 ${categoryStats[0].percent}%, ${categoryStats[1].color} ${categoryStats[0].percent}% ${categoryStats[0].percent + categoryStats[1].percent}%, ${categoryStats[2].color} ${categoryStats[0].percent + categoryStats[1].percent}% 100%)`,
}));

const notices = [
  {
    title: "本周门店药品效期巡检安排",
    content: "请各门店管理员在周五前完成效期低于 90 天药品的排查，并将结果同步到库存模块。",
    time: "2026-04-01 09:15:20",
  },
  {
    title: "销售模块演示数据维护提醒",
    content: "教师答辩前请使用系统管理员账号确认演示账号状态正常，并检查库存是否已恢复到初始化数据。",
    time: "2026-03-30 16:48:10",
  },
  {
    title: "冷链药品储存记录补录通知",
    content: "涉及冷链储存的药品，请在门店巡检后更新备注，便于后续课程设计展示完整业务流程。",
    time: "2026-03-28 10:26:08",
  },
];

const accessStats = [
  { day: "周一", value: 3 },
  { day: "周二", value: 5 },
  { day: "周三", value: 4 },
  { day: "周四", value: 6 },
  { day: "周五", value: 7 },
  { day: "周六", value: 4 },
  { day: "周日", value: 9 },
];
</script>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 18px;
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 26px 28px;
  background:
    linear-gradient(135deg, #ffffff 0%, #f8fffd 52%, #f4fbff 100%),
    radial-gradient(circle at top right, rgba(12, 122, 92, 0.08), transparent 24%);
}

.hero-left {
  display: flex;
  align-items: center;
  gap: 18px;
}

.hero-avatar {
  width: 82px;
  height: 82px;
  border-radius: 24px;
  background: linear-gradient(180deg, #d8f7ec 0%, #b7ebd7 100%);
  display: grid;
  place-items: center;
  box-shadow: inset 0 0 0 1px rgba(12, 122, 92, 0.12);
}

.avatar-core {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  background: linear-gradient(180deg, #14b87a 0%, #0c7a5c 100%);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 28px;
  font-weight: 700;
}

.hero-copy h3 {
  margin: 6px 0 10px;
  font-size: 28px;
}

.hero-copy p {
  margin: 4px 0;
  color: #64748b;
}

.hero-tag {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: #eaf8f2;
  color: #0c7a5c;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(92px, 1fr));
  gap: 20px;
  min-width: 480px;
}

.hero-stat {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  padding: 6px 0;
}

.hero-stat span {
  color: #94a3b8;
  font-size: 13px;
}

.hero-stat strong {
  color: #16a36f;
  font-size: 30px;
  font-weight: 700;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.summary-card {
  padding: 24px;
  display: flex;
  gap: 18px;
  align-items: center;
}

.summary-icon {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: #f2f7fb;
  color: #4b5563;
  font-size: 34px;
}

.summary-card span {
  color: #64748b;
  font-size: 14px;
}

.summary-card h4 {
  margin: 8px 0 6px;
  font-size: 34px;
  font-weight: 500;
  color: #334155;
}

.summary-card p {
  margin: 0;
  color: #94a3b8;
  font-size: 13px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.chart-card,
.notice-card,
.donut-card,
.access-card {
  padding: 22px;
}

.chart-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.chart-head h4 {
  margin: 0;
  font-size: 18px;
}

.chart-head p {
  margin: 6px 0 0;
  color: #94a3b8;
  font-size: 13px;
}

.chart-mark {
  display: inline-flex;
  align-items: center;
  padding: 7px 10px;
  border-radius: 999px;
  background: #f3f8fd;
  color: #64748b;
  font-size: 12px;
}

.chart-svg {
  width: 100%;
  height: auto;
}

.grid-line {
  stroke: #e9eef5;
  stroke-width: 1;
}

.axis-text {
  fill: #94a3b8;
  font-size: 12px;
}

.axis-bottom {
  text-anchor: middle;
}

.trend-line {
  fill: none;
  stroke: #2a9cff;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.trend-dot {
  fill: #2a9cff;
  stroke: #ffffff;
  stroke-width: 2;
}

.bar-rect {
  fill: #1f8fff;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1.05fr 1.45fr;
  gap: 18px;
}

.donut-body {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 20px;
  align-items: center;
}

.donut-chart {
  width: 220px;
  height: 220px;
  border-radius: 50%;
  position: relative;
  margin: 10px auto 0;
}

.donut-chart::before {
  content: "";
  position: absolute;
  inset: 34px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: inset 0 0 0 1px #edf2f7;
}

.donut-center {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  text-align: center;
  z-index: 1;
}

.donut-center strong {
  display: block;
  font-size: 24px;
  color: #334155;
}

.donut-center span {
  color: #94a3b8;
  font-size: 13px;
}

.donut-legend {
  display: grid;
  gap: 16px;
}

.legend-item {
  display: grid;
  grid-template-columns: 12px 1fr auto;
  gap: 12px;
  align-items: center;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
}

.legend-label {
  color: #475569;
}

.notice-list {
  display: grid;
  gap: 14px;
}

.notice-item {
  padding: 16px 0;
  border-bottom: 1px solid #edf2f7;
}

.notice-item:last-child {
  border-bottom: none;
}

.notice-item h5 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #334155;
}

.notice-item p {
  margin: 0 0 12px;
  color: #64748b;
  line-height: 1.8;
  font-size: 14px;
}

.notice-item time {
  color: #94a3b8;
  font-size: 12px;
}

.access-bars {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 18px;
  padding-top: 6px;
}

.access-col {
  display: grid;
  justify-items: center;
  gap: 10px;
}

.access-value {
  color: #64748b;
  font-size: 13px;
}

.access-track {
  width: 100%;
  max-width: 72px;
  height: 150px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f2f7fb 0%, #edf3f8 100%);
  display: flex;
  align-items: flex-end;
  padding: 8px;
}

.access-fill {
  width: 100%;
  border-radius: 14px;
  background: linear-gradient(180deg, #4ec8ff 0%, #12b981 100%);
  min-height: 12px;
}

.access-col small {
  color: #94a3b8;
}

@media (max-width: 1400px) {
  .hero-card,
  .bottom-grid,
  .chart-grid,
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .hero-card {
    flex-direction: column;
  }

  .hero-stats {
    min-width: 0;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .donut-body {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .summary-grid,
  .chart-grid,
  .bottom-grid {
    grid-template-columns: 1fr;
  }

  .hero-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .access-bars {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
