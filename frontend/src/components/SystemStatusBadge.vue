<template>
  <div class="system-status" :class="online ? 'is-online' : 'is-offline'">
    <span class="dot" />
    <span>{{ online ? "系统在线" : "后端离线" }}</span>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const online = ref(true);
let timerId = null;

const checkBackend = async () => {
  try {
    const response = await fetch("/api/", { cache: "no-store" });
    // 2xx / 3xx / 4xx 都说明网络与后端可达（例如 401/404）
    online.value = response.status > 0;
  } catch (error) {
    online.value = false;
  }
};

onMounted(async () => {
  await checkBackend();
  timerId = setInterval(checkBackend, 15000);
});

onBeforeUnmount(() => {
  if (timerId) {
    clearInterval(timerId);
  }
});
</script>

