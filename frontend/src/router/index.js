import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import AddFeeds from '@/components/AddFeeds'

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/add',
            name: 'Add Feeds',
            component: AddFeeds
        },
        {
            path: '/',
            name: 'Podcasts',
            component: Home
        },
    ],
})