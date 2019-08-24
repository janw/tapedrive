<template>
  <b-card class="flex-md-row mb-4 overflow-hidden" no-body>
    <router-link :to="{ name: 'PodcastDetail', params: { slug: item.slug }}" class="card-full-link"></router-link>
    <img
      v-if="item.image"
      class="card-img-top d-md-none border-bottom"
      :src="item.image.url"
      alt="Card image cap"
    />
    <b-card-body class="d-flex flex-column align-objects-start">
      <h3 class="card-title">
        {{item.title}}
        <small>
          <b-badge>{{item.id}}</b-badge>
        </small>
      </h3>

      <h6 v-if="item.subtitle" class="card-text text-muted">{{ item.subtitle }}</h6>
      {{item.feed_url}}
    </b-card-body>
  </b-card>
</template>

<script>
export default {
  props: {
    item: {
      type: Object,
      // Object or array defaults must be returned from
      // a factory function
      default() {
        return {
          title: "Untitled",
          subtitle: "Lorem Ipsum"
        };
      }
    }
  },
  data() {
    return {
      //   title: "Fancy Podcast",
      //   artist: "This cool artist",
      //   badges: ["politics", "music"],
      //   image: "/bla.png"
      // },
      modalShow: false,
      isInTapeDrive: false
    };
  }
};
</script>
