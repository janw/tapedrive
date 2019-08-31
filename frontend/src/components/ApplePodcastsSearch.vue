<template>
  <div>
    <b-row>
      <b-col>
        <h3 class="mb-0 text-muted">Looking for something specific?</h3>
        <h2>Search the Apple Podcasts Directory</h2>
      </b-col>
    </b-row>
    <b-row class="mb-3">
      <b-col>
        <b-form @submit="search" class="mb-3">
          <label class="sr-only" label-for="feed-url">Feed URL</label>
          <b-input-group>
            <b-form-input v-model="searchTerm" placeholder="Enter URL" />
            <b-input-group-append>
              <b-button
                class="px-4"
                :disabled="buttonDisabled"
                @click="search"
                title="Add Feed to Tape Drive"
              >
                <b-spinner v-if="buttonDisabled" small></b-spinner>
                <span>Search</span>
              </b-button>
            </b-input-group-append>
          </b-input-group>
        </b-form>
      </b-col>
    </b-row>
    <b-row>
      <ApplePodcastsSearchItem
        v-for="(result, $index) in results"
        :key="$index"
        :item="result"
        :cols="resultCols"
      />
      <b-col cols="12" v-if="resultCount == 0">
        <p class="text-center">Sorry, there were no results for your search. 👎</p>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import ApplePodcastsSearchItem from "./ApplePodcastsSearchItem.vue";
import axios from "axios";

export default {
  data() {
    return {
      searchEndpoint: "https://itunes.apple.com/search",
      addEndpoint: "/api/podcasts/add/",
      buttonDisabled: false,
      showModal: false,
      searchTerm: "5by5",
      resultCount: null,
      results: []
    };
  },
  methods: {
    search() {
      if (this.searchTerm.length > 2) {
        this.buttonDisabled = true;
        axios
          .get(this.searchEndpoint, {
            params: {
              media: "podcast",
              term: this.searchTerm
            }
          })
          .then(response => {
            this.resultCount = response.data.resultCount;
            this.results = response.data.results;
          })
          .catch(error => {
            console.error(error);
          })
          .then(() => {
            this.buttonDisabled = false;
          });
      }
    }
  },
  computed: {
    resultCols() {
      if (!this.resultCount) {
        return;
      } else if (this.resultCount <= 3) {
        return 4;
      } else {
        return 3;
      }
    }
  },
  components: {
    ApplePodcastsSearchItem
  }
};
</script>