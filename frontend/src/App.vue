<template>
  <div class="app-shell">
    <header class="app-header">
      <h1>OpenDataInsight</h1>
      <nav>
        <RouterLink to="/">Datasets</RouterLink>
        <RouterLink to="/upload">Upload</RouterLink>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid #e6e6e6;
}

.app-header nav {
  display: flex;
  gap: 16px;
}

.app-main {
  padding: 24px;
}
</style>
