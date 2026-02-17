/*
import { createRouter, createWebHistory } from "vue-router";
import MainLayout from "./layouts/MainLayout.vue";

import Molds from "./views/Molds.vue";
import Tasks from "./views/Tasks.vue";
import ReportMobile from "./views/ReportMobile.vue";

import Materials from "./views/Materials.vue";
import Products from "./views/Products.vue";
import Inventory from "./views/Inventory.vue";

const routes = [
  {
    path: "/",
    component: MainLayout,
    children: [
      { path: "", redirect: "/tasks" },

      { path: "tasks", component: Tasks },
      { path: "molds", component: Molds },

      // ✅ 放进布局里（侧边栏点击就一定能进去）
      { path: "report", component: ReportMobile },

      { path: "materials", component: Materials },
      { path: "products", component: Products },
      { path: "inventory", component: Inventory }
    ]
  }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
*/

import { createRouter, createWebHashHistory } from "vue-router";
import MainLayout from "./layouts/MainLayout.vue";

import Molds from "./views/Molds.vue";
import Tasks from "./views/Tasks.vue";
import ReportMobile from "./views/ReportMobile.vue";

import Materials from "./views/Materials.vue";
import Products from "./views/Products.vue";
import Inventory from "./views/Inventory.vue";

const routes = [
  {
    path: "/",
    component: MainLayout,
    children: [
      { path: "", redirect: "/tasks" },

      { path: "tasks", component: Tasks },
      { path: "molds", component: Molds },
      { path: "report", component: ReportMobile },
      { path: "materials", component: Materials },
      { path: "products", component: Products },
      { path: "inventory", component: Inventory }
    ]
  }
];

export default createRouter({
  history: createWebHashHistory(),  // ⭐ 改这里
  routes
});
