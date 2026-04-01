<template>
  <div class="page-card logistics-page">
    <div class="toolbar logistics-toolbar">
      <div>
        <h3 class="page-title">物流信息</h3>
        <p class="page-subtitle">查看订单物流进度，并为订单追加配送动态。</p>
      </div>
      <div class="toolbar-actions wrap-actions">
        <el-input v-model="keyword" placeholder="按订单编号、客户名称搜索" clearable style="width: 260px;" @keyup.enter="loadSales" />
        <el-select v-model="statusFilter" clearable placeholder="订单状态" style="width: 140px;">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-button @click="loadSales">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>

    <el-table :data="sales" border>
      <el-table-column prop="order_no" label="订单编号" min-width="190" />
      <el-table-column prop="customer_name" label="客户名称" min-width="130" />
      <el-table-column prop="order_status_label" label="当前状态" width="120">
        <template #default="scope">
          <el-tag :type="statusTagType(scope.row.order_status)">{{ scope.row.order_status_label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="物流内容" min-width="280">
        <template #default="scope">{{ scope.row.latest_logistics?.content || '暂无物流记录' }}</template>
      </el-table-column>
      <el-table-column label="发布时间" min-width="180">
        <template #default="scope">{{ formatDateTime(scope.row.latest_logistics?.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="110">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">修改物流</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="修改物流" width="860px" destroy-on-close>
      <template v-if="currentOrder">
        <div class="dialog-block">
          <div class="block-title">当前物流</div>
          <el-table :data="currentOrder.logistics" border max-height="240">
            <el-table-column prop="content" label="物流信息" min-width="280" />
            <el-table-column prop="created_at" label="操作时间" min-width="180">
              <template #default="scope">{{ formatDateTime(scope.row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </div>

        <div class="dialog-block">
          <div class="block-title">更新物流</div>
          <el-form :model="logisticsForm" label-position="top">
            <el-form-item label="物流备注">
              <el-input v-model="logisticsForm.content" type="textarea" :rows="5" placeholder="请输入物流更新内容，例如：配送员正在派送。" />
            </el-form-item>
            <el-form-item label="同步更新订单状态">
              <el-select v-model="logisticsForm.status_after" placeholder="不修改状态" clearable style="width: 220px;">
                <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>

        <div class="dialog-actions">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitLogistics">修改</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { addLogisticsApi, getSaleDetailApi, getSalesApi } from "../api/sales";

const sales = ref([]);
const keyword = ref("");
const statusFilter = ref("");
const dialogVisible = ref(false);
const currentOrder = ref(null);
const submitting = ref(false);
const logisticsForm = reactive({ content: "", status_after: "" });

const statusOptions = [
  { label: "待付款", value: "pending_payment" },
  { label: "已下单", value: "ordered" },
  { label: "配送中", value: "delivering" },
  { label: "已收货", value: "completed" },
];

const formatDateTime = (value) => {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 16);
};
const statusTagType = (status) => ({ pending_payment: "warning", ordered: "info", delivering: "primary", completed: "success" }[status] || "info");

const loadSales = async () => {
  const params = {};
  if (keyword.value) params.search = keyword.value;
  if (statusFilter.value) params.status = statusFilter.value;
  const { data } = await getSalesApi(params);
  sales.value = data;
};

const resetFilters = () => {
  keyword.value = "";
  statusFilter.value = "";
  loadSales();
};

const openDialog = async (row) => {
  const { data } = await getSaleDetailApi(row.id);
  currentOrder.value = data;
  logisticsForm.content = "";
  logisticsForm.status_after = "";
  dialogVisible.value = true;
};

const submitLogistics = async () => {
  if (!logisticsForm.content.trim()) {
    ElMessage.warning("请先填写物流备注。");
    return;
  }
  submitting.value = true;
  try {
    await addLogisticsApi(currentOrder.value.id, {
      content: logisticsForm.content,
      status_after: logisticsForm.status_after || undefined,
    });
    ElMessage.success("物流信息已更新。");
    dialogVisible.value = false;
    await loadSales();
  } finally {
    submitting.value = false;
  }
};

onMounted(loadSales);
</script>

<style scoped>
.logistics-page {
  padding: 22px;
}

.logistics-toolbar {
  margin-bottom: 18px;
}

.wrap-actions {
  flex-wrap: wrap;
  gap: 10px;
}

.dialog-block {
  margin-bottom: 18px;
  padding: 16px;
  border: 1px solid #d9e3ef;
  border-radius: 16px;
  background: #fbfdff;
}

.block-title {
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
