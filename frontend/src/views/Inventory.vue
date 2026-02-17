<template>
  <div class="grid">
    <div class="card box">
      <div class="row">
        <div class="h">库存台账</div>
        <div class="spacer"></div>
        <el-button @click="load">刷新</el-button>
      </div>

      <el-table :data="inventory" style="width: 100%; margin-top: 10px" height="560">
        <el-table-column prop="material_code" label="物料编码" width="160" />
        <el-table-column prop="material_name" label="物料名称" min-width="240" />
        <el-table-column prop="unit" label="单位" width="90" />
        <el-table-column prop="on_hand" label="现存" width="90" />
        <el-table-column prop="reserved" label="预留" width="90" />
        <el-table-column prop="available" label="可用" width="90" />
        <el-table-column label="预警" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.on_hand < (row.safety_stock||0)" type="danger" effect="dark">低库存</el-tag>
            <el-tag v-else type="success" effect="dark">正常</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="card box">
      <div class="h">入库</div>
      <div class="muted" style="margin-top: 6px;">最小版本：只做手工入库（StockMove 记录为 MANUAL/IN）</div>

      <el-form :model="inForm" label-width="90px" style="margin-top: 12px;">
        <el-form-item label="选择物料">
          <el-select v-model="inForm.material_id" filterable style="width: 100%" placeholder="选择物料">
            <el-option
              v-for="x in inventory"
              :key="x.material_id"
              :label="`${x.material_code} / ${x.material_name}`"
              :value="x.material_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="入库数量">
          <el-input-number v-model="inForm.qty" :min="1" :step="1" style="width: 180px" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="doIn">确认入库</el-button>
        </el-form-item>
      </el-form>

      <div class="muted tip">发料在「生产任务」页面内按任务操作。</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { api } from "../api";
import { ElMessage } from "element-plus";

const inventory = ref([]);
const inForm = reactive({ material_id: null, qty: 1 });

async function load() {
  const res = await api.get("/inventory");
  inventory.value = res.data;
}

async function doIn() {
  try {
    await api.post("/inventory/in", inForm);
    ElMessage.success("入库成功");
    inForm.qty = 1;
    await load();
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || "入库失败");
  }
}

onMounted(load);
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1fr 420px; gap: 12px; }
.box { padding: 12px; }
.row { display: flex; align-items: center; gap: 10px; }
.h { font-weight: 800; }
.spacer { flex: 1; }
.muted { color: var(--muted); font-size: 12px; }
.tip { margin-top: 10px; }
@media (max-width: 1100px) { .grid { grid-template-columns: 1fr; } }
</style>
