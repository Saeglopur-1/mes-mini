<template>
  <div class="grid">
    <div class="card box">
      <div class="row">
        <div class="h">产品</div>
        <div class="spacer"></div>
        <el-button type="primary" @click="openCreateProduct">新增产品</el-button>
        <el-button @click="reload">刷新</el-button>
      </div>

      <el-table
        :data="products"
        style="width: 100%; margin-top: 10px"
        height="560"
        @row-click="selectProduct"
        highlight-current-row
      >
        <el-table-column prop="product_code" label="产品编码" width="160" />
        <el-table-column prop="product_name" label="产品名称" min-width="220" />
        <el-table-column prop="version" label="版本" width="120" />
        <el-table-column label="操作" width="170">
          <template #default="{ row }">
            <el-button size="small" @click.stop="openEditProduct(row)">编辑</el-button>
            <el-button size="small" type="danger" @click.stop="removeProduct(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="muted tip">点击某个产品行 → 右侧维护 BOM</div>
    </div>

    <div class="card box">
      <div class="row">
        <div class="h">BOM</div>
        <div class="spacer"></div>
        <el-button :disabled="!currentProduct" @click="openCsvImport">CSV导入</el-button>
        <el-button type="primary" :disabled="!currentProduct" @click="openAddBom">新增行</el-button>
      </div>

      <div v-if="!currentProduct" class="empty muted">
        请选择左侧一个产品
      </div>

      <template v-else>
        <div class="muted" style="margin-top: 8px;">
          当前产品：{{ currentProduct.product_code }} / {{ currentProduct.product_name }}
        </div>

        <el-table :data="bom" style="width: 100%; margin-top: 10px" height="520">
          <el-table-column prop="material_code" label="物料编码" width="160" />
          <el-table-column prop="material_name" label="物料名称" min-width="200" />
          <el-table-column prop="unit" label="单位" width="90" />
          <el-table-column prop="qty_per_unit" label="用量/件" width="110" />
          <el-table-column label="操作" width="130">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="removeBom(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>

      <!-- 产品弹窗 -->
      <el-dialog v-model="dlgProduct" :title="productDlgTitle" width="520px">
        <el-form :model="productForm" label-width="90px">
          <el-form-item label="产品编码"><el-input v-model="productForm.product_code" /></el-form-item>
          <el-form-item label="产品名称"><el-input v-model="productForm.product_name" /></el-form-item>
          <el-form-item label="版本"><el-input v-model="productForm.version" placeholder="可空" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dlgProduct=false">取消</el-button>
          <el-button type="primary" @click="saveProduct">保存</el-button>
        </template>
      </el-dialog>

      <!-- 新增BOM行 -->
      <el-dialog v-model="dlgBom" title="新增BOM行" width="560px">
        <el-form :model="bomForm" label-width="110px">
          <el-form-item label="选择物料">
            <el-select v-model="bomForm.material_id" filterable style="width: 100%" placeholder="选择物料">
              <el-option
                v-for="m in materials"
                :key="m.id"
                :label="`${m.material_code} / ${m.material_name}`"
                :value="m.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="用量/件 qty">
            <el-input-number v-model="bomForm.qty_per_unit" :min="1" :step="1" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dlgBom=false">取消</el-button>
          <el-button type="primary" @click="addBom">保存</el-button>
        </template>
      </el-dialog>

      <!-- CSV 导入 -->
      <el-dialog v-model="dlgCsv" title="CSV文本导入BOM" width="700px">
        <div class="muted">
          表头必须为：product_code,material_code,qty_per_unit
        </div>
        <el-input
          v-model="csvText"
          type="textarea"
          :rows="10"
          placeholder="product_code,material_code,qty_per_unit
P-001,STD-001,4
P-001,STD-002,2"
          style="margin-top: 10px;"
        />
        <template #footer>
          <el-button @click="dlgCsv=false">取消</el-button>
          <el-button type="primary" @click="importCsv">导入</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { api } from "../api";
import { ElMessage, ElMessageBox } from "element-plus";

