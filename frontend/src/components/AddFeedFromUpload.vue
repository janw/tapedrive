<template>
  <div>
    <b-row>
      <b-col>
        <h3 class="mb-0 text-muted">Have one handy?</h3>
        <h2>Add from a feed link</h2>
      </b-col>
    </b-row>
    <b-form @submit="addFeed" class="mb-3">
      <label class="sr-only" label-for="feed-url">Feed URL</label>
      <b-input-group>
        <b-form-input :state="validInput" v-model="feed_url" placeholder="Enter URL" />
        <b-input-group-append>
          <b-button
            class="px-4"
            :disabled="buttonDisabled"
            @click="addFeed"
            title="Add Feed to Tape Drive"
          >
            <b-spinner v-if="buttonDisabled" small></b-spinner>
            <span>Add</span>
          </b-button>
        </b-input-group-append>
      </b-input-group>
      <b-form-invalid-feedback
        v-if="upstreamError"
        :state="validInput"
      >Invalid response for this URL: {{upstreamError.status}} {{upstreamError.statusText}}</b-form-invalid-feedback>
    </b-form>
    <AddFeedProcessedUrl v-for="(item, $index) in data" :key="$index" :item="item" />
  </div>
</template>

<script>
import AddFeedProcessedUrl from "./AddFeedProcessedUrl";
export default {
  data() {
    return {
      feed_url: "",
      validInput: null,
      upstreamError: null,
      upstreamErrorCtx: null,
      buttonDisabled: false,
      data: []
    };
  },
  methods: {
    validationError(msg) {
      this.validInput = false;
      this.validationErrors = null;
    },
    addFeed() {
      if (this.feed_url.length >= 4) {
        this.validInput = null;
        this.buttonDisabled = true;
        this.$api
          .post("/api/podcasts/add/", {
            feed_url: this.feed_url
          })
          .then(response => {
            this.data.unshift(response.data);
            this.feed_url = "";
          })
          .catch(error => {
            console.log(error);
            this.validInput = false;
            this.upstreamError = error;
            if (error.data) {
              this.upstreamErrorCtx = error.data;
            }
          })
          .then(() => {
            setTimeout(() => {
              this.buttonDisabled = false;
            }, 100);
          });
      } else {
        this.validationError("Input is not long enough.");
      }
    }
  },
  components: { AddFeedProcessedUrl }
};
</script>
