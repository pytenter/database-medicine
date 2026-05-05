<template>
  <GlobalTopProgress />
  <SystemStatusBadge />
  <RouterView />
</template>

<script setup>
import { RouterView } from "vue-router";
import GlobalTopProgress from "./components/GlobalTopProgress.vue";
import SystemStatusBadge from "./components/SystemStatusBadge.vue";
</script>
