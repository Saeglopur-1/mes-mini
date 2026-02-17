<template>
  <div class="card box">
    <el-form :model="form" label-width="80px">
      <el-form-item label="任务单号">
        <el-input v-model="form.task_no" />
      </el-form-item>

      <el-form-item label="模具">
        <el-select v-model="form.mold_id">
          <el-option
            v-for="m in molds"
            :key="m.id"
            :label="m.mold_code"
            :value="m.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="操作工">
        <el-input v-model="form.operator_name" />
      </el-form-item>

      <el-form-item label="目标数量">
        <el-input-number v-model="form.target_qty" :min="1" />
      </el-form-item>

      <el-button type="primary" @click="createTask">创建任务</el-button>
    </el-form>

    <el-table :data="tasks" style="margin-top: 20px;">
      <el-table-column prop="task_no" label="任务单号" />
      <el-table-column prop="operator_name" label="操作工" />
      <el-table-column label="进度">
        <template #default="{ row }">
          {{ row.done_qty }} / {{ row.target_qty }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { api } from "../api";

const molds = ref([]);
const tasks = ref([]);

const form = reactive({
  task_no: "",
  mold_id: null,
  operator_name: "",
  target_qty: 1
});

async function load() {
  const m = await api.get("/molds");
  molds.value = m.data;
  const t = await api.get("/tasks");
  tasks.value = t.data;
}

async function createTask() {
  await api.post("/tasks", form);
  await load();
}

onMounted(load);
</script>

<style scoped>
.box { padding: 12px; }
</style>
