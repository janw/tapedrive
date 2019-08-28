<template>
  <div
    v-if="data === null"
    class="d-flex flex-column justify-content-center align-items-center mb-3 spinner-container"
  >
    <b-spinner variant="secondary" label="Loading ..."></b-spinner>
    <p class="mt-3 text-muted">Loading …</p>
  </div>
</template>

<script>
export default {
  props: ["data"]
};
</script>

<style scoped>
.spinner-container {
  height: 20rem;
}
</style>