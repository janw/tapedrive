<template>
  <div>
    <div class="backdrop"></div>
    <a
      id="credit_badge"
      class="d-none d-sm-block delay-visibility"
      href="https://unsplash.com/photos/byW_4p0EKMA?utm_source=unsplash&utm_medium=referral&utm_content=creditBadge"
      target="_blank"
      rel="nofollow noopener noreferrer"
      title="Photo by Michael Mroczek via Unsplash.com"
    >
      <span style="display:inline-block;padding:2px 3px;">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          style="height:12px;width:auto;position:relative;vertical-align:middle;top:-1px;fill:#333;"
          viewBox="0 0 32 32"
        >
          <title>unsplash-logo</title>
          <path
            d="M20.8 18.1c0 2.7-2.2 4.8-4.8 4.8s-4.8-2.1-4.8-4.8c0-2.7 2.2-4.8 4.8-4.8 2.7.1 4.8 2.2 4.8 4.8zm11.2-7.4v14.9c0 2.3-1.9 4.3-4.3 4.3h-23.4c-2.4 0-4.3-1.9-4.3-4.3v-15c0-2.3 1.9-4.3 4.3-4.3h3.7l.8-2.3c.4-1.1 1.7-2 2.9-2h8.6c1.2 0 2.5.9 2.9 2l.8 2.4h3.7c2.4 0 4.3 1.9 4.3 4.3zm-8.6 7.5c0-4.1-3.3-7.5-7.5-7.5-4.1 0-7.5 3.4-7.5 7.5s3.3 7.5 7.5 7.5c4.2-.1 7.5-3.4 7.5-7.5z"
          />
        </svg>
      </span>
      <span style="display:inline-block;padding:2px 3px;">Michael Mroczek</span>
    </a>
  </div>
</template>

<style lang="scss">
@import "~bootstrap/scss/functions";
@import "~bootstrap/scss/variables";
@import "~bootstrap/scss/mixins";

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
