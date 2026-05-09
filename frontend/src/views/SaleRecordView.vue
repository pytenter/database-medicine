<template>
  <div class="page-card order-page">
    <div class="toolbar order-toolbar">
      <div>
        <h3 class="page-title">订单信息</h3>
      </div>
      <div class="toolbar-actions wrap-actions">
        <el-input v-model="keyword" placeholder="按订单编号、客户或电话搜索" clearable style="width: 260px;" @keyup.enter="loadSales" />
        <el-button @click="loadSales">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button v-if="canCreateOrder" type="primary" @click="goCreate">新增订单</el-button>
      </div>
    </div>

    <el-table :data="sales" border>
      <el-table-column prop="order_no" label="订单编号" min-width="190" />
      <el-table-column prop="customer_name" label="客户名称" min-width="120" />
      <el-table-column prop="customer_phone" label="联系电话" min-width="130" />
      <el-table-column prop="store_name" label="所属门店" min-width="140" />
      <el-table-column prop="total_amount" label="订单金额" width="120">
        <template #default="scope">{{ formatMoney(scope.row.total_amount) }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="下单时间" min-width="180">
        <template #default="scope">{{ formatDateTime(scope.row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="110">
        <template #default="scope">
          <el-button link type="primary" @click="showDetail(scope.row)">订单详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" title="订单详情" width="1120px" destroy-on-close>
      <template v-if="currentOrder">
        <div class="detail-grid">
          <section class="detail-card">
            <div class="detail-title">基础信息</div>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="订单编号">{{ currentOrder.order_no }}</el-descriptions-item>
              <el-descriptions-item label="客户名称">{{ currentOrder.customer_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="联系方式">{{ currentOrder.customer_phone || '-' }}</el-descriptions-item>
              <el-descriptions-item label="订单金额">{{ formatMoney(currentOrder.total_amount) }}</el-descriptions-item>
              <el-descriptions-item label="下单时间">{{ formatDateTime(currentOrder.created_at) }}</el-descriptions-item>
              <el-descriptions-item label="销售人员">{{ currentOrder.salesperson_name || '-' }}</el-descriptions-item>
            </el-descriptions>
          </section>

          <section class="detail-card">
            <div class="detail-title">药店信息</div>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="药店名称">{{ currentOrder.store_name }}</el-descriptions-item>
              <el-descriptions-item label="药店地址">{{ currentOrder.store_address || '-' }}</el-descriptions-item>
              <el-descriptions-item label="联系方式">{{ currentOrder.store_phone || '-' }}</el-descriptions-item>
            </el-descriptions>
          </section>
        </div>

        <section class="detail-card">
          <div class="detail-title">购买药品信息</div>
          <el-table :data="currentOrder.items" border>
            <el-table-column prop="medicine_name" label="药品名称" min-width="170" />
            <el-table-column prop="manufacturer_name" label="品牌" min-width="150" />
            <el-table-column prop="quantity" label="数量" width="90" />
            <el-table-column prop="unit_price" label="单价" width="120">
              <template #default="scope">{{ formatMoney(scope.row.unit_price) }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="120">
              <template #default="scope">{{ formatMoney(scope.row.amount) }}</template>
            </el-table-column>
          </el-table>
        </section>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { getSaleDetailApi, getSalesApi } from "../api/sales";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const sales = ref([]);
const keyword = ref("");
const detailVisible = ref(false);
const currentOrder = ref(null);
const canCreateOrder = computed(() => auth.role === "salesperson");

const formatDateTime = (value) => {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
};
const formatMoney = (value) => `¥${Number(value || 0).toFixed(2)}`;

const loadSales = async () => {
  const params = {};
  if (keyword.value) params.search = keyword.value;
  const { data } = await getSalesApi(params);
  sales.value = data;
};

const resetFilters = () => {
  keyword.value = "";
  loadSales();
};

const showDetail = async (row) => {
  const { data } = await getSaleDetailApi(row.id);
  currentOrder.value = data;
  detailVisible.value = true;
};

const goCreate = () => {
  router.push("/sales/create");
};

onMounted(loadSales);
</script>

<style scoped>
.order-page {
  padding: 22px;
}

.order-toolbar {
  margin-bottom: 18px;
}

.wrap-actions {
  flex-wrap: wrap;
  gap: 10px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.detail-card {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #d8e3f0;
  border-radius: 8px;
  background: #fbfdff;
}

.detail-title {
  margin-bottom: 12px;
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
}

@media (max-width: 980px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
