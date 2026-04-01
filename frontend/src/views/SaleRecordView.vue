<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">销售记录</h3>
        <p class="page-subtitle">查看销售单及其明细内容。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="按订单号或顾客搜索" style="width: 260px;" clearable @keyup.enter="loadSales" />
        <el-button @click="loadSales">查询</el-button>
      </div>
    </div>

    <el-table :data="sales" border>
      <el-table-column prop="order_no" label="订单号" min-width="180" />
      <el-table-column prop="store_name" label="门店" min-width="140" />
      <el-table-column prop="salesperson_name" label="销售人员" min-width="140" />
      <el-table-column prop="customer_name" label="顾客姓名" min-width="140" />
      <el-table-column prop="total_amount" label="总金额" width="140" />
      <el-table-column prop="created_at" label="创建时间" min-width="180" />
      <el-table-column label="操作" width="110">
        <template #default="scope">
          <el-button link type="primary" @click="showDetail(scope.row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" title="销售单详情" width="760px">
      <el-descriptions v-if="currentOrder" :column="2" border style="margin-bottom: 16px;">
        <el-descriptions-item label="订单号">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="门店">{{ currentOrder.store_name }}</el-descriptions-item>
        <el-descriptions-item label="销售人员">{{ currentOrder.salesperson_name }}</el-descriptions-item>
        <el-descriptions-item label="顾客姓名">{{ currentOrder.customer_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="总金额">{{ currentOrder.total_amount }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentOrder.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="currentOrder?.items || []" border>
        <el-table-column prop="medicine_code" label="药品编码" width="130" />
        <el-table-column prop="medicine_name" label="药品名称" min-width="180" />
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="unit_price" label="单价" width="120" />
        <el-table-column prop="amount" label="金额" width="120" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getSalesApi } from "../api/sales";

const sales = ref([]);
const keyword = ref("");
const detailVisible = ref(false);
const currentOrder = ref(null);

const loadSales = async () => {
  const { data } = await getSalesApi(keyword.value ? { search: keyword.value } : {});
  sales.value = data;
};

const showDetail = (row) => {
  currentOrder.value = row;
  detailVisible.value = true;
};

onMounted(loadSales);
</script>

<style scoped>
.page-box {
  padding: 22px;
}
</style>
