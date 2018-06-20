<template>
  <div>
    <div class="row">
      <div class="col">
        <h3 class="mb-0 text-muted ">Looking for something specific?</h3>
        <h2>Search the Apple Podcasts Directory</h2>
      </div>
    </div>
    <div class="row mb-3">
      <div class="col">
        <div id="apsearch">
          <label class="sr-only" for="id_search_term">Search Term</label>
          <div class="input-group">
            <input type="text" class="form-control my-2" name="search_term" id="id_search_term" placeholder="Search Term" v-model="searchTerm" @keyup.enter="search">
            <div class="input-group-append">
              <button class="btn btn-secondary my-2 px-4" @click="search">
              Search <spinner :status="loading" color="#ccc" size="16"></spinner>
            </button>
            </div>
          </div>

          <div class="row px-2 mb-3 mt-2"
               v-if="results.length > 0">
            <a href="#" class="discovery-cover"
               data-toggle="modal" data-target="#apsearch-details" data-id="#"
               v-for="result in results" >
              <img class="img-fluid" :src="result.image" alt="Podcast Cover Art">
            </a>
          </div>
          <div id="apsearch-noresults" class="row mb-3" style="display:none;">
            <div class="col-12">
              <p class="text-center">Sorry, there were no results for your search. 👎</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Spinner from 'vue-spinner-component/src/Spinner.vue'

export default {
  data () {
    return {
      loading: false,
      searchTerm: 'freakshow',
      results: []
    }
  },
  methods: {
    search () {
      const searchTerm = this.searchTerm.trim()
      if (searchTerm) {
        this.loading = true;
        this.$http.post('search/', {
          term: searchTerm
        })
        .then((response) => {
          this.results = response.data;
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          console.log(err);
        })
      }
    }
  },
  components: {
    Spinner
  }
}

</script>


<style>

.sl-spinner{
  display: inline-block;
  margin-bottom: -2px;
  margin-left: 6px;
}

</style>
