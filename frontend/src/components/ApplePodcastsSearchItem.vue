<template>
  <b-col>
    <a @click="modalShow = !modalShow" class="discovery-cover">
      <img class="img-fluid" :src="result.image" alt="Podcast Cover Art" />
    </a>
    <b-modal v-model="modalShow" :title="result.title">
      <div class="text-center">
        <b-img img-fluid rounded src="#" alt="Podcast Cover Art"></b-img>
        <h3 class="mt-3" id="apsearch-title">{{result.title}}</h3>
        <h4 class="my-2 text-muted" id="apsearch-artist">{{result.artist}}</h4>
        <div>
          <b-badge v-for="badge in result.badges" :key="badge">{{badge}}</b-badge>
        </div>
      </div>
      <div slot="modal-footer">
        <b-button variant="secondary" @click="modalShow=false">Add to Tape Drive</b-button>
      </div>
    </b-modal>
  </b-col>
</template>

<script>
export default {
  data() {
    return {
      result: {
        title: "Fancy Podcast",
        artist: "This cool artist",
        badges: ["politics", "music"],
        image: "/bla.png"
      },
      modalShow: false,
      isInTapeDrive: false
    };
  }
};
</script>
