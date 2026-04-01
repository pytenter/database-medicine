<template>
  <div>
    <div class="page-card page-box">
      <div class="toolbar">
        <div>
          <h3 class="page-title">销售开单</h3>
          <p class="page-subtitle">从当前门店库存中查询药品、加入购物车并提交销售单。</p>
        </div>
      </div>

      <el-row :gutter="18">
        <el-col :span="14">
          <el-input v-model="keyword" placeholder="按药品名称、厂商或编码搜索" clearable @keyup.enter="loadInventory" />
          <el-table :data="inventoryRows" border style="margin-top: 14px;">
            <el-table-column prop="medicine_code" label="药品编码" width="120" />
            <el-table-column prop="medicine_name" label="药品名称" min-width="160" />
            <el-table-column prop="manufacturer_name" label="生产厂商" min-width="150" />
            <el-table-column prop="quantity" label="库存" width="90" />
            <el-table-column label="操作" width="110">
              <template #default="scope">
                <el-button link type="primary" @click="addToCart(scope.row)">加入</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
        <el-col :span="10">
          <div class="cart-panel">
            <el-form :model="saleForm" label-position="top">
              <el-form-item label="顾客姓名"><el-input v-model="saleForm.customer_name" /></el-form-item>
              <el-form-item label="备注"><el-input v-model="saleForm.remark" type="textarea" /></el-form-item>
            </el-form>
            <el-table :data="cart" border max-height="320">
              <el-table-column prop="medicine_name" label="药品名称" min-width="120" />
              <el-table-column label="数量" width="120">
                <template #default="scope">
                  <el-input-number v-model="scope.row.quantity" :min="1" :max="scope.row.max" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="scope">
                  <el-button link type="danger" @click="removeFromCart(scope.$index)">移除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" style="width: 100%; margin-top: 14px;" @click="submitSale">提交销售单</el-button>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { getInventoryApi } from "../api/inventory";
import { createSaleApi } from "../api/sales";

const keyword = ref("");
const inventoryRows = ref([]);
const cart = ref([]);
const saleForm = reactive({ customer_name: "", remark: "" });

const loadInventory = async () => {
  const { data } = await getInventoryApi(keyword.value ? { search: keyword.value } : {});
  inventoryRows.value = data.filter((item) => item.quantity > 0);
};

const addToCart = (row) => {
  const existing = cart.value.find((item) => item.medicine_id === row.medicine);
  if (existing) {
    existing.quantity = Math.min(existing.quantity + 1, existing.max);
    return;
  }
  cart.value.push({
    medicine_id: row.medicine,
    medicine_name: row.medicine_name,
    quantity: 1,
    max: row.quantity,
  });
};

const removeFromCart = (index) => {
  cart.value.splice(index, 1);
};

const submitSale = async () => {
  if (!cart.value.length) {
    ElMessage.warning("请至少添加一种药品。")
    return;
  }
  const payload = {
    customer_name: saleForm.customer_name,
    remark: saleForm.remark,
    items: cart.value.map((item) => ({ medicine_id: item.medicine_id, quantity: item.quantity })),
  };
  try {
    const { data } = await createSaleApi(payload);
    ElMessage.success(`销售单 ${data.order_no} 创建成功。`)
    cart.value = [];
    saleForm.customer_name = "";
    saleForm.remark = "";
    loadInventory();
  } catch (error) {
    ElMessage.error(error.response?.data?.items?.[0] || "创建销售单失败。")
  }
};

onMounted(loadInventory);
</script>

<style scoped>
.page-box {
  padding: 22px;
}

.cart-panel {
  padding: 18px;
  border: 1px solid #d8e1ef;
  border-radius: 16px;
  background: #fcfffe;
}
</style>
