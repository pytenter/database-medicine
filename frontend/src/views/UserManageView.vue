<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">用户管理</h3>
        <p class="page-subtitle">仅系统管理员可以管理药店管理员和销售人员。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="按用户名或姓名搜索" style="width: 260px;" clearable @keyup.enter="loadUsers" />
        <el-button @click="loadUsers">查询</el-button>
        <el-button type="primary" @click="openDialog()">新增用户</el-button>
      </div>
    </div>

    <el-table :data="users" border>
      <el-table-column prop="id" label="编号" width="70" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="full_name" label="姓名" />
      <el-table-column prop="role_display" label="角色" />
      <el-table-column prop="store_name" label="所属门店" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'info'">{{ scope.row.is_active ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">编辑</el-button>
          <el-button link type="warning" @click="resetPassword(scope.row)">重置密码</el-button>
          <el-button link type="danger" @click="deleteUser(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑用户' : '新增用户'" width="560px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="Boolean(editingId)" />
        </el-form-item>
        <el-form-item label="密码" v-if="!editingId">
          <el-input v-model="form.password" show-password placeholder="留空则默认 Admin@123" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width: 100%;">
            <el-option label="系统管理员" value="system_admin" />
            <el-option label="药店管理员" value="pharmacy_admin" />
            <el-option label="销售人员" value="salesperson" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属门店">
          <el-select v-model="form.store" style="width: 100%;" clearable :disabled="form.role === 'system_admin'">
            <el-option v-for="store in stores" :key="store.id" :label="store.name" :value="store.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
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

import { getStoresApi } from "../api/inventory";
import { createUserApi, deleteUserApi, getUsersApi, resetPasswordApi, updateUserApi } from "../api/users";

const users = ref([]);
const stores = ref([]);
const keyword = ref("");
const dialogVisible = ref(false);
const editingId = ref(null);
const form = reactive({
  username: "",
  password: "",
  full_name: "",
  role: "salesperson",
  phone: "",
  email: "",
  is_active: true,
  store: null,
});

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, {
    username: "",
    password: "",
    full_name: "",
    role: "salesperson",
    phone: "",
    email: "",
    is_active: true,
    store: null,
  });
};

const loadUsers = async () => {
  const { data } = await getUsersApi(keyword.value ? { search: keyword.value } : {});
  users.value = data;
};

const loadStores = async () => {
  const { data } = await getStoresApi();
  stores.value = data;
};

const openDialog = (row = null) => {
  resetForm();
  if (row) {
    editingId.value = row.id;
    Object.assign(form, {
      username: row.username,
      password: "",
      full_name: row.full_name,
      role: row.role,
      phone: row.phone,
      email: row.email,
      is_active: row.is_active,
      store: row.store,
    });
  }
  dialogVisible.value = true;
};

const submitForm = async () => {
  const payload = { ...form };
  if (!payload.password) {
    delete payload.password;
  }
  if (payload.role === "system_admin") {
    payload.store = null;
  }
  try {
    if (editingId.value) {
      await updateUserApi(editingId.value, payload);
      ElMessage.success("用户修改成功。");
    } else {
      await createUserApi(payload);
      ElMessage.success("用户创建成功。");
    }
    dialogVisible.value = false;
    loadUsers();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "操作失败。")
  }
};

const deleteUser = async (row) => {
  await ElMessageBox.confirm(`确认删除用户 ${row.username} 吗？`, "提示", { type: "warning" });
  await deleteUserApi(row.id);
  ElMessage.success("用户删除成功。");
  loadUsers();
};

const resetPassword = async (row) => {
  await resetPasswordApi(row.id);
  ElMessage.success(`用户 ${row.username} 的密码已重置为 Admin@123。`);
};

onMounted(() => {
  loadUsers();
  loadStores();
});
</script>

<style scoped>
.page-box {
  padding: 22px;
}
</style>
