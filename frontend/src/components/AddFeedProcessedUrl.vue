<template>
  <b-alert v-model="showAlert" variant="secondary" dismissible>
    <span v-if="item.created_now">Added</span>
    <span v-else>Subscribed to</span>
    <router-link
      :to="{ name: 'PodcastDetail', params: { slug: item.slug }}"
      class="alert-link"
    >{{item.title}}</router-link>
    from {{item.feed_url}}
  </b-alert>
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
          feed_url: "https://tapedrive.io/randomfeed.xml",
          slug: "slug-123",
          created_now: true
        };
      }
    }
  },
  data() {
    return {
      showAlert: true
    };
  }
};
</script>
