<template>
  <b-col :cols="cols" class="mb-3">
    <div @click="modalShow = !modalShow">
      <div class="thumbnail">
        <b-img rounded fluid :src="image" alt="Cover Art" />
      </div>
      <b-modal v-model="modalShow" :title="title">
        <div class="text-center">
          <b-img fluid rounded :src="image" alt="Cover Art"></b-img>
          <h3 class="mt-3" id="apsearch-title">{{title}}</h3>
          <h4 class="my-2 text-muted" id="apsearch-artist">{{item.artist}}</h4>
          <div>
            <b-badge v-for="badge in result.badges" :key="badge">{{badge}}</b-badge>
          </div>

          <div>
            <b-link :href="external_url" target="_blank">Apple Podcasts</b-link>
          </div>
        </div>
        <div slot="modal-footer">
          <b-button
            v-if="!addedToTapeDrive"
            :disabled="buttonDisabled"
            @click="addFeed"
            title="Add Feed to Tape Drive"
            variant="outline-secondary"
          >
            <b-spinner v-if="buttonDisabled" small></b-spinner>
            <span>Add to Tape Drive</span>
          </b-button>
          <b-button v-else variant="outline-success" @click="showFeed">Show in Tape Drive</b-button>
        </div>
      </b-modal>
      <p class="mt-2 text-center">
        <small>{{title}}</small>
      </p>
    </div>
  </b-col>
</template>

<script>
export default {
  props: {
    cols: { type: Number, default: 4 },
    item: {
      type: Object,
      default() {
        return {
          image: null
        };
      }
    }
  },
  data() {
    return {
      buttonDisabled: false,
      result: {
        title: "Fancy Podcast",
        artist: "This cool artist",
        badges: ["politics", "music"],
        image: "/bla.png"
      },
      modalShow: false,
      isInTapeDrive: false,
      addedToTapeDrive: null
    };
  },
  computed: {
    image() {
      if (this.item.artworkUrl600) {
        return this.item.artworkUrl600;
      }
    },
    title() {
      if (this.item.trackName) {
        return this.item.trackName;
      }
    },
    external_url() {
      if (this.item.collectionViewUrl) {
        return this.item.collectionViewUrl;
      }
    },
    feed_url() {
      if (this.item.feedUrl) {
        return this.item.feedUrl;
      }
    }
  },
  methods: {
    addFeed() {
      this.buttonDisabled = true;
      this.$api
        .post("/api/podcasts/add/", {
          feed_url: this.feed_url
        })
        .then(response => {
          this.addedToTapeDrive = response.data;
        })
        .catch(error => {
          console.log(error);
        })
        .then(() => {
          this.buttonDisabled = false;
        });
    },
    showFeed() {
      if (this.addedToTapeDrive) {
        this.$router.push({
          name: "PodcastDetail",
          params: { slug: this.addedToTapeDrive.slug }
        });
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.thumbnail {
  position: relative;
  overflow: hidden;
  padding-bottom: 100%;
  & img {
    position: absolute;
  }
}
</style>
