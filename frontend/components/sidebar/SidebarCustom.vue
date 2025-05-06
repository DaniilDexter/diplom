<script setup lang="ts">
import { type SidebarProps, useSidebar } from '@/components/ui/sidebar'
import { SIDEBAR_COOKIE_NAME } from '@/components/ui/sidebar/utils'
import { watch } from 'vue'
import { useRoute } from 'vue-router'

const sidebarState = useCookie<boolean>(SIDEBAR_COOKIE_NAME)

const props = withDefaults(defineProps<SidebarProps>(), {
  collapsible: 'icon'
})

const { open } = useSidebar()

const authToken = useCookie('authT')

if (!authToken.value) {
  navigateTo('/')
}

const delayOpen = ref<boolean>(open.value)

watch(open, (newValue) => {
  if (newValue) {
    setTimeout(() => {
      delayOpen.value = newValue
    }, 100)
  } else {
    delayOpen.value = newValue
  }
})

const route = useRoute()
const projectStore = useProjectStore()
await projectStore.fetchProjects()

const newBoardName = ref('')
const newBoardPayload = ref(null)
const boardAddApi = useApi('/boards/', {
  method: 'POST',
  body: newBoardPayload,
  watch: false,
  immediate: false
});

const { currentProject, isLoading } = storeToRefs(projectStore)
const isAddingBoard = ref(false)

const createBoard = async () => {
  newBoardPayload.value = {
    project_id: route.params.id,
    name: newBoardName.value
  }

  try {
    await boardAddApi.execute()
    if (boardAddApi.data.value) {
      currentProject.value.boards.push(boardAddApi.data.value)
    }
    newBoardName.value = '';
  } catch (error) {
    console.error('Ошибка создания доски:', error);
  }
};

const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') createBoard()
  if (e.key === 'Escape') isAddingBoard.value = false
}

const members = computed(() => currentProject.value?.members || []);

const tags = computed(() => currentProject.value?.tags || []);
const priorities = computed(() => currentProject.value?.priorities || []);

const isMembersDialogOpen = ref(false)
const isPrioritiesDialogOpen = ref(false)

const isTagsDialogOpen = ref(false)

const newTagName = ref('');
const newTagPayload = ref(null);

const tagAddApi = useApi('/tag/', {
  method: 'POST',
  body: newTagPayload,
  watch: false,
  immediate: false
});

const createTag = async () => {
  newTagPayload.value = {
    project: route.params.id,
    name: newTagName.value
  };

  try {
    await tagAddApi.execute();
    if (tagAddApi.data.value) {
      tags.value.push(tagAddApi.data.value);
    }
    newTagName.value = '';
  } catch (error) {
    console.error('Ошибка создания тега:', error);
  }
};

const selectedTagId = ref(null);


const tagDeleteApiUrl = computed(() => 
  selectedTagId.value ? `/tag/${selectedTagId.value}/` : null
)

const tagDeleteApi = useApi(tagDeleteApiUrl, {
  method: 'DELETE',
  watch: false,
  immediate: false
});

const deleteTag = async (tagId) => {
  selectedTagId.value = tagId;
  
  try {
    tagDeleteApi.execute();
    currentProject.value.tags = tags.value.filter(tag => tag.id !== tagId);
  } catch (error) {
    console.error('Ошибка удаления тега:', error);
  } finally {
    selectedTagId.value = null;
  }
};

const currentlyEditingTag = ref(null)
const selectedColor = ref('#ffffff')

const tagUpdateApiUrl = computed(() => 
  currentlyEditingTag.value ? `/tag/${currentlyEditingTag.value.id}/` : null
)

const tagUpdateApi = useApi(tagUpdateApiUrl, {
  method: 'PATCH',
  body: computed(() => ({ color: selectedColor.value })),
  watch: false,
  immediate: false
})

const openColorPicker = (tag) => {
  currentlyEditingTag.value = tag
  selectedColor.value = tag.color || '#3b82f6'
}

