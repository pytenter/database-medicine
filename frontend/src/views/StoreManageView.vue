<template>
  <div class="store-page">
    <section class="page-card store-hero">
      <div class="hero-copy">
        <span class="hero-tag">连锁门店网络</span>
        <h3>药店管理</h3>
        <p>统一维护连锁药店编码、负责人、联系方式与门店状态，并在地图面板中查看门店分布。</p>
      </div>
      <div class="hero-stats">
        <article class="hero-stat">
          <span>门店总数</span>
          <strong>{{ stats.total }}</strong>
        </article>
        <article class="hero-stat">
          <span>营业中</span>
          <strong>{{ stats.active }}</strong>
        </article>
        <article class="hero-stat">
          <span>暂停营业</span>
          <strong>{{ stats.inactive }}</strong>
        </article>
        <article class="hero-stat">
          <span>覆盖片区</span>
          <strong>{{ stats.regions }}</strong>
        </article>
      </div>
    </section>

    <section class="page-card panel-card list-card">
      <div class="toolbar store-toolbar">
        <div class="toolbar-copy">
          <h3 class="page-title">门店列表</h3>
          <p class="page-subtitle">支持按门店编码、名称、负责人和营业状态进行检索。</p>
        </div>
        <div class="toolbar-actions filter-group">
          <el-input
            v-model="filters.keyword"
            placeholder="输入门店编码或名称"
            class="filter-input"
            clearable
            @keyup.enter="loadStores"
          />
          <el-select v-model="filters.status" clearable placeholder="营业状态" class="filter-select">
            <el-option label="营业中" :value="true" />
            <el-option label="暂停营业" :value="false" />
          </el-select>
          <el-button @click="loadStores">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
          <el-button v-if="canEdit" type="primary" @click="openDialog()">新增门店</el-button>
        </div>
      </div>

      <div class="table-shell">
        <el-table :data="storeRows" border class="store-table">
          <el-table-column prop="code" label="门店编码" width="130" />
          <el-table-column prop="name" label="门店名称" min-width="180" />
          <el-table-column prop="manager_name" label="负责人" width="100" />
          <el-table-column prop="phone" label="联系方式" width="140" />
          <el-table-column label="营业状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'info'">
                {{ scope.row.is_active ? '营业中' : '暂停营业' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="address" label="门店地址" min-width="240" show-overflow-tooltip />
          <el-table-column label="创建时间" width="170">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="openDetail(scope.row)">详情</el-button>
              <el-button v-if="canEdit" link type="warning" @click="openDialog(scope.row)">编辑</el-button>
              <el-button v-if="canEdit" link type="danger" @click="removeStore(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>

    <section class="bottom-grid">
      <section class="page-card panel-card map-card">
        <div class="panel-head">
          <div>
            <h4>门店分布地图</h4>
            <p>演示版地图以静态定位方式展示不同门店所在片区。</p>
          </div>
          <span class="head-tag">地图总览</span>
        </div>
        <div class="map-board">
          <svg viewBox="0 0 560 340" class="map-svg">
            <defs>
              <linearGradient id="mapBg" x1="0" x2="1" y1="0" y2="1">
                <stop offset="0%" stop-color="#dff6ec" />
                <stop offset="100%" stop-color="#edf5ff" />
              </linearGradient>
            </defs>
            <rect x="0" y="0" width="560" height="340" rx="28" fill="url(#mapBg)" />
            <path d="M18 256 C118 180, 166 190, 238 122 S404 52, 540 102" class="road-major" />
            <path d="M30 86 C122 124, 194 130, 310 86 S470 66, 530 132" class="road-sub" />
            <path d="M68 302 C164 246, 280 252, 510 220" class="road-sub" />
            <path d="M168 36 C190 100, 218 178, 236 308" class="road-sub" />
            <path d="M356 22 C346 108, 332 184, 302 320" class="road-sub" />
            <circle cx="104" cy="72" r="36" class="zone zone-a" />
            <circle cx="420" cy="86" r="44" class="zone zone-b" />
            <circle cx="466" cy="262" r="58" class="zone zone-c" />
            <circle cx="172" cy="252" r="48" class="zone zone-d" />

            <g v-for="store in mapStores" :key="`map-${store.id}`">
              <line :x1="store.map.x" :y1="store.map.y + 8" :x2="store.map.x" :y2="store.map.y + 26" class="pin-shadow" />
              <circle :cx="store.map.x" :cy="store.map.y" r="16" :class="['pin-core', store.is_active ? 'pin-active' : 'pin-inactive']" />
              <path :d="pinPath(store.map.x, store.map.y)" :class="['pin-body', store.is_active ? 'pin-active' : 'pin-inactive']" />
              <circle :cx="store.map.x" :cy="store.map.y" r="5" class="pin-dot" />
              <text :x="store.map.x + 20" :y="store.map.y + 6" class="pin-label">{{ store.name }}</text>
            </g>
          </svg>
        </div>
        <div class="map-legend">
          <span><i class="legend-dot active"></i> 营业中</span>
          <span><i class="legend-dot inactive"></i> 暂停营业</span>
        </div>
      </section>

      <section
        v-for="store in featuredCards"
        :key="`featured-${store.id}`"
        class="page-card panel-card feature-card"
      >
        <div class="panel-head">
          <div>
            <h4>{{ store.meta.bannerLabel }}</h4>
            <p>{{ store.meta.region }} · 连锁药店重点展示</p>
          </div>
          <span class="head-tag">门店卡片</span>
        </div>
        <article class="showcase-item single-card">
          <div class="showcase-banner" :style="bannerStyle(store.id)">
            <span>{{ store.meta.bannerLabel }}</span>
          </div>
          <div class="showcase-copy">
            <div class="showcase-headline">
              <h5>{{ store.name }}</h5>
              <el-tag size="small" :type="store.is_active ? 'success' : 'info'">
                {{ store.is_active ? '营业中' : '暂停营业' }}
              </el-tag>
            </div>
            <p>{{ store.address }}</p>
            <div class="showcase-meta">
              <span>负责人：{{ store.manager_name || '待分配' }}</span>
              <span>联系电话：{{ store.phone || '未填写' }}</span>
              <span>营业时间：{{ store.meta.businessHours }}</span>
            </div>
          </div>
        </article>
      </section>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑门店' : '新增门店'" width="640px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="门店编码">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="门店名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="form.manager_name" />
        </el-form-item>
        <el-form-item label="联系方式">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="门店地址">
          <el-input v-model="form.address" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="营业状态">
          <el-switch v-model="form.is_active" active-text="营业中" inactive-text="暂停营业" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="药店详情" width="860px" class="detail-dialog">
      <template v-if="selectedStore">
        <div class="detail-layout">
          <section class="detail-section">
            <h4>药店信息</h4>
            <div class="detail-grid">
              <div class="detail-item"><span>门店名称：</span><strong>{{ selectedStore.name }}</strong></div>
              <div class="detail-item"><span>门店编码：</span><strong>{{ selectedStore.code }}</strong></div>
              <div class="detail-item"><span>营业状态：</span><strong :class="selectedStore.is_active ? 'text-success' : 'text-muted'">{{ selectedStore.is_active ? '营业中' : '暂停营业' }}</strong></div>
              <div class="detail-item"><span>负责人：</span><strong>{{ selectedStore.manager_name || '待分配' }}</strong></div>
              <div class="detail-item"><span>联系电话：</span><strong>{{ selectedStore.phone || '未填写' }}</strong></div>
              <div class="detail-item"><span>营业时间：</span><strong>{{ selectedStore.meta.businessHours }}</strong></div>
              <div class="detail-item detail-address"><span>详细地址：</span><strong>{{ selectedStore.address }}</strong></div>
              <div class="detail-item"><span>片区：</span><strong>{{ selectedStore.meta.region }}</strong></div>
            </div>
          </section>

          <section class="detail-section">
            <h4>药店图片</h4>
            <div class="photo-strip">
              <div class="photo-card photo-a">
                <span>门头外景</span>
              </div>
              <div class="photo-card photo-b">
                <span>夜间灯箱</span>
              </div>
            </div>
          </section>

          <section class="detail-section">
            <h4>药店位置</h4>
            <div class="detail-map">
              <svg viewBox="0 0 700 300" class="detail-map-svg">
                <rect x="0" y="0" width="700" height="300" rx="20" fill="#eef6ff" />
                <path d="M20 216 C128 138, 204 124, 326 94 S518 72, 680 136" class="road-major" />
                <path d="M84 40 C118 92, 136 156, 144 258" class="road-sub" />
                <path d="M320 24 C298 108, 284 192, 248 276" class="road-sub" />
                <path d="M506 34 C520 108, 548 180, 612 260" class="road-sub" />
                <g>
                  <circle :cx="selectedStore.map.x * 1.16" :cy="selectedStore.map.y * 0.86" r="20" :class="['pin-core', selectedStore.is_active ? 'pin-active' : 'pin-inactive']" />
                  <path :d="pinPath(selectedStore.map.x * 1.16, selectedStore.map.y * 0.86)" :class="['pin-body', selectedStore.is_active ? 'pin-active' : 'pin-inactive']" />
                  <circle :cx="selectedStore.map.x * 1.16" :cy="selectedStore.map.y * 0.86" r="6" class="pin-dot" />
                  <text :x="selectedStore.map.x * 1.16 + 26" :y="selectedStore.map.y * 0.86 + 6" class="pin-label large">{{ selectedStore.name }}</text>
                </g>
              </svg>
            </div>
          </section>
        </div>
      </template>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import { createStoreApi, deleteStoreApi, getStoresApi, updateStoreApi } from "../api/inventory";

const currentUser = JSON.parse(localStorage.getItem("current_user") || "null");
const canEdit = computed(() => ["system_admin", "pharmacy_admin"].includes(currentUser?.role));

const stores = ref([]);
const filters = reactive({
  keyword: "",
  status: "",
});
const dialogVisible = ref(false);
const detailVisible = ref(false);
const editingId = ref(null);
const selectedStore = ref(null);
const form = reactive({
  code: "",
  name: "",
  manager_name: "",
  phone: "",
  address: "",
  is_active: true,
});

const storeMetaMap = {
  default: {
    businessHours: "08:00-22:00",
    region: "主城区",
    bannerLabel: "标准化门头",
    map: { x: 180, y: 228 },
  },
  1: {
    businessHours: "08:00-22:00",
    region: "市中心片区",
    bannerLabel: "核心示范店",
    map: { x: 188, y: 224 },
  },
  2: {
    businessHours: "09:00-21:30",
    region: "东区社区片区",
    bannerLabel: "社区便民店",
    map: { x: 394, y: 118 },
  },
  3: {
    businessHours: "08:30-21:00",
    region: "南站片区",
    bannerLabel: "交通枢纽店",
    map: { x: 448, y: 246 },
  },
  4: {
    businessHours: "07:30-23:00",
    region: "西区片区",
    bannerLabel: "24小时值守店",
    map: { x: 128, y: 104 },
  },
};

const decorateStore = (store, index = 0) => {
  const fallbackMeta = {
    ...storeMetaMap.default,
    map: {
      x: 150 + (index % 3) * 120,
      y: 110 + Math.floor(index / 3) * 110,
    },
  };
  const meta = storeMetaMap[store.id] || fallbackMeta;
  return {
    ...store,
    meta,
    map: meta.map,
  };
};

const storeRows = computed(() => {
  let rows = stores.value.map((item, index) => decorateStore(item, index));
  if (filters.status !== "") {
    rows = rows.filter((item) => item.is_active === filters.status);
  }
  return rows;
});

const stats = computed(() => {
  const rows = storeRows.value;
  const active = rows.filter((item) => item.is_active).length;
  const regionSet = new Set(rows.map((item) => item.meta.region));
  return {
    total: rows.length,
    active,
    inactive: rows.length - active,
    regions: regionSet.size,
  };
});

const featuredStores = computed(() => storeRows.value.slice(0, 3));
const featuredCards = computed(() => {
  const primary = featuredStores.value[0];
  const secondary = featuredStores.value[1];
  return [primary, secondary].filter(Boolean);
});
const mapStores = computed(() => storeRows.value);

const formatDate = (value) => {
  if (!value) return "-";
  const raw = String(value).replace("T", " ").split("+")[0].split(".")[0];
  return raw.slice(0, 16);
};

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, {
    code: "",
    name: "",
    manager_name: "",
    phone: "",
    address: "",
    is_active: true,
  });
};

