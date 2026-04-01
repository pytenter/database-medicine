import { createRouter, createWebHistory } from "vue-router";

import MainLayout from "../layout/MainLayout.vue";
import DashboardView from "../views/DashboardView.vue";
import InventoryView from "../views/InventoryView.vue";
import LoginView from "../views/LoginView.vue";
import MedicineManageView from "../views/MedicineManageView.vue";
import SaleCreateView from "../views/SaleCreateView.vue";
import SaleRecordView from "../views/SaleRecordView.vue";
import UserManageView from "../views/UserManageView.vue";

const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: { public: true },
  },
  {
    path: "/",
    component: MainLayout,
    children: [
      {
        path: "",
        redirect: "/dashboard",
      },
      {
        path: "/dashboard",
        name: "dashboard",
        component: DashboardView,
        meta: { title: "Dashboard", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
      },
      {
        path: "/users",
        name: "users",
        component: UserManageView,
        meta: { title: "User Management", roles: ["system_admin"] },
      },
      {
        path: "/medicines",
        name: "medicines",
        component: MedicineManageView,
        meta: { title: "Medicine Management", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
      },
      {
        path: "/inventory",
        name: "inventory",
        component: InventoryView,
        meta: { title: "Inventory Management", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
      },
      {
        path: "/sales/create",
        name: "sale-create",
        component: SaleCreateView,
        meta: { title: "Create Sale", roles: ["salesperson"] },
      },
      {
        path: "/sales/records",
        name: "sale-records",
        component: SaleRecordView,
        meta: { title: "Sales Records", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("access_token");
  const user = JSON.parse(localStorage.getItem("current_user") || "null");

  if (to.meta.public) {
    next();
    return;
  }

  if (!token || !user) {
    next("/login");
    return;
  }

  if (to.meta.roles && !to.meta.roles.includes(user.role)) {
    next("/dashboard");
    return;
  }

  next();
});

export default router;

