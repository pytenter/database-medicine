<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">采购订单</h3>
        <p class="page-subtitle">为当前门店维护采购单、到货计划和采购状态。</p>
      </div>
      <div class="toolbar-actions toolbar-wrap">
        <el-input v-model="keyword" placeholder="按采购单号或厂商搜索" style="width: 260px;" clearable @keyup.enter="loadOrders" />
        <el-select v-model="statusFilter" clearable placeholder="采购状态" style="width: 160px;">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-button @click="loadOrders">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="openDialog()">新增采购单</el-button>
      </div>
    </div>

    <el-table :data="orders" border>
      <el-table-column prop="order_no" label="采购单号" min-width="160" />
      <el-table-column prop="manufacturer_name" label="厂商名称" min-width="160" />
      <el-table-column prop="item_summary" label="采购内容" min-width="220" />
      <el-table-column prop="purchaser_name" label="采购人" min-width="120" />
      <el-table-column prop="planned_date" label="计划到货" width="120" />
      <el-table-column prop="total_amount" label="采购金额" width="120">
        <template #default="scope">? {{ Number(scope.row.total_amount).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="status_display" label="采购状态" width="110">
        <template #default="scope">
          <el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" min-width="160">
        <template #default="scope">{{ formatDateTime(scope.row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">编辑</el-button>
          <el-button link type="danger" @click="removeOrder(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑采购单' : '新增采购单'" width="620px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="采购单号"><el-input v-model="form.order_no" :disabled="Boolean(editingId)" /></el-form-item>
        <el-form-item label="厂商名称">
          <el-select v-model="form.manufacturer" style="width: 100%;">
            <el-option v-for="item in manufacturers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="采购人"><el-input v-model="form.purchaser_name" /></el-form-item>
        <el-form-item label="计划到货"><el-date-picker v-model="form.planned_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" /></el-form-item>
        <el-form-item label="采购金额"><el-input-number v-model="form.total_amount" :min="0" :precision="2" style="width: 100%;" /></el-form-item>
        <el-form-item label="采购状态">
          <el-select v-model="form.status" style="width: 100%;">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="采购内容"><el-input v-model="form.item_summary" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import { getManufacturersApi } from "../api/medicines";
import {
  createPurchaseOrderApi,
  deletePurchaseOrderApi,
  getPurchaseOrdersApi,
  updatePurchaseOrderApi,
} from "../api/inventory";

const currentUser = JSON.parse(localStorage.getItem("current_user") || "null");
const orders = ref([]);
const manufacturers = ref([]);
const keyword = ref("");
const statusFilter = ref("");
const dialogVisible = ref(false);
const editingId = ref(null);
const statusOptions = [
  { value: "pending", label: "待采购" },
  { value: "ordered", label: "已下单" },
  { value: "received", label: "已入库" },
  { value: "cancelled", label: "已取消" },
];
const form = reactive({
  order_no: "",
  store: currentUser?.store || null,
  manufacturer: null,
  purchaser_name: currentUser?.full_name || "",
  planned_date: "",
  total_amount: 0,
  status: "pending",
  item_summary: "",
  remark: "",
});

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, {
    order_no: `PO${Date.now()}`,
    store: currentUser?.store || null,
    manufacturer: null,
    purchaser_name: currentUser?.full_name || "",
    planned_date: "",
    total_amount: 0,
    status: "pending",
    item_summary: "",
    remark: "",
  });
};

const formatDateTime = (value) => {
  if (!value) return "-";
  return value.slice(0, 16).replace("T", " ");
};

const statusTagType = (status) => ({ pending: "warning", ordered: "primary", received: "success", cancelled: "info" }[status] || "info");

const loadOrders = async () => {
  const params = {};
  if (keyword.value) params.search = keyword.value;
  if (statusFilter.value) params.status = statusFilter.value;
  const { data } = await getPurchaseOrdersApi(params);
  orders.value = data;
};

const loadManufacturers = async () => {
  const { data } = await getManufacturersApi();
  manufacturers.value = data;
};

const resetFilters = () => {
  keyword.value = "";
  statusFilter.value = "";
  loadOrders();
};

const openDialog = (row = null) => {
  resetForm();
  if (row) {
    editingId.value = row.id;
    Object.assign(form, {
      order_no: row.order_no,
      store: row.store,
      manufacturer: row.manufacturer,
      purchaser_name: row.purchaser_name,
      planned_date: row.planned_date,
      total_amount: Number(row.total_amount),
      status: row.status,
      item_summary: row.item_summary,
      remark: row.remark,
    });
  }
  dialogVisible.value = true;
};

const submitForm = async () => {
  try {
    const payload = { ...form, store: currentUser?.store };
    if (editingId.value) {
      await updatePurchaseOrderApi(editingId.value, payload);
      ElMessage.success("采购单更新成功。");
    } else {
      await createPurchaseOrderApi(payload);
      ElMessage.success("采购单创建成功。");
    }
    dialogVisible.value = false;
    loadOrders();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "保存采购单失败。");
  }
};

const removeOrder = async (row) => {
  await ElMessageBox.confirm(`确认删除采购单 ${row.order_no} 吗？`, "提示", { type: "warning" });
  await deletePurchaseOrderApi(row.id);
  ElMessage.success("采购单已删除。");
  loadOrders();
};

onMounted(() => {
  resetForm();
  loadOrders();
  loadManufacturers();
});
</script>

<style scoped>
.page-box {
  padding: 22px;
}

.toolbar-wrap {
  flex-wrap: wrap;
}
</style>
