<template>
  <div>
    <h1 v-if="hasData">Your Podcasts</h1>
    <b-row>
      <b-col>
        <PodcastListItem v-for="(item, $index) in data" :key="$index" :item="item" />
        <infinite-loading @infinite="infiniteHandler"></infinite-loading>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import PodcastListItem from "./PodcastListItem.vue";
export default {
  components: {
    PodcastListItem
  },
  data() {
    return {
      endpoint: "/api/podcasts/",
      page: 1,
      data: []
    };
  },
  computed: {
    hasData: function() {
      return this.data.length > 0;
    }
  }
};
</script>
