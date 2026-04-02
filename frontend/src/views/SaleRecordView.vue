<template>
  <div class="page-card order-page">
    <div class="toolbar order-toolbar">
      <div>
        <h3 class="page-title">订单信息</h3>
        <p class="page-subtitle">查看销售订单、订单详情和当前物流状态。</p>
      </div>
      <div class="toolbar-actions wrap-actions">
        <el-input v-model="keyword" placeholder="按订单编号、客户或电话搜索" clearable style="width: 260px;" @keyup.enter="loadSales" />
        <el-select v-model="statusFilter" clearable placeholder="订单状态" style="width: 140px;">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
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
      <el-table-column prop="order_status_label" label="订单状态" width="120">
        <template #default="scope">
          <el-tag :type="statusTagType(scope.row.order_status)">{{ scope.row.order_status_label }}</el-tag>
        </template>
      </el-table-column>
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
        <el-steps :active="statusIndex(currentOrder.order_status)" finish-status="success" align-center class="order-steps">
          <el-step title="待付款" />
          <el-step title="已下单" />
          <el-step title="配送中" />
          <el-step title="已收货" />
        </el-steps>

        <div class="detail-grid">
          <section class="detail-card">
            <div class="detail-title">基础信息</div>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="工单编号">{{ currentOrder.order_no }}</el-descriptions-item>
              <el-descriptions-item label="客户名称">{{ currentOrder.customer_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="联系方式">{{ currentOrder.customer_phone || '-' }}</el-descriptions-item>
              <el-descriptions-item label="当前状态">{{ currentOrder.order_status_label }}</el-descriptions-item>
              <el-descriptions-item label="订单金额">{{ formatMoney(currentOrder.total_amount) }}</el-descriptions-item>
              <el-descriptions-item label="下单时间">{{ formatDateTime(currentOrder.created_at) }}</el-descriptions-item>
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

        <section class="detail-card">
          <div class="detail-title">当前物流</div>
          <el-table :data="currentOrder.logistics" border>
            <el-table-column prop="content" label="物流信息" min-width="280" />
            <el-table-column prop="status_after_label" label="状态更新" width="120">
              <template #default="scope">{{ scope.row.status_after_label || '-' }}</template>
            </el-table-column>
            <el-table-column prop="operator_name" label="操作人员" width="130" />
            <el-table-column prop="created_at" label="操作时间" min-width="180">
              <template #default="scope">{{ formatDateTime(scope.row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </section>

        <section class="detail-card">
          <div class="detail-title">订单评价</div>
          <div v-if="currentOrder.review" class="review-box">
            <el-rate :model-value="currentOrder.review.rating" disabled />
            <p>{{ currentOrder.review.content || '客户未填写文字评价。' }}</p>
            <span>{{ currentOrder.review.reviewer_name || '匿名评价' }} · {{ formatDateTime(currentOrder.review.updated_at) }}</span>
          </div>
          <el-empty v-else description="当前订单暂未评价" :image-size="72" />
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
const statusFilter = ref("");
const detailVisible = ref(false);
const currentOrder = ref(null);
const canCreateOrder = computed(() => auth.role === "salesperson");

const statusOptions = [
  { label: "待付款", value: "pending_payment" },
  { label: "已下单", value: "ordered" },
  { label: "配送中", value: "delivering" },
  { label: "已收货", value: "completed" },
];

const formatDateTime = (value) => {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
};
const formatMoney = (value) => `￥${Number(value || 0).toFixed(2)}`;
const statusTagType = (status) => ({ pending_payment: "warning", ordered: "info", delivering: "primary", completed: "success" }[status] || "info");
const statusIndex = (status) => ({ pending_payment: 0, ordered: 1, delivering: 2, completed: 3 }[status] ?? 1);

const loadSales = async () => {
  const params = {};
  if (keyword.value) params.search = keyword.value;
  if (statusFilter.value) params.status = statusFilter.value;
  const { data } = await getSalesApi(params);
  sales.value = data;
};

const resetFilters = () => {
  keyword.value = "";
  statusFilter.value = "";
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

.order-steps {
  margin-bottom: 20px;
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
  border-radius: 18px;
  background: #fbfdff;
}

.detail-title {
  margin-bottom: 12px;
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
}

.review-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
  color: #475569;
}

.review-box p {
  margin: 0;
  line-height: 1.7;
}

.review-box span {
  color: #94a3b8;
  font-size: 13px;
}

@media (max-width: 980px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
