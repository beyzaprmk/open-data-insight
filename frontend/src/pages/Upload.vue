<template>
  <section>
    <h2>Upload</h2>
    <UploadForm @submit="handleSubmit" />
  </section>
</template>

<script setup>
import UploadForm from "../components/UploadForm.vue";

function handleSubmit(payload) {
  // Placeholder for upload action.
  console.log("upload", payload);
}
</script>