const products = ref([]);
const materials = ref([]);
const bom = ref([]);

const currentProduct = ref(null);

const dlgProduct = ref(false);
const editingProductId = ref(null);
const productForm = reactive({ product_code: "", product_name: "", version: "" });
const productDlgTitle = computed(() => (editingProductId.value ? "编辑产品" : "新增产品"));

const dlgBom = ref(false);
const bomForm = reactive({ material_id: null, qty_per_unit: 1 });

const dlgCsv = ref(false);
const csvText = ref("");

async function loadProducts() {
  const res = await api.get("/products");
  products.value = res.data;
}
async function loadMaterials() {
  const res = await api.get("/materials");
  materials.value = res.data;
}
async function loadBom(productId) {
  const res = await api.get(`/products/${productId}/bom`);
  bom.value = res.data;
}

async function reload() {
  await Promise.all([loadProducts(), loadMaterials()]);
  if (currentProduct.value) await loadBom(currentProduct.value.id);
}

function selectProduct(row) {
  currentProduct.value = row;
  loadBom(row.id);
}

function openCreateProduct() {
  editingProductId.value = null;
  Object.assign(productForm, { product_code: "", product_name: "", version: "" });
  dlgProduct.value = true;
}
function openEditProduct(row) {
  editingProductId.value = row.id;
  Object.assign(productForm, { product_code: row.product_code, product_name: row.product_name, version: row.version || "" });
  dlgProduct.value = true;
}

async function saveProduct() {
  try {
    if (editingProductId.value) {
      await api.put(`/products/${editingProductId.value}`, productForm);
    } else {
      await api.post("/products", productForm);
    }
    dlgProduct.value = false;
    await loadProducts();
    ElMessage.success("已保存");
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || "保存失败");
  }
}

async function removeProduct(row) {
  try {
    await ElMessageBox.confirm(`确认删除产品 ${row.product_code}？（会同时删除BOM）`, "提示", { type: "warning" });
    await api.delete(`/products/${row.id}`);
    if (currentProduct.value?.id === row.id) {
      currentProduct.value = null;
      bom.value = [];
    }
    await loadProducts();
    ElMessage.success("已删除");
  } catch {}
}

function openAddBom() {
  if (!currentProduct.value) return;
  Object.assign(bomForm, { material_id: null, qty_per_unit: 1 });
  dlgBom.value = true;
}

async function addBom() {
  try {
    await api.post(`/products/${currentProduct.value.id}/bom`, bomForm);
    dlgBom.value = false;
    await loadBom(currentProduct.value.id);
    ElMessage.success("已保存");
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || "保存失败");
  }
}

async function removeBom(row) {
  try {
    await ElMessageBox.confirm(`删除 BOM 行：${row.material_code}？`, "提示", { type: "warning" });
    await api.delete(`/bom_items/${row.id}`);
    await loadBom(currentProduct.value.id);
    ElMessage.success("已删除");
  } catch {}
}

function openCsvImport() {
  if (!currentProduct.value) return;
  const p = currentProduct.value.product_code;
  csvText.value =
`product_code,material_code,qty_per_unit
${p},STD-001,1
`;
  dlgCsv.value = true;
}

async function importCsv() {
  try {
    const res = await api.post("/bom/import_csv", { csv: csvText.value });
    dlgCsv.value = false;
    await loadBom(currentProduct.value.id);
    ElMessage.success(`导入完成：created=${res.data.created}, updated=${res.data.updated}, skipped=${res.data.skipped}`);
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || "导入失败");
  }
}

onMounted(reload);
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1fr 1.3fr; gap: 12px; }
.box { padding: 12px; }
.row { display: flex; align-items: center; gap: 10px; }
.h { font-weight: 800; }
.spacer { flex: 1; }
.muted { color: var(--muted); font-size: 12px; }
.tip { margin-top: 10px; }
.empty { margin-top: 16px; padding: 14px; border: 1px dashed var(--border); border-radius: 10px; background: var(--panel2); }
@media (max-width: 1200px) { .grid { grid-template-columns: 1fr; } }
</style>
