<template>
  <section>
    <h2>Datasets</h2>
    <button @click="load">Refresh</button>
    <div class="dataset-grid">
      <ImageCard
        v-for="item in datasets"
        :key="item.id"
        :title="item.name"
        :subtitle="item.description"
        :image-url="item.coverUrl"
      />
    </div>
  </section>
</template>

<script setup>
import { onMounted, computed } from "vue";
import { useDatasetsStore } from "../stores/datasets";
import ImageCard from "../components/ImageCard.vue";

const store = useDatasetsStore();
const datasets = computed(() => store.items);

function load() {
  store.loadAll();
}

onMounted(() => {
  load();
});
</script>

<style scoped>
.dataset-grid {
  margin-top: 16px;
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}
</style>
