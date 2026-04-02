<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">公告管理</h3>
        <p class="page-subtitle">发布系统公告，供各门店管理员和销售人员查看。</p>
      </div>
      <div class="toolbar-actions">
        <el-input v-model="keyword" placeholder="输入公告标题搜索" style="width: 260px;" clearable @keyup.enter="loadAnnouncements" />
        <el-button @click="loadAnnouncements">查询</el-button>
        <el-button type="primary" @click="openDialog()">新增公告</el-button>
      </div>
    </div>

    <el-table :data="announcements" border>
      <el-table-column prop="title" label="公告标题" min-width="220" />
      <el-table-column prop="content" label="公告内容" min-width="420" show-overflow-tooltip />
      <el-table-column label="发布状态" width="110">
        <template #default="scope">
          <el-tag :type="scope.row.is_published ? 'success' : 'info'">{{ scope.row.is_published ? '已发布' : '草稿' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_by_name" label="发布人" width="120" />
      <el-table-column label="创建时间" width="170">
        <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">编辑</el-button>
          <el-button link type="danger" @click="deleteAnnouncement(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑公告' : '新增公告'" width="680px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="公告标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="公告内容">
          <el-input v-model="form.content" type="textarea" :rows="8" />
        </el-form-item>
        <el-form-item label="发布状态">
          <el-switch v-model="form.is_published" active-text="已发布" inactive-text="草稿" />
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

import { createAnnouncementApi, deleteAnnouncementApi, getAnnouncementsApi, updateAnnouncementApi } from "../api/announcements";

const announcements = ref([]);
const keyword = ref("");
const dialogVisible = ref(false);
const editingId = ref(null);
const form = reactive({ title: "", content: "", is_published: true });

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, { title: "", content: "", is_published: true });
};

const formatDate = (value) => String(value || "").replace("T", " ").split("+")[0].slice(0, 16);

const loadAnnouncements = async () => {
  const params = {};
  if (keyword.value) params.search = keyword.value;
  const { data } = await getAnnouncementsApi(params);
  announcements.value = data;
};

const openDialog = (row = null) => {
  resetForm();
  if (row) {
    editingId.value = row.id;
    Object.assign(form, { title: row.title, content: row.content, is_published: row.is_published });
  }
  dialogVisible.value = true;
};

const submitForm = async () => {
  try {
    if (editingId.value) {
      await updateAnnouncementApi(editingId.value, form);
      ElMessage.success("æ´æ°å¬åæå");
    } else {
      await createAnnouncementApi(form);
      ElMessage.success("æ°å¢å¬åæå");
    }
    dialogVisible.value = false;
    loadAnnouncements();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "ä¿å­å¬åå¤±è´¥");
  }
};

const deleteAnnouncement = async (row) => {
  await ElMessageBox.confirm(`ç¡®è®¤å é¤å¬åâ${row.title}âåï¼`, "æç¤º", { type: "warning" });
  await deleteAnnouncementApi(row.id);
  ElMessage.success("å é¤å¬åæå");
  loadAnnouncements();
};

onMounted(loadAnnouncements);
</script>

<style scoped>
.page-box {
  padding: 22px;
}
</style>
