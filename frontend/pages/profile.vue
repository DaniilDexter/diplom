<script setup lang="ts">
import { debounce } from '@/utils/debounce'
import { vAutoAnimate } from '@formkit/auto-animate/vue'


const searchQuery = ref('')
const activeTab = ref('search')
const message = ref('')
const messageType = ref<'success' | 'error'>('success')
const selectedUser = ref({
  username: ''
})

const resetMessage = () => {
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

const { 
  data: searchResults, 
  execute: executeSearch 
} = useApi('/auth/search/', {
  method: 'GET',
  query: { username: searchQuery },
  watch: false,
  immediate: false
})

const userStore = useUserStore()

const { userFriends } = storeToRefs(userStore)

await userStore.fetchFriends()

const addFriendApi = useApi('/auth/add_friend/', {
  method: 'POST',
  body: selectedUser,
  watch: false,
  immediate: false
})

const removeFriendApi = useApi('/auth/remove_friend/', {
  method: 'POST',
  body: selectedUser,
  watch: false,
  immediate: false
})

const searchUsers = debounce(() => {
  if (searchQuery.value.trim()) {
    executeSearch()
  }
}, 300)

const addFriend = async (username: string) => {
  try {
    selectedUser.value.username = username
    await addFriendApi.execute()
    
    message.value = `${username} добавлен в друзья`
    messageType.value = 'success'
    resetMessage()
    
    userFriends.value.push(addFriendApi.data.value.friend)
    selectedUser.value.username = ''
    if (searchResults.value) {
      searchResults.value = searchResults.value.filter(u => u.username !== username)
    }
  } catch (error) {
    message.value = error.data?.message || 'Не удалось добавить в друзья'
    messageType.value = 'error'
    resetMessage()
  }
}

const removeFriend = async (username: string) => {
  try {
    selectedUser.value.username = username
    await removeFriendApi.execute()
    
    message.value = `${username} удален из друзей`
    messageType.value = 'success'
    resetMessage()
    
    userFriends.value = (removeFriendApi.data.value.friends)
    selectedUser.value.username = ''
  } catch (error) {
    message.value = error.data?.message || 'Не удалось удалить из друзей'
    messageType.value = 'error'
    resetMessage()
  }
}
</script>

<template>
  <div v-auto-animate class="max-w-md mx-auto p-4 space-y-6">
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
      <TabsList class="grid w-full grid-cols-2">
        <TabsTrigger value="search">
          <Icon name="lucide:search" class="mr-2 size-4" />
          Поиск
        </TabsTrigger>
        <TabsTrigger value="friends">
          <Icon name="lucide:users" class="mr-2 size-4" />
          Друзья ({{ userFriends?.length || 0 }})
        </TabsTrigger>
      </TabsList>
      
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
              @click="addFriend(user.username)"
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
    </Tabs>
  </div>
</template>