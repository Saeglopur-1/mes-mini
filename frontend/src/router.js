import { createRouter, createWebHistory } from "vue-router";
import MainLayout from "./layouts/MainLayout.vue";
import Molds from "./views/Molds.vue";
import Tasks from "./views/Tasks.vue";
import ReportMobile from "./views/ReportMobile.vue";

const routes = [
  {
    path: "/",
    component: MainLayout,
    children: [
      { path: "", redirect: "/molds" },
      { path: "molds", component: Molds },
      { path: "tasks", component: Tasks }
    ]
  },
  { path: "/report", component: ReportMobile }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
