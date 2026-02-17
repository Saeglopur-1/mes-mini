<template>
  <div class="wrap">
    <div class="card panel">
      <h2>生产报工</h2>

      <el-form :model="form" label-position="top">
        <el-form-item label="任务单号">
          <el-input v-model="form.task_no" />
        </el-form-item>

        <el-form-item label="数量">
          <el-input-number v-model="form.qty" :min="1" />
        </el-form-item>

        <el-button type="primary" @click="submit">提交</el-button>
      </el-form>

      <div v-if="result" class="result">
        <p>当前进度：{{ result.task.done_qty }} / {{ result.task.target_qty }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { api } from "../api";

const form = reactive({
  task_no: "",
  qty: 1
});

const result = ref(null);

async function submit() {
  const res = await api.post("/report", form);
  result.value = res.data;
}
</script>

<style scoped>
.wrap {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.panel {
  padding: 20px;
  width: 100%;
  max-width: 400px;
}
</style>