const updateTagColor = async () => {
  try {
    await tagUpdateApi.execute()
    if (tagUpdateApi.data.value) {
      const index = tags.value.findIndex(t => t.id === currentlyEditingTag.value.id)
      if (index !== -1) {
        tags.value[index] = { ...tags.value[index], color: selectedColor.value }
      }
    }
  } catch (error) {
    console.error('Ошибка обновления цвета тега:', error)
  }
}

const newPriorityName = ref('');
const newPriorityPayload = ref(null);

const priorityAddApi = useApi('/priority/', {
  method: 'POST',
  body: newPriorityPayload,
  watch: false,
  immediate: false
});

const createPriority = async () => {
  newPriorityPayload.value = {
    project: route.params.id,
    name: newPriorityName.value
  };

  try {
    await priorityAddApi.execute();
    if (priorityAddApi.data.value) {
      priorities.value.push(priorityAddApi.data.value);
    }
    newPriorityName.value = '';
  } catch (error) {
    console.error('Ошибка создания приоритета:', error);
  }
};

const selectedPriorityId = ref(null);

const priorityDeleteApiUrl = computed(() => 
  selectedPriorityId.value ? `/priority/${selectedPriorityId.value}/` : null
);

const priorityDeleteApi = useApi(priorityDeleteApiUrl, {
  method: 'DELETE',
  watch: false,
  immediate: false
});

const deletePriority = async (priorityId) => {
  selectedPriorityId.value = priorityId;
  
  try {
    await priorityDeleteApi.execute();
    currentProject.value.priorities = priorities.value.filter(priority => priority.id !== priorityId);
  } catch (error) {
    console.error('Ошибка удаления приоритета:', error);
  } finally {
    selectedPriorityId.value = null;
  }
};

const currentlyEditingPriority = ref(null);
const selectedPriorityColor = ref('#ffffff');

const priorityUpdateApiUrl = computed(() => 
  currentlyEditingPriority.value ? `/priority/${currentlyEditingPriority.value.id}/` : null
);

const priorityUpdateApi = useApi(priorityUpdateApiUrl, {
  method: 'PATCH',
  body: computed(() => ({ color: selectedPriorityColor.value })),
  watch: false,
  immediate: false
});

const openPriorityColorPicker = (priority) => {
  currentlyEditingPriority.value = priority;
  selectedPriorityColor.value = priority.color || '#3b82f6';
};

const updatePriorityColor = async () => {
  try {
    await priorityUpdateApi.execute();
    if (priorityUpdateApi.data.value) {
      const index = priorities.value.findIndex(p => p.id === currentlyEditingPriority.value.id);
      if (index !== -1) {
        priorities.value[index] = { ...priorities.value[index], color: selectedPriorityColor.value };
      }
    }
  } catch (error) {
    console.error('Ошибка обновления цвета приоритета:', error);
  }
};

const selectedUsers = ref([]);
const userStore = useUserStore();

// Загружаем друзей при открытии диалога
watch(isMembersDialogOpen, async (isOpen) => {
  if (isOpen) {
    await userStore.fetchFriends();
    selectedUsers.value = [];
  }
});

const { userFriends } = storeToRefs(userStore);

// API для обновления участников проекта
const updateMembersApi = useApi(
  computed(() => `/project/${route.params.id}/update-members/`),
  {
    method: 'POST',
    body: computed(() => ({
      members: [
        ...currentProject.value.members.map(m => m.user.id),
        ...selectedUsers.value.map(u => u.id)
      ]
    })),
    watch: false,
    immediate: false
  }
);

// Добавление участников
const addMembers = async () => {
  try {
    await updateMembersApi.execute();
    if (updateMembersApi.data.value) {
      // Обновляем локальное состояние
      currentProject.value.members = updateMembersApi.data.value.members;
      selectedUsers.value = [];
    }
  } catch (error) {
    console.error('Ошибка добавления участников:', error);
  }
};

const removeMemberPayload = ref<{ user_id: number } | null>(null);

const removeMemberApi = useApi(`/project/${route.params.id}/remove-member/`, {
  method: "POST",
  body: removeMemberPayload,
  watch: false,
  immediate: false
});

