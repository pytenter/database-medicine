<template>
  <div class="page-card page-box">
    <div class="toolbar">
      <div>
        <h3 class="page-title">销售人员排班</h3>
        <p class="page-subtitle">为当前门店销售人员安排班次，列表按星期几展示，方便快速查看轮班情况。</p>
      </div>
      <div class="toolbar-actions toolbar-wrap">
        <el-select v-model="salespersonFilter" clearable placeholder="选择销售人员" style="width: 180px;">
          <el-option v-for="item in salespeople" :key="item.id" :label="item.full_name" :value="item.id" />
        </el-select>
        <el-date-picker v-model="dateFilter" type="date" value-format="YYYY-MM-DD" placeholder="排班日期" style="width: 170px;" />
        <el-button @click="loadSchedules">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="openDialog()">新增排班</el-button>
      </div>
    </div>

    <el-table :data="schedules" border>
      <el-table-column prop="salesperson_name" label="销售人员" min-width="120" />
      <el-table-column prop="shift_weekday" label="星期" width="100" />
      <el-table-column prop="shift_period_display" label="班次" width="100" />
      <el-table-column label="时间段" min-width="150">
        <template #default="scope">{{ scope.row.start_time }} - {{ scope.row.end_time }}</template>
      </el-table-column>
      <el-table-column prop="note" label="排班说明" min-width="220" />
      <el-table-column prop="created_by_name" label="安排人" min-width="120" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="openDialog(scope.row)">编辑</el-button>
          <el-button link type="danger" @click="removeSchedule(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑排班' : '新增排班'" width="620px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="销售人员">
          <el-select v-model="form.salesperson" style="width: 100%;">
            <el-option v-for="item in salespeople" :key="item.id" :label="item.full_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排班日期"><el-date-picker v-model="form.shift_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" /></el-form-item>
        <el-form-item label="班次类型">
          <el-select v-model="form.shift_period" style="width: 100%;">
            <el-option v-for="item in shiftOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间"><el-time-picker v-model="form.start_time" value-format="HH:mm:ss" style="width: 100%;" /></el-form-item>
        <el-form-item label="结束时间"><el-time-picker v-model="form.end_time" value-format="HH:mm:ss" style="width: 100%;" /></el-form-item>
        <el-form-item label="排班说明"><el-input v-model="form.note" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import {
  createShiftScheduleApi,
  deleteShiftScheduleApi,
  getShiftSalespeopleApi,
  getShiftSchedulesApi,
  updateShiftScheduleApi,
} from "../api/shifts";

const currentUser = JSON.parse(localStorage.getItem("current_user") || "null");
const schedules = ref([]);
const salespeople = ref([]);
const salespersonFilter = ref("");
const dateFilter = ref("");
const dialogVisible = ref(false);
const editingId = ref(null);
const weekdayLabels = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"];
const shiftOptions = [
  { value: "morning", label: "早班" },
  { value: "afternoon", label: "中班" },
  { value: "evening", label: "晚班" },
];
const form = reactive({
  store: currentUser?.store || null,
  salesperson: null,
  shift_date: "",
  shift_period: "morning",
  start_time: "08:00:00",
  end_time: "12:00:00",
  note: "",
});

const getShiftWeekday = (dateText) => {
  if (!dateText) return "-";
  const date = new Date(`${dateText}T00:00:00`);
  if (Number.isNaN(date.getTime())) return dateText;
  return weekdayLabels[date.getDay()];
};

const resetForm = () => {
  editingId.value = null;
  Object.assign(form, {
    store: currentUser?.store || null,
    salesperson: null,
    shift_date: "",
    shift_period: "morning",
    start_time: "08:00:00",
    end_time: "12:00:00",
    note: "",
  });
};

const loadSchedules = async () => {
  const params = {};
  if (salespersonFilter.value) params.salesperson = salespersonFilter.value;
  if (dateFilter.value) params.shift_date = dateFilter.value;
  const { data } = await getShiftSchedulesApi(params);
  schedules.value = data.map((item) => ({
    ...item,
    shift_weekday: getShiftWeekday(item.shift_date),
  }));
};

const loadSalespeople = async () => {
  const { data } = await getShiftSalespeopleApi();
  salespeople.value = data;
};

const resetFilters = () => {
  salespersonFilter.value = "";
  dateFilter.value = "";
  loadSchedules();
};

const openDialog = (row = null) => {
  resetForm();
  if (row) {
    editingId.value = row.id;
    Object.assign(form, {
      store: row.store,
      salesperson: row.salesperson,
      shift_date: row.shift_date,
      shift_period: row.shift_period,
      start_time: row.start_time,
      end_time: row.end_time,
      note: row.note,
    });
  }
  dialogVisible.value = true;
};

const submitForm = async () => {
  try {
    const payload = { ...form, store: currentUser?.store };
    if (editingId.value) {
      await updateShiftScheduleApi(editingId.value, payload);
      ElMessage.success("排班信息更新成功。");
    } else {
      await createShiftScheduleApi(payload);
      ElMessage.success("排班创建成功。");
    }
    dialogVisible.value = false;
    loadSchedules();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "保存排班失败。");
  }
};

const removeSchedule = async (row) => {
  try {
    const weekdayText = row.shift_weekday || getShiftWeekday(row.shift_date);
    await ElMessageBox.confirm(`确认删除 ${row.salesperson_name} 在${weekdayText}的排班吗？`, "提示", { type: "warning" });
    await deleteShiftScheduleApi(row.id);
    ElMessage.success("排班已删除。");
    loadSchedules();
  } catch (error) {
    if (error === "cancel") return;
    ElMessage.error(error.response?.data?.detail || "删除排班失败。");
  }
};

onMounted(() => {
  loadSalespeople();
  loadSchedules();
});
</script>

<style scoped>
.page-box {
  padding: 22px;
}

.toolbar-wrap {
  flex-wrap: wrap;
}
</style>
