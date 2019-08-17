import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home.vue'
import AddFeeds from '@/components/AddFeeds.vue'

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/',
            name: 'Podcasts',
            component: Home
        },
        {
            path: '/add',
            name: 'Add Feeds',
            component: AddFeeds
        }
    ],
    linkActiveClass: "active",
})