<template>
  <div class="system-status" :class="online ? 'is-online' : 'is-offline'">
    <span class="dot" aria-hidden="true" />
    <span>{{ online ? "系统在线" : "后端离线" }}</span>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const online = ref(true);
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "/api";
const statusUrl = `${apiBaseUrl.replace(/\/$/, "")}/`;
let timerId = null;

const checkBackend = async () => {
  try {
    const response = await fetch(statusUrl, { cache: "no-store" });
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
