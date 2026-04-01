<template>
  <div class="page-card review-page">
    <div class="toolbar review-toolbar">
      <div>
        <h3 class="page-title">订单评价</h3>
        <p class="page-subtitle">为销售订单补充满意度评价与文字反馈。</p>
      </div>
      <div class="toolbar-actions wrap-actions">
        <el-input v-model="keyword" placeholder="按订单编号、客户名称搜索" clearable style="width: 260px;" @keyup.enter="loadSales" />
        <el-button @click="loadSales">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>

    <el-table :data="sales" border>
      <el-table-column prop="order_no" label="订单编号" min-width="190" />
      <el-table-column prop="customer_name" label="客户名称" min-width="130" />
      <el-table-column prop="total_amount" label="订单金额" width="120">
        <template #default="scope">{{ formatMoney(scope.row.total_amount) }}</template>
      </el-table-column>
      <el-table-column label="评价状态" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.review ? 'success' : 'info'">{{ scope.row.review ? '已评价' : '待评价' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="评分" width="120">
        <template #default="scope">
          <el-rate :model-value="scope.row.review?.rating || 0" disabled />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">{{ scope.row.review ? '修改评价' : '填写评价' }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="订单评价" width="760px" destroy-on-close>
      <template v-if="currentOrder">
        <div class="review-dialog-grid">
          <section class="review-summary">
            <h4>{{ currentOrder.order_no }}</h4>
            <p>客户：{{ currentOrder.customer_name || '到店顾客' }}</p>
            <p>门店：{{ currentOrder.store_name }}</p>
            <p>金额：{{ formatMoney(currentOrder.total_amount) }}</p>
            <p>状态：{{ currentOrder.order_status_label }}</p>
          </section>

          <section class="review-form-card">
            <el-form :model="reviewForm" label-position="top">
              <el-form-item label="评分">
                <el-rate v-model="reviewForm.rating" />
              </el-form-item>
              <el-form-item label="评价内容">
                <el-input v-model="reviewForm.content" type="textarea" :rows="6" placeholder="请输入订单评价内容" />
              </el-form-item>
            </el-form>
          </section>
        </div>
        <div class="dialog-actions">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitReview">提交评价</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { getSaleDetailApi, getSalesApi, submitReviewApi } from "../api/sales";

const sales = ref([]);
const keyword = ref("");
const dialogVisible = ref(false);
const currentOrder = ref(null);
const submitting = ref(false);
const reviewForm = reactive({ rating: 5, content: "" });

const formatMoney = (value) => `￥${Number(value || 0).toFixed(2)}`;

const loadSales = async () => {
  const { data } = await getSalesApi(keyword.value ? { search: keyword.value } : {});
  sales.value = data;
};

const resetFilters = () => {
  keyword.value = "";
  loadSales();
};

const openDialog = async (row) => {
  const { data } = await getSaleDetailApi(row.id);
  currentOrder.value = data;
  reviewForm.rating = data.review?.rating || 5;
  reviewForm.content = data.review?.content || "";
  dialogVisible.value = true;
};

const submitReview = async () => {
  submitting.value = true;
  try {
    await submitReviewApi(currentOrder.value.id, { rating: reviewForm.rating, content: reviewForm.content });
    ElMessage.success("订单评价已保存。");
    dialogVisible.value = false;
    await loadSales();
  } finally {
    submitting.value = false;
  }
};

onMounted(loadSales);
</script>

<style scoped>
.review-page {
  padding: 22px;
}

.review-toolbar {
  margin-bottom: 18px;
}

.wrap-actions {
  flex-wrap: wrap;
  gap: 10px;
}

.review-dialog-grid {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 18px;
  margin-bottom: 18px;
}

.review-summary,
.review-form-card {
  padding: 18px;
  border: 1px solid #d9e3ef;
  border-radius: 18px;
  background: #fbfdff;
}

.review-summary h4 {
  margin: 0 0 14px;
  font-size: 20px;
  color: #0f172a;
}

.review-summary p {
  margin: 0 0 10px;
  color: #475569;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 860px) {
  .review-dialog-grid {
    grid-template-columns: 1fr;
  }
}
</style>
