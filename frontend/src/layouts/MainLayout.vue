<template>
  <div class="wrap">
    <aside class="sidebar">
      <div class="brand">
        <div class="dot"></div>
        <div>
          <div class="title">MES Mini</div>
          <div class="sub">Phase 2 (MRP-lite)</div>
        </div>
      </div>

      <div class="group">执行</div>
      <el-menu
        :default-active="active"
        class="menu"
        background-color="transparent"
        text-color="var(--text)"
        active-text-color="var(--text)"
        router
      >
        <el-menu-item index="/tasks">生产任务</el-menu-item>
        <el-menu-item index="/molds">模具管理</el-menu-item>
        <el-menu-item index="/report">手机报工</el-menu-item>
      </el-menu>

      <div class="group">主数据/仓库</div>
      <el-menu
        :default-active="active"
        class="menu"
        background-color="transparent"
        text-color="var(--text)"
        active-text-color="var(--text)"
        router
      >
        <el-menu-item index="/materials">物料管理</el-menu-item>
        <el-menu-item index="/products">产品 & BOM</el-menu-item>
        <el-menu-item index="/inventory">库存台账</el-menu-item>
      </el-menu>
    </aside>

    <main class="main">
      <div class="topbar card">
        <div>
          <div class="h1">{{ pageTitle }}</div>
          <div class="h2">{{ pageHint }}</div>
        </div>
        <el-tag type="info" effect="dark">Phase 2</el-tag>
      </div>

      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
const route = useRoute();
const active = computed(() => route.path);

const pageTitle = computed(() => {
  if (route.path.startsWith("/tasks")) return "生产任务";
  if (route.path.startsWith("/molds")) return "模具管理";
  if (route.path.startsWith("/materials")) return "物料管理";
  if (route.path.startsWith("/products")) return "产品与BOM";
  if (route.path.startsWith("/inventory")) return "库存台账";
  return "MES";
});

const pageHint = computed(() => {
  if (route.path.startsWith("/tasks")) return "创建任务、自动生成用料需求、按任务发料";
  if (route.path.startsWith("/materials")) return "物料主数据（编码/单位/安全库存）";
  if (route.path.startsWith("/products")) return "维护产品、BOM（支持CSV文本导入）";
  if (route.path.startsWith("/inventory")) return "入库、查看可用量、低于安全库存预警";
  return "";
});
</script>

<style scoped>
.wrap { display: grid; grid-template-columns: 250px 1fr; height: 100%; }
.sidebar { border-right: 1px solid var(--border); background: var(--panel2); padding: 14px 12px; overflow: auto; }
.brand { display: flex; gap: 10px; align-items: center; padding: 8px 8px 14px 8px; }
.dot { width: 12px; height: 12px; border-radius: 3px; background: #4b5563; }
.title { font-weight: 800; letter-spacing: 0.2px; }
.sub { font-size: 12px; color: var(--muted); margin-top: 2px; }
.group { margin: 10px 8px 6px; font-size: 12px; color: var(--muted); }
.menu { border: 0; margin-bottom: 10px; }

.main { padding: 16px; overflow: auto; }
.topbar { padding: 14px; display: flex; justify-content: space-between; align-items: center; }
.h1 { font-size: 16px; font-weight: 800; }
.h2 { font-size: 12px; color: var(--muted); margin-top: 2px; }
.content { margin-top: 12px; }

@media (max-width: 900px) {
  .wrap { grid-template-columns: 1fr; }
  .sidebar { display: none; }
}
</style>
