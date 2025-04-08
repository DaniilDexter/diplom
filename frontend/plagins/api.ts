export default defineNuxtPlugin(() => {
  const authT = useCookie('authT')

  const api = $fetch.create({
    baseURL: 'http://127.0.0.1:8000/api/v1/',
    onRequest({ options }) {
      options.headers = options.headers || new Headers()
      options.headers.set('Accept', 'application/json')
      if (authT.value) {
        options.headers.set('Authorization', `Bearer ${authT.value}`)
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        console.error('Unauthorized')
      }
    }
  })

  return {
    provide: {
      api
    }
  }
})