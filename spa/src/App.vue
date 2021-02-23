<template>
    <div id="app">
        <auth :auth="auth" v-if="!auth.isAuth"></auth>
        <profile :auth="auth" v-if="auth.isAuth"></profile>
        <users-list :auth="auth"></users-list>
    </div>
</template>

<script>
import UsersList from "./components/UsersList";
import Auth from "./components/Auth";
import Profile from "./components/Profile";

export default {
    components: {Profile, Auth, UsersList},
    computed : {
        auth() { // -> router
            let user = this.$store.getters['auth/getUser'],
                isAuth = this.$store.getters['auth/isAuth']
            return {user, isAuth}
        },
    },
}
</script>