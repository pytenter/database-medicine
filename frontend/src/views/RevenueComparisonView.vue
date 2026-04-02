<template>
  <div class="revenue-page">
    <section class="page-card hero-card">
      <div>
        <span class="hero-tag">营业分析</span>
        <h3>各药店营业额对比</h3>
        <p>根据历史销售订单自动汇总各门店的营业额、订单量和经营情况。</p>
      </div>
      <div class="hero-stats">
        <article>
          <span>门店数量</span>
          <strong>{{ stats.storeCount }}</strong>
        </article>
        <article>
          <span>订单总量</span>
          <strong>{{ stats.orderCount }}</strong>
        </article>
        <article>
          <span>营业总额</span>
          <strong>¥{{ stats.totalRevenue.toFixed(2) }}</strong>
        </article>
      </div>
    </section>

    <section class="compare-grid">
      <article class="page-card compare-card">
        <div class="panel-head">
          <div>
            <h4>门店营业额排行</h4>
            <p>按营业额从高到低展示各门店的经营情况。</p>
          </div>
        </div>
        <div class="bars-wrap">
          <div v-for="item in compareRows" :key="item.id" class="bar-row">
            <div class="bar-meta">
              <strong>{{ item.name }}</strong>
              <span>{{ item.orderCount }} 单</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: `${item.percent}%` }"></div>
            </div>
            <div class="bar-value">¥{{ item.revenue.toFixed(2) }}</div>
          </div>
        </div>
      </article>

      <article class="page-card compare-card">
        <div class="panel-head">
          <div>
            <h4>详细数据</h4>
            <p>查看各门店的负责人、地址、订单量和营业额。</p>
          </div>
        </div>
        <el-table :data="compareRows" border>
          <el-table-column prop="name" label="门店名称" min-width="140" />
          <el-table-column prop="manager_name" label="负责人" width="110" />
          <el-table-column prop="address" label="地址" min-width="220" show-overflow-tooltip />
          <el-table-column label="订单量" width="100">
            <template #default="scope">{{ scope.row.orderCount }}</template>
          </el-table-column>
          <el-table-column label="营业额" width="130">
            <template #default="scope">¥{{ scope.row.revenue.toFixed(2) }}</template>
          </el-table-column>
        </el-table>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { getStoresApi } from "../api/inventory";
import { getSalesApi } from "../api/sales";

const stores = ref([]);
const sales = ref([]);

const loadData = async () => {
  const [{ data: storeData }, { data: salesData }] = await Promise.all([getStoresApi(), getSalesApi()]);
  stores.value = storeData;
  sales.value = salesData;
};

const compareRows = computed(() => {
  const revenueMap = new Map();
  for (const store of stores.value) {
    revenueMap.set(store.id, { ...store, revenue: 0, orderCount: 0 });
  }
  for (const order of sales.value) {
    const item = revenueMap.get(order.store);
    if (!item) continue;
    item.revenue += Number(order.total_amount || 0);
    item.orderCount += 1;
  }
  const rows = [...revenueMap.values()].sort((a, b) => b.revenue - a.revenue);
  const maxRevenue = rows[0]?.revenue || 1;
  return rows.map((item) => ({ ...item, percent: Math.max(8, (item.revenue / maxRevenue) * 100) }));
});

const stats = computed(() => ({
  storeCount: stores.value.length,
  orderCount: sales.value.length,
  totalRevenue: compareRows.value.reduce((sum, item) => sum + item.revenue, 0),
}));

onMounted(loadData);
</script>

<style scoped>
.revenue-page {
  display: grid;
  gap: 18px;
}

.hero-card {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  background: linear-gradient(135deg, #ffffff 0%, #f7fbff 60%, #f4fffb 100%);
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

.hero-card h3 {
  margin: 12px 0 10px;
  font-size: 30px;
}

.hero-card p {
  margin: 0;
  color: #64748b;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(120px, 1fr));
  gap: 16px;
  min-width: 420px;
}

.hero-stats article {
  padding: 16px;
  border: 1px solid #e5edf7;
  border-radius: 18px;
  background: rgba(255,255,255,0.78);
}

.hero-stats span {
  display: block;
  color: #94a3b8;
  font-size: 13px;
}

.hero-stats strong {
  display: block;
  margin-top: 8px;
  color: #0f172a;
  font-size: 28px;
}

.compare-grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 18px;
}

.compare-card {
  padding: 22px;
}

.panel-head {
  margin-bottom: 16px;
}

.panel-head h4 {
  margin: 0;
  font-size: 20px;
}

.panel-head p {
  margin: 6px 0 0;
  color: #94a3b8;
}

.bars-wrap {
  display: grid;
  gap: 16px;
}

.bar-row {
  display: grid;
  grid-template-columns: 150px 1fr 120px;
  gap: 14px;
  align-items: center;
}

.bar-meta strong {
  display: block;
  color: #0f172a;
}

.bar-meta span {
  color: #94a3b8;
  font-size: 13px;
}

.bar-track {
  height: 14px;
  border-radius: 999px;
  background: #eef4f8;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #0ea5e9 0%, #10b981 100%);
}

.bar-value {
  text-align: right;
  font-weight: 700;
  color: #0f172a;
}

@media (max-width: 1200px) {
  .hero-card,
  .compare-grid {
    grid-template-columns: 1fr;
  }

  .hero-card {
    flex-direction: column;
  }

  .hero-stats {
    min-width: 0;
  }
}
</style>
