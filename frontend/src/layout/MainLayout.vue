<template>
  <el-container style="min-height: 100vh;">
    <el-aside width="250px" class="aside-panel">
      <div class="brand-block">
        <div class="brand-tag">数据库课程设计</div>
        <h1>药店管理系统</h1>
        <p>{{ auth.user?.full_name || auth.user?.username }}</p>
      </div>
      <el-menu :default-active="route.path" router class="side-menu">
        <el-menu-item v-for="item in visibleMenus" :key="item.path" :index="item.path">
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
      <div class="aside-footer">
        <span>{{ roleText }}</span>
        <el-button link type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </el-aside>
    <el-container>
      <el-header class="header-panel">
        <div>
          <h2>{{ currentTitle }}</h2>
          <p>基于 Vue、Django 和 openGauss 的连锁药店管理系统。</p>
        </div>
      </el-header>
      <el-main class="main-panel">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter, RouterView } from "vue-router";

import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const allMenus = [
  { path: "/dashboard", label: "系统首页", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
  { path: "/users", label: "用户管理", roles: ["system_admin"] },
  { path: "/stores", label: "药店管理", roles: ["system_admin", "pharmacy_admin"] },
  { path: "/medicines", label: "药品管理", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
  { path: "/inventory", label: "库存管理", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
  { path: "/sales/create", label: "销售开单", roles: ["salesperson"] },
  { path: "/sales/records", label: "销售记录", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
];

const visibleMenus = computed(() => allMenus.filter((item) => item.roles.includes(auth.role)));
const currentTitle = computed(() => route.meta?.title || "系统首页");
const roleText = computed(() => {
  const mapping = {
    system_admin: "系统管理员",
    pharmacy_admin: "药店管理员",
    salesperson: "销售人员",
  };
  return mapping[auth.role] || "未知角色";
});

const handleLogout = () => {
  auth.logout();
  router.push("/login");
};
</script>

<style scoped>
.aside-panel {
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: linear-gradient(180deg, #0f172a 0%, #12384a 100%);
  color: #f8fafc;
}

.brand-block {
  padding: 18px;
  margin-bottom: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
}

.brand-block h1 {
  margin: 10px 0 8px;
  font-size: 26px;
}

.brand-block p {
  margin: 0;
  color: rgba(248, 250, 252, 0.78);
}

.brand-tag {
  font-size: 12px;
  letter-spacing: 0.12em;
  color: #9ae6b4;
}

.side-menu {
  border-right: none;
  background: transparent;
}

.side-menu :deep(.el-menu-item) {
  color: rgba(248, 250, 252, 0.9);
  border-radius: 12px;
  margin-bottom: 8px;
}

.side-menu :deep(.el-menu-item.is-active) {
  background: rgba(16, 185, 129, 0.16);
  color: #d1fae5;
}

.aside-footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: rgba(248, 250, 252, 0.85);
}

.header-panel {
  display: flex;
  align-items: center;
  padding: 24px 30px 0;
}

.header-panel h2 {
  margin: 0;
  font-size: 28px;
}

.header-panel p {
  margin: 8px 0 0;
  color: #64748b;
}

.main-panel {
  padding: 22px 30px 30px;
}
</style>