const removeMember = async (memberId: number) => {
  
  try {
    removeMemberPayload.value = { user_id: memberId };
    await removeMemberApi.execute();
    
    if (removeMemberApi.data.value) {
      currentProject.value.members = removeMemberApi.data.value.members;
    }
  } catch (error) {
    console.error("Ошибка при удалении участника:", error);
  } finally {
    removeMemberPayload.value = null;
  }
};

const availableFriends = computed(() => {
  return userFriends.value.filter(friend => 
    !currentProject.value?.members.some(member => member.user.id === friend.id)
  )
})

// Проверяем, есть ли доступные друзья для добавления
const hasAvailableFriends = computed(() => availableFriends.value.length > 0)

const availableIcons = [
  'fxemoji:briefcase',
  'fxemoji:calendar',
  'fxemoji:clipboard',
  'fxemoji:whiteheavycheckmark',
  'fxemoji:satelliteantenna',
  'fxemoji:barchart',
  'fxemoji:oncomingautomobile',
  'fxemoji:rocket',
  'fxemoji:pushpin',
  'fxemoji:leftmagnifyingglass',
  'fxemoji:hourglass',
  'fxemoji:envelope',
  'fxemoji:paperclip',
  'fxemoji:triangularflagonpost',
  'fxemoji:bookmark',
  'fxemoji:spiralnotepad',
  'fxemoji:lowerleftfountainpen',
  'fxemoji:pencil',
  'fxemoji:lightbulb',
  'fxemoji:stockchart',
  'fxemoji:folder',
  'fxemoji:openfolder',
  'fxemoji:document',
  'fxemoji:personalcomputer',
  'fxemoji:cellphone',
  'fxemoji:clock3oclock',
  'fxemoji:hammer',
  'fxemoji:graduationcap',
  'fxemoji:noentry',
  'fxemoji:squaredsos'
];



const selectedIcon = ref('')
const selectedBoard = ref(null) // доска, которую редактируем
const isIconDialogOpen = ref(false)

const iconUpdatePayload = ref({
  icon: '',
  name: '' 
})
const iconUpdateApiUrl = computed(() => selectedBoard.value ? `/boards/${selectedBoard.value.id}/` : null)
const iconUpdateApi = useApi(iconUpdateApiUrl, {
  method: 'PATCH',
  body: iconUpdatePayload,
  watch: false,
  immediate: false
})

const updateBoardIcon = async () => {
  if (!selectedBoard.value) return;
  iconUpdatePayload.value = { 
    icon: selectedIcon.value,
    name: iconUpdatePayload.value.name // Включаем название в payload
  }

  try {
    await iconUpdateApi.execute()
    const updatedBoard = iconUpdateApi.data.value
    if (updatedBoard) {
      const index = currentProject.value.boards.findIndex(b => b.id === updatedBoard.id)
      if (index !== -1) {
        currentProject.value.boards[index].icon = updatedBoard.icon
        currentProject.value.boards[index].name = updatedBoard.name
      }
      isIconDialogOpen.value = false
    }
  } catch (error) {
    console.error('Ошибка обновления иконки:', error)
  }
}

const openIconDialog = (board) => {
  selectedBoard.value = board
  selectedIcon.value = board.icon
  iconUpdatePayload.value.name = board.name
  isIconDialogOpen.value = true
}

// Payloads для API
const promotePayload = ref<{ user_id: number } | null>(null);
const demotePayload = ref<{ user_id: number } | null>(null);

// API для назначения руководителем
const promoteApi = useApi(`/project/${route.params.id}/promote-to-leader/`, {
  method: "POST",
  body: promotePayload,
  watch: false,
  immediate: false
});

// API для понижения до участника
const demoteApi = useApi(`/project/${route.params.id}/demote-to-member/`, {
  method: "POST",
  body: demotePayload,
  watch: false,
  immediate: false
});

const promoteToLeader = async (userId: number) => {
  try {
    promotePayload.value = { user_id: userId };
    await promoteApi.execute();
    
    if (promoteApi.data.value) {
      currentProject.value.members = promoteApi.data.value.members;
    }
  } catch (error) {
    console.error("Ошибка при назначении руководителя:", error);
  } finally {
    promotePayload.value = null;
  }
};

