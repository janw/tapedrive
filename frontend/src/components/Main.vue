<template>
  <div id="app">
    <div class="wrapper">
      <header v-if="!$route.meta.hideHeader" id="navbar" class="border-bottom pt-3 p-md-2 mb-3">
        <div class="container d-flex flex-column flex-md-row align-items-center">
          <a
            class="d-flex align-items-center align-items-center align-items-md-center site-title"
            href="/"
          >
            <img class="img-logo" src="../images/icon@2x.png" alt />

            <h1>
              Tape Drive
              <small class="d-block d-md-inline-block text-muted">Podcast Archive</small>
            </h1>
          </a>

          <b-nav class="justify-content-center mt-2 mt-md-0 ml-md-auto">
            <b-nav-item
              v-bind:class="{ active: $route.path === route.path }"
              v-for="route in menuRoutes"
              :to="route"
              :key="route.path"
            >{{route.name}}</b-nav-item>
            <b-nav-item-dropdown id="dropdown-settings" :text="username">
              <b-dropdown-header class="pb-0">Logged in as</b-dropdown-header>
              <p class="mx-4 mb-2">{{username}}</p>
              <b-dropdown-divider></b-dropdown-divider>
              <b-dropdown-item>
                <a href="/admin">Administration</a>
              </b-dropdown-item>
              <b-dropdown-item>Settings</b-dropdown-item>
              <b-dropdown-divider></b-dropdown-divider>
              <b-dropdown-item v-on:click="logOut()">Log out</b-dropdown-item>
            </b-nav-item-dropdown>
          </b-nav>
        </div>
      </header>
      <main role="main" class="container pt-3">
        <transition name="fade" mode="out-in">
          <router-view></router-view>
        </transition>
      </main>
      <footer class="footer">
        <div class="container">
          <small class="my-0 text-muted">
            <a class="text-muted" href="https://tapedrive.io">Tape Drive</a>
            is licensed under the Apache License 2.0. Thank you for using it.
          </small>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: "wrapper",
  data() {
    return {
      loading: true
    };
  },
  computed: {
    menuRoutes() {
      return this.$router.options.routes.filter(function(route) {
        return route.showOnMenu == true;
      });
    },
    username() {
      return localStorage.getItem("user");
    }
  },
  methods: {
    logOut() {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      this.$router.push("/login");
    }
  }
};
</script>

<style>
a h1 {
  color: #333;
}

.fade-enter-active,
.fade-leave-active {
  transition-duration: 0.1s;
  transition-property: opacity;
  transition-timing-function: ease-in-out;
}

.fade-enter,
.fade-leave-active {
  opacity: 0;
}
</style>