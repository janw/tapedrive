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
      console.error(error);
      if (error.response.status == 401) {
        Vue.$router.push({ name: 'Login' });
      } else if (error.response.status >= 400) {
        return Promise.reject(error.response);
      }
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
      statusCodes: [403],
    });
    createErrorHandlerInterceptor(api);

    Vue.prototype.$api = api;
  },
};
