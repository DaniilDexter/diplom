<script setup lang="ts">

const userStore = useUserStore()

await userStore.fetchUser()

</script>

<template>
  <Header />
  <main>
    <slot />
  </main>
</template>