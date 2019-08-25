import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import VueResource from 'vue-resource'
import VueSpinners from 'vue-spinners'
import axios from 'axios';
import createAuthRefreshInterceptor from 'axios-auth-refresh';

const apiRoot = process.env.API_ROOT ? process.env.API_ROOT : null

const api = axios.create({
	baseURL: apiRoot,
	headers: {
		Authorization: {
			toString() {
				return `Bearer ${localStorage.getItem('access')}`
			}
		}
	}
})

// Function to refresh auth token
const refreshAuthLogic = failedRequest => api.post(
	'/api/auth/token/refresh/', { refresh: localStorage.getItem('refresh') })
	.then(resp => {
		localStorage.setItem('access', resp.data.access);
		failedRequest.response.config.headers['Authentication'] = 'Bearer ' + resp.data.token;
		return Promise.resolve();
	});

// Instantiate the interceptor to refresh auth token
createAuthRefreshInterceptor(api, refreshAuthLogic, {
	statusCodes: [401, 403]
});


var VueCookie = require('vue-cookie2');

Vue.use(BootstrapVue);
Vue.use(VueResource);
Vue.use(VueCookie);
Vue.use(VueSpinners);

import Main from './components/Main.vue'
import router from './router'

Vue.use({
	install(Vue) {
		Vue.prototype.$api = api
	}
})

new Vue({
	el: '#app',
	router,
	template: '<Main/>',
	components: { Main }
})


import 'typeface-fira-sans-condensed'
import './scss/main.scss'