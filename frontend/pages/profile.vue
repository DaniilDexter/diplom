<script setup lang="ts">
import { debounce } from '@/utils/debounce'
import { vAutoAnimate } from '@formkit/auto-animate/vue'

const searchQuery = ref('')
const activeTab = ref('search')
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

const resetMessage = () => {
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

const userStore = useUserStore()
const { userFriends } = storeToRefs(userStore)
await userStore.fetchFriends()


const { data: searchResults, execute: executeSearch } = useApi('/auth/search/', {
  method: 'GET',
  query: { username: searchQuery },
  watch: false,
  immediate: false
})

const searchUsers = debounce(() => {
  if (searchQuery.value.trim()) {
    executeSearch()
  }
}, 300)

const sendRequestPayload = ref(null)
const sendFriendRequestApi = useApi('/auth/send-friend-request/', {
  method: 'POST',
  body: sendRequestPayload,
  watch: false,
  immediate: false
})

const removeFriendPayload = ref(null)
const removeFriendApi = useApi('/auth/remove-friend/', {
  method: 'POST',
  body: removeFriendPayload,
  watch: false,
  immediate: false
})

const friendRequestsApi = useApi('/auth/friend-requests/', {
  method: 'GET',
  watch: false,
  immediate: true
})

const friendRequest = computed(() => friendRequestsApi.data?.value || [])

const respondRequestPayload = ref(null)
const respondFriendRequestApi = useApi('/auth/respond-friend-request/', {
  method: 'POST',
  body: respondRequestPayload,
  watch: false,
  immediate: false
})

const sendFriendRequest = async (username: string) => {
  sendRequestPayload.value = { username }
  try {
    await sendFriendRequestApi.execute()
    message.value = `Запрос отправлен пользователю ${username}`
    messageType.value = 'success'
    resetMessage()
    if (searchResults.value) {
      searchResults.value = searchResults.value.filter(u => u.username !== username)
    }
  } catch (error) {
    message.value = error.data?.message || 'Ошибка при отправке запроса'
    messageType.value = 'error'
    resetMessage()
  }
}

const removeFriend = async (username: string) => {
  removeFriendPayload.value = { username }
  try {
    await removeFriendApi.execute()
    message.value = `${username} удален из друзей`
    messageType.value = 'success'
    resetMessage()
    userFriends.value = removeFriendApi.data.value.friends
  } catch (error) {
    message.value = error.data?.message || 'Ошибка при удалении'
    messageType.value = 'error'
    resetMessage()
  }
}

const respondToFriendRequest = async (requestId: number, accept: boolean) => {
  respondRequestPayload.value = { request_id: requestId, accept }
  try {
    await respondFriendRequestApi.execute()
    message.value = accept ? 'Запрос принят' : 'Запрос отклонён'
    messageType.value = 'success'
    resetMessage()
    await friendRequestsApi.execute()
    userFriends.value = respondFriendRequestApi.data.value.friends
  } catch (error) {
    message.value = error.data?.message || 'Ошибка обработки запроса'
    messageType.value = 'error'
    resetMessage()
  }
}

const userUpdatePayload = ref(null)
const updateUserApi = useApi('/auth/update-profile/', {
  method: 'PATCH',
  body: userUpdatePayload,
  watch: false,
  immediate: false
})

const selectedPhoto = ref<File | null>(null)
const selectedRoleId = ref(userStore.user.role?.id || null)

// Получить список ролей
const rolesApi = useApi('/role/', {
  method: 'GET',
  watch: false,
  immediate: true
})

const roles = computed(() => rolesApi.data?.value || []);

const availabelRoles = roles.value.slice(1)


const updateUser = async () => {
  const formData = new FormData()
  if (selectedPhoto.value) {
    formData.append('photo', selectedPhoto.value)
  }
  if (selectedRoleId.value) {
    formData.append('role', selectedRoleId.value.toString())
  }

  userUpdatePayload.value = formData

  try {
    await updateUserApi.execute()
    if (updateUserApi.data.value.id) {
      userStore.user = updateUserApi.data.value
    }
    message.value = 'Профиль обновлён'
    messageType.value = 'success'
    resetMessage()
  } catch (error) {
    message.value = error.data?.message || 'Ошибка при обновлении профиля'
    messageType.value = 'error'
    resetMessage()
  }
}

const onFileChange = (e: Event) => {
  const files = (e.target as HTMLInputElement).files
  if (files && files.length > 0) {
    selectedPhoto.value = files[0]
  }
}


</script>


<template>
  <div v-auto-animate class="max-w-3xl mx-auto p-4 space-y-6">
    <h1 class="text-2xl font-bold">Мои друзья</h1>

    <div 
      v-if="message"
      :class="{
        'bg-green-100 text-green-800': messageType === 'success',
        'bg-red-100 text-red-800': messageType === 'error'
      }"
      class="p-3 rounded-md"
    >
      {{ message }}
    </div>
    
    <Tabs v-model="activeTab">
      <TabsList class="grid w-full grid-cols-4">
        <TabsTrigger value="search">
          <Icon name="lucide:search" mode="svg" class="mr-2 size-4" />
          Поиск
        </TabsTrigger>
        <TabsTrigger value="friends">
          <Icon name="lucide:book-user" mode="svg" class="mr-2 size-4" />
          Друзья ({{ userFriends?.length || 0 }})
        </TabsTrigger>
        <TabsTrigger value="requests">
          <Icon name="lucide:inbox" mode="svg" class="mr-2 size-4" />
          Запросы ({{ friendRequest?.length || 0 }})
        </TabsTrigger>
        <TabsTrigger value="profile">
          <Icon name="lucide:user" mode="svg" class="mr-2 size-4" />
          Профиль
        </TabsTrigger>
      </TabsList>

      <TabsContent value="profile" class="space-y-4">
        <div class="space-y-4">
          <div class="flex items-center gap-4">
            <Avatar class="w-16 h-16">
              <AvatarImage v-if="userStore.user.photo" :src="userStore.user.photo" />
              <AvatarFallback>{{ userStore.user.username.charAt(0).toUpperCase() }}</AvatarFallback>
            </Avatar>
            <div>
              <p class="text-lg font-bold">{{ userStore.user.username }}</p>
              <p class="text-sm text-muted-foreground">{{ userStore.user.email }}</p>
            </div>
          </div>

          <div class="space-y-2">
            <label class="block text-sm font-medium">Фото</label>
            <Input type="file" @change="onFileChange" />
          </div>


          <div class="space-y-2">
            <label class="block text-sm font-medium">Роль</label>
            <Select v-model="selectedRoleId">
              <SelectTrigger class="w-full">
                <SelectValue placeholder="Выберите роль" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="role in availabelRoles"
                  :key="role.id"
                  :value="role.id"
                >
                  {{ role.name }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button @click="updateUser">
            Сохранить изменения
          </Button>
        </div>
      </TabsContent>
      
      <TabsContent value="search" class="space-y-4">
        <div class="relative">
          <Input
            v-model="searchQuery"
            placeholder="Поиск по username..."
            class="pl-10"
            @input="searchUsers"
          />
          <Icon
            name="lucide:search"
            class="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground"
          />
        </div>
        
        <div v-if="searchResults" class="space-y-2">
          <div
            v-for="user in searchResults"
            :key="user.id"
            class="flex items-center justify-between p-3 border rounded-lg"
          >
            <div class="flex items-center gap-3">
              <Avatar>
                <AvatarImage :src="user.photo || ''" />
                <AvatarFallback>
                  {{ user.username.charAt(0).toUpperCase() }}
                </AvatarFallback>
              </Avatar>
              <div>
                <p class="font-medium">{{ user.username }}</p>
                <p class="text-sm text-muted-foreground">{{ user.email }}</p>
              </div>
            </div>
            <Button
              size="sm"
              @click="sendFriendRequest(user.username)"
            >
              <Icon name="lucide:user-plus" class="mr-2 size-4" />
              Добавить
            </Button>
          </div>
        </div>
      </TabsContent>
      
      <TabsContent value="friends" class="space-y-4">
        <div v-if="userFriends?.length" class="space-y-2">
          <div
            v-for="friend in userFriends"
            :key="friend.id"
            class="flex items-center justify-between p-3 border rounded-lg"
          >
            <div class="flex items-center gap-3">
              <Avatar>
                <AvatarImage :src="friend.photo || ''" />
                <AvatarFallback>
                  {{ friend.username.charAt(0).toUpperCase() }}
                </AvatarFallback>
              </Avatar>
              <div>
                <p class="font-medium">{{ friend.username }}</p>
                <p class="text-sm text-muted-foreground">{{ friend.email }}</p>
              </div>
            </div>
            <Button
              variant="destructive"
              size="sm"
              @click="removeFriend(friend.username)"
            >
              <Icon name="lucide:user-x" class="mr-2 size-4" />
              Удалить
            </Button>
          </div>
        </div>
        <div v-else class="text-center py-8 text-muted-foreground">
          <Icon name="lucide:users" class="mx-auto size-8" />
          <p class="mt-2">Список друзей пуст</p>
          <p class="text-sm">Найдите друзей через поиск</p>
        </div>
      </TabsContent>

      <TabsContent value="requests" class="space-y-4">
        <div v-if="friendRequest.length" class="space-y-2">
          <div
            v-for="req in friendRequest"
            :key="req.id"
            class="flex items-center justify-between p-3 border rounded-lg"
          >
            <div>
              <p class="font-medium">{{ req.sender.username }}</p>
              <p class="text-sm text-muted-foreground">{{ req.sender.email }}</p>
            </div>
            <div class="flex gap-2">
              <Button size="sm" @click="respondToFriendRequest(req.id, true)">
                Принять
              </Button>
              <Button size="sm" variant="destructive" @click="respondToFriendRequest(req.id, false)">
                Отклонить
              </Button>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-muted-foreground">
          <Icon name="lucide:inbox" class="mx-auto size-8" />
          <p class="mt-2">Нет входящих запросов</p>
        </div>
      </TabsContent>
    </Tabs>
  </div>
</template>