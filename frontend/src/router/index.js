import Vue from 'vue';
import Router from 'vue-router';
import Home from '../components/Home.vue';
import Login from '../components/Login.vue';
import PodcastDetail from '../components/PodcastDetail.vue';
import EpisodeDetail from '../components/EpisodeDetail.vue';
import AddFeeds from '../components/AddFeeds.vue';
import ResetPassword from '../components/ResetPassword.vue';
Vue.use(Router);

const router = new Router({
  routes: [
    {
      path: '/add',
      name: 'Add Feeds',
      component: AddFeeds,
      showOnMenu: true,
    },
    {
      path: '/',
      name: 'Podcasts',
      component: Home,
      showOnMenu: true,
    },
    {
      path: '/podcast/:slug',
      name: 'PodcastDetail',
      component: PodcastDetail,
      props: true,
    },
    {
      path: '/podcast/:slug/:episode',
      name: 'EpisodeDetail',
      component: EpisodeDetail,
      props: true,
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
      allowedLoggedOut: true,
      meta: {
        showBackdrop: true,
        hideHeader: true,
      },
    },
    {
      path: '/reset-password',
      name: 'ResetPassword',
      component: ResetPassword,
      allowedLoggedOut: true,
      meta: {
        showBackdrop: true,
        hideHeader: true,
      },
    },
  ],
});

router.beforeEach((to, from, next) => {
  if (localStorage.getItem('access') == null && typeof to.allowedLoggedOut !== 'undefined' && to.allowedLoggedOut == true) {
    console.log('Redirecting to login');
    next({
      path: '/login',
      params: { redirect: to.fullPath },
    });
  } else {
    next();
  }
});

export default router;
