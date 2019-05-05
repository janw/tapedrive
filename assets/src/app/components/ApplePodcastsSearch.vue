<template>
  <div>
    <div class="row">
      <div class="col">
        <h3 class="mb-0 text-muted">Looking for something specific?</h3>
        <h2>Search the Apple Podcasts Directory</h2>
      </div>
    </div>
    <div class="row mb-3">
      <div class="col">
        <div id="apsearch">
          <label class="sr-only" for="id_search_term">Search Term</label>
          <div class="input-group">
            <input
              type="text"
              class="form-control my-2"
              name="search_term"
              id="id_search_term"
              placeholder="Search Term"
              v-model="searchTerm"
              @keyup.enter="search"
            >
            <div class="input-group-append">
              <button class="btn btn-secondary my-2 px-4" @click="search">
                Search
                <square v-bind:loading="loading"></square>
              </button>
            </div>
          </div>

          <div class="row px-2 mb-3 mt-2" v-if="results.length > 0">
            <ApplePodcastsSearchItem
              v-for="result in results"
              :key="result.id"
              :result="result"
              @details="showDetails"
            />
          </div>
          <div id="apsearch-noresults" class="row mb-3" style="display:none;">
            <div class="col-12">
              <p class="text-center">Sorry, there were no results for your search. 👎</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <b-modal v-model="showModal" ref="resultDetailsModal" hide-header>
      <img class="img-fluid rounded" :src="shownResult.image" alt="Podcast Cover Art">
      <h3 class="mt-3">{{shownResult.title}}</h3>
      <h4 class="my-2 text-muted">{{shownResult.author}}</h4>

      <div slot="modal-footer" class="w-100">
        <b-btn
          class="float-left"
          :disabled="addButton.disabled"
          :variant="addButton.variant"
          @click="addPodcast(shownResult)"
        >
          {{addButton.text}}
          <square v-bind:loading="addButton.spinner"></square>
        </b-btn>
        <b-btn class="float-right" variant="secondary" @click="showModal=false">Dismiss</b-btn>
      </div>
    </b-modal>
  </div>
</template>

<script>
import ApplePodcastsSearchItem from "./ApplePodcastsSearchItem.vue";

function initState() {
  return {
    loading: false,
    addButton: {
      spinner: false,
      variant: "primary",
      disabled: false,
      text: "Add to Tape Drive"
    },
    showModal: false,
    searchTerm: "",
    results: [],
    shownResult: {
      title: "<Title>",
      author: "<Author>"
    }
  };
}

export default {
  data() {
    return initState();
  },
  methods: {
    search() {
      const searchTerm = this.searchTerm.trim();
      if (searchTerm) {
        this.loading = true;
        this.$http
          .post("search/", {
            term: searchTerm
          })
          .then(response => {
            this.results = response.data;
            this.loading = false;
          })
          .catch(err => {
            this.loading = false;
            console.log(err);
          });
      }
    },
    showDetails(result) {
      this.shownResult = result;
      this.addButton = initState().addButton;
      this.showModal = true;
    },
    addPodcast(result) {
      this.addButton.disabled = true;
      this.addButton.spinner = true;
      console.log("Adding ", result);
      this.$http
        .post("add/", {
          feed_url: result.feed_url
        })
        .then(response => {
          this.addButton.variant = "success";
          this.addButton.spinner = false;
          this.addButton.text = "Successfully added";
        })
        .catch(err => {
          console.log(err);
          this.addButton.variant = "danger";
          this.addButton.spinner = false;
          this.addButton.text = "Something went wrong";
        });
    }
  },
  components: {
    ApplePodcastsSearchItem
  }
};
</script>


<style>
.sl-spinner {
  display: inline-block;
  margin-bottom: -2px;
  margin-left: 6px;
}
</style>
