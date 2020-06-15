import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import InfiniteLoading from 'vue-infinite-loading';
import VueSpinners from 'vue-spinners';

import router from './router';
import Api from './api';
import Mixins from './mixins';
import Main from './components/Main';
import Spinner from './components/Spinner';
import InfiniteNoMore from './components/InfiniteNoMore';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import "./filters";

Vue.component('fa-icon', FontAwesomeIcon);
Vue.use(BootstrapVue);
Vue.use(VueSpinners);

Vue.use(InfiniteLoading, {
  slots: {
    spinner: Spinner,
    noResults: '',
    noMore: InfiniteNoMore,
  },
});

Vue.use(Api);
Vue.use(Mixins);

export default new Vue({
  el: '#app',
  router,
  template: '<Main/>',
  components: { Main },
});

import 'typeface-fira-sans-condensed';
import './scss/main.scss';