const bannerStyle = (id) => {
  const styles = {
    1: "linear-gradient(135deg, rgba(12,122,92,0.9), rgba(22,163,116,0.55)), linear-gradient(135deg, #bfe9d8, #e8fff5)",
    2: "linear-gradient(135deg, rgba(30,136,229,0.92), rgba(110,187,255,0.58)), linear-gradient(135deg, #dff0ff, #eff7ff)",
    3: "linear-gradient(135deg, rgba(249,115,22,0.92), rgba(255,191,115,0.55)), linear-gradient(135deg, #fff0dd, #fff7ed)",
  };
  return { background: styles[id] || "linear-gradient(135deg, rgba(12,122,92,0.9), rgba(89,185,152,0.55)), linear-gradient(135deg, #dff6ec, #f5fbff)" };
};

const pinPath = (x, y) => `M ${x} ${y + 18} C ${x - 12} ${y + 8}, ${x - 14} ${y - 10}, ${x} ${y - 18} C ${x + 14} ${y - 10}, ${x + 12} ${y + 8}, ${x} ${y + 18}`;

const loadStores = async () => {
  const params = {};
  if (filters.keyword) params.search = filters.keyword;
  const { data } = await getStoresApi(params);
  stores.value = data;
};

const resetFilters = async () => {
  filters.keyword = "";
  filters.status = "";
  await loadStores();
};

