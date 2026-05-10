<template>
  <article class="card">
    <img v-if="imageUrl" :src="imageUrl" :alt="title" />
    <div class="card-body">
      <h3>{{ title }}</h3>
      <p>{{ subtitle }}</p>
    </div>
  </article>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  imageUrl: { type: String, default: "" }
});
</script>

<style scoped>
.card {
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.card img {
  width: 100%;
  height: 140px;
  object-fit: cover;
}

.card-body {
  padding: 12px;
}
</style>
