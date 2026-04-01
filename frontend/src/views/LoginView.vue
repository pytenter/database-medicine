<template>
  <div class="login-shell">
    <div class="login-panel page-card">
      <div class="login-copy">
        <div class="login-tag">COURSE DESIGN</div>
        <h1>Chain Pharmacy Management System</h1>
        <p>Vue 3 + Django + openGauss</p>
      </div>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" @keyup.enter="handleLogin">
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" placeholder="Enter your username" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="form.password" show-password placeholder="Enter your password" />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%;" :loading="loading" @click="handleLogin">
          Login
        </el-button>
      </el-form>
      <div class="demo-users">
        <p>Demo users:</p>
        <p>`sysadmin / Admin@123`</p>
        <p>`storeadmin / Admin@123`</p>
        <p>`sales01 / Admin@123`</p>
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
  username: [{ required: true, message: "Please input username", trigger: "blur" }],
  password: [{ required: true, message: "Please input password", trigger: "blur" }],
};

const resolveErrorMessage = (error) => {
  if (!error.response) {
    return "Cannot connect to backend. Make sure Django is running at http://127.0.0.1:8000/.";
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
  return "Login failed.";
};

const handleLogin = async () => {
  await formRef.value.validate();
  loading.value = true;
  try {
    await auth.login(form);
    ElMessage.success("Login successful.");
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
