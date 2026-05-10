<template>
  <form class="upload-form" @submit.prevent="submit">
    <label>
      Dataset Name
      <input v-model="name" type="text" required />
    </label>
    <label>
      Image File
      <input @change="handleFile" type="file" accept="image/*" required />
    </label>
    <button type="submit">Upload</button>
  </form>
</template>

<script setup>
import { ref } from "vue";

const emit = defineEmits(["submit"]);
const name = ref("");
const file = ref(null);

function handleFile(event) {
  file.value = event.target.files[0] || null;
}

function submit() {
  emit("submit", { name: name.value, file: file.value });
}
</script>

<style scoped>
.upload-form {
  display: grid;
  gap: 12px;
  max-width: 420px;
}

.upload-form input {
  width: 100%;
  margin-top: 6px;
}
</style>
