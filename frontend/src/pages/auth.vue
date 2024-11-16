<template>
    <main>
        <form @submit.prevent="login">
            <input type="text" v-model="user.email">
            <input type="password" v-model="user.password">
            <button type="submit">login</button>
        </form>
    </main>
</template>

<script>

import { PATHS } from '../constants';

export default {
    name: 'AuthPage',

    data() {
        return {
            user: {
                email: '',
                password: '',
            },
            tryCount: 0,
            isBlocked: false,
            leftTime: 10
        };
    },
    computed: {
        error() {
            return this.$store.getters.error;
        },
    },
    methods: {
        exit() {
            window.location.href = 'https://google.com';
        },
        login() {
            const self = this;

            self.$store.dispatch('auth/login', this.user).then(() => {
                self.$router.push(PATHS.HOME);
            })


        }
    }
}
</script>

<style lang="scss" scoped>

</style>