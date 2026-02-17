<template>
  <div class="card box">
    <div class="row">
      <el-input v-model="q" placeholder="搜索：编号/名称" style="max-width: 280px" @keyup.enter="load" />
      <div class="spacer"></div>
      <el-button type="primary" @click="openCreate">新增模具</el-button>
      <el-button @click="load">刷新</el-button>
    </div>

    <el-table :data="molds" style="width: 100%; margin-top: 10px" height="560">
      <el-table-column prop="mold_code" label="模具编号" width="140" />
      <el-table-column prop="mold_name" label="模具名称" min-width="200" />
      <el-table-column prop="total_life" label="总寿命" width="100" />
      <el-table-column prop="used_count" label="已使用" width="100" />
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="tagType(row.status)" effect="dark">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="170">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" :title="dlgTitle" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="模具编号"><el-input v-model="form.mold_code" /></el-form-item>
        <el-form-item label="模具名称"><el-input v-model="form.mold_name" /></el-form-item>
        <el-form-item label="总寿命"><el-input-number v-model="form.total_life" :min="0" /></el-form-item>
        <el-form-item label="已使用"><el-input-number v-model="form.used_count" :min="0" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 180px">
            <el-option label="空闲" value="空闲" />
            <el-option label="使用中" value="使用中" />
            <el-option label="维修" value="维修" />
          </el-select>
        </el-form-item>
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

const molds = ref([]);
const q = ref("");

const dlg = ref(false);
const editingId = ref(null);

const form = reactive({
  mold_code: "",
  mold_name: "",
  total_life: 0,
  used_count: 0,
  status: "空闲"
});

const dlgTitle = computed(() => (editingId.value ? "编辑模具" : "新增模具"));

function tagType(status) {
  if (status === "使用中") return "success";
  if (status === "维修") return "warning";
  return "info";
}

async function load() {
  const res = await api.get("/molds", { params: { q: q.value } });
  molds.value = res.data;
}

function openCreate() {
  editingId.value = null;
  Object.assign(form, { mold_code: "", mold_name: "", total_life: 0, used_count: 0, status: "空闲" });
  dlg.value = true;
}

function openEdit(row) {
  editingId.value = row.id;
  Object.assign(form, {
    mold_code: row.mold_code,
    mold_name: row.mold_name,
    total_life: row.total_life,
    used_count: row.used_count,
    status: row.status
  });
  dlg.value = true;
}

async function save() {
  try {
    if (editingId.value) await api.put(`/molds/${editingId.value}`, form);
    else await api.post("/molds", form);
    dlg.value = false;
    await load();
    ElMessage.success("已保存");
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || "保存失败");
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(`确认删除模具 ${row.mold_code}？`, "提示", { type: "warning" });
    await api.delete(`/molds/${row.id}`);
    await load();
    ElMessage.success("已删除");
  } catch {}
}

onMounted(load);
</script>

<style scoped>
.box { padding: 12px; }
.row { display: flex; align-items: center; gap: 10px; }
.spacer { flex: 1; }
</style>
