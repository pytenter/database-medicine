<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">厂商管理</h3>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="输入厂商名称搜索" style="width: 260px;" clearable @keyup.enter="loadManufacturers" />
        <el-button @click="loadManufacturers">查询</el-button>
        <el-button type="primary" @click="openDialog()">新增厂商</el-button>
      </div>
    </div>

    <el-table :data="manufacturers" border>
      <el-table-column prop="name" label="厂商名称" min-width="220" />
      <el-table-column prop="contact_person" label="联系人" min-width="120" />
      <el-table-column prop="contact_phone" label="联系电话" min-width="160" />
      <el-table-column prop="created_at" label="创建时间" min-width="180">
        <template #default="scope">{{ formatDateTime(scope.row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">编辑</el-button>
          <el-button link type="danger" @click="removeManufacturer(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑厂商' : '新增厂商'" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="厂商名称 ⭐️"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact_person" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.contact_phone" /></el-form-item>
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

import {
  createManufacturerApi,
  deleteManufacturerApi,
  getManufacturersApi,
  updateManufacturerApi,
} from "../api/medicines";

const manufacturers = ref([]);
const keyword = ref("");
const dialogVisible = ref(false);
const editingId = ref(null);
const form = reactive({ name: "", contact_person: "", contact_phone: "" });

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, { name: "", contact_person: "", contact_phone: "" });
};

const formatDateTime = (value) => {
  if (!value) return "-";
  return value.slice(0, 16).replace("T", " ");
};

const loadManufacturers = async () => {
  const params = keyword.value ? { search: keyword.value } : {};
  const { data } = await getManufacturersApi(params);
  manufacturers.value = data;
};

const openDialog = (row = null) => {
  resetForm();
  if (row) {
    editingId.value = row.id;
    Object.assign(form, {
      name: row.name,
      contact_person: row.contact_person,
      contact_phone: row.contact_phone,
    });
  }
  dialogVisible.value = true;
};

const submitForm = async () => {
  if (!form.name.trim()) {
    ElMessage.warning("请填写厂商名称。");
    return;
  }
  try {
    if (editingId.value) {
      await updateManufacturerApi(editingId.value, form);
      ElMessage.success("厂商信息更新成功。");
    } else {
      await createManufacturerApi(form);
      ElMessage.success("厂商创建成功。");
    }
    dialogVisible.value = false;
    loadManufacturers();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "保存厂商失败。");
  }
};

const removeManufacturer = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认删除厂商 ${row.name} 吗？删除后将从当前列表隐藏，历史采购和药品数据会保留。`,
      "提示",
      { type: "warning", confirmButtonText: "确认删除", cancelButtonText: "取消" },
    );
    const { data } = await deleteManufacturerApi(row.id);
    ElMessage.success(data?.detail || "厂商已从当前列表隐藏，历史采购和药品数据保留。");
    loadManufacturers();
  } catch (error) {
    if (error === "cancel") return;
    ElMessage.error(error.response?.data?.detail || "删除厂商失败。");
  }
};

onMounted(loadManufacturers);
</script>

<style scoped>
.page-box {
  padding: 22px;
}
</style>
