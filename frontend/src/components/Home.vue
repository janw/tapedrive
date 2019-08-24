<template>
  <div></div>
</template>

<script>
export default {
  name: "home",
  data() {
    return {
      msg: "Welcome to Your Vue.js App"
    };
  },
  mounted() {
    axios
      .get("https://api.coindesk.com/v1/bpi/currentprice.json")
      .then(response => (this.info = response));
  }
};
</script>
