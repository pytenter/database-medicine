<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">Sales Records</h3>
        <p class="page-subtitle">Review sale orders and their detail lines.</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="Search order number or customer" style="width: 260px;" clearable @keyup.enter="loadSales" />
        <el-button @click="loadSales">Search</el-button>
      </div>
    </div>

    <el-table :data="sales" border>
      <el-table-column prop="order_no" label="Order No" min-width="180" />
      <el-table-column prop="store_name" label="Store" min-width="140" />
      <el-table-column prop="salesperson_name" label="Salesperson" min-width="140" />
      <el-table-column prop="customer_name" label="Customer" min-width="140" />
      <el-table-column prop="total_amount" label="Total Amount" width="140" />
      <el-table-column prop="created_at" label="Created At" min-width="180" />
      <el-table-column label="Action" width="110">
        <template #default="scope">
          <el-button link type="primary" @click="showDetail(scope.row)">Detail</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" title="Sale Order Detail" width="760px">
      <el-descriptions v-if="currentOrder" :column="2" border style="margin-bottom: 16px;">
        <el-descriptions-item label="Order No">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="Store">{{ currentOrder.store_name }}</el-descriptions-item>
        <el-descriptions-item label="Salesperson">{{ currentOrder.salesperson_name }}</el-descriptions-item>
        <el-descriptions-item label="Customer">{{ currentOrder.customer_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Total Amount">{{ currentOrder.total_amount }}</el-descriptions-item>
        <el-descriptions-item label="Remark">{{ currentOrder.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="currentOrder?.items || []" border>
        <el-table-column prop="medicine_code" label="Medicine Code" width="130" />
        <el-table-column prop="medicine_name" label="Medicine Name" min-width="180" />
        <el-table-column prop="quantity" label="Quantity" width="100" />
        <el-table-column prop="unit_price" label="Unit Price" width="120" />
        <el-table-column prop="amount" label="Amount" width="120" />
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
