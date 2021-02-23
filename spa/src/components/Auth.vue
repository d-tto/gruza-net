<template>
    <b-navbar type="light" variant="light" id="user-account">
        <b-form inline v-if="mode === 'signIn'" @submit.prevent="signIn">
            <b-form-input class="mb-2 mr-sm-2 mb-sm-0" type="text" placeholder="username" v-model="form.username"/>
            <b-form-input class="mb-2 mr-sm-2 mb-sm-0" type="password" placeholder="password" v-model="form.password"/>
            <b-button class="mb-2 mr-sm-2 mb-sm-0" type="submit">Войти</b-button>
        </b-form>
        <b-form inline v-if="mode === 'signUp'" @submit.prevent="signUp">
            <b-form-input class="mb-2 mr-sm-2 mb-sm-0" type="text" placeholder="username" v-model="form.username"/>
            <b-form-input class="mb-2 mr-sm-2 mb-sm-0" type="text" placeholder="email" v-model="form.email"/>
            <b-form-input class="mb-2 mr-sm-2 mb-sm-0" type="password" placeholder="password" v-model="form.password"/>
            <b-button class="mb-2 mr-sm-2 mb-sm-0" type="submit">Регистрация</b-button>
        </b-form>
        <b-link @click.prevent="mode = isSignInForm ? 'signUp' : 'signIn'">
            {{ isSignInForm ? 'Регистрация' : 'Вход' }}
        </b-link>
    </b-navbar>
</template>

<script>
export default {
    name: "Auth",
    data() {
        return {
            mode: 'signIn',
            form: {
                username: '',
                email: '',
                password: '',
            }
        }
    },
    props: ['auth'],
    computed : {
        isSignInForm() {
            return this.mode === 'signIn'
        }
    },
    methods: {
        signIn() {
            this.$store.dispatch('auth/login', {
                username: this.form.username,
                password: this.form.password,
            })
        },
        signUp() {
            this.$store.dispatch('auth/register', {
                username: this.form.username,
                email: this.form.email,
                password: this.form.password,
            })
        },
    }
}
</script>

<style scoped>

</style>