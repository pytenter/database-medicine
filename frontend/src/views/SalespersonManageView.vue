<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">销售人员管理</h3>
        <p class="page-subtitle">统一管理各门店销售人员账号、状态和所属门店。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="输入用户名或姓名搜索" style="width: 260px;" clearable @keyup.enter="loadUsers" />
        <el-button @click="loadUsers">查询</el-button>
        <el-button type="primary" @click="openDialog()">新增销售人员</el-button>
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
          <el-button link type="danger" :disabled="!scope.row.is_active" @click="deleteUser(scope.row)">{{ scope.row.is_active ? "停用" : "已停用" }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑销售人员' : '新增销售人员'" width="560px">
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
const form = reactive({ username: "", password: "", full_name: "", role: "salesperson", phone: "", email: "", is_active: true, store: null });

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, { username: "", password: "", full_name: "", role: "salesperson", phone: "", email: "", is_active: true, store: null });
};

const loadUsers = async () => {
  const params = { role: "salesperson", is_active: true };
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
    Object.assign(form, { username: row.username, password: "", full_name: row.full_name, role: "salesperson", phone: row.phone, email: row.email, is_active: row.is_active, store: row.store });
  }
  dialogVisible.value = true;
};

const submitForm = async () => {
  const payload = { ...form, role: "salesperson" };
  if (!payload.password) delete payload.password;
  try {
    if (editingId.value) {
      await updateUserApi(editingId.value, payload);
      ElMessage.success("更新销售人员成功");
    } else {
      await createUserApi(payload);
      ElMessage.success("新增销售人员成功");
    }
    dialogVisible.value = false;
    loadUsers();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "保存用户失败");
  }
};

const deleteUser = async (row) => {
  if (!row.is_active) {
    ElMessage.info("\u8be5\u8d26\u53f7\u5df2\u505c\u7528\u3002");
    return;
  }
  try {
    await ElMessageBox.confirm(`\u786e\u8ba4\u505c\u7528\u7528\u6237 ${row.username} \u5417\uff1f\u505c\u7528\u540e\u8be5\u8d26\u53f7\u5c06\u65e0\u6cd5\u767b\u5f55\uff0c\u4f46\u5386\u53f2\u4e1a\u52a1\u8bb0\u5f55\u4f1a\u4fdd\u7559\u3002`, "\u63d0\u793a", { type: "warning" });
    await deleteUserApi(row.id);
    await loadUsers();
    await ElMessageBox.alert("停用后，该账号已从当前销售人员列表中隐藏，历史销售记录会继续保留。", "停用成功", { type: "success" });
  } catch (error) {
    if (error === "cancel") return;
    ElMessage.error(error.response?.data?.detail || "\u505c\u7528\u7528\u6237\u5931\u8d25\u3002");
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