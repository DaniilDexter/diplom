import axios from 'axios';

import { BACKEND_URL } from './config';

const instanceApi = axios.create({
    baseURL: BACKEND_URL,
});

export const api = {
    login: ({ email, password }) => instanceApi.post('/auth/login/', { email, password }),
    register: ({ email, username, password }) => instanceApi.post('/auth/register/', { email, username, password }),
    me: ({ token }) => instanceApi.get('/auth/me/', { headers: { Authorization: `Bearer ${token}` } }),
};