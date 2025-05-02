export const useBreadcrumbs = () => {
  const route = useRoute()
  const breadcrumbs = ref<{title: string, href?: string}[]>([])

  const updateBreadcrumbs = async () => {
    const crumbs = [{title: 'Главная', href: '/'}, {title: 'Проекты', href: '/projects'}]
    const authToken = useCookie('authT').value
    
    if (route.params.id) {
      const project = await $fetch(`/project/${route.params.id}`, {
        baseURL: 'http://127.0.0.1:8000/api/v1/',
        headers: {
          Authorization: authToken ? `Bearer ${authToken}` : '',
          Accept: 'application/json'
        }
      })
      crumbs.push({
        title: project?.name || 'Проект',
        href: `/projects/${route.params.id}/boards`
      })
    }

    if (route.params.boardID) {
      const board = await $fetch(`/boards/${route.params.boardID}`, {
        baseURL: 'http://127.0.0.1:8000/api/v1/',
        headers: {
          Authorization: authToken ? `Bearer ${authToken}` : '',
          Accept: 'application/json'
        }
      })
      crumbs.push({
        title: board?.name || 'Доска'
      })
    }

    breadcrumbs.value = crumbs
  }

  watch(() => route.fullPath, updateBreadcrumbs, {immediate: true})

  return { breadcrumbs }
}