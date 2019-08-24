<template>
  <div class="h-100 d-flex align-items-center py-5 text-center">
    <div class="form-signin">
      <b-form @submit="doLogin">
        <b-form-group label="Username" label-for="username">
          <b-form-input v-model="username"></b-form-input>
        </b-form-group>
        <b-form-group label="Password" label-for="password">
          <b-form-input type="password" v-model="password"></b-form-input>
        </b-form-group>
        <b-button type="submit" class="btn-lg mt-3">Log in</b-button>
      </b-form>
    </div>
    <div class="backdrop"></div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: "",
      password: ""
    };
  },
  methods: {
    doLogin(e) {
      console.log("Logging in");
      e.preventDefault();
      this.$api
        .post("/auth/token/", {
          username: this.username,
          password: this.password
        })
        .then(response => {
          localStorage.setItem("access", response.data.access);
          localStorage.setItem("refresh", response.data.refresh);

          if (localStorage.getItem("access") != null) {
            localStorage.setItem("user", this.username);
            this.$emit("loggedIn");
            if (this.$route.params.nextUrl != null) {
              this.$router.push(this.$route.params.nextUrl);
            } else {
              this.$router.push("/");
            }
          }
        })

        .catch(function(error) {
          console.error(error.response);
        });
    },
    loggedIn() {
      console.log("Logged in");
    }
  }
};
</script>
