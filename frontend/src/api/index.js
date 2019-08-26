import Vue from '../app.js';
import axios from 'axios';
import createAuthRefreshInterceptor from 'axios-auth-refresh';
const apiRoot = process.env.API_ROOT ? process.env.API_ROOT : null;

function createErrorHandlerInterceptor(api) {
    return api.interceptors.response.use((response) => {
        return response;
    }, (error) => {
        // Do something with response error
        if (error.response.status >= 500) {
            console.log(error);
            Vue.$bvToast.toast(`${error} when requesting ${error.response.config.url}.`, {
                title: 'Backend Error',
                autoHideDelay: 5000,
                appendToast: true,
                toaster: "b-toaster-bottom-right",
                visible: true
            })
        }
        return Promise.reject(error.response);
    });
}


const refreshAuthLogic = failedRequest => api.post('/api/auth/token/refresh/', {
    refresh: localStorage.getItem('refresh')
}).then(resp => {
    localStorage.setItem('access', resp.data.access);
    failedRequest.response.config.headers['Authentication'] = 'Bearer ' + resp.data.token;
    return Promise.resolve();
});

export default {
    install(Vue, options) {
        const api = axios.create({
            baseURL: apiRoot,
            headers: {
                Authorization: {
                    toString() {
                        return `Bearer ${localStorage.getItem('access')}`;
                    }
                }
            }
        });

        createAuthRefreshInterceptor(api, refreshAuthLogic, {
            statusCodes: [401, 403]
        });
        createErrorHandlerInterceptor(api);

        Vue.prototype.$api = api
    }
}