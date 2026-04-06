<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">药店管理员管理</h3>
        <p class="page-subtitle">统一管理各门店管理员账号、状态和所属门店。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="输入用户名或姓名搜索" style="width: 260px;" clearable @keyup.enter="loadUsers" />
        <el-button @click="loadUsers">查询</el-button>
        <el-button type="primary" @click="openDialog()">新增药店管理员</el-button>
      </div>
    </div>

    <el-table :data="users" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户名" min-width="140" />
      <el-table-column prop="full_name" label="姓名" min-width="120" />
      <el-table-column prop="store_name" label="所属门店" min-width="140" />
      <el-table-column prop="phone" label="联系电话" min-width="140" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
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

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑药店管理员' : '新增药店管理员'" width="560px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" :disabled="Boolean(editingId)" />
        </el-form-item>
        <el-form-item label="密码" v-if="!editingId">
          <el-input v-model="form.password" show-password placeholder="默认密码为 Admin@123" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="所属门店">
          <el-select v-model="form.store" style="width: 100%;">
            <el-option v-for="store in stores" :key="store.id" :label="store.name" :value="store.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="启用状态">
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
const form = reactive({ username: "", password: "", full_name: "", role: "pharmacy_admin", phone: "", email: "", is_active: true, store: null });

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, { username: "", password: "", full_name: "", role: "pharmacy_admin", phone: "", email: "", is_active: true, store: null });
};

const loadUsers = async () => {
  const params = { role: "pharmacy_admin" };
  if (keyword.value) params.search = keyword.value;
  const { data } = await getUsersApi(params);
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
    Object.assign(form, { username: row.username, password: "", full_name: row.full_name, role: "pharmacy_admin", phone: row.phone, email: row.email, is_active: row.is_active, store: row.store });
  }
  dialogVisible.value = true;
};

const submitForm = async () => {
  const payload = { ...form, role: "pharmacy_admin" };
  if (!payload.password) delete payload.password;
  try {
    if (editingId.value) {
      await updateUserApi(editingId.value, payload);
      ElMessage.success("更新药店管理员成功");
    } else {
      await createUserApi(payload);
      ElMessage.success("新增药店管理员成功");
    }
    dialogVisible.value = false;
    loadUsers();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "保存用户失败");
  }
};

const deleteUser = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除用户 ${row.username} 吗？`, "提示", { type: "warning" });
    await deleteUserApi(row.id);
    ElMessage.success("删除用户成功");
    loadUsers();
  } catch (error) {
    if (error === "cancel") return;
    ElMessage.error(error.response?.data?.detail || "删除用户失败");
  }
};

const resetPassword = async (row) => {
  await resetPasswordApi(row.id);
  ElMessage.success(`已将 ${row.username} 的密码重置为 Admin@123。`);
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