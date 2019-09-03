<template>
  <div
    class="d-flex justify-content-center align-items-center mb-3 spinner-container"
    :class="{ 'flex-column': stacked }"
  >
    <b-spinner variant="secondary"></b-spinner>
    <p class="my-3 mx-3 text-muted">Loading</p>
  </div>
</template>

<script>
export default {
  props: {
    stacked: {
      type: Boolean,
      default: true
    }
  }
};
</script>

<style scoped>
.spinner-container {
  height: 20rem;
}
</style>
