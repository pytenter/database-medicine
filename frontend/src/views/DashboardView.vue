<template>
  <div>
    <div class="toolbar">
      <div>
        <h3 class="page-title">Project Dashboard</h3>
        <p class="page-subtitle">Use this page to quickly show teacher the scope, roles, and core functions.</p>
      </div>
    </div>

    <el-row :gutter="18">
      <el-col :span="8" v-for="card in cards" :key="card.title">
        <div class="page-card metric-card">
          <span>{{ card.label }}</span>
          <h4>{{ card.title }}</h4>
          <p>{{ card.description }}</p>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="18" style="margin-top: 18px;">
      <el-col :span="14">
        <div class="page-card section-card">
          <h4>Function Checklist</h4>
          <el-timeline>
            <el-timeline-item timestamp="Admin">Manage users, roles, store assignment, and password reset.</el-timeline-item>
            <el-timeline-item timestamp="Pharmacy">Manage medicines, manufacturers, categories, and stock data.</el-timeline-item>
            <el-timeline-item timestamp="Sales">Search medicines, create sale orders, and view records.</el-timeline-item>
            <el-timeline-item timestamp="Database">Indexes, view, trigger, transaction, and permission design.</el-timeline-item>
          </el-timeline>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="page-card section-card">
          <h4>Current User</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Username">{{ auth.user?.username }}</el-descriptions-item>
            <el-descriptions-item label="Full Name">{{ auth.user?.full_name }}</el-descriptions-item>
            <el-descriptions-item label="Role">{{ auth.user?.role }}</el-descriptions-item>
            <el-descriptions-item label="Store">{{ auth.user?.store_name || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from "vue";

import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();

const cards = computed(() => [
  {
    label: "Role Coverage",
    title: "3 User Roles",
    description: "System administrator, pharmacy administrator, and salesperson.",
  },
  {
    label: "Core Modules",
    title: "5 Functional Areas",
    description: "Authentication, user management, medicine management, inventory, and sales.",
  },
  {
    label: "Database Focus",
    title: "openGauss Native SQL",
    description: "Schema, indexes, view, trigger, and seed data prepared for course submission.",
  },
]);
</script>

<style scoped>
.metric-card,
.section-card {
  padding: 22px;
}

.metric-card span {
  color: #0c7a5c;
  font-size: 13px;
  letter-spacing: 0.06em;
}

.metric-card h4 {
  margin: 10px 0 8px;
  font-size: 28px;
}

.metric-card p,
.section-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.section-card h4 {
  margin-top: 0;
  margin-bottom: 16px;
}
</style>
