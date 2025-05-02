export const useUserStore = defineStore(
  'User',
  () => {
    const user = ref(null)
    const authToken = useCookie('authT')
    const isAuthenticated = computed(() => !!authToken.value)
    const userFriends = ref(null)

    const fetchUserApi = useApi('/auth/me', {
      method: 'GET',
      watch: false,
      immediate: false
    })

    const { 
      data: friends, 
      execute: refreshFriends 
    } = useApi('/auth/friends/', {
      method: 'GET',
      immediate: true
    })

    const fetchUser = async () => {
      if (!isAuthenticated.value || user.value) return
      try {
        await fetchUserApi.execute()
        if (fetchUserApi.data.value) {
          user.value = fetchUserApi.data.value
        } else {
          throw new Error('Пользователь не найден')
        }
      } catch (e) {
        console.error('Ошибка загрузки пользователя:', e)
        throw e
      }
    }

    const fetchFriends = async () => {
      if (userFriends.value) return
      try {
        await refreshFriends()
        if (friends.value) {
          userFriends.value = friends.value
        }
      } catch (e) {
        console.error('Ошибка загрузки пользователя:', e)
        throw e
      }
    }

    return {
      user,
      isAuthenticated,
      userFriends,
      fetchFriends,
      fetchUser
    }
  },
  {
    persist: true
  }
)