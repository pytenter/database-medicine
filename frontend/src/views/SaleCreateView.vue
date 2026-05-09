<template>
  <div class="sale-page">
    <div class="page-card sale-shell">
      <div class="toolbar sale-toolbar">
        <div>
          <h3 class="page-title">销售开单</h3>
        </div>
        <div class="toolbar-actions">
          <el-input v-model="keyword" placeholder="搜索药品名称、厂商或编码" clearable style="width: 280px;" @keyup.enter="loadInventory" />
          <el-button @click="loadInventory">查询药品</el-button>
        </div>
      </div>

      <div class="sale-grid">
        <section class="inventory-panel">
          <div class="section-head">
            <h4>可售药品</h4>
            <span>仅显示当前门店存在库存的药品</span>
          </div>
          <el-table :data="inventoryRows" border height="520">
            <el-table-column prop="medicine_code" label="药品编码" width="130" />
            <el-table-column prop="medicine_name" label="药品名称" min-width="170" />
            <el-table-column prop="manufacturer_name" label="生产厂商" min-width="160" />
            <el-table-column prop="quantity" label="库存" width="90" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button link type="primary" @click="addToCart(scope.row)">加入订单</el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>

        <section class="order-panel">
          <div class="section-head">
            <h4>订单信息</h4>
            <span>填写客户信息并确认销售明细</span>
          </div>

          <el-form :model="saleForm" label-position="top" class="order-form">
            <el-form-item label="客户名称">
              <el-input v-model="saleForm.customer_name" placeholder="请输入客户姓名" />
            </el-form-item>
            <el-form-item label="联系电话">
              <el-input v-model="saleForm.customer_phone" placeholder="请输入联系电话" />
            </el-form-item>
            <el-form-item label="订单备注">
              <el-input v-model="saleForm.remark" type="textarea" :rows="3" placeholder="可填写用药提醒、顾客备注等" />
            </el-form-item>
          </el-form>

          <div class="cart-head">
            <span>订单明细 ⭐️</span>
            <span class="cart-count">共 {{ cart.length }} 项</span>
          </div>
          <el-table :data="cart" border max-height="280" empty-text="请先从左侧加入药品">
            <el-table-column prop="medicine_name" label="药品名称" min-width="160" />
            <el-table-column label="数量" width="140">
              <template #default="scope">
                <el-input-number v-model="scope.row.quantity" :min="1" :max="scope.row.max" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="100">
              <template #default="scope">{{ formatMoney(scope.row.unit_price) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="scope">
                <el-button link type="danger" @click="removeFromCart(scope.$index)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="summary-card">
            <div>
              <span>订单总额</span>
              <strong>{{ formatMoney(totalAmount) }}</strong>
            </div>
            <el-button type="primary" size="large" :disabled="submitting" @click="submitSale">
              提交销售订单
            </el-button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { getInventoryApi } from "../api/inventory";
import { createSaleApi } from "../api/sales";

const keyword = ref("");
const inventoryRows = ref([]);
const cart = ref([]);
const submitting = ref(false);
const saleForm = reactive({ customer_name: "", customer_phone: "", remark: "" });

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
    unit_price: Number(row.retail_price || 0),
  });
};

const removeFromCart = (index) => {
  cart.value.splice(index, 1);
};

const totalAmount = computed(() =>
  cart.value.reduce((sum, item) => sum + Number(item.unit_price || 0) * Number(item.quantity || 0), 0),
);

const formatMoney = (value) => `￥${Number(value || 0).toFixed(2)}`;

const submitSale = async () => {
  if (!cart.value.length) {
    ElMessage.warning("请至少添加一种药品。");
    return;
  }
  submitting.value = true;
  try {
    const payload = {
      customer_name: saleForm.customer_name,
      customer_phone: saleForm.customer_phone,
      remark: saleForm.remark,
      items: cart.value.map((item) => ({ medicine_id: item.medicine_id, quantity: item.quantity })),
    };
    const { data } = await createSaleApi(payload);
    ElMessage.success(`销售单 ${data.order_no} 创建成功。`);
    cart.value = [];
    saleForm.customer_name = "";
    saleForm.customer_phone = "";
    saleForm.remark = "";
    await loadInventory();
  } catch (error) {
    ElMessage.error(error.response?.data?.items?.[0] || "创建销售订单失败。");
  } finally {
    submitting.value = false;
  }
};

onMounted(loadInventory);
</script>

<style scoped>
.sale-shell {
  padding: 22px;
}

.sale-toolbar {
  margin-bottom: 18px;
}

.sale-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(340px, 0.95fr);
  gap: 20px;
}

.inventory-panel,
.order-panel {
  padding: 20px;
  border: 1px solid #d9e3f1;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 251, 255, 0.98) 100%);
  box-shadow: 0 20px 45px rgba(148, 163, 184, 0.12);
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 16px;
}

.section-head h4 {
  margin: 0;
  font-size: 22px;
  color: #0f172a;
}

.section-head span {
  color: #64748b;
  font-size: 13px;
}

.order-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}

.order-form :deep(.el-form-item:last-child) {
  grid-column: 1 / -1;
}

.cart-head {
  display: flex;
  justify-content: space-between;
  margin: 8px 0 10px;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.cart-count {
  color: #10b981;
}

.summary-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 18px 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, #0f766e 0%, #38bdf8 100%);
  color: #fff;
}

.summary-card span {
  display: block;
  font-size: 13px;
  opacity: 0.88;
}

.summary-card strong {
  display: block;
  margin-top: 6px;
  font-size: 28px;
}

@media (max-width: 1260px) {
  .sale-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .order-form {
    grid-template-columns: 1fr;
  }

  .summary-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }
}
</style>
