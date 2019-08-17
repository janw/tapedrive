import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import VueResource from 'vue-resource'
import VueSpinners from 'vue-spinners'
var VueCookie = require('vue-cookie2');

Vue.use(BootstrapVue);
Vue.use(VueResource);
Vue.use(VueCookie);
Vue.use(VueSpinners);

Vue.http.options.root = '/api';
Vue.http.interceptors.push(function (request) {
	var token = window.$cookies.get('csrftoken');
	request.headers.set('X-CSRFToken', token);
});

import ApplePodcastsSearch from './components/ApplePodcastsSearch.vue'
import Main from './components/Main.vue'
import router from './router'

new Vue({
	el: '#app',
	router,
	template: '<Main/>',
	components: { Main }
})


import 'typeface-fira-sans-condensed'
import './scss/main.scss'