<template>
  <div class="overlay-wrapper">
    <div class="form-signin text-center border rounded shadow">
      <img class="img-logo w-50 mt-3" src="../images/icon@3x.png" alt="Tape Drive Logo" />
      <h1 class="my-4">Reset Password</h1>

      <div v-if="resetToken">
        <b-form @submit="confirmReset">
          <label class="sr-only" for="new_password1">New Password</label>
          <b-form-input
            name="new_password1"
            type="password"
            v-model="password"
            placeholder="New Password"
          ></b-form-input>
          <label class="sr-only" for="new_password2">Confirm New Password</label>
          <b-form-input
            name="new_password2"
            type="password"
            v-model="password"
            placeholder="Confirm New Password"
          ></b-form-input>

          <b-button
            variant="outline-secondary"
            :disabled="notFilledYet"
            type="submit"
            class="btn-lg mt-3"
          >Confirm</b-button>
        </b-form>
      </div>
      <div v-else>
        <p>To reset your password, please enter the email address associated with your account.</p>
        <b-alert
          v-bind:show="requestSubmitted"
          variant="warning"
        >Thank you. If an account is found for that address, you will shortly receive further instructions via email.</b-alert>
        <b-form @submit="submitRequest">
          <label class="sr-only" for="email">Email address</label>
          <b-form-input name="email" v-model="email" placeholder="Email address"></b-form-input>

          <b-button
            variant="secondary"
            :disabled="submitDisabled"
            type="submit"
            class="btn mt-3"
          >Submit</b-button>
        </b-form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      resetToken: "",
      requestSubmitted: false,
      email: ""
    };
  },
  computed: {
    submitDisabled: function() {
      return this.email.length < 3 || this.requestSubmitted;
    }
  },
  methods: {
    confirmReset(e) {
      e.preventDefault();
    },
    submitRequest(e) {
      e.preventDefault();
      this.requestSubmitted = true;
      this.$api
        .post("/api/auth/token/", {
          email: this.email
        })
        .then(response => {})
        .catch(error => {
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

.form-signin {
  width: 100%;
  max-width: 500px;
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
