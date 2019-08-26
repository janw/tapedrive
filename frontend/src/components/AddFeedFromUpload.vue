<template>
  <div>
    <b-form @submit="addFeed" v-if="showForm">
      <b-form-group
        label="Feed URL"
        label-for="feed-url"
        description="Named by the format, this is often also called 'RSS feed'."
      >
        <b-input-group>
          <b-form-input :state="validInput" v-model="feed_url" placeholder="Enter a feed URL" />
          <b-input-group-append>
            <b-button @click="addFeed" title="Add Feed to Tape Drive">Add</b-button>
          </b-input-group-append>
        </b-input-group>
        <b-form-invalid-feedback
          v-for="error in validationErrors"
          :key="error.id"
          :state="validInput"
        >{{error}}</b-form-invalid-feedback>
      </b-form-group>
    </b-form>
    <AddFeedProcessedUrl v-for="item in data" v-bind:key="item.id" :item="item" />
  </div>
</template>

<script>
import AddFeedProcessedUrl from "./AddFeedProcessedUrl";
export default {
  data() {
    return {
      feed_url: "",
      opml_file: null,
      showForm: true,
      showResults: false,
      validInput: null,
      validationErrors: null,
      data: [
        {
          title: "Untitled",
          url: "https://tapedrive.io/randomfeed.xml",
          slug: "slug-123",
          created: true
        }
      ]
    };
  },
  methods: {
    validationError(msg) {
      this.validInput = false;
      this.validationErrors = null;
    },
    addFeed() {
      if (this.feed_url.length >= 4) {
        this.$api
          .post("/api/podcasts/add/", {
            feed_url: this.feed_url
          })
          .then(response => {
            var data = response.data;
            data["url"] = this.feed_url;
            response.status == 200
              ? (data["created"] = false)
              : (data["created"] = true);
            this.data.unshift(data);
            this.feed_url = "";
          })
          .catch(error => {
            console.log(error);
            this.validInput = false;
            this.validationErrors = error.data;
          });
      } else {
        this.validationError("Input is not long enough.");
      }
    }
  },
  components: { AddFeedProcessedUrl }
};
</script>