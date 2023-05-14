<template>
  <div v-if="data">
    <b-row>
      <b-col>
        <div class="list-group mb-4">
          <EpisodeListItem
            v-for="item in data"
            :key="item.id"
            :item="item"
            :slug="slug"
            v-on:showModal="showModal"
          />
        </div>
        <infinite-loading @infinite="infiniteHandler"></infinite-loading>
        <div class="text-center" v-if="data.length == 0">
          <small class="text-muted">For new podcasts it takes a few minutes for episodes to appear.</small>
        </div>
      </b-col>
    </b-row>
    <b-modal v-if="selectedModal" size="lg" v-model="selectedModal" title="Episode Details">
      <EpisodeDetailModal :item="selectedItem" />
      <div slot="modal-footer">
        <b-button variant="outline-secondary" @click="hideModal">Close</b-button>
      </div>
    </b-modal>
  </div>
</template>

<script>
import EpisodeListItem from "./EpisodeListItem.vue";
import EpisodeDetailModal from "./EpisodeDetailModal.vue";

export default {
  props: ["slug"],
  data() {
    return {
      endpoint: `/api/podcastepisodes/${this.slug}/`,
      page: 1,
      data: [],
      selectedItem: {},
      selectedModal: false
    };
  },
  methods: {
    showModal(item) {
      this.selectedItem = item;
      this.$api
        .get(`/api/episodes/${item.id}/`)
        .then(response => (this.selectedItem = response.data))
        .catch(e => {});

      this.selectedModal = true;
    },
    hideModal() {
      this.selectedModal = false;
      this.selectedItem = {};
    }
  },
  components: { EpisodeListItem, EpisodeDetailModal }
};
</script>