const demoteToMember = async (userId: number) => {
  try {
    demotePayload.value = { user_id: userId };
    await demoteApi.execute();
    
    if (demoteApi.data.value) {
      currentProject.value.members = demoteApi.data.value.members;
    }
  } catch (error) {
    console.error("Ошибка при понижении участника:", error);
  } finally {
    demotePayload.value = null;
  }
};

</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <NuxtLink :to="`/projects/${route.params.id}/boards`" class="logo-link">
              <img v-if="delayOpen" class="h-8 w-[78px]" src="/logo.svg" alt="Logo icon" />
              <img v-else class="size-8" src="/logo.svg" alt="Logo icon" />
              <p>Zadachnick +</p>
            </NuxtLink>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel class="font-medium">Доски проекта</SidebarGroupLabel>
        <SidebarGroupContent>
          <div v-if="isLoading">Загрузка...</div>
          <SidebarMenu v-else-if="currentProject">
            <SidebarMenuItem v-for="board in currentProject.boards" :key="board.id">
              <SidebarMenuButton as-child>
                <NuxtLink 
                  :to="`/projects/${route.params.id}/boards/${board.id}`"
                  class="flex items-center gap-2"
                >
                  <Icon :name="board.icon" mode="svg" class="size-4" />
                  <span class="truncate">{{ board.name }}</span>
                </NuxtLink>
              </SidebarMenuButton>
              <SidebarMenuAction v-if="!board.is_sprint && userStore.currentProjectRole === 1" @click="openIconDialog(board)">
                <Icon name="lucide:settings" class="size-4" />
              </SidebarMenuAction>

            </SidebarMenuItem>

            <template v-if="sidebarState">
              <SidebarMenuItem v-if="isAddingBoard">
                <div class="px-3 py-1.5 w-full">
                  <Input
                    v-model="newBoardName"
                    placeholder="Название доски"
                    class="w-full"
                    autofocus
                    @keydown="handleKeyDown"
                  />
                  <p class="text-xs text-muted-foreground mt-1">
                    Нажмите Enter для создания
                  </p>
                </div>
              </SidebarMenuItem>

              <SidebarMenuItem v-else>
                <SidebarMenuButton 
                  class="text-green-600 hover:bg-green-50"
                  @click="isAddingBoard = true"
                >
                  <Icon name="lucide:plus" class="mr-2 size-4" />
                  Добавить доску
                </SidebarMenuButton>
              </SidebarMenuItem>
            </template>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
      
      <template v-if="sidebarState">
        <!-- Участники проекта с выпадающим меню -->
        <SidebarMenu>
          <Collapsible>
            <SidebarMenuItem>
              <CollapsibleTrigger asChild>
                <SidebarMenuButton>
                  <Icon name="lucide:users" class="mr-2 size-4" />
                  <span>Участники проекта</span>
                </SidebarMenuButton>
              </CollapsibleTrigger>
              <SidebarMenuAction v-if="userStore.currentProjectRole === 1" @click="isMembersDialogOpen = true">
                <Icon name="lucide:settings" class="size-4" />
              </SidebarMenuAction>
              <CollapsibleContent>
                <SidebarMenuSub>
                  <SidebarMenuSubItem v-for="member in members" :key="member.id">
                    <div class="flex items-center gap-2">
                      <Icon name="lucide:user" mode="svg" class="size-4" />
                      <span class="truncate">{{ member.user.username }}</span>
                      <Badge variant="outline" class="max-w-24">
                        <p class="truncate">{{ member.role.name }}</p>
                      </Badge>
                    </div>
                  </SidebarMenuSubItem>
                </SidebarMenuSub>
              </CollapsibleContent>
            </SidebarMenuItem>
          </Collapsible>
        </SidebarMenu>

        <!-- Теги проекта с выпадающим меню -->
        <SidebarMenu>
          <Collapsible>
            <SidebarMenuItem>
              <CollapsibleTrigger asChild>
                <SidebarMenuButton>
                  <Icon name="lucide:tags" class="mr-2 size-4" />
                  <span>Теги проекта</span>
                </SidebarMenuButton>
              </CollapsibleTrigger>
              <SidebarMenuAction v-if="userStore.currentProjectRole === 1" @click="isTagsDialogOpen = true">
                <Icon name="lucide:settings" class="size-4" />
              </SidebarMenuAction>
              <CollapsibleContent>
                <SidebarMenuSub>
                  <template v-if="tags.length">
                    <SidebarMenuSubItem v-for="tag in tags" :key="tag.id">
                      <div class="flex items-center gap-2">
                        <Icon name="lucide:tag" mode="svg" class="size-4" :style="{ color: tag.color }"/>
                        <span class="truncate">{{ tag.name }}</span>
                      </div>
                    </SidebarMenuSubItem>
                  </template>
                  <SidebarMenuSubItem v-else>
                      <div class="flex items-center gap-2">
                        <span class="truncate text-sm">Тегов не найдено</span>
                      </div>
                    </SidebarMenuSubItem>
                </SidebarMenuSub>
              </CollapsibleContent>
            </SidebarMenuItem>
          </Collapsible>
        </SidebarMenu>

        <!-- Приоритеты проекта с выпадающим меню -->
        <SidebarMenu>
          <Collapsible>
            <SidebarMenuItem>
              <CollapsibleTrigger asChild>
                <SidebarMenuButton>
                  <Icon name="lucide:flag" class="mr-2 size-4" />
                  <span>Приоритеты проекта</span>
                </SidebarMenuButton>
              </CollapsibleTrigger>
              <SidebarMenuAction v-if="userStore.currentProjectRole === 1" @click="isPrioritiesDialogOpen = true">
                <Icon name="lucide:settings" class="size-4" />
              </SidebarMenuAction>
              <CollapsibleContent>
                <SidebarMenuSub>
                  <template v-if="priorities.length">
                    <SidebarMenuSubItem v-for="priority in priorities" :key="priority.id">
                      <div class="flex items-center gap-2">
                        <Icon name="lucide:flag" mode="svg" class="size-4" :style="{ color: priority.color }"/>
                        <span class="truncate">{{ priority.name }}</span>
                      </div>
                    </SidebarMenuSubItem>                   
                  </template>
                  <SidebarMenuSubItem v-else>
                      <div class="flex items-center gap-2">
                        <span class="truncate text-sm">Приоритетов не найдено</span>
                      </div>
                    </SidebarMenuSubItem>
                </SidebarMenuSub>
              </CollapsibleContent>
            </SidebarMenuItem>
          </Collapsible>
        </SidebarMenu>
      </template>
    </SidebarContent>
    <SidebarRail />

    <!-- Диалог управления участниками -->
    <Dialog v-model:open="isMembersDialogOpen">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle>Управление участниками</DialogTitle>
          <DialogDescription>
            Добавляйте и удаляйте участников проекта
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div class="space-y-2 max-h-60 overflow-y-auto">
            <div v-for="member in currentProject.members" :key="member.user.id" class="flex items-center justify-between p-2 hover:bg-muted/50 rounded">
              <div class="flex items-center gap-2">
                <Avatar class="h-8 w-8">
                  <AvatarFallback>{{ member.user.username.charAt(0) }}</AvatarFallback>
                </Avatar>
                <div>
                  <div class="flex items-center gap-2">
                    <p class="text-sm font-medium">{{ member.user.username }}</p>
                    <Badge variant="outline">{{ member.role.name }}</Badge>
                  </div>
                  <p class="text-xs text-muted-foreground">{{ member.user.email }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <!-- Кнопка назначения руководителем -->
                <Button 
                  v-if="member.user.id !== userStore.user.id && member.user.id !== currentProject.owner && userStore.currentProjectRole === 1 && member.role.id !== 1"
                  variant="ghost" 
                  size="sm"
                  @click="promoteToLeader(member.user.id)"
                >
                  <Icon name="lucide:crown" class="size-4 text-yellow-500" />
                </Button>
                
                <!-- Кнопка понижения до участника -->
                <Button 
                  v-if="member.user.id !== userStore.user.id && member.user.id !== currentProject.owner && userStore.currentProjectRole === 1 && member.role.id === 1"
                  variant="ghost" 
                  size="sm"
                  @click="demoteToMember(member.user.id)"
                >
                  <Icon name="lucide:user" class="size-4 text-blue-500" />
                </Button>
                
                <!-- Кнопка удаления -->
                <Button 
                  v-if="member.user.id !== userStore.user.id && member.user.id !== currentProject.owner && userStore.currentProjectRole === 1"
                  variant="ghost" 
                  size="sm"
                  @click="removeMember(member.user.id)"
                >
                  <Icon name="lucide:trash-2" class="size-4 text-destructive" />
                </Button>
              </div>
            </div>
          </div>
          
          <!-- Форма добавления новых участников -->
          <div class="space-y-2" v-if="hasAvailableFriends">
            <Select v-model="selectedUsers" :multiple="true">
              <SelectTrigger class="w-full justify-between">
                <span v-if="selectedUsers.length > 0">
                  {{ selectedUsers.map(user => user.username).join(', ') }}
                </span>
                <span v-else>Добавьте участников</span>
              </SelectTrigger>

              <SelectContent class="w-full">
                <SelectGroup>
                  <SelectLabel>Друзья</SelectLabel>

                  <SelectItem
                    v-for="friend in availableFriends"
                    :key="friend.id"
                    :value="friend"
                  >
                    <div class="flex items-center justify-between w-full">
                      <div class="flex items-center space-x-2">
                        <Icon name="lucide:user" class="size-4" />
                        <span>{{ friend.username }}</span>
                      </div>
                      <Badge variant="outline">{{ friend.role.name }}</Badge>
                    </div>
                  </SelectItem>
                </SelectGroup>

                <div v-if="availableFriends.length === 0" class="px-4 py-2 text-sm text-muted-foreground">
                  Не найдено участников.
                </div>
              </SelectContent>
            </Select>


            <Button 
              variant="outline" 
              @click="addMembers"
              :disabled="selectedUsers.length === 0"
              class="w-full"
            >
              Добавить выбранных участников
            </Button>
          </div>

          <!-- Сообщение, если все друзья уже добавлены -->
          <div v-else class="text-center py-4 text-muted-foreground">
            Все ваши друзья уже являются участниками проекта
          </div>
        </div>
        
        <DialogFooter>
          <DialogClose as-child>
            <Button variant="outline">
              Закрыть
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Диалог управления тегами -->
    <Dialog v-model:open="isTagsDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Управление тегами</DialogTitle>
          <DialogDescription>
            Создавайте и удаляйте теги для задач проекта
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div v-for="tag in tags" :key="tag.id" class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Icon name="lucide:tag" class="size-4" :style="{ color: tag.color }" />
              <span>{{ tag.name }}</span>
            </div>
            <div class="flex gap-2">
              <Popover>
                <PopoverTrigger as-child>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    @click="openColorPicker(tag)"
                  >
                    <Icon name="lucide:pipette" class="size-4" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent class="w-auto p-4">
                  <div class="grid gap-4">
                    <div class="space-y-2">
                      <h4 class="font-medium leading-none">Цвет тега</h4>
                      <p class="text-sm text-muted-foreground">
                        Выберите цвет для "{{ currentlyEditingTag?.name }}"
                      </p>
                    </div>
                    <div class="flex flex-col gap-3">
                      <div class="flex items-center gap-2">
                        <div 
                          class="w-6 h-6 rounded-full border" 
                          :style="{ backgroundColor: selectedColor }"
                        ></div>
                        <span class="text-sm">{{ selectedColor }}</span>
                      </div>
                      <input 
                        type="color" 
                        v-model="selectedColor" 
                        class="w-full h-10 cursor-pointer"
                      >
                      <Button 
                        size="sm" 
                        @click="updateTagColor"
                        :disabled="tagUpdateApi.isPending"
                      >
                        Сохранить
                      </Button>
                    </div>
                  </div>
                </PopoverContent>
              </Popover>
              <Button 
                variant="destructive" 
                size="sm"
                @click="deleteTag(tag.id)"
                :disabled="tagDeleteApi.isPending"
              >
                <Icon name="lucide:trash-2" class="size-4" />
              </Button>
            </div>
          </div>
          
          <!-- Форма добавления нового тега -->
          <div class="flex gap-2">
            <Input 
              v-model="newTagName" 
              placeholder="Название нового тега" 
              @keyup.enter="createTag"
            />
            <Button variant="outline" @click="createTag">
              Добавить
            </Button>
          </div>
        </div>
        
        <DialogFooter>
          <DialogClose>
            <Button>
              Закрыть
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="isPrioritiesDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Управление приоритетами</DialogTitle>
          <DialogDescription>
            Настройте приоритеты для задач проекта
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div v-for="priority in priorities" :key="priority.id" class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Icon 
                name="lucide:signal" 
                class="size-4" 
                :style="{ color: priority.color }" 
              />
              <span>{{ priority.name }}</span>
            </div>
            <div class="flex gap-2">
              <Popover>
                <PopoverTrigger as-child>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    @click="openPriorityColorPicker(priority)"
                  >
                    <Icon name="lucide:pipette" class="size-4" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent class="w-auto p-4">
                  <div class="grid gap-4">
                    <div class="space-y-2">
                      <h4 class="font-medium leading-none">Цвет приоритета</h4>
                      <p class="text-sm text-muted-foreground">
                        Выберите цвет для "{{ currentlyEditingPriority?.name }}"
                      </p>
                    </div>
                    <div class="flex flex-col gap-3">
                      <div class="flex items-center gap-2">
                        <div 
                          class="w-6 h-6 rounded-full border" 
                          :style="{ backgroundColor: selectedPriorityColor }"
                        ></div>
                        <span class="text-sm">{{ selectedPriorityColor }}</span>
                      </div>
                      <input 
                        type="color" 
                        v-model="selectedPriorityColor" 
                        class="w-full h-10 cursor-pointer"
                      >
                      <Button 
                        size="sm" 
                        @click="updatePriorityColor"
                        :disabled="priorityUpdateApi.isPending"
                      >
                        Сохранить
                      </Button>
                    </div>
                  </div>
                </PopoverContent>
              </Popover>
              <Button 
                variant="destructive" 
                size="sm"
                @click="deletePriority(priority.id)"
                :disabled="priorityDeleteApi.isPending"
              >
                <Icon name="lucide:trash-2" class="size-4" />
              </Button>
            </div>
          </div>
          
          <!-- Форма добавления нового приоритета -->
          <div class="flex gap-2">
            <Input 
              v-model="newPriorityName" 
              placeholder="Название нового приоритета" 
              @keyup.enter="createPriority"
            />
            <Button 
              variant="outline" 
              @click="createPriority"
              :disabled="priorityAddApi.isPending"
            >
              Добавить
            </Button>
          </div>
        </div>
        
        <DialogFooter>
          <DialogClose>
            <Button>
              Закрыть
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    <Dialog v-model:open="isIconDialogOpen" :autoFocus="false">
      <DialogContent class="max-w-md">
        <DialogHeader>
          <DialogTitle>Редактирование доски</DialogTitle>
          <DialogDescription>
            Измените иконку и название доски.
          </DialogDescription>
        </DialogHeader>

        <!-- Поле для ввода названия -->
        <div class="space-y-2">
          <Label for="board-name">Название доски</Label>
          <Input 
            id="board-name" 
            v-model="iconUpdatePayload.name" 
            placeholder="Введите название доски" 
          />
        </div>

        <!-- Выбор иконки -->
        <div class="space-y-2">
          <Label>Иконка доски</Label>
          <div class="grid grid-cols-6 gap-4 py-4 max-h-64 overflow-y-auto">
            <button 
              v-for="icon in availableIcons" 
              :key="icon" 
              @click="selectedIcon = icon"
              :class="['p-2 rounded border', selectedIcon === icon ? 'border-primary' : 'border-transparent']"
            >
              <Icon :name="icon" class="size-6" />
            </button>
          </div>
        </div>

        <DialogFooter>
          <Button @click="updateBoardIcon" :disabled="iconUpdateApi.isPending">
            Сохранить
          </Button>
          <DialogClose>
            <Button variant="ghost">Отмена</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </Sidebar>
</template>