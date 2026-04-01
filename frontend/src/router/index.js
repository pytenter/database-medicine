import { createRouter, createWebHistory } from "vue-router";

import MainLayout from "../layout/MainLayout.vue";
import DashboardView from "../views/DashboardView.vue";
import InventoryView from "../views/InventoryView.vue";
import LoginView from "../views/LoginView.vue";
import LogisticsManageView from "../views/LogisticsManageView.vue";
import MedicineManageView from "../views/MedicineManageView.vue";
import OrderReviewView from "../views/OrderReviewView.vue";
import SaleCreateView from "../views/SaleCreateView.vue";
import SaleRecordView from "../views/SaleRecordView.vue";
import StoreManageView from "../views/StoreManageView.vue";
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
        meta: { title: "系统首页", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
      },
      {
        path: "/users",
        name: "users",
        component: UserManageView,
        meta: { title: "用户管理", roles: ["system_admin"] },
      },
      {
        path: "/stores",
        name: "stores",
        component: StoreManageView,
        meta: { title: "药店管理", roles: ["system_admin", "pharmacy_admin"] },
      },
      {
        path: "/medicines",
        name: "medicines",
        component: MedicineManageView,
        meta: { title: "药品管理", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
      },
      {
        path: "/inventory",
        name: "inventory",
        component: InventoryView,
        meta: { title: "库存管理", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
      },
      {
        path: "/sales/create",
        name: "sale-create",
        component: SaleCreateView,
        meta: { title: "销售开单", roles: ["salesperson"] },
      },
      {
        path: "/sales/records",
        name: "sale-records",
        component: SaleRecordView,
        meta: { title: "订单信息", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
      },
      {
        path: "/sales/logistics",
        name: "sale-logistics",
        component: LogisticsManageView,
        meta: { title: "物流信息", roles: ["salesperson"] },
      },
      {
        path: "/sales/reviews",
        name: "sale-reviews",
        component: OrderReviewView,
        meta: { title: "订单评价", roles: ["salesperson"] },
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
