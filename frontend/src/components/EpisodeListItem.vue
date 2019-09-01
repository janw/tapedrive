<template>
  <b-list-group-item class="flex-column align-items-start">
    <h3 class="my-2">{{item.title}}</h3>
    <h5 v-if="item.subtitle" class="mb-2 text-muted" v-html="item.subtitle"></h5>

    <div class="w-100 d-md-flex justify-content-between">
      <small class="mt-3 text-muted">Published {{item.published | moment("calendar")}}</small>
      <div class="mt-2 text-center text-md-left">
        <b-button-group>
          <b-button v-on:click="$emit('showModal', item)" variant="outline-secondary">Peek</b-button>
          <b-button
            v-if="slug"
            :to="{ name: 'EpisodeDetail', params: { slug: slug, episode: item.id }}"
            variant="outline-secondary"
          >Details</b-button>
        </b-button-group>
      </div>
    </div>
  </b-list-group-item>
</template>

<script>
export default {
  props: {
    slug: {
      type: String
    },
    item: {
      type: Object,
      // Object or array defaults must be returned from
      // a factory function
      default() {
        return {
          title: "Untitled",
          id: "762b12ae-e163-4215-b290-4204193d24d3",
          published: "2019-08-28T02:16:44+02:00",
          downloaded: null
        };
      }
    }
  },
  data() {
    return {
      modalShow: false
    };
  }
};
</script>
