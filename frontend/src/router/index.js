import Vue from 'vue';
import Router from 'vue-router';
import Home from '../components/Home';
import Login from '../components/Login';
import PodcastDetail from '../components/PodcastDetail';
import EpisodeDetail from '../components/EpisodeDetail';
import AddFeeds from '../components/AddFeeds';

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
      meta: {
        hideHeader: true,
      },
    },
  ],
});

router.beforeEach((to, from, next) => {
  if (localStorage.getItem('access') == null && to.name !== 'Login') {
    console.log('Redirecting to login');
    next({
      path: '/login',
      params: { nextUrl: to.fullPath },
    });
  } else {
    next();
  }
});

export default router;
