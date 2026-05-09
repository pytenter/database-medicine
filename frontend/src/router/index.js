import { createRouter, createWebHistory } from "vue-router";

import MainLayout from "../layout/MainLayout.vue";
import AnnouncementManageView from "../views/AnnouncementManageView.vue";
import DashboardView from "../views/DashboardView.vue";
import InventoryView from "../views/InventoryView.vue";
import LoginView from "../views/LoginView.vue";
import ManufacturerManageView from "../views/ManufacturerManageView.vue";
import MedicineManageView from "../views/MedicineManageView.vue";
import PharmacyAdminManageView from "../views/PharmacyAdminManageView.vue";
import PurchaseOrderView from "../views/PurchaseOrderView.vue";
import RevenueComparisonView from "../views/RevenueComparisonView.vue";
import SaleCreateView from "../views/SaleCreateView.vue";
import SaleRecordView from "../views/SaleRecordView.vue";
import SalespersonManageView from "../views/SalespersonManageView.vue";
import ShiftScheduleView from "../views/ShiftScheduleView.vue";
import StoreManageView from "../views/StoreManageView.vue";

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
      { path: "", redirect: "/dashboard" },
      {
        path: "/dashboard",
        name: "dashboard",
        component: DashboardView,
        meta: { title: "首页概览", roles: ["system_admin", "pharmacy_admin", "salesperson"] },
      },
      {
        path: "/stores",
        name: "stores",
        component: StoreManageView,
        meta: { title: "药店管理", roles: ["system_admin"] },
      },
      {
        path: "/users/pharmacy-admins",
        name: "pharmacy-admins",
        component: PharmacyAdminManageView,
        meta: { title: "药店管理员管理", roles: ["system_admin"] },
      },
      {
        path: "/users/salespeople",
        name: "salespeople",
        component: SalespersonManageView,
        meta: { title: "销售人员管理", roles: ["system_admin"] },
      },
      {
        path: "/announcements",
        name: "announcements",
        component: AnnouncementManageView,
        meta: { title: "公告管理", roles: ["system_admin"] },
      },
      {
        path: "/revenue-comparison",
        name: "revenue-comparison",
        component: RevenueComparisonView,
        meta: { title: "营业额对比", roles: ["system_admin"] },
      },
      {
        path: "/manufacturers",
        name: "manufacturers",
        component: ManufacturerManageView,
        meta: { title: "厂商管理", roles: ["pharmacy_admin"] },
      },
      {
        path: "/medicines",
        name: "medicines",
        component: MedicineManageView,
        meta: { title: "药品管理", roles: ["pharmacy_admin", "salesperson"] },
      },
      {
        path: "/inventory",
        name: "inventory",
        component: InventoryView,
        meta: { title: "库存管理", roles: ["pharmacy_admin", "salesperson"] },
      },
      {
        path: "/purchase-orders",
        name: "purchase-orders",
        component: PurchaseOrderView,
        meta: { title: "采购订单", roles: ["pharmacy_admin"] },
      },
      {
        path: "/shift-schedules",
        name: "shift-schedules",
        component: ShiftScheduleView,
        meta: { title: "班次排班", roles: ["pharmacy_admin"] },
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
