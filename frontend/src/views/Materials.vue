<template>
  <div class="card box">
    <div class="row">
      <div class="spacer"></div>
      <el-button type="primary" @click="openCreate">新增物料</el-button>
      <el-button @click="load">刷新</el-button>
    </div>

    <el-table :data="materials" style="width: 100%; margin-top: 10px" height="560">
      <el-table-column prop="material_code" label="物料编码" width="160" />
      <el-table-column prop="material_name" label="物料名称" min-width="240" />
      <el-table-column prop="unit" label="单位" width="90" />
      <el-table-column prop="safety_stock" label="安全库存" width="110" />
      <el-table-column label="操作" width="170">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="dlgTitle" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="物料编码"><el-input v-model="form.material_code" /></el-form-item>
        <el-form-item label="物料名称"><el-input v-model="form.material_name" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.unit" placeholder="pcs / set / kg" /></el-form-item>
        <el-form-item label="安全库存"><el-input-number v-model="form.safety_stock" :min="0" /></el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dlg=false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { api } from "../api";
import { ElMessage, ElMessageBox } from "element-plus";

const materials = ref([]);
const dlg = ref(false);
const editingId = ref(null);

const form = reactive({
  material_code: "",
  material_name: "",
  unit: "pcs",
  safety_stock: 0
});

const dlgTitle = computed(() => (editingId.value ? "编辑物料" : "新增物料"));

async function load() {
  const res = await api.get("/materials");
  materials.value = res.data;
}

function openCreate() {
  editingId.value = null;
  Object.assign(form, { material_code: "", material_name: "", unit: "pcs", safety_stock: 0 });
  dlg.value = true;
}

function openEdit(row) {
  editingId.value = row.id;
  Object.assign(form, row);
  dlg.value = true;
}

async function save() {
  try {
    if (editingId.value) await api.put(`/materials/${editingId.value}`, form);
    else await api.post("/materials", form);
    dlg.value = false;
    await load();
    ElMessage.success("已保存");
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || "保存失败");
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(`确认删除物料 ${row.material_code}？`, "提示", { type: "warning" });
    await api.delete(`/materials/${row.id}`);
    await load();
    ElMessage.success("已删除");
  } catch {}
}

onMounted(load);
</script>

<style scoped>
.box { padding: 12px; }
.row { display: flex; gap: 10px; align-items: center; }
.spacer { flex: 1; }
</style>