const openDialog = (row = null) => {
  resetForm();
  if (row) {
    editingId.value = row.id;
    Object.assign(form, {
      code: row.code,
      name: row.name,
      manager_name: row.manager_name,
      phone: row.phone,
      address: row.address,
      is_active: row.is_active,
    });
  }
  dialogVisible.value = true;
};

const openDetail = (row) => {
  selectedStore.value = row;
  detailVisible.value = true;
};

const submitForm = async () => {
  const payload = { ...form };
  if (editingId.value) {
    await updateStoreApi(editingId.value, payload);
    ElMessage.success("门店信息修改成功。");
  } else {
    await createStoreApi(payload);
    ElMessage.success("门店创建成功。");
  }
  dialogVisible.value = false;
  await loadStores();
};

const removeStore = async (row) => {
  await ElMessageBox.confirm(`确认删除门店 ${row.name} 吗？`, "提示", { type: "warning" });
  await deleteStoreApi(row.id);
  ElMessage.success("门店删除成功。");
  await loadStores();
};

onMounted(() => {
  loadStores();
});
</script>

<style scoped>
.store-page {
  display: grid;
  gap: 18px;
  width: 100%;
  min-width: 0;
}

.store-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  gap: 24px;
  padding: 26px 28px;
  background:
    radial-gradient(circle at top right, rgba(12, 122, 92, 0.12), transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f7fffb 54%, #f4fbff 100%);
}

