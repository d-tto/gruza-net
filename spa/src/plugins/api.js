import instance from '@/api/instance'

export default {
    install(Vue) {
        Vue.prototype.$api = instance
    }
}