import Vue from '../app.js';

function createErrorHandlerInterceptor(api) {
    return api.interceptors.response.use((response) => {
        return response;
    }, function (error) {
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

export default createErrorHandlerInterceptor