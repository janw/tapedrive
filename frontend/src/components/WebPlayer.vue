<template>
  <div v-if="showPlayer" class="navbar fixed-bottom navbar-dark bg-dark">
    <img class="img-logo" src="../images/icon@2x.png" alt />
    <a class="navbar-brand" href="#">Web Player</a>
    <b-button @click="showPlayer = !showPlayer" size="sm" variant="dark">
      <span class="text-muted">Hide</span>
    </b-button>
  </div>
</template>

<script>
export default {
  data() {
    return { showPlayer: true };
  }
};
</script>

<style lang="scss" scoped>
.img-logo {
  filter: opacity(0.25);
}
</style>