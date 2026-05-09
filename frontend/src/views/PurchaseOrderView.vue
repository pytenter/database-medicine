<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">采购订单</h3>
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
      <el-table-column prop="order_no" label="采购单号" min-width="170" />
      <el-table-column prop="manufacturer_name" label="厂商名称" min-width="160" />
      <el-table-column prop="item_summary" label="采购内容" min-width="220" />
      <el-table-column prop="purchaser_name" label="采购人" min-width="120" />
      <el-table-column prop="planned_date" label="计划到货" width="120" />
      <el-table-column prop="total_amount" label="采购金额" width="120">
        <template #default="scope">{{ formatMoney(scope.row.total_amount) }}</template>
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

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑采购单' : '新增采购单'" width="900px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="采购单号"><el-input :model-value="editingId ? form.order_no : nextOrderNo" disabled /></el-form-item>
        <el-form-item label="厂商名称 ⭐️">
          <el-select v-model="form.manufacturer" style="width: 100%;" @change="handleManufacturerChange">
            <el-option v-for="item in manufacturers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="采购人 ⭐️"><el-input v-model="form.purchaser_name" /></el-form-item>
        <el-form-item label="计划到货"><el-date-picker v-model="form.planned_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" /></el-form-item>
        <el-form-item label="采购金额"><el-input :model-value="formatMoney(computedTotal)" disabled /></el-form-item>
        <el-form-item label="采购状态 ⭐️">
          <el-select v-model="form.status" style="width: 100%;">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="采购明细 ⭐️" class="items-form-item">
          <div class="items-editor">
            <el-table :data="form.item_details" border>
              <el-table-column label="药品" min-width="220">
                <template #default="scope">
                  <el-select v-model="scope.row.medicine" filterable placeholder="选择药品" style="width: 100%;" @change="syncSelectedMedicine(scope.row)">
                    <el-option
                      v-for="medicine in filteredMedicines"
                      :key="medicine.id"
                      :label="`${medicine.name} / ${medicine.specification}`"
                      :value="medicine.id"
                    />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="规格" min-width="130">
                <template #default="scope">{{ scope.row.specification || "-" }}</template>
              </el-table-column>
              <el-table-column label="进货价" width="110">
                <template #default="scope">{{ formatMoney(scope.row.unit_price) }}</template>
              </el-table-column>
              <el-table-column label="数量" width="150">
                <template #default="scope">
                  <el-input-number v-model="scope.row.quantity" :min="1" :step="1" step-strictly style="width: 120px;" />
                </template>
              </el-table-column>
              <el-table-column label="小计" width="120">
                <template #default="scope">{{ formatMoney(lineAmount(scope.row)) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="scope">
                  <el-button link type="danger" @click="removeItem(scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="items-actions">
              <el-button type="primary" plain @click="addItem">添加药品</el-button>
              <span class="total-text">合计：{{ formatMoney(computedTotal) }}</span>
            </div>
          </div>
        </el-form-item>
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
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import { getManufacturersApi, getMedicinesApi } from "../api/medicines";
import {
  createPurchaseOrderApi,
  deletePurchaseOrderApi,
  getNextPurchaseOrderNoApi,
  getPurchaseOrdersApi,
  updatePurchaseOrderApi,
} from "../api/inventory";

const currentUser = JSON.parse(localStorage.getItem("current_user") || "null");
const orders = ref([]);
const manufacturers = ref([]);
const medicines = ref([]);
const keyword = ref("");
const statusFilter = ref("");
const dialogVisible = ref(false);
const editingId = ref(null);
const nextOrderNo = ref("");
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
  status: "pending",
  item_details: [],
  remark: "",
});

const filteredMedicines = computed(() => {
  if (!form.manufacturer) return medicines.value;
  return medicines.value.filter((medicine) => medicine.manufacturer === form.manufacturer);
});

const computedTotal = computed(() => form.item_details.reduce((sum, item) => sum + lineAmount(item), 0));

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, {
    order_no: "",
    store: currentUser?.store || null,
    manufacturer: null,
    purchaser_name: currentUser?.full_name || "",
    planned_date: "",
    status: "pending",
    item_details: [],
    remark: "",
  });
};

const formatDateTime = (value) => {
  if (!value) return "-";
  return value.slice(0, 16).replace("T", " ");
};

const formatMoney = (value) => `¥${Number(value || 0).toFixed(2)}`;

