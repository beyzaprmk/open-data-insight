<template>
  <section>
    <h2>Analysis Result</h2>
    <ResultSummary :result="result" />
  </section>
</template>

<script setup>
import { onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { useAnalysisStore } from "../stores/analysis";
import ResultSummary from "../components/ResultSummary.vue";

const route = useRoute();
const store = useAnalysisStore();
const result = computed(() => store.result);

onMounted(() => {
  store.loadResult(route.params.id);
});
</script>
