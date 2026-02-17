<template>
  <div class="card box">
    <div class="row">
      <el-button type="primary" @click="openCreate">新增模具</el-button>
      <el-button @click="load">刷新</el-button>
    </div>

    <el-table :data="molds" style="width: 100%; margin-top: 10px" height="520">
      <el-table-column prop="mold_code" label="编号" width="120" />
      <el-table-column prop="mold_name" label="名称" min-width="150" />
      <el-table-column prop="total_life" label="总寿命" width="100" />
      <el-table-column prop="used_count" label="已使用" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dlg" title="模具">
      <el-form :model="form" label-width="80px">
        <el-form-item label="编号">
          <el-input v-model="form.mold_code" />
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="form.mold_name" />
        </el-form-item>
        <el-form-item label="总寿命">
          <el-input-number v-model="form.total_life" :min="0" />
        </el-form-item>
        <el-form-item label="已使用">
          <el-input-number v-model="form.used_count" :min="0" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
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
import { ref, reactive, onMounted } from "vue";
import { api } from "../api";
import { ElMessage } from "element-plus";

const molds = ref([]);
const dlg = ref(false);
const editingId = ref(null);

const form = reactive({
  mold_code: "",
  mold_name: "",
  total_life: 0,
  used_count: 0,
  status: "空闲"
});

async function load() {
  const res = await api.get("/molds");
  molds.value = res.data;
}

function openCreate() {
  editingId.value = null;
  Object.assign(form, {
    mold_code: "",
    mold_name: "",
    total_life: 0,
    used_count: 0,
    status: "空闲"
  });
  dlg.value = true;
}

function openEdit(row) {
  editingId.value = row.id;
  Object.assign(form, row);
  dlg.value = true;
}

async function save() {
  try {
    if (editingId.value) {
      await api.put(`/molds/${editingId.value}`, form);
    } else {
      await api.post("/molds", form);
    }
    dlg.value = false;
    await load();
  } catch (e) {
    ElMessage.error("保存失败");
  }
}

async function remove(row) {
  await api.delete(`/molds/${row.id}`);
  await load();
}

onMounted(load);
</script>

<style scoped>
.box { padding: 12px; }
.row { display: flex; gap: 10px; }
</style>
