<template>
  <div>
    <h1>Your Podcasts</h1>
    <b-row>
      <b-col>
        <Spinner :data="data" />
        <PodcastListItem v-for="(item, $index) in data" :key="$index" :item="item" />
        <infinite-loading @infinite="infiniteHandler"></infinite-loading>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import PodcastListItem from "./PodcastListItem";
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
  }
};
</script>
