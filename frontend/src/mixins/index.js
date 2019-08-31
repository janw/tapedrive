export default {
  install(Vue) {
    Vue.mixin({
      methods: {
        infiniteHandler($state) {
          this.$api
            .get(this.endpoint, {
              params: {
                page: this.page,
              },
            })
            .then((response) => {
              if (response.data.results.length) {
                this.page += 1;
                this.data.push(...response.data.results);
                $state.loaded();
              }
              if (response.data.next == null) {
                $state.complete();
              }
            });
        },
      },
    });
  },
};
