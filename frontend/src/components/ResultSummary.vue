<template>
  <div v-if="result" class="result-card">
    <h3>AI Interpretation</h3>
    <p>{{ result.interpretation }}</p>
    <MetricsPanel :metrics="result.metrics" />
  </div>
</template>

<script setup>
import MetricsPanel from "./MetricsPanel.vue";

defineProps({
  result: { type: Object, default: null }
});
</script>

<style scoped>
.result-card {
  padding: 16px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
}
</style>
