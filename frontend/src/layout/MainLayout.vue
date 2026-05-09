<template>
  <el-container style="min-height: 100vh;">
    <el-aside width="250px" class="aside-panel">
      <div class="brand-block">
        <div class="brand-mark">+</div>
        <div>
          <h1>连锁药店系统</h1>
        </div>
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
import { RouterView, useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const allMenus = [
  { path: "/dashboard", label: "首页概览", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
  { path: "/stores", label: "药店管理", roles: ["system_admin"] },
  { path: "/users/pharmacy-admins", label: "药店管理员管理", roles: ["system_admin"] },
  { path: "/users/salespeople", label: "销售人员管理", roles: ["system_admin"] },
  { path: "/announcements", label: "公告管理", roles: ["system_admin"] },
  { path: "/revenue-comparison", label: "营业额对比", roles: ["system_admin"] },
  { path: "/manufacturers", label: "厂商管理", roles: ["pharmacy_admin"] },
  { path: "/medicines", label: "药品管理", roles: ["pharmacy_admin", "salesperson"] },
  { path: "/inventory", label: "库存管理", roles: ["pharmacy_admin", "salesperson"] },
  { path: "/purchase-orders", label: "采购订单", roles: ["pharmacy_admin"] },
  { path: "/shift-schedules", label: "班次排班", roles: ["pharmacy_admin"] },
  { path: "/sales/create", label: "销售开单", roles: ["salesperson"] },
  { path: "/sales/records", label: "订单信息", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
];

const visibleMenus = computed(() => allMenus.filter((item) => item.roles.includes(auth.role)));
const currentTitle = computed(() => route.meta?.title || "首页概览");
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
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background:
    radial-gradient(circle at 30px 34px, rgba(45, 212, 191, 0.26), transparent 28px),
    radial-gradient(circle at 220px 118px, rgba(34, 197, 94, 0.18), transparent 70px),
    linear-gradient(180deg, #0f172a 0%, #10283a 48%, #0b3b37 100%);
  color: #f8fafc;
}

.aside-panel::before {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.055) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.8), transparent 78%);
  pointer-events: none;
}

.aside-panel::after {
  content: "";
  position: absolute;
  left: -40px;
  right: -40px;
  top: 146px;
  height: 160px;
  background: linear-gradient(135deg, transparent 18%, rgba(16, 185, 129, 0.18) 18%, rgba(16, 185, 129, 0.02) 54%, transparent 54%);
  transform: rotate(-8deg);
  pointer-events: none;
}

.brand-block {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 16px;
  margin-bottom: 20px;
  border-radius: 20px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.06)),
    rgba(15, 23, 42, 0.24);
  border: 1px solid rgba(209, 250, 229, 0.18);
  box-shadow: 0 18px 34px rgba(0, 0, 0, 0.16);
  backdrop-filter: blur(10px);
}

.brand-mark {
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: #064e3b;
  font-size: 32px;
  line-height: 1;
  font-weight: 800;
  background: linear-gradient(135deg, #d1fae5, #5eead4);
  box-shadow: 0 10px 22px rgba(45, 212, 191, 0.26);
}

.brand-block h1 {
  margin: 0;
  font-size: 20px;
  line-height: 1.15;
  white-space: nowrap;
  letter-spacing: 0;
}

.side-menu {
  position: relative;
  z-index: 1;
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
  position: relative;
  z-index: 1;
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.35);
}

.header-panel {
  display: flex;
  align-items: center;
  padding: 24px 28px 0;
}

.header-panel h2 {
  margin: 0;
  font-size: 34px;
  color: #0f172a;
}

.header-panel p {
  margin: 8px 0 0;
  color: #64748b;
}

.main-panel {
  padding: 24px 28px 28px;
}

@media (max-width: 960px) {
  .aside-panel {
    width: 210px;
    padding: 16px;
  }

  .brand-block h1 {
    font-size: 18px;
  }

  .header-panel h2 {
    font-size: 28px;
  }
}
</style>
