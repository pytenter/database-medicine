<template>
  <div class="global-progress" :class="{ active: pending > 0 }">
    <div class="global-progress-bar" />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { appRequestState } from "../stores/requestState";

const pending = computed(() => appRequestState.pending);
</script>
