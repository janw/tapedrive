import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import InfiniteLoading from 'vue-infinite-loading';
import VueSpinners from 'vue-spinners';

import router from './router';
import Api from './api';
import Mixins from './mixins';
import Main from './App.vue';
import Spinner from './components/Spinner.vue';
import InfiniteNoMore from './components/InfiniteNoMore.vue';

import "./filters";

import 'typeface-fira-sans-condensed';
import './scss/main.scss';


Vue.use(BootstrapVue);
Vue.use(VueSpinners);

Vue.use(InfiniteLoading, {
  slots: {
    spinner: Spinner,
    noResults: InfiniteNoMore,
    noMore: InfiniteNoMore,
  },
});

Vue.use(Api);
Vue.use(Mixins);
Vue.use(router);

export default new Vue({
  el: '#app',
  router,
  template: '<Main/>',
  components: { Main },
});
