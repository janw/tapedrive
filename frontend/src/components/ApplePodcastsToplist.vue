<template>
  <div>
    <b-row>
      <b-col>
        <h3 class="mb-0 text-muted">Don't know what to look for?</h3>
        <h2 class="mb-3">Discover Something New</h2>
        <b-button v-on:click="loadTopList">Show Apple Podcasts Top List 🥇</b-button>
      </b-col>
    </b-row>
    <b-row>
      <ApplePodcastsSearchItem v-for="(result, $index) in results" :key="$index" :result="result" />
    </b-row>
  </div>
</template>


<script>
import ApplePodcastsSearchItem from "./ApplePodcastsSearchItem.vue";

export default {
  data() {
    return {
      results: [{ id: "aaa", title: "Not So Fancy Podcast" }, { id: "bbb" }]
    };
  },

  methods: {
    loadTopList() {
      console.log("clicked!");
    }
  },
  components: { ApplePodcastsSearchItem }
};
</script>
