<template>
  <div>
    <h1 class="text-center text-md-left">Add New Podcasts</h1>

    <b-row>
      <b-col class="mb-4 text-center text-md-left">
        <add-feed-from-upload></add-feed-from-upload>
      </b-col>
    </b-row>
    <b-row>
      <b-col class="mb-4 text-center text-md-left">
        <apple-podcasts-search></apple-podcasts-search>
      </b-col>
    </b-row>
    <!-- <b-row>
      <b-col class="mb-4 text-center text-md-left">
        <apple-podcasts-toplist></apple-podcasts-toplist>
      </b-col>
    </b-row>-->
    <b-row v-if="showAppleAttribution">
      <b-col class="text-center my-3">
        <small class="text-muted">
          Search Results and Content courtesy of iTunes,
          <br />Copyright © 2018 Apple Inc. All rights reserved.
        </small>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import AddFeedFromUpload from "./AddFeedFromUpload.vue";
import ApplePodcastsSearch from "./ApplePodcastsSearch.vue";
import ApplePodcastsToplist from "./ApplePodcastsToplist.vue";

export default {
  name: "addfeeds",
  data() {
    return {
      showAppleAttribution: false,
      msg: "Welcome to Your Vue.js App"
    };
  },
  components: {
    ApplePodcastsSearch,
    ApplePodcastsToplist,
    AddFeedFromUpload
  }
};
</script>
