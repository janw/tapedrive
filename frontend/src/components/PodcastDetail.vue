<template>
  <div v-if="podcast">
    <h1 class="mb-1 text-center text-md-left">{{podcast.title}}</h1>

    <div class="row">
      <div class="col">Henlo</div>
    </div>
  </div>
</template>

<script>
export default {
  props: ["slug"],
  data() {
    return {
      podcast: {}
    };
  },
  created() {
    this.$api
      .get(`/podcasts/${this.slug}/`)
      .then(response => {
        this.podcast = response.data;
      })
      .catch(e => {
        this.errors.push(e);
      });
  }
};
</script>
