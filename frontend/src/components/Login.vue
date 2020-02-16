<template>
  <div class="overlay-wrapper">
    <div class="form-signin text-center border rounded shadow">
      <img class="img-logo w-50 mt-3" src="../images/icon@3x.png" alt="Tape Drive Logo" />
      <h1 class="my-4">Tape Drive</h1>
      <b-form @submit="doLogin">
        <b-alert v-bind:show="loginFailed" variant="danger">Login failed. Please try again.</b-alert>

        <label class="sr-only" for="username">Username</label>
        <b-form-input name="username" v-model="username" placeholder="Username"></b-form-input>

        <label class="sr-only" for="password">Password</label>
        <b-form-input name="password" type="password" v-model="password" placeholder="Password"></b-form-input>

        <b-button
          variant="outline-secondary"
          :disabled="notFilledYet"
          type="submit"
          class="px-4 mt-3 mb-2"
        >Log in</b-button>
      </b-form>
      <b-link
        :to="{ name: 'ResetPassword' }"
        class="reset_link text-muted"
      >Forgot your username or password?</b-link>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      loginFailed: false,
      username: "",
      password: ""
    };
  },
  computed: {
    notFilledYet: function() {
      return this.username.length == 0 || this.password.length == 0;
    }
  },
  methods: {
    doLogin(e) {
      e.preventDefault();
      this.loginFailed = false;
      this.$api
        .post("/api/auth/token/", {
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
        .catch(error => {
          console.error(error.response);
          this.loginFailed = true;
        });
    },
    loggedIn() {
      console.log("Logged in");
    }
  }
};
</script>

<style lang="scss">
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";
@import "~bootstrap/scss/mixins";

.overlay-wrapper {
  display: -webkit-flex;
  display: flex;
  -webkit-box-align: center;
  -webkit-flex-align: center;
  -ms-flex-align: center;
  -webkit-align-items: center;
  align-items: center;
  position: fixed;
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
}

.form-signin {
  width: 100%;
  max-width: 400px;
  margin: auto;
  padding: 20px;
  z-index: 10;

  @include media-breakpoint-up(sm) {
    padding: 60px;
  }

  &,
  & input {
    -webkit-backdrop-filter: blur(5px);
    backdrop-filter: blur(5px);
    background: rgba($white, 0.9);
  }

  & .form-control {
    position: relative;
    box-sizing: border-box;
    height: auto;
    padding: 10px;
    font-size: 16px;
  }

  & input[name="username"],
  & input[name="new_password1"] {
    margin-bottom: -1px;
    border-bottom-right-radius: 0;
    border-bottom-left-radius: 0;
  }
  & input[name="password"],
  & input[name="new_password2"] {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

  & input:focus,
  & button:focus {
    outline: none;
    box-shadow: 0 0 3px $secondary;
    border-color: $secondary;
    z-index: 2;
    background: rgba($secondary, 0.1);
    border-radius: $border-radius !important;
  }

  .reset_link {
    font-size: 0.8rem;
  }
}

.footer {
  z-index: -5;
}
</style>
