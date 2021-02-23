<template>
    <div id="user-info">
        <b-navbar type="light" variant="light">
            <b-form inline @submit.prevent="userUpdate">
                <b-form-input class="mb-2 mr-sm-2 mb-sm-0" type="text" :placeholder="auth.user.username" v-model="form.username"/>
                <b-form-input class="mb-2 mr-sm-2 mb-sm-0" type="password" placeholder="password" v-model="form.password"/>
                <b-button class="mb-2 mr-sm-2 mb-sm-0" type="submit">Обновить</b-button>
            </b-form>
            <b-button class="mb-2 mr-sm-2 mb-sm-0" variant="danger" @click.prevent="userRemove">Удалить</b-button>
            <div>
                <a href="#" @click.prevent="Logout">Выход</a>
            </div>
        </b-navbar>
        <b-container fluid v-if="info">
            <span>{{ auth.user.username }} followed: </span>
            <span v-for="(fol, key) in info.followed">
                <span>{{fol.username}}</span>
                <span v-if="key+1 != info.followed.length">, </span>
            </span>
        </b-container>
    </div>
</template>

<script>
export default {
    name: "Profile",
    data() {
        return {
            form: {
                username: '',
                password: '',
            }
        }
    },
    props: ['auth'],
    computed : {
        info() {
            return this.$store.getters['auth/getProfile']
        },
    },
    methods: {
        userUpdate() {
            this.$api.put(`/update/${this.auth.user.public_id}`, this.form, {
                headers: {
                    'x-access-token': `${this.auth.user.token}`,
                }
            })
            .then(resp => {
                this.$store.dispatch('auth/refresh', resp.data)
            })
            .catch(err => {
                console.log(err.response.data)
            })
        },
        userRemove() {
            this.$api.delete(`/delete/${this.auth.user.public_id}`, {
                headers: {
                    'x-access-token': `${this.auth.user.token}`,
                }
            })
            .then(resp => {
                this.$store.dispatch('auth/logout')
            })
            .catch(err => {
                console.log(err.response.data)
            })
        },
        userInfo() {
            this.$store.dispatch('auth/profile')
        },
        Logout() {
            this.$store.dispatch('auth/logout')
        }
    },
    mounted() {
        if (!this.info) {
            this.userInfo()
        }
    }
}
</script>

<style scoped>

</style>