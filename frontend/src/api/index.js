import Vue from '../app.js';
import axios from 'axios';
import createAuthRefreshInterceptor from 'axios-auth-refresh';
const apiRoot = process.env.API_ROOT ? process.env.API_ROOT : null;

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';
const api = axios.create({
  baseURL: apiRoot,
  headers: {
    Authorization: {
      toString() {
        return `Bearer ${localStorage.getItem('access')}`;
      },
    },
  },
});

const createErrorHandlerInterceptor = (api) => {
  return api.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      if (error.response.status >= 500) {
        console.log(error);
        const h = Vue.$createElement;
        const vNodesMsg = h('p', { class: ['mb-0'] }, [
          `${error} on`,
          h('br'),
          h('code', {}, [
            error.response.config.method.toUpperCase(),
            ' ',
            error.response.config.url,
          ]),
        ]);
        Vue.$bvToast.toast([vNodesMsg], {
          title: 'Backend Error',
          variant: 'danger',
          autoHideDelay: 5000,
          appendToast: true,
          toaster: 'b-toaster-bottom-right',
          visible: true,
          solid: true,
        });
      }
      return Promise.reject(error.response);
    }
  );
};

const refreshAuthLogic = (failedRequest) =>
  api
    .post('/api/auth/token/refresh/', {
      refresh: localStorage.getItem('refresh'),
    })
    .then((resp) => {
      localStorage.setItem('access', resp.data.access);
      failedRequest.response.config.headers['Authentication'] =
        'Bearer ' + resp.data.token;
      return Promise.resolve();
    });

export default {
  install(Vue) {
    createAuthRefreshInterceptor(api, refreshAuthLogic, {
      statusCodes: [401, 403],
    });
    createErrorHandlerInterceptor(api);

    Vue.prototype.$api = api;
  },
};
