<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">库存管理</h3>
        <p class="page-subtitle">维护库存数量和预警阈值。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="按药品或门店搜索" style="width: 260px;" clearable @keyup.enter="loadInventory" />
        <el-button @click="loadInventory">查询</el-button>
        <el-button v-if="canEdit" type="primary" @click="openDialog()">新增库存</el-button>
      </div>
    </div>

    <el-table :data="inventoryRows" border>
      <el-table-column prop="store_name" label="门店" min-width="140" />
      <el-table-column prop="medicine_code" label="药品编码" width="120" />
      <el-table-column prop="medicine_name" label="药品名称" min-width="160" />
      <el-table-column prop="manufacturer_name" label="生产厂商" min-width="150" />
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
      <el-form :model="form" label-width="140px">
        <el-form-item label="门店">
          <el-select v-model="form.store" style="width: 100%;" :disabled="Boolean(editingId)">
            <el-option v-for="store in stores" :key="store.id" :label="store.name" :value="store.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="药品">
          <el-select v-model="form.medicine" filterable style="width: 100%;" :disabled="Boolean(editingId)">
            <el-option v-for="medicine in medicines" :key="medicine.id" :label="`${medicine.code} - ${medicine.name}`" :value="medicine.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="库存数量"><el-input-number v-model="form.quantity" :min="0" style="width: 100%;" /></el-form-item>
        <el-form-item label="预警阈值"><el-input-number v-model="form.warning_threshold" :min="0" style="width: 100%;" /></el-form-item>
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
import { createInventoryApi, deleteInventoryApi, getInventoryApi, getStoresApi, updateInventoryApi } from "../api/inventory";

const currentUser = JSON.parse(localStorage.getItem("current_user") || "null");
const canEdit = computed(() => ["system_admin", "pharmacy_admin"].includes(currentUser?.role));
const inventoryRows = ref([]);
const stores = ref([]);
const medicines = ref([]);
const keyword = ref("");
const dialogVisible = ref(false);
const editingId = ref(null);
const form = reactive({ store: null, medicine: null, quantity: 0, warning_threshold: 10 });

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, { store: null, medicine: null, quantity: 0, warning_threshold: 10 });
};

const loadInventory = async () => {
  const { data } = await getInventoryApi(keyword.value ? { search: keyword.value } : {});
  inventoryRows.value = data;
};

const loadReference = async () => {
  const [{ data: storeData }, { data: medicineData }] = await Promise.all([getStoresApi(), getMedicinesApi()]);
  stores.value = storeData;
  medicines.value = medicineData;
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

const submitForm = async () => {
  if (editingId.value) {
    await updateInventoryApi(editingId.value, form);
    ElMessage.success("库存修改成功。")
  } else {
    await createInventoryApi(form);
    ElMessage.success("库存创建成功。")
  }
  dialogVisible.value = false;
  loadInventory();
};

const removeRow = async (row) => {
  await ElMessageBox.confirm(`确认删除 ${row.medicine_name} 的库存记录吗？`, "提示", { type: "warning" });
  await deleteInventoryApi(row.id);
  ElMessage.success("库存记录删除成功。")
  loadInventory();
};

onMounted(() => {
  loadInventory();
  loadReference();
});
</script>

<style scoped>
.page-box {
  padding: 22px;
}
</style>
