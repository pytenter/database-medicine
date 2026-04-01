<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">User Management</h3>
        <p class="page-subtitle">Only system administrators can manage pharmacy administrators and salespersons.</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="Search username or full name" style="width: 260px;" clearable @keyup.enter="loadUsers" />
        <el-button @click="loadUsers">Search</el-button>
        <el-button type="primary" @click="openDialog()">New User</el-button>
      </div>
    </div>

    <el-table :data="users" border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="Username" />
      <el-table-column prop="full_name" label="Full Name" />
      <el-table-column prop="role" label="Role" />
      <el-table-column prop="store_name" label="Store" />
      <el-table-column prop="phone" label="Phone" />
      <el-table-column label="Status" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'info'">{{ scope.row.is_active ? 'Active' : 'Disabled' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="260" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">Edit</el-button>
          <el-button link type="warning" @click="resetPassword(scope.row)">Reset Password</el-button>
          <el-button link type="danger" @click="deleteUser(scope.row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? 'Edit User' : 'New User'" width="560px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="Username">
          <el-input v-model="form.username" :disabled="Boolean(editingId)" />
        </el-form-item>
        <el-form-item label="Password" v-if="!editingId">
          <el-input v-model="form.password" show-password placeholder="Default Admin@123 if blank" />
        </el-form-item>
        <el-form-item label="Full Name">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="Role">
          <el-select v-model="form.role" style="width: 100%;">
            <el-option label="System Administrator" value="system_admin" />
            <el-option label="Pharmacy Administrator" value="pharmacy_admin" />
            <el-option label="Salesperson" value="salesperson" />
          </el-select>
        </el-form-item>
        <el-form-item label="Store">
          <el-select v-model="form.store" style="width: 100%;" clearable :disabled="form.role === 'system_admin'">
            <el-option v-for="store in stores" :key="store.id" :label="store.name" :value="store.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="Status">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save</el-button>
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
      ElMessage.success("User updated.");
    } else {
      await createUserApi(payload);
      ElMessage.success("User created.");
    }
    dialogVisible.value = false;
    loadUsers();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "Operation failed.");
  }
};

const deleteUser = async (row) => {
  await ElMessageBox.confirm(`Delete user ${row.username}?`, "Warning", { type: "warning" });
  await deleteUserApi(row.id);
  ElMessage.success("User deleted.");
  loadUsers();
};

const resetPassword = async (row) => {
  await resetPasswordApi(row.id);
  ElMessage.success(`Password for ${row.username} has been reset to Admin@123.`);
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
