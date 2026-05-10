<template>
  <section>
    <h2>Dataset Detail</h2>
    <div v-if="dataset" class="detail-card">
      <h3>{{ dataset.name }}</h3>
      <p>{{ dataset.description }}</p>
      <MetricsPanel :metrics="dataset.metrics" />
    </div>
  </section>
</template>

<script setup>
import { onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { useDatasetsStore } from "../stores/datasets";
import MetricsPanel from "../components/MetricsPanel.vue";

const route = useRoute();
const store = useDatasetsStore();
const dataset = computed(() => store.selected);

onMounted(() => {
  store.loadById(route.params.id);
});
</script>

<style scoped>
.detail-card {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
}
</style>
