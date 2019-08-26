import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import VueResource from 'vue-resource';
import VueSpinners from 'vue-spinners';
Vue.use(require('vue-moment'));
Vue.use(BootstrapVue);
Vue.use(VueSpinners);

import Main from './components/Main.vue';
import router from './router';
import Api from './api';

Vue.use(Api);

export default new Vue({
  el: '#app',
  router,
  template: '<Main/>',
  components: { Main },
});

import 'typeface-fira-sans-condensed';
import './scss/main.scss';
