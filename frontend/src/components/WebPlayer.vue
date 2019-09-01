<template>
  <div v-if="showPlayer" class="navbar fixed-bottom navbar-light justify-content-center">
    <!-- <img class="img-logo" src="../images/icon@2x.png" alt /> -->

    <!-- <b-navbar-nav>
      <b-nav-item href="#">Link</b-nav-item>
    </b-navbar-nav>-->
    <div class="container flex-nowrap">
      <b-button-toolbar class="flex-nowrap">
        <b-button-group class="mx-1" size="sm">
          <b-button variant="outline-secondary" class="px-3">
            <fa-icon :icon="icons.faUndo" fixed-width />
          </b-button>
          <b-button variant="outline-secondary" class="px-3">
            <fa-icon :icon="icons.faPlay" fixed-width />
          </b-button>
          <b-button variant="outline-secondary" class="px-3">
            <fa-icon :icon="icons.faRedo" fixed-width />
          </b-button>
        </b-button-group>
        <b-button-group class="mx-1" size="sm">
          <b-button variant="outline-secondary" class="px-2">
            <fa-icon :icon="icons.faStepBackward" fixed-width />
          </b-button>
          <b-button variant="outline-secondary" class="px-2">
            <fa-icon :icon="icons.faList" fixed-width />
          </b-button>
          <b-button variant="outline-secondary" class="px-2">
            <fa-icon :icon="icons.faStepForward" fixed-width />
          </b-button>
        </b-button-group>
      </b-button-toolbar>
      <div class="d-flex flex-column mx-1 minwidth-0">
        <div class="d-flex align-items-end minwidth-0">
          <div class="title">{{playbackState.title}}</div>
          <div class="timestamp flex-shrink-0 ml-2">12:34 / 1:12:51</div>
        </div>
        <b-progress
          :value="playbackState.currentDuration"
          :max="playbackState.totalDuration"
          variant="secondary"
          height="7px"
        ></b-progress>
      </div>
    </div>
  </div>
</template>

<script>
import {
  faList,
  faUndo,
  faRedo,
  faFastBackward,
  faStepBackward,
  faFastForward,
  faStepForward,
  faPlay,
  faWindowClose
} from "@fortawesome/free-solid-svg-icons";

export default {
  data() {
    return {
      icons: {
        faList: faList,
        faUndo: faUndo,
        faRedo: faRedo,
        faFastBackward: faFastBackward,
        faStepBackward: faStepBackward,
        faFastForward: faFastForward,
        faStepForward: faStepForward,
        faWindowClose: faWindowClose,
        faPlay: faPlay
      },
      showPlayer: true,
      playbackState: {
        title:
          "Reconcilable Differences 111: Brackets Around the Brackets Reconcilable Differences 111: Brackets Around the Brackets",
        podcast: "reconcilable-differences",
        episode: "0d02b057-b9ca-4b41-9dcb-4a162831313a",
        currentDuration: 102,
        totalDuration: 1512
      }
    };
  },
  computed: {
    currentPercentage() {
      return (
        this.playbackState.currentDuration / this.playbackState.totalDuration
      );
    }
  }
};
</script>

<style lang="scss" scoped>
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";

.img-logo {
  filter: opacity(0.25);
}
.navbar {
  font-size: 0.75rem;
  border-top: 1px solid rgba(50, 50, 50, 0.1);
  background-color: darken($white, 5%);
}
.btn-group {
  & > .btn:last-child:not(.dropdown-toggle),
  & > .btn-group:last-child > .btn {
    border-top-right-radius: 1.15rem;
    border-bottom-right-radius: 1.15rem;
  }
  & > .btn:first-child:not(.dropdown-toggle),
  & > .btn-group:first-child > .btn {
    border-top-left-radius: 1.15rem;
    border-bottom-left-radius: 1.15rem;
  }
}
.minwidth-0 {
  min-width: 0;
}
.title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
