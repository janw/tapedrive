<template>
  <div class="overlay-wrapper">
    <div class="form-signin text-center border rounded shadow">
      <img class="img-logo w-50" src="../images/icon@3x.png" alt="Tape Drive Logo" />
      <h1 class="my-4">Tape Drive</h1>
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

.backdrop {
  position: fixed;
  top: 0px;
  left: 0px;
  width: 100%;
  height: 100%;
  z-index: -100;
  background-image: url("../images/michael-mroczek-195362-unsplash.jpg");
  background-repeat: no-repeat;
  background-position: center center;
  background-attachment: fixed;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  opacity: 0.5;
  animation: filter-animation 4s;
}

.filter-fade {
  filter: grayscale(1) brightness(60%) contrast(150%);
  opacity: 0.5;
}

@keyframes filter-animation {
  0%,
  25% {
    opacity: 0;
  }

  0%,
  75% {
    filter: grayscale(1);
  }

  100% {
    filter: grayscale(0);
    opacity: 0.5;
  }
}

#credit_badge {
  position: fixed;
  background: rgba(white, 0.8);
  color: #333;
  text-decoration: none;
  left: 4px;
  bottom: 4px;
  padding: 2px 3px;
  font-size: 10px;
  display: inline-block;
  border-radius: 3px;
}

.delay-visibility {
  animation: delayed-opacity-animation 4s;
}

@keyframes delayed-opacity-animation {
  0%,
  65% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
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

  #reset_link {
    font-size: 0.8rem;
  }
}

.footer {
  z-index: -5;
}
</style>