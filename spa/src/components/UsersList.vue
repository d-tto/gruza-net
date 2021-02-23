<template>
    <b-container fluid id="user-list">
        <table class="table mt-3">
            <tbody v-if="users">
                <tr v-if="!(auth.isAuth && auth.user.public_id == user.public_id)"
                    v-for="user in users" :key="user.public_id">
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td v-if="auth.isAuth">
                        <a href="#" v-if="followed && !followed.includes(user.public_id)"
                           @click.prevent="Follow(user.public_id)">
                            Follow
                        </a>
                        <a href="#" v-if="followed && followed.includes(user.public_id)"
                           @click.prevent="Unfollow(user.public_id)">
                            Unfollow
                        </a>
                    </td>
                </tr>
            </tbody>
        </table>
        <ul class="pagination" v-if="pagination.pages">
            <li v-for="i in pagination.pages" :key="i" class="page-item"
                :class="{active: i == pagination.page}">
                <a href="#" class="page-link" @click.prevent="getList(i)">
                    {{ i }}
                </a>
            </li>
        </ul>
    </b-container >
</template>

<script>
export default {
    name: "UsersList",
    data() {
        return {
            users: null,
            pagination: {
                page: null,
                pages: null
            }
        }
    },
    props: ['auth'],
    computed : {
        followed() {
            let info = this.$store.getters['auth/getProfile'],
                followed = null
            if (info) {
                followed =  info.followed.map(u => u.public_id)
            }
            return followed
        },
    },
    methods: {
        getList(page) {
            this.$api.get(`list/${page}`)
            .then(resp => {
                this.users = resp.data.users
                this.pagination.page = page
                this.pagination.pages = resp.data.pages
            })
            .catch(err => {
                console.log(err.response.data)
            })
        },
        followedInfo() {
            this.$store.dispatch('auth/profile')
        },
        Follow(public_id) {
            this.$api.post(`/follow/${public_id}`, {}, {
                headers: {
                    'x-access-token': `${this.auth.user.token}`,
                }
            })
            .then(resp => {
                this.followedInfo()
            })
            .catch(err => {
                console.log(err.response.data)
            })
        },
        Unfollow(public_id) {
            this.$api.post(`/unfollow/${public_id}`, {}, {
                headers: {
                    'x-access-token': `${this.auth.user.token}`,
                }
            })
            .then(resp => {
                this.followedInfo()
            })
            .catch(err => {
                console.log(err.response.data)
            })
        }
    },
    created() {
        if (!this.users) {
            this.getList(1)
        }
        if (this.auth.isAuth && !this.followed) {
            this.followedInfo()
        }
    }
}
</script>

<style scoped>

</style>