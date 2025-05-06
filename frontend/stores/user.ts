export const useUserStore = defineStore(
  'User',
  () => {
    const user = ref(null)
    const authToken = useCookie('authT')
    const isAuthenticated = computed(() => !!authToken.value)
    const userFriends = ref(null)
    const projectsStore = useProjectStore()

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

    watch(user, (newUser) => {
      if (newUser) {
        userFriends.value = null
        fetchFriends()
      } else {
        userFriends.value = null
      }
    }, { immediate: true })

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

    const currentProjectRole = computed(() => {
      if (!user.value || !projectsStore.currentProject) return null
      
      const currentUserMember = projectsStore.currentProject.members.find(
        member => member.user.id === user.value.id
      )
      
      return currentUserMember ? currentUserMember.role.id : null
    })


    return {
      user,
      isAuthenticated,
      userFriends,
      currentProjectRole,
      fetchFriends,
      fetchUser
    }
  },
  {
    persist: true
  }
)