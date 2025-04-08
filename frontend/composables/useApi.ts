export function useApi<T>(url: string, options: UseFetchOptions<T> = {}) {
  return useFetch(url, {
    ...options,
    baseURL: 'http://127.0.0.1:8000/api/v1/',
    async onRequest({ options }) {
      const authT = useCookie('authT').value
      options.headers = {
        ...options.headers,
        Accept: 'application/json',
        ...(authT ? { Authorization: `Bearer ${authT}` } : {})
      }
    },
    async onResponseError({ response }) {
      if (response.status === 401) {
        console.error('Unauthorized')
        // Можно добавить редирект на страницу логина
        navigateTo('/login')
      }
    }
  })
}