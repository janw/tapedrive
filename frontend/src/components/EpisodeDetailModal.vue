<template>
  <div v-if="item">
    <b-container fluid>
      <h1 class="mb-3">{{item.title}}</h1>
      <b-row class="mb-4">
        <b-col v-html="item.description"></b-col>
      </b-row>

      <b-row class="mb-4">
        <b-col>
          <div
            class="d-flex justify-content-around flex-wrap px-0 py-2 border-top border-bottom text-center"
          >
            <div>
              <p class="text-muted mb-0">Published</p>
              <p class="mb-0">{{item.published | fromLocalDateTime}}</p>
            </div>
            <div v-if="item.downloaded" class>
              <p class="text-muted mb-0">Downloaded</p>
              <p class="mb-0">{{item.downloaded | fromLocalDateTime}}</p>
            </div>
          </div>
        </b-col>
      </b-row>

      <div v-if="has_chapters" class="row mb-2">
        <div class="col">
          <p class="text-center">
            <b-button v-b-toggle.collapse-chapters variant="outline-secondary">
              <span class="when-opened">Hide</span>
              <span class="when-closed">Show</span> Chapters
            </b-button>
          </p>
          <b-collapse id="collapse-chapters" class="mt-2">
            <table class="table table-hover">
              <tr>
                <th class="text-right">Timestamp</th>
                <th>Title</th>
              </tr>
              <tr v-for="chapter in item.chapters" :key="chapter.id">
                <td class="text-muted text-right text-mono">
                  <small>{{chapter.starttime | millisToTimestamp }}</small>
                </td>
                <td>{{chapter.title}}</td>
              </tr>
            </table>
          </b-collapse>
        </div>
      </div>
      <b-row v-if="shownotesContent" class="mb-3">
        <b-col>
          <div class="container shownotes" v-html="shownotesContent"></div>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
export default {
  props: ["item"],
  data() {
    return {
      shownotesContent: null,
      shownotesAvailable: false
    };
  },
  computed: {
    has_chapters() {
      if (this.item.chapters && this.item.chapters.length > 0) {
        return true;
      }
    },
    has_shownotes() {
      if (this.item.shownotes && this.item.shownotes.length > 0) {
        return true;
      }
    }
  }
};
</script>

<style lang="scss">
@import "./node_modules/bootstrap/scss/functions";
@import "./node_modules/bootstrap/scss/variables";
@import "./node_modules/bootstrap/scss/mixins";
@import "./node_modules/bootstrap/scss/utilities";

.collapsed > .when-opened,
:not(.collapsed) > .when-closed {
  display: none;
}

.shownotes {
  & img {
    @include img-fluid;
  }
}
.img-has-src {
  @extend .border;
  @extend .rounded;
  display: inline-block;
  padding: 0.5rem;
  margin: 0.1rem;
  font-size: 0.8rem;
  text-align: center;
  & > img {
    display: none;
  }
}

.text-mono {
  font-family: $font-family-monospace;
  font-size: 0.95rem;
}
</style>
