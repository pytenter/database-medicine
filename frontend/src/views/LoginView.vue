<template>
  <div class="login-shell">
    <div class="login-panel page-card">
      <div class="login-copy">
        <div class="login-tag">数据库课程设计</div>
        <h1>连锁药店管理系统</h1>
        <p>Vue 3 + Django + openGauss</p>
      </div>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" @keyup.enter="handleLogin">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%;" :loading="loading" @click="handleLogin">
          登录
        </el-button>
      </el-form>
      <div class="demo-users">
        <p>演示账号：</p>
        <p>sysadmin / Admin@123</p>
        <p>storeadmin / Admin@123</p>
        <p>sales01 / Admin@123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const formRef = ref();
const loading = ref(false);
const form = reactive({
  username: "sysadmin",
  password: "Admin@123",
});
const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

const resolveErrorMessage = (error) => {
  if (!error.response) {
    return "无法连接后端服务，请确认 Django 已运行在 http://127.0.0.1:8000/。";
  }

  const data = error.response.data;
  if (typeof data === "string") {
    return data;
  }
  if (data?.non_field_errors?.length) {
    return data.non_field_errors[0];
  }
  if (data?.detail) {
    return data.detail;
  }
  const firstValue = Object.values(data || {}).find((value) => Array.isArray(value) ? value.length : value);
  if (Array.isArray(firstValue)) {
    return firstValue[0];
  }
  if (typeof firstValue === "string") {
    return firstValue;
  }
  return "登录失败。";
};

const handleLogin = async () => {
  await formRef.value.validate();
  loading.value = true;
  try {
    await auth.login(form);
    ElMessage.success("登录成功。");
    router.push("/dashboard");
  } catch (error) {
    ElMessage.error(resolveErrorMessage(error));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at right top, rgba(12, 122, 92, 0.22), transparent 28%),
    linear-gradient(135deg, #f6fffb 0%, #eff4fb 100%);
}

.login-panel {
  width: min(460px, 100%);
  padding: 34px;
}

.login-copy h1 {
  margin: 8px 0;
  font-size: 32px;
}

.login-copy p {
  margin: 0 0 24px;
  color: #64748b;
}

.login-tag {
  color: #0c7a5c;
  font-size: 12px;
  letter-spacing: 0.18em;
}

.demo-users {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 13px;
}

.demo-users p {
  margin: 4px 0;
}
</style>
