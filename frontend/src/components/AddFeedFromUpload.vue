<template>
  <div>
    <b-form @submit="onSubmit" v-if="showForm">
      <b-form-group
        label="Feed URL"
        label-for="feed-url"
        description="Named by the format, this is often also called 'RSS feed'."
      >
        <b-form-input v-model="feed_url" placeholder="Enter a RSS feed URL"></b-form-input>
      </b-form-group>
      <b-form-group
        label="OPML File"
        label-for="feed-url"
        description="Many podcast clients allow you to export all you subscriptions at once as an OPML file."
      >
        <b-form-file
          v-model="opml_file"
          placeholder="Choose an file or drop it here"
          drop-placeholder="Drop here"
        ></b-form-file>
      </b-form-group>
      <b-button type="submit" class="btn-lg mt-3">Add Podcasts</b-button>
    </b-form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      feed_url: "",
      opml_file: null,
      showForm: true,
      showResults: false
    };
  },
  methods: {
    onSubmit() {
      console.log("Boom!");
    }
  }
};
</script>