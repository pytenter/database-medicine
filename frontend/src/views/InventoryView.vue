<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">Inventory Management</h3>
        <p class="page-subtitle">Maintain stock quantity and low-stock warning threshold.</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="Search medicine or store" style="width: 260px;" clearable @keyup.enter="loadInventory" />
        <el-button @click="loadInventory">Search</el-button>
        <el-button v-if="canEdit" type="primary" @click="openDialog()">New Inventory Row</el-button>
      </div>
    </div>

    <el-table :data="inventoryRows" border>
      <el-table-column prop="store_name" label="Store" min-width="140" />
      <el-table-column prop="medicine_code" label="Code" width="120" />
      <el-table-column prop="medicine_name" label="Medicine" min-width="160" />
      <el-table-column prop="manufacturer_name" label="Manufacturer" min-width="150" />
      <el-table-column prop="quantity" label="Quantity" width="100" />
      <el-table-column prop="warning_threshold" label="Threshold" width="110" />
      <el-table-column label="Warning" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_warning ? 'danger' : 'success'">{{ scope.row.is_warning ? 'Low' : 'Normal' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="canEdit" label="Actions" width="160" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">Edit</el-button>
          <el-button link type="danger" @click="removeRow(scope.row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? 'Edit Inventory' : 'New Inventory'" width="600px">
      <el-form :model="form" label-width="140px">
        <el-form-item label="Store">
          <el-select v-model="form.store" style="width: 100%;" :disabled="Boolean(editingId)">
            <el-option v-for="store in stores" :key="store.id" :label="store.name" :value="store.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Medicine">
          <el-select v-model="form.medicine" filterable style="width: 100%;" :disabled="Boolean(editingId)">
            <el-option v-for="medicine in medicines" :key="medicine.id" :label="`${medicine.code} - ${medicine.name}`" :value="medicine.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Quantity"><el-input-number v-model="form.quantity" :min="0" style="width: 100%;" /></el-form-item>
        <el-form-item label="Warning Threshold"><el-input-number v-model="form.warning_threshold" :min="0" style="width: 100%;" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save</el-button>
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
    ElMessage.success("Inventory updated.");
  } else {
    await createInventoryApi(form);
    ElMessage.success("Inventory created.");
  }
  dialogVisible.value = false;
  loadInventory();
};

const removeRow = async (row) => {
  await ElMessageBox.confirm(`Delete inventory row for ${row.medicine_name}?`, "Warning", { type: "warning" });
  await deleteInventoryApi(row.id);
  ElMessage.success("Inventory row deleted.");
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
