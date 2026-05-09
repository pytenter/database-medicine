<template>
  <div class="login-shell">
    <div class="login-bg" aria-hidden="true">
      <div class="bg-shelf shelf-left">
        <span v-for="index in 18" :key="`left-${index}`"></span>
      </div>
      <div class="bg-shelf shelf-right">
        <span v-for="index in 20" :key="`right-${index}`"></span>
      </div>
      <div class="bg-cross cross-one"></div>
      <div class="bg-cross cross-two"></div>
      <div class="bg-ribbon"></div>
    </div>
    <div class="login-panel page-card">
      <div class="login-copy">
        <h1>连锁药店系统</h1>
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
  position: relative;
  overflow: hidden;
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    linear-gradient(115deg, rgba(236, 253, 245, 0.96) 0 36%, rgba(241, 250, 255, 0.92) 36% 68%, rgba(232, 247, 244, 0.94) 68% 100%),
    #f7fbff;
}

.login-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    repeating-linear-gradient(0deg, rgba(15, 118, 110, 0.055) 0 1px, transparent 1px 84px),
    repeating-linear-gradient(90deg, rgba(15, 118, 110, 0.048) 0 1px, transparent 1px 84px);
  mask-image: linear-gradient(90deg, transparent 0%, #000 14%, #000 86%, transparent 100%);
}

.login-shell::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(255, 255, 255, 0.18) 0 21%, transparent 21% 79%, rgba(255, 255, 255, 0.2) 79% 100%),
    linear-gradient(180deg, transparent 0 68%, rgba(255, 255, 255, 0.64) 100%);
}

.login-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.bg-shelf {
  position: absolute;
  display: grid;
  grid-template-columns: repeat(6, 38px);
  gap: 18px 14px;
  padding: 28px;
  border: 1px solid rgba(20, 184, 166, 0.18);
  background:
    repeating-linear-gradient(0deg, transparent 0 64px, rgba(13, 148, 136, 0.16) 64px 66px),
    rgba(255, 255, 255, 0.34);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.08);
  opacity: 0.72;
}

.bg-shelf span {
  display: block;
  width: 28px;
  height: 42px;
  align-self: end;
  justify-self: center;
  border-radius: 7px 7px 4px 4px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.78) 0 20%, transparent 20% 100%),
    linear-gradient(135deg, rgba(20, 184, 166, 0.28), rgba(59, 130, 246, 0.2));
  border: 1px solid rgba(20, 184, 166, 0.2);
}

.bg-shelf span:nth-child(3n) {
  height: 34px;
  border-radius: 50%;
}

.bg-shelf span:nth-child(4n) {
  width: 34px;
  height: 28px;
  border-radius: 5px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.22), rgba(16, 185, 129, 0.24));
}

.shelf-left {
  left: 5vw;
  top: 14vh;
  transform: rotate(-4deg);
}

.shelf-right {
  right: 4vw;
  bottom: 12vh;
  grid-template-columns: repeat(5, 38px);
  transform: rotate(5deg);
}

.bg-cross {
  position: absolute;
  width: 210px;
  aspect-ratio: 1;
  opacity: 0.42;
}

.bg-cross::before,
.bg-cross::after {
  content: "";
  position: absolute;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(14, 165, 233, 0.15));
}

.bg-cross::before {
  inset: 40% 6%;
}

.bg-cross::after {
  inset: 6% 40%;
}

.cross-one {
  left: 20vw;
  bottom: 10vh;
  transform: rotate(-10deg);
}

.cross-two {
  right: 18vw;
  top: 9vh;
  width: 150px;
  transform: rotate(14deg);
}

.bg-ribbon {
  position: absolute;
  left: 50%;
  top: -18vh;
  width: 34vw;
  min-width: 420px;
  height: 140vh;
  transform: translateX(-50%) rotate(22deg);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.58), rgba(20, 184, 166, 0.08), rgba(14, 165, 233, 0.12));
  border-left: 1px solid rgba(255, 255, 255, 0.7);
  border-right: 1px solid rgba(255, 255, 255, 0.7);
}

.login-panel {
  position: relative;
  z-index: 1;
  width: min(460px, 100%);
  padding: 34px;
  border: 1px solid rgba(148, 163, 184, 0.38);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.16);
  backdrop-filter: blur(14px);
}

.login-copy h1 {
  margin: 0 0 18px;
  font-size: 32px;
}

.login-copy p {
  margin: 0 0 24px;
  color: #64748b;
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

@media (max-width: 900px) {
  .bg-shelf {
    opacity: 0.3;
  }

  .shelf-left {
    left: -120px;
  }

  .shelf-right {
    right: -120px;
  }

  .bg-ribbon {
    min-width: 320px;
  }
}
</style>
