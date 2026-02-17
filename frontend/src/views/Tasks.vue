<template>
  <div class="grid">
    <div class="card box">
      <div class="h">创建任务</div>
      <el-form :model="form" label-width="90px" style="margin-top: 10px">
        <el-form-item label="任务单号">
          <el-input v-model="form.task_no" placeholder="如 T-20260217-001" />
        </el-form-item>

        <el-form-item label="选择模具">
          <el-select v-model="form.mold_id" filterable style="width: 100%" placeholder="选择模具">
            <el-option
              v-for="m in molds"
              :key="m.id"
              :label="`${m.mold_code} / ${m.mold_name} (${m.status})`"
              :value="m.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="产品(可选)">
          <el-select v-model="form.product_id" filterable clearable style="width: 100%" placeholder="不选则不生成用料需求">
            <el-option
              v-for="p in products"
              :key="p.id"
              :label="`${p.product_code} / ${p.product_name}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="操作工">
          <el-input v-model="form.operator_name" placeholder="如 张三" />
        </el-form-item>

        <el-form-item label="目标数量">
          <el-input-number v-model="form.target_qty" :min="1" :step="1" style="width: 180px" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="createTask">创建</el-button>
          <el-button @click="reloadAll">刷新</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card box">
      <div class="row">
        <div class="h">任务列表</div>
        <div class="spacer"></div>
        <el-button @click="reloadAll">刷新</el-button>
      </div>

      <el-table :data="tasks" style="width: 100%; margin-top: 10px" height="560">
        <el-table-column prop="task_no" label="任务单号" width="170" />
        <el-table-column label="模具/产品" min-width="260">
          <template #default="{ row }">
            <div>{{ row.mold_code }} / {{ row.mold_name }}</div>
            <div class="muted" v-if="row.product_code">产品：{{ row.product_code }} / {{ row.product_name }}</div>
            <div class="muted">操作工：{{ row.operator_name }}</div>
          </template>
        </el-table-column>

        <el-table-column label="进度" width="220">
          <template #default="{ row }">
            <div class="muted">{{ row.done_qty }} / {{ row.target_qty }}</div>
            <el-progress :percentage="pct(row)" :stroke-width="10" />
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status==='已完成' ? 'success':'info'" effect="dark">{{ row.status }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="用料" width="140">
          <template #default="{ row }">
            <el-button size="small" :disabled="!row.product_id" @click="openMaterials(row)">
              查看/发料
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="muted tip">
        手机报工入口：/report（侧边栏也可进入）
      </div>
    </div>

    <!-- 任务用料抽屉 -->
    <el-drawer v-model="drawer" size="520px" :title="drawerTitle" direction="rtl">
      <div v-if="!drawerTask" class="muted">未选择任务</div>

      <template v-else>
        <div class="muted">
          任务：{{ drawerTask.task_no }} ｜ 产品：{{ drawerTask.product_code }} ｜ 目标：{{ drawerTask.target_qty }}
        </div>

        <el-table :data="taskMaterials" style="width: 100%; margin-top: 10px" height="360">
          <el-table-column prop="material_code" label="物料编码" width="150" />
          <el-table-column prop="material_name" label="物料名称" min-width="180" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column label="需求/已发" width="120">
            <template #default="{ row }">
              <div class="muted">{{ row.required_qty }} / {{ row.issued_qty }}</div>
            </template>
          </el-table-column>
          <el-table-column label="缺口" width="90">
            <template #default="{ row }">
              <el-tag v-if="row.shortage_qty>0" type="danger" effect="dark">{{ row.shortage_qty }}</el-tag>
              <el-tag v-else type="success" effect="dark">0</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="sep"></div>

        <div class="h2">按任务发料</div>
        <el-form :model="issueForm" label-width="90px" style="margin-top: 10px">
          <el-form-item label="物料">
            <el-select v-model="issueForm.material_id" filterable style="width: 100%">
              <el-option
                v-for="m in taskMaterials"
                :key="m.material_id"
                :label="`${m.material_code} / ${m.material_name}`"
                :value="m.material_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="数量">
            <el-input-number v-model="issueForm.qty" :min="1" :step="1" style="width: 180px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="issue">发料</el-button>
            <el-button @click="refreshDrawer">刷新用料</el-button>
          </el-form-item>
        </el-form>

        <div class="muted tip2">
          发料会扣减库存（/inventory 可查看），并累加 issued_qty。
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from "vue";
import { api } from "../api";
import { ElMessage } from "element-plus";

const molds = ref([]);
const products = ref([]);
const tasks = ref([]);

const form = reactive({
  task_no: "",
  mold_id: null,
  product_id: null,
  operator_name: "",
  target_qty: 1
});

function pct(row) {
  if (!row.target_qty) return 0;
  return Math.round((row.done_qty / row.target_qty) * 100);
}

async function loadMolds() {
  const res = await api.get("/molds");
  molds.value = res.data;
}
async function loadProducts() {
  const res = await api.get("/products");
  products.value = res.data;
}
async function loadTasks() {
  const res = await api.get("/tasks");
  tasks.value = res.data;
}
async function reloadAll() {
  await Promise.all([loadMolds(), loadProducts(), loadTasks()]);
}

async function createTask() {
  try {
    await api.post("/tasks", form);
    ElMessage.success("任务已创建");
    form.task_no = "";
    form.mold_id = null;
    form.product_id = null;
    form.operator_name = "";
    form.target_qty = 1;
    await reloadAll();
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || "创建失败");
  }
}

/* Drawer: task materials + issue */
const drawer = ref(false);
const drawerTask = ref(null);
const taskMaterials = ref([]);

const issueForm = reactive({ material_id: null, qty: 1 });

const drawerTitle = computed(() => drawerTask.value ? `任务用料｜${drawerTask.value.task_no}` : "任务用料");

async function openMaterials(taskRow) {
  drawerTask.value = taskRow;
  drawer.value = true;
  await refreshDrawer();
}

async function refreshDrawer() {
  if (!drawerTask.value) return;
  const res = await api.get(`/tasks/${drawerTask.value.id}/materials`);
  taskMaterials.value = res.data;
  issueForm.material_id = taskMaterials.value[0]?.material_id || null;
  issueForm.qty = 1;
}

async function issue() {
  try {
    if (!drawerTask.value) return;
    await api.post(`/tasks/${drawerTask.value.id}/issue`, issueForm);
    ElMessage.success("发料成功");
    await refreshDrawer();
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || "发料失败");
  }
}

onMounted(reloadAll);
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 380px 1fr; gap: 12px; }
.box { padding: 12px; }
.h { font-weight: 800; }
.row { display: flex; align-items: center; gap: 10px; }
.spacer { flex: 1; }
.muted { color: var(--muted); font-size: 12px; }
.tip { margin-top: 10px; }
.sep { height: 1px; background: var(--border); margin: 12px 0; }
.h2 { font-weight: 800; }
.tip2 { margin-top: 8px; }
@media (max-width: 1100px) { .grid { grid-template-columns: 1fr; } }
</style>