const statusTagType = (status) => ({ pending: "warning", ordered: "primary", received: "success", cancelled: "info" }[status] || "info");

const lineAmount = (item) => Number(item.unit_price || 0) * Number(item.quantity || 0);

const loadOrders = async () => {
  const params = {};
  if (keyword.value) params.search = keyword.value;
  if (statusFilter.value) params.status = statusFilter.value;
  const { data } = await getPurchaseOrdersApi(params);
  orders.value = data;
};

const loadManufacturers = async () => {
  const [{ data: manufacturerData }, { data: medicineData }] = await Promise.all([
    getManufacturersApi(),
    getMedicinesApi(),
  ]);
  manufacturers.value = manufacturerData;
  medicines.value = medicineData;
};

const resetFilters = () => {
  keyword.value = "";
  statusFilter.value = "";
  loadOrders();
};

const openDialog = async (row = null) => {
  resetForm();
  if (row) {
    editingId.value = row.id;
    Object.assign(form, {
      order_no: row.order_no,
      store: row.store,
      manufacturer: row.manufacturer,
      purchaser_name: row.purchaser_name,
      planned_date: row.planned_date,
      status: row.status,
      item_details: (row.items || []).map((item) => ({
        medicine: item.medicine,
        medicine_name: item.medicine_name,
        specification: item.specification,
        unit: item.unit,
        unit_price: Number(item.unit_price),
        quantity: item.quantity,
      })),
      remark: row.remark,
    });
  } else {
    await loadNextOrderNo();
    addItem();
  }
  dialogVisible.value = true;
};

const loadNextOrderNo = async () => {
  const { data } = await getNextPurchaseOrderNoApi();
  nextOrderNo.value = data.order_no;
};

const addItem = () => {
  form.item_details.push({
    medicine: null,
    medicine_name: "",
    specification: "",
    unit: "",
    unit_price: 0,
    quantity: 1,
  });
};

const removeItem = (index) => {
  form.item_details.splice(index, 1);
};

const syncSelectedMedicine = (row) => {
  const medicine = medicines.value.find((item) => item.id === row.medicine);
  if (!medicine) return;
  row.medicine_name = medicine.name;
  row.specification = medicine.specification;
  row.unit = medicine.unit;
  row.unit_price = Number(medicine.purchase_price);
};

const handleManufacturerChange = () => {
  form.item_details = form.item_details.filter((item) => {
    const medicine = medicines.value.find((entry) => entry.id === item.medicine);
    return !medicine || medicine.manufacturer === form.manufacturer;
  });
  if (!form.item_details.length) addItem();
};

const submitForm = async () => {
  try {
    const payload = {
      store: currentUser?.store,
      manufacturer: form.manufacturer,
      purchaser_name: form.purchaser_name,
      planned_date: form.planned_date,
      status: form.status,
      remark: form.remark,
      item_details: form.item_details.map((item) => ({
        medicine: item.medicine,
        quantity: item.quantity,
      })),
    };
    if (!payload.store) {
      ElMessage.warning("当前账号未关联门店，无法创建采购单。");
      return;
    }
    if (!payload.manufacturer) {
      ElMessage.warning("请选择厂商。");
      return;
    }
    if (!payload.purchaser_name.trim()) {
      ElMessage.warning("请填写采购人。");
      return;
    }
    if (!payload.status) {
      ElMessage.warning("请选择采购状态。");
      return;
    }
    if (!payload.item_details.length || payload.item_details.some((item) => !item.medicine || !item.quantity || item.quantity <= 0)) {
      ElMessage.warning("请完整填写采购药品和数量。");
      return;
    }
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
    const data = error.response?.data;
    ElMessage.error(data?.detail || data?.item_details || "保存采购单失败。");
  }
};

const removeOrder = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除采购单 ${row.order_no} 吗？`, "提示", { type: "warning" });
    await deletePurchaseOrderApi(row.id);
    ElMessage.success("采购单已删除。");
    loadOrders();
  } catch (error) {
    if (error === "cancel") return;
    ElMessage.error(error.response?.data?.detail || "删除采购单失败。");
  }
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

.items-form-item :deep(.el-form-item__content) {
  display: block;
}

.items-editor {
  width: 100%;
}

.items-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.total-text {
  font-weight: 700;
  color: #0f172a;
}
</style>