.hero-copy {
  max-width: 560px;
}

.hero-tag,
.head-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: #eaf8f2;
  color: #0c7a5c;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.hero-copy h3 {
  margin: 12px 0 10px;
  font-size: 32px;
}

.hero-copy p {
  margin: 0;
  line-height: 1.8;
  color: #64748b;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  min-width: 0;
}

.hero-stat {
  padding: 18px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid #e6eef6;
  display: grid;
  gap: 10px;
}

.hero-stat span {
  color: #94a3b8;
  font-size: 13px;
}

.hero-stat strong {
  color: #16a36f;
  font-size: 30px;
}

.panel-card {
  padding: 22px;
  min-width: 0;
}

.store-toolbar {
  align-items: flex-start;
  flex-wrap: wrap;
}

.toolbar-copy {
  flex: 1 1 280px;
  min-width: 220px;
}

.filter-group {
  flex: 1 1 560px;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.filter-input {
  width: 220px;
}

.filter-select {
  width: 140px;
}

.table-shell {
  width: 100%;
  min-width: 0;
  overflow-x: auto;
  overflow-y: hidden;
}

.store-table {
  width: 100%;
  min-width: 1180px;
}

.store-table :deep(.el-table__cell) {
  vertical-align: top;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1.12fr 1fr 1fr;
  gap: 18px;
  align-items: stretch;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.panel-head h4 {
  margin: 0;
  font-size: 18px;
}

.panel-head p {
  margin: 6px 0 0;
  color: #94a3b8;
  font-size: 13px;
  line-height: 1.7;
}

.map-card,
.feature-card {
  display: flex;
  flex-direction: column;
}

.map-board {
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid #e6eef6;
}

.map-svg,
.detail-map-svg {
  width: 100%;
  height: auto;
  display: block;
}

.road-major {
  fill: none;
  stroke: #7bc7ff;
  stroke-width: 14;
  stroke-linecap: round;
  opacity: 0.72;
}

.road-sub {
  fill: none;
  stroke: #ffffff;
  stroke-width: 10;
  stroke-linecap: round;
}

.zone {
  opacity: 0.75;
}

.zone-a {
  fill: #c7f1df;
}

.zone-b {
  fill: #d9ebff;
}

.zone-c {
  fill: #ffe9d3;
}

.zone-d {
  fill: #dbf4ef;
}

.pin-shadow {
  stroke: rgba(15, 23, 42, 0.14);
  stroke-width: 5;
  stroke-linecap: round;
}

.pin-body,
.pin-core {
  stroke: none;
}

.pin-active {
  fill: #ef4444;
}

.pin-inactive {
  fill: #94a3b8;
}

.pin-dot {
  fill: #ffffff;
}

.pin-label {
  fill: #334155;
  font-size: 12px;
  font-weight: 600;
}

.pin-label.large {
  font-size: 14px;
}

.map-legend {
  display: flex;
  gap: 20px;
  padding-top: 14px;
  color: #64748b;
  font-size: 13px;
  margin-top: auto;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 8px;
  border-radius: 50%;
}

.legend-dot.active {
  background: #ef4444;
}

.legend-dot.inactive {
  background: #94a3b8;
}

.showcase-item {
  border: 1px solid #e6eef6;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
}

.single-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.showcase-banner {
  height: 132px;
  padding: 18px;
  display: flex;
  align-items: flex-end;
  color: #ffffff;
  font-size: 18px;
  font-weight: 700;
  background-blend-mode: multiply;
}

.showcase-copy {
  padding: 18px;
  display: grid;
  gap: 12px;
}

.showcase-headline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.showcase-headline h5 {
  margin: 0;
  font-size: 18px;
}

.showcase-copy p {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.showcase-meta {
  display: grid;
  gap: 8px;
  color: #94a3b8;
  font-size: 13px;
}

.detail-layout {
  display: grid;
  gap: 18px;
}

.detail-section h4 {
  margin: 0 0 14px;
  font-size: 18px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 18px;
}

.detail-item {
  padding: 14px 16px;
  border-radius: 16px;
  background: #f8fbfe;
  border: 1px solid #e8eef6;
  color: #475569;
}

.detail-item span {
  color: #94a3b8;
}

.detail-item strong {
  color: #334155;
  font-weight: 600;
}

.detail-address {
  grid-column: 1 / -1;
}

.text-success {
  color: #0c7a5c !important;
}

.text-muted {
  color: #64748b !important;
}

.photo-strip {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.photo-card {
  height: 132px;
  border-radius: 18px;
  display: flex;
  align-items: flex-end;
  padding: 14px;
  color: #ffffff;
  font-size: 18px;
  font-weight: 700;
}

.photo-a {
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.1), rgba(15, 23, 42, 0.55)),
    linear-gradient(135deg, #16a36f, #5bc6a0 60%, #d4f5e8 100%);
}

.photo-b {
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.08), rgba(15, 23, 42, 0.5)),
    linear-gradient(135deg, #1f8fff, #5cbcff 55%, #dbeeff 100%);
}

.detail-map {
  border-radius: 22px;
  overflow: hidden;
  border: 1px solid #e6eef6;
}

@media (max-width: 1280px) {
  .store-hero,
  .bottom-grid {
    grid-template-columns: 1fr;
  }

  .hero-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .detail-grid,
  .photo-strip,
  .hero-stats {
    grid-template-columns: 1fr;
  }

  .filter-group {
    justify-content: flex-start;
  }

  .filter-input,
  .filter-select {
    width: 100%;
  }
}
</style>
