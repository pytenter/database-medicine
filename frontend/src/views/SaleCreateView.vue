<template>
  <div>
    <div class="page-card page-box">
      <div class="toolbar">
        <div>
          <h3 class="page-title">Create Sale Order</h3>
          <p class="page-subtitle">Search medicine from current store inventory, add to cart, and submit the order.</p>
        </div>
      </div>

      <el-row :gutter="18">
        <el-col :span="14">
          <el-input v-model="keyword" placeholder="Search medicine name, manufacturer, or code" clearable @keyup.enter="loadInventory" />
          <el-table :data="inventoryRows" border style="margin-top: 14px;">
            <el-table-column prop="medicine_code" label="Code" width="120" />
            <el-table-column prop="medicine_name" label="Medicine" min-width="160" />
            <el-table-column prop="manufacturer_name" label="Manufacturer" min-width="150" />
            <el-table-column prop="quantity" label="Stock" width="90" />
            <el-table-column label="Action" width="110">
              <template #default="scope">
                <el-button link type="primary" @click="addToCart(scope.row)">Add</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
        <el-col :span="10">
          <div class="cart-panel">
            <el-form :model="saleForm" label-position="top">
              <el-form-item label="Customer Name"><el-input v-model="saleForm.customer_name" /></el-form-item>
              <el-form-item label="Remark"><el-input v-model="saleForm.remark" type="textarea" /></el-form-item>
            </el-form>
            <el-table :data="cart" border max-height="320">
              <el-table-column prop="medicine_name" label="Medicine" min-width="120" />
              <el-table-column label="Qty" width="120">
                <template #default="scope">
                  <el-input-number v-model="scope.row.quantity" :min="1" :max="scope.row.max" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="Action" width="80">
                <template #default="scope">
                  <el-button link type="danger" @click="removeFromCart(scope.$index)">Remove</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" style="width: 100%; margin-top: 14px;" @click="submitSale">Submit Sale</el-button>
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
    ElMessage.warning("Please add at least one medicine.");
    return;
  }
  const payload = {
    customer_name: saleForm.customer_name,
    remark: saleForm.remark,
    items: cart.value.map((item) => ({ medicine_id: item.medicine_id, quantity: item.quantity })),
  };
  try {
    const { data } = await createSaleApi(payload);
    ElMessage.success(`Sale order ${data.order_no} created.`);
    cart.value = [];
    saleForm.customer_name = "";
    saleForm.remark = "";
    loadInventory();
  } catch (error) {
    ElMessage.error(error.response?.data?.items?.[0] || "Failed to create sale order.");
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
