import { api } from '@/api';
import { cookie } from '@/cookie';
import { ACCESS_TOKEN } from '@/constants';

export const authModule = {
    namespaced: true,
    state: () => ({
        user: null,
        status: 'init', // init, loading, success, error
        error: null,
    }),
    mutations: {
        setUser: (state, user) => state.user = user,
        setStatus: (state, status) => state.status = status,
        setError: (state, error) => state.error = error,
    },
    actions: {
        login: async ({ commit }, { email, password }) => {
            commit('setStatus', 'loading');
            commit('setError', null);

            try {
                const { data: { access, data } } = await api.login({
                    email,
                    password
                });

                cookie.setCookie(ACCESS_TOKEN, access);

                commit('setStatus', 'success');
                commit('setUser', data);
            } catch (error) {
                if (error instanceof Error) {
                    commit('setStatus', 'error');
                    commit('setError', error.message);
                }
            }
        },
        me: async ({ commit }) => {
            commit('setStatus', 'loading');
            commit('setError', null);

            const token = cookie.getCookie(ACCESS_TOKEN);

            try {
                const { data } = await api.me({ token });

                commit('setStatus', 'success');
                commit('setUser', data);
            } catch (error) {
                if (error instanceof Error) {
                    commit('setStatus', 'error');
                    commit('setError', error.message);
                }
            }
        },
        // logout: async ({ commit }, body) => {
        //     commit('setStatus', 'loading');
        //     commit('setError', null);

        //     const { error } = body || { error: null };
        //     const token = cookie.getCookie(ACCESS_TOKEN);

        //     try {
        //         await api.logout({ token, error });

        //         cookie.deleteCookie(ACCESS_TOKEN);

        //         commit('setStatus', 'init');
        //         commit('setUser', null);
        //     } catch (error) {
        //         if (error instanceof Error) {
        //             commit('setStatus', 'error');
        //             commit('setError', error.message);
        //         }
        //     }
        // },
        // register: async ({ commit }, user) => {
        //     commit('setStatus', 'loading');
        //     commit('setError', null);
        //     try {
        //         await api.register(user);

        //         commit('setStatus', 'success');
        //     } catch (error) {
        //         if (error instanceof Error) {
        //             commit('setStatus', 'error');
        //             commit('setError', error.message);
        //         }
        //     }
        // },
    },
    getters: {
        user: state => state.user,
        status: state => state.status,
        error: state => state.error,
    }
}