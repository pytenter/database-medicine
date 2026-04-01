<template>
  <div>
    <div class="page-card page-box">
      <div class="toolbar">
        <div>
          <h3 class="page-title">Medicine Management</h3>
          <p class="page-subtitle">Support fuzzy search by medicine name, manufacturer, or code.</p>
        </div>
        <div class="toolbar-actions">
          <el-input v-model="keyword" placeholder="Search medicine" style="width: 260px;" clearable @keyup.enter="loadMedicines" />
          <el-button @click="loadMedicines">Search</el-button>
          <el-button v-if="canEdit" type="success" @click="manufacturerDialog = true">New Manufacturer</el-button>
          <el-button v-if="canEdit" type="warning" @click="categoryDialog = true">New Category</el-button>
          <el-button v-if="canEdit" type="primary" @click="openDialog()">New Medicine</el-button>
        </div>
      </div>

      <el-table :data="medicines" border>
        <el-table-column prop="code" label="Code" width="140" />
        <el-table-column prop="name" label="Name" min-width="180" />
        <el-table-column prop="manufacturer_name" label="Manufacturer" min-width="160" />
        <el-table-column prop="category_name" label="Category" width="140" />
        <el-table-column prop="retail_price" label="Retail Price" width="120" />
        <el-table-column prop="expiry_date" label="Expiry Date" width="140" />
        <el-table-column label="Status" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">{{ scope.row.is_active ? 'Active' : 'Disabled' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="canEdit" label="Actions" width="160" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openDialog(scope.row)">Edit</el-button>
            <el-button link type="danger" @click="removeMedicine(scope.row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? 'Edit Medicine' : 'New Medicine'" width="680px">
      <el-form :model="form" label-width="140px">
        <el-form-item label="Code"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="Name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="Specification"><el-input v-model="form.specification" /></el-form-item>
        <el-form-item label="Unit"><el-input v-model="form.unit" /></el-form-item>
        <el-form-item label="Purchase Price"><el-input-number v-model="form.purchase_price" :min="0.01" :precision="2" style="width: 100%;" /></el-form-item>
        <el-form-item label="Retail Price"><el-input-number v-model="form.retail_price" :min="0.01" :precision="2" style="width: 100%;" /></el-form-item>
        <el-form-item label="Manufacturer">
          <el-select v-model="form.manufacturer" style="width: 100%;">
            <el-option v-for="item in manufacturers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="form.category" style="width: 100%;">
            <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Approval Number"><el-input v-model="form.approval_number" /></el-form-item>
        <el-form-item label="Production Date"><el-date-picker v-model="form.production_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" /></el-form-item>
        <el-form-item label="Expiry Date"><el-date-picker v-model="form.expiry_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" /></el-form-item>
        <el-form-item label="Status"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="manufacturerDialog" title="New Manufacturer" width="500px">
      <el-form :model="manufacturerForm" label-width="140px">
        <el-form-item label="Name"><el-input v-model="manufacturerForm.name" /></el-form-item>
        <el-form-item label="Contact Person"><el-input v-model="manufacturerForm.contact_person" /></el-form-item>
        <el-form-item label="Contact Phone"><el-input v-model="manufacturerForm.contact_phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="manufacturerDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitManufacturer">Save</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="categoryDialog" title="New Category" width="500px">
      <el-form :model="categoryForm" label-width="140px">
        <el-form-item label="Name"><el-input v-model="categoryForm.name" /></el-form-item>
        <el-form-item label="Description"><el-input v-model="categoryForm.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitCategory">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import {
  createCategoryApi,
  createManufacturerApi,
  createMedicineApi,
  deleteMedicineApi,
  getCategoriesApi,
  getManufacturersApi,
  getMedicinesApi,
  updateMedicineApi,
} from "../api/medicines";

const currentUser = JSON.parse(localStorage.getItem("current_user") || "null");
const canEdit = computed(() => ["system_admin", "pharmacy_admin"].includes(currentUser?.role));
const medicines = ref([]);
const manufacturers = ref([]);
const categories = ref([]);
const keyword = ref("");
const dialogVisible = ref(false);
const manufacturerDialog = ref(false);
const categoryDialog = ref(false);
const editingId = ref(null);
const form = reactive({
  code: "",
  name: "",
  specification: "",
  unit: "box",
  purchase_price: 10,
  retail_price: 12,
  manufacturer: null,
  category: null,
  approval_number: "",
  production_date: "",
  expiry_date: "",
  is_active: true,
});
const manufacturerForm = reactive({ name: "", contact_person: "", contact_phone: "" });
const categoryForm = reactive({ name: "", description: "" });

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, {
    code: "",
    name: "",
    specification: "",
    unit: "box",
    purchase_price: 10,
    retail_price: 12,
    manufacturer: null,
    category: null,
    approval_number: "",
    production_date: "",
    expiry_date: "",
    is_active: true,
  });
};

const loadMedicines = async () => {
  const { data } = await getMedicinesApi(keyword.value ? { search: keyword.value } : {});
  medicines.value = data;
};

const loadBaseData = async () => {
  const [{ data: manufacturersData }, { data: categoriesData }] = await Promise.all([
    getManufacturersApi(),
    getCategoriesApi(),
  ]);
  manufacturers.value = manufacturersData;
  categories.value = categoriesData;
};

const openDialog = (row = null) => {
  resetForm();
  if (row) {
    editingId.value = row.id;
    Object.assign(form, { ...row });
  }
  dialogVisible.value = true;
};

const submitForm = async () => {
  const payload = { ...form };
  if (editingId.value) {
    await updateMedicineApi(editingId.value, payload);
    ElMessage.success("Medicine updated.");
  } else {
    await createMedicineApi(payload);
    ElMessage.success("Medicine created.");
  }
  dialogVisible.value = false;
  loadMedicines();
};

const removeMedicine = async (row) => {
  await ElMessageBox.confirm(`Delete medicine ${row.name}?`, "Warning", { type: "warning" });
  await deleteMedicineApi(row.id);
  ElMessage.success("Medicine deleted.");
  loadMedicines();
};

const submitManufacturer = async () => {
  await createManufacturerApi(manufacturerForm);
  ElMessage.success("Manufacturer created.");
  manufacturerDialog.value = false;
  Object.assign(manufacturerForm, { name: "", contact_person: "", contact_phone: "" });
  loadBaseData();
};

const submitCategory = async () => {
  await createCategoryApi(categoryForm);
  ElMessage.success("Category created.");
  categoryDialog.value = false;
  Object.assign(categoryForm, { name: "", description: "" });
  loadBaseData();
};

onMounted(() => {
  loadMedicines();
  loadBaseData();
});
</script>

<style scoped>
.page-box {
  padding: 22px;
}
</style>
