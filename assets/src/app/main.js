import Vue from 'vue'
import VueResource from 'vue-resource'
Vue.use(VueResource);
var VueCookie = require('vue-cookie');
Vue.use(VueCookie);

Vue.http.options.root = '/api';
Vue.http.interceptors.push(function (request){
  	var token = this.$cookie.get('csrftoken');
    request.headers.set('X-CSRFToken', token);
});


Vue.component('spinner', require('vue-spinner-component/src/Spinner.vue'));
import ApplePodcastsSearch from './components/ApplePodcastsSearch.vue'

import BootstrapVue from 'bootstrap-vue'
Vue.use(BootstrapVue);

new Vue({
	el: '.app',
	components: {
		ApplePodcastsSearch,
	},
   	loading: false,
	methods: {
	}
})

// import 'bootstrap/dist/css/bootstrap.css'
// import 'bootstrap-vue/dist/bootstrap-vue.css'
