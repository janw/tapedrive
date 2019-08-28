<template>
  <div>
    <h1>Your Podcasts</h1>
    <div class="row">
      <div class="col">
        <Spinner :data="data" />
        <PodcastListItem v-for="item in data" v-bind:key="item.id" :item="item" />
      </div>
    </div>
  </div>
</template>

<script>
import PodcastListItem from "./PodcastListItem";
import Spinner from "./Spinner";
export default {
  name: "home",
  components: {
    PodcastListItem,
    Spinner
  },
  data() {
    return {
      msg: "Welcome to Your Vue.js App",
      data: null
    };
  },
  created() {
    this.$api
      .get("/api/podcasts/")
      .then(response => (this.data = response.data));
  }
};
</script>
