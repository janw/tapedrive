<template>
  <div>
    <h1>Your Podcasts</h1>
    <div class="row">
      <div class="col">
        <PodcastListItem v-for="item in data" v-bind:key="item.id" :item="item" />
      </div>
    </div>
  </div>
</template>

<script>
import PodcastListItem from "./PodcastListItem";
export default {
  name: "home",
  components: {
    PodcastListItem
  },
  data() {
    return {
      msg: "Welcome to Your Vue.js App",
      data: null
    };
  },
  mounted() {
    this.$api.get("/podcasts/").then(response => (this.data = response.data));
  }
};
</script>
