<template>
  <div class="metrics">
    <div class="metric" v-for="(value, key) in metrics" :key="key">
      <span class="label">{{ key }}</span>
      <span class="value">{{ value }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  metrics: { type: Object, default: () => ({}) }
});
</script>

<style scoped>
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.metric {
  padding: 12px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
}

.label {
  display: block;
  font-size: 12px;
  color: #666;
}

.value {
  font-size: 16px;
  font-weight: 600;
}
</style>
