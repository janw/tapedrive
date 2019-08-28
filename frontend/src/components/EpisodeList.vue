<template>
  <div class="row" v-if="data">
    <div class="col-12">
      <div class="list-group mb-4">
        <EpisodeListItem
          v-for="item in data.results"
          :key="item.id"
          :item="item"
          v-on:showModal="showModal"
        />

        <div v-if="selectedModal">
          <b-modal size="lg" v-model="selectedModal" title="Episode Details">
            <EpisodeDetailModal :item="selectedItem" />
            <div slot="modal-footer">
              <b-button variant="outline-secondary" @click="hideModal">Close</b-button>
            </div>
          </b-modal>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EpisodeListItem from "./EpisodeListItem";
import EpisodeDetailModal from "./EpisodeDetailModal";

export default {
  props: ["slug"],
  data() {
    return {
      data: null,
      selectedItem: {},
      selectedModal: false
    };
  },
  mounted() {
    this.$api
      .get(`/api/podcastepisodes/${this.slug}/`)
      .then(response => (this.data = response.data))
      .catch(e => {});
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