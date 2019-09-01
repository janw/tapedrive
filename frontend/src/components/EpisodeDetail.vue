<template>
  <div v-if="item">
    <h3 class="mb-0">
      <router-link
        class="text-muted"
        :to="{ name: 'PodcastDetail', params:{slug: item.podcast.slug}}"
      >{{item.podcast.title}}</router-link>
    </h3>
    <h2>{{item.title}}</h2>
    <b-row class="mb-4">
      <b-col>
        <img
          v-if="item.image"
          class="img-fluid rounded float-right col-md-4 mt-3 mt-md-0 ml-md-4 mb-1 px-0"
          :src="item.image"
        />
        <div v-if="item.description" id="podcast-summary" class="my-4" v-html="item.description"></div>
      </b-col>
    </b-row>

    <b-row class="mb-4">
      <b-col>
        <div
          class="d-flex justify-content-around flex-wrap px-0 py-2 border-top border-bottom text-center"
        >
          <div>
            <p class="text-muted mb-0">Published</p>
            <p class="mb-0">{{item.published | moment("from")}}</p>
          </div>
          <div v-if="item.downloaded" class>
            <p class="text-muted mb-0">Downloaded</p>
            <p class="mb-0">{{item.downloaded | moment("from")}}</p>
          </div>
        </div>
      </b-col>
    </b-row>
    <h3>Shownotes</h3>
    <b-row v-if="shownotes" class="mb-4">
      <b-col>
        <div class="shownotes" v-html="shownotes"></div>
        <div class="mt-5 text-center">
          <small class="text-muted">The above content has been taken from the podcast's feed.</small>
        </div>
      </b-col>
    </b-row>
  </div>
</template>

<script>
export default {
  props: ["slug", "episode"],
  data() {
    return {
      item: null,
      podcastData: null,
      shownotes: null
    };
  },
  created() {
    this.$api
      .get(`/api/episodes/${this.episode}/`)
      .then(response => (this.item = response.data));
    this.$api
      .get(`/api/episodes/${this.episode}/shownotes/`)
      .then(response => (this.shownotes = response.data));
  }
};
</script>

<style lang="scss" scoped>
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";
@import "~bootstrap/scss/mixins";
@import "~bootstrap/scss/utilities";

.shownotes {
  & img {
    @include img-fluid;
  }
}
</style>
