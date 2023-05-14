<template>
  <div v-if="data">
    <h1 class="mb-1 text-center text-md-left">{{data.title}}</h1>

    <div class="row">
      <div class="col">
        <h5 class="text-muted mb-1" v-html="data.subtitle"></h5>
        <img
          v-if="data.image"
          class="img-fluid rounded float-right col-md-4 mt-3 mt-md-0 ml-md-4 mb-1 px-0"
          :src="data.image"
        />
        <div v-if="data.summary" id="podcast-summary" class="my-4" v-html="summary_p"></div>
      </div>
    </div>
    <EpisodeList :slug="data.slug" />
  </div>
</template>

<script>
import EpisodeList from "./EpisodeList.vue";
export default {
  props: ["slug"],
  data() {
    return {
      data: null
    };
  },
  computed: {
    summary_p() {
      if (this.data.summary.startsWith("<p>")) {
        return this.data.summary;
      }
      return "<p>" + this.data.summary + "</p>";
    }
  },
  created() {
    this.$api
      .get(`/api/podcasts/${this.slug}/`)
      .then(response => (this.data = response.data))
      .catch(e => {});
  },
  components: { EpisodeList }
};
</script>
