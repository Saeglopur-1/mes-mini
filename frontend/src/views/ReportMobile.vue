<template>
  <div class="wrap">
    <div class="panel card">
      <div class="title">生产报工</div>
      <div class="sub">输入任务单号 + 本次数量</div>

      <el-form :model="form" label-position="top" style="margin-top: 12px">
        <el-form-item label="任务单号 Task No.">
          <el-input v-model="form.task_no" placeholder="如 T-001" size="large" />
        </el-form-item>

        <el-form-item label="本次完工数量 Qty">
          <el-input-number v-model="form.qty" :min="1" :step="1" size="large" style="width: 100%" />
        </el-form-item>

        <el-button type="primary" size="large" style="width: 100%" @click="submit">
          提交报工
        </el-button>
      </el-form>

      <div v-if="result" class="result card">
        <div class="r1"><div class="k">任务</div><div class="v">{{ result.task.task_no }}（{{ result.task.status }}）</div></div>
        <div class="r1"><div class="k">进度</div><div class="v">{{ result.task.done_qty }} / {{ result.task.target_qty }}</div></div>
        <div class="r1"><div class="k">模具已使用</div><div class="v">{{ result.mold.used_count }} / {{ result.mold.total_life }}</div></div>
      </div>

      <div class="back">
        <a href="/" class="muted">返回PC端</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { api } from "../api";
import { ElMessage } from "element-plus";

const form = reactive({ task_no: "", qty: 1 });
const result = ref(null);

async function submit() {
  try {
    const res = await api.post("/report", form);
    result.value = res.data;
    ElMessage.success("报工成功");
    form.qty = 1;
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || "报工失败");
  }
}
</script>

<style scoped>
.wrap { min-height: 100%; display: flex; align-items: center; justify-content: center; padding: 18px; }
.panel { width: min(480px, 100%); padding: 14px; }
.title { font-size: 18px; font-weight: 900; }
.sub { font-size: 12px; color: var(--muted); margin-top: 4px; }
.result { margin-top: 12px; padding: 12px; border: 1px solid var(--border); background: var(--panel2); }
.r1 { display: flex; justify-content: space-between; gap: 10px; padding: 6px 0; }
.k { color: var(--muted); font-size: 12px; }
.v { font-weight: 800; }
.back { margin-top: 12px; text-align: center; }
.muted { color: var(--muted); font-size: 12px; }
</style>

