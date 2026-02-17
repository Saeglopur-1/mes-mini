<template>
  <div class="wrap">
    <aside class="sidebar">
      <div class="brand">
        <div class="dot"></div>
        <div>
          <div class="title">MES Mini</div>
          <div class="sub">Mold Factory</div>
        </div>
      </div>

      <el-menu
        :default-active="active"
        class="menu"
        background-color="transparent"
        text-color="var(--text)"
        active-text-color="var(--text)"
        router
      >
        <el-menu-item index="/molds">模具管理</el-menu-item>
        <el-menu-item index="/tasks">生产任务</el-menu-item>
        <el-menu-item index="/report">手机报工</el-menu-item>
      </el-menu>
    </aside>

    <main class="main">
      <div class="topbar card">
        <div>
          <div class="h1">{{ pageTitle }}</div>
          <div class="h2">{{ pageHint }}</div>
        </div>
        <el-tag type="info" effect="dark">Phase 1</el-tag>
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
  if (route.path.startsWith("/molds")) return "模具管理";
  if (route.path.startsWith("/tasks")) return "生产任务";
  return "MES";
});

const pageHint = computed(() => {
  if (route.path.startsWith("/molds")) return "模具增删改查与寿命跟踪";
  if (route.path.startsWith("/tasks")) return "创建任务、查看进度";
  return "";
});
</script>

<style scoped>
.wrap {
  display: grid;
  grid-template-columns: 240px 1fr;
  height: 100%;
}

.sidebar {
  border-right: 1px solid var(--border);
  background: #0c0f13;
  padding: 14px 12px;
}

.brand {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px 10px 16px 10px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  background: #4b5563;
}

.title { font-weight: 700; }
.sub { font-size: 12px; color: var(--muted); }

.menu { border: 0; }

.main {
  padding: 16px;
  overflow: auto;
}

.topbar {
  padding: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.h1 { font-size: 16px; font-weight: 700; }
.h2 { font-size: 12px; color: var(--muted); }

.content { margin-top: 12px; }

@media (max-width: 900px) {
  .wrap { grid-template-columns: 1fr; }
  .sidebar { display: none; }
}
</style>
