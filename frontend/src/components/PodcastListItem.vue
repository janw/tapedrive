<template>
  <b-card class="flex-md-row mb-4 overflow-hidden" no-body>
    <router-link :to="{ name: 'PodcastDetail', params: { slug: item.slug }}" class="card-full-link"></router-link>
    <img
      v-if="item.image"
      class="card-img-top d-md-none border-bottom"
      :src="item.image"
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

      <p class="card-text mt-auto mb-0 text-muted">
        <span
          v-if="item.fetched !== null"
        >{{item.num_episodes}} episodes, last one published {{item.last_published | moment("from", "now")}}.</span>
        <span v-else>Episodes have not been fetched yet</span>
      </p>
    </b-card-body>
    <div class="d-none d-md-block bg-dark card-img-container">
      <div class="d-none d-md-flex flex-column h-100 justify-content-center align-objects-center">
        <img v-if="item.image" :src="item.image" class="card-img-right" />
        <div v-else>
          <h6 class="mx-3 mt-3 text-muted">{{object.title}}</h6>
          <p class="mx-3 text-muted">{% trans "(No Cover)" %}</p>
        </div>
      </div>
    </div>
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
