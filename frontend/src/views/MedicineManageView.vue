<template>
  <div>
    <div class="page-card page-box">
      <div class="toolbar">
        <div>
          <h3 class="page-title">药品管理</h3>
        </div>
        <div class="toolbar-actions">
          <el-input v-model="keyword" placeholder="请输入药品关键词" style="width: 260px;" clearable @keyup.enter="loadMedicines" />
          <el-button @click="loadMedicines">查询</el-button>
          <el-button v-if="canEdit" type="success" @click="manufacturerDialog = true">新增厂商</el-button>
          <el-button v-if="canEdit" type="warning" @click="categoryDialog = true">新增分类</el-button>
          <el-button v-if="canEdit" type="primary" @click="openDialog()">新增药品</el-button>
        </div>
      </div>

      <el-table :data="medicines" border>
        <el-table-column prop="code" label="药品编码" width="140" />
        <el-table-column prop="name" label="药品名称" min-width="180" />
        <el-table-column prop="manufacturer_name" label="生产厂商" min-width="160" />
        <el-table-column prop="category_name" label="分类" width="140" />
        <el-table-column prop="retail_price" label="零售价" width="120" />
        <el-table-column prop="expiry_date" label="有效期至" width="140" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">{{ scope.row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="canEdit" label="操作" width="160" fixed="right">
          <template #default="scope">
            <el-button link type="primary" @click="openDialog(scope.row)">编辑</el-button>
            <el-button link type="danger" @click="removeMedicine(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑药品' : '新增药品'" width="680px">
      <el-form :model="form" label-width="140px">
        <el-form-item label="药品编码"><el-input :model-value="editingId ? form.code : nextMedicineCode" disabled /></el-form-item>
        <el-form-item label="药品名称 ⭐️"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="规格 ⭐️"><el-input v-model="form.specification" /></el-form-item>
        <el-form-item label="单位 ⭐️"><el-input v-model="form.unit" /></el-form-item>
        <el-form-item label="进价 ⭐️"><el-input-number v-model="form.purchase_price" :min="0.01" :precision="2" style="width: 100%;" /></el-form-item>
        <el-form-item label="零售价 ⭐️"><el-input-number v-model="form.retail_price" :min="0.01" :precision="2" style="width: 100%;" /></el-form-item>
        <el-form-item label="生产厂商 ⭐️">
          <el-select v-model="form.manufacturer" style="width: 100%;">
            <el-option v-for="item in manufacturers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="药品分类 ⭐️">
          <el-select v-model="form.category" style="width: 100%;">
            <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="批准文号"><el-input v-model="form.approval_number" /></el-form-item>
        <el-form-item label="生产日期"><el-date-picker v-model="form.production_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" /></el-form-item>
        <el-form-item label="有效期至"><el-date-picker v-model="form.expiry_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="manufacturerDialog" title="新增厂商" width="500px">
      <el-form :model="manufacturerForm" label-width="140px">
        <el-form-item label="厂商名称 ⭐️"><el-input v-model="manufacturerForm.name" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="manufacturerForm.contact_person" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="manufacturerForm.contact_phone" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="manufacturerDialog = false">取消</el-button>
        <el-button type="primary" @click="submitManufacturer">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="categoryDialog" title="新增分类" width="500px">
      <el-form :model="categoryForm" label-width="140px">
        <el-form-item label="分类名称 ⭐️"><el-input v-model="categoryForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCategory">保存</el-button>
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
  getNextMedicineCodeApi,
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
const nextMedicineCode = ref("");
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
const categoryForm = reactive({ name: "" });

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

const ensureManufacturerOption = (row) => {
  if (!row?.manufacturer || !row?.manufacturer_name) return;
  const exists = manufacturers.value.some((item) => item.id === row.manufacturer);
  if (!exists) {
    manufacturers.value = [
      ...manufacturers.value,
      {
        id: row.manufacturer,
        name: `${row.manufacturer_name}（已隐藏）`,
      },
    ];
  }
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

const openDialog = async (row = null) => {
  resetForm();
  if (row) {
    ensureManufacturerOption(row);
    editingId.value = row.id;
    Object.assign(form, { ...row });
  } else {
    await loadNextMedicineCode();
  }
  dialogVisible.value = true;
};

const loadNextMedicineCode = async () => {
  const { data } = await getNextMedicineCodeApi();
  nextMedicineCode.value = data.code;
};

const submitForm = async () => {
  const payload = { ...form };
  if (!editingId.value) delete payload.code;
  if (!payload.name.trim()) {
    ElMessage.warning("请填写药品名称。");
    return;
  }
  if (!payload.specification.trim()) {
    ElMessage.warning("请填写药品规格。");
    return;
  }
  if (!payload.unit.trim()) {
    ElMessage.warning("请填写药品单位。");
    return;
  }
  if (!payload.manufacturer) {
    ElMessage.warning("请选择生产厂商。");
    return;
  }
  if (!payload.category) {
    ElMessage.warning("请选择药品分类。");
    return;
  }
  if (!payload.purchase_price || Number(payload.purchase_price) <= 0) {
    ElMessage.warning("请填写大于 0 的进价。");
    return;
  }
  if (!payload.retail_price || Number(payload.retail_price) <= 0) {
    ElMessage.warning("请填写大于 0 的零售价。");
    return;
  }
  try {
    if (editingId.value) {
      delete payload.code;
      await updateMedicineApi(editingId.value, payload);
      ElMessage.success("药品修改成功。");
    } else {
      await createMedicineApi(payload);
      ElMessage.success("药品创建成功。");
    }
    dialogVisible.value = false;
    loadMedicines();
    loadBaseData();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "保存药品失败。");
  }
};

const removeMedicine = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认删除药品 ${row.name} 吗？删除后将从当前列表隐藏，历史订单信息会保留。`,
      "提示",
      { type: "warning", confirmButtonText: "确认删除", cancelButtonText: "取消" },
    );
    const { data } = await deleteMedicineApi(row.id);
    ElMessage.success(data?.detail || "药品已从当前列表隐藏，历史订单信息保留不受影响。");
    loadMedicines();
  } catch (error) {
    if (error === "cancel") return;
    ElMessage.error(error.response?.data?.detail || "删除药品失败。");
  }
};

const submitManufacturer = async () => {
  if (!manufacturerForm.name.trim()) {
    ElMessage.warning("请填写厂商名称。");
    return;
  }
  try {
    await createManufacturerApi(manufacturerForm);
    ElMessage.success("厂商创建成功。");
    manufacturerDialog.value = false;
    Object.assign(manufacturerForm, { name: "", contact_person: "", contact_phone: "" });
    loadBaseData();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "保存厂商失败。");
  }
};

const submitCategory = async () => {
  if (!categoryForm.name.trim()) {
    ElMessage.warning("请填写分类名称。");
    return;
  }
  try {
    await createCategoryApi(categoryForm);
    ElMessage.success("分类创建成功。");
    categoryDialog.value = false;
    Object.assign(categoryForm, { name: "" });
    loadBaseData();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "保存分类失败。");
  }
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
