<template>
  <div>
    <b-alert v-model="showAlert" variant="secondary" dismissible>
      <span v-if="item.created">Added</span>
      <span v-else>Subscribed to</span>
      <router-link
        :to="{ name: 'PodcastDetail', params: { slug: item.slug }}"
        class="alert-link"
      >{{item.title}}</router-link>
      from {{item.url}}
    </b-alert>
  </div>
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
          created: true
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
