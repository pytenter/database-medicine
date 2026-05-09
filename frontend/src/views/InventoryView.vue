<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">库存管理</h3>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="按药品名称或厂商搜索" style="width: 260px;" clearable @keyup.enter="loadInventory" />
        <el-button @click="loadInventory">查询</el-button>
        <el-button v-if="canEdit" type="primary" @click="openDialog()">新增库存</el-button>
      </div>
    </div>

    <el-table :data="inventoryRows" border>
      <el-table-column prop="store_name" label="所属门店" min-width="140" />
      <el-table-column prop="medicine_code" label="药品编码" width="130" />
      <el-table-column prop="medicine_name" label="药品名称" min-width="170" />
      <el-table-column prop="manufacturer_name" label="生产厂商" min-width="160" />
      <el-table-column prop="quantity" label="库存数量" width="100" />
      <el-table-column prop="warning_threshold" label="预警阈值" width="110" />
      <el-table-column label="预警状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_warning ? 'danger' : 'success'">{{ scope.row.is_warning ? '库存不足' : '正常' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="canEdit" label="操作" width="160" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">编辑</el-button>
          <el-button link type="danger" @click="removeRow(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑库存' : '新增库存'" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="所属门店">
          <el-input :model-value="currentUser?.store_name || '-'" disabled />
        </el-form-item>
        <el-form-item label="药品 ⭐️">
          <el-select v-model="form.medicine" filterable style="width: 100%;" :disabled="Boolean(editingId)">
            <el-option v-for="medicine in medicines" :key="medicine.id" :label="`${medicine.code} - ${medicine.name}`" :value="medicine.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="库存数量 ⭐️"><el-input-number v-model="form.quantity" :min="0" style="width: 100%;" /></el-form-item>
        <el-form-item label="预警阈值 ⭐️"><el-input-number v-model="form.warning_threshold" :min="0" style="width: 100%;" /></el-form-item>
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

import { getMedicinesApi } from "../api/medicines";
import { createInventoryApi, deleteInventoryApi, getInventoryApi, updateInventoryApi } from "../api/inventory";

const currentUser = JSON.parse(localStorage.getItem("current_user") || "null");
const canEdit = computed(() => currentUser?.role === "pharmacy_admin");
const inventoryRows = ref([]);
const medicines = ref([]);
const keyword = ref("");
const dialogVisible = ref(false);
const editingId = ref(null);
const form = reactive({ store: currentUser?.store || null, medicine: null, quantity: 0, warning_threshold: 10 });

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, { store: currentUser?.store || null, medicine: null, quantity: 0, warning_threshold: 10 });
};

const loadInventory = async () => {
  const { data } = await getInventoryApi(keyword.value ? { search: keyword.value } : {});
  inventoryRows.value = data;
};

const loadMedicines = async () => {
  const { data } = await getMedicinesApi();
  medicines.value = data;
};

const openDialog = (row = null) => {
  resetForm();
  if (row) {
    editingId.value = row.id;
    Object.assign(form, {
      store: row.store,
      medicine: row.medicine,
      quantity: row.quantity,
      warning_threshold: row.warning_threshold,
    });
  }
  dialogVisible.value = true;
};

const getSubmitErrorMessage = (error, fallback) => {
  const payload = error?.response?.data;
  if (!payload) return fallback;
  if (typeof payload.detail === "string") return payload.detail;
  const firstValue = Object.values(payload)[0];
  if (Array.isArray(firstValue) && firstValue.length) return String(firstValue[0]);
  if (typeof firstValue === "string") return firstValue;
  return fallback;
};

const submitForm = async () => {
  const payload = { ...form, store: currentUser?.store };
  if (!payload.store) {
    ElMessage.warning("当前账号未关联门店，无法维护库存。");
    return;
  }
  if (!payload.medicine) {
    ElMessage.warning("请选择药品。");
    return;
  }
  if (payload.quantity === null || payload.quantity === undefined || Number(payload.quantity) < 0) {
    ElMessage.warning("请填写不小于 0 的库存数量。");
    return;
  }
  if (payload.warning_threshold === null || payload.warning_threshold === undefined || Number(payload.warning_threshold) < 0) {
    ElMessage.warning("请填写不小于 0 的预警阈值。");
    return;
  }
  try {
    if (editingId.value) {
      await updateInventoryApi(editingId.value, payload);
      ElMessage.success("库存修改成功。");
    } else {
      await createInventoryApi(payload);
      ElMessage.success("库存已保存；若该药品已存在于当前门店，则已自动累加数量。");
    }
    dialogVisible.value = false;
    loadInventory();
  } catch (error) {
    ElMessage.error(getSubmitErrorMessage(error, "保存库存失败。"));
  }
};

const removeRow = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认删除 ${row.medicine_name} 的库存记录吗？删除后将从当前列表隐藏，历史订单信息会保留。`,
      "提示",
      { type: "warning", confirmButtonText: "确认删除", cancelButtonText: "取消" },
    );
    const { data } = await deleteInventoryApi(row.id);
    ElMessage.success(data?.detail || "库存记录已从当前列表隐藏，历史订单信息保留不受影响。");
    loadInventory();
  } catch (error) {
    if (error === "cancel") return;
    ElMessage.error(error.response?.data?.detail || "删除库存记录失败。");
  }
};

onMounted(() => {
  loadInventory();
  if (canEdit.value) {
    loadMedicines();
  }
});
</script>

<style scoped>
.page-box {
  padding: 22px;
}
</style>
