<template>
  <div class="container">
    <b-row>
      <b-col>
        <h3 class="mb-0 text-muted">Don't know what to look for?</h3>
        <h2>Discover Something New</h2>
        <b-button v-on:click="loadTopList" class="btn-sm mb-2">Show Apple Podcasts Top List 🥇</b-button>
      </b-col>
    </b-row>
    <b-row>
      <ApplePodcastsSearchItem v-for="result in results" :key="result.id" :result="result" />
    </b-row>
  </div>
</template>


<script>
import ApplePodcastsSearchItem from "./ApplePodcastsSearchItem";

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