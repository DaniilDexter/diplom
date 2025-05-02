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
    // Обработка ошибки
  }
};

const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') createBoard()
  if (e.key === 'Escape') isAddingBoard.value = false
}

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
            <!-- Список досок -->
            <SidebarMenuItem v-for="board in currentProject.boards" :key="board.id">
              <SidebarMenuButton as-child>
                <NuxtLink 
                  :to="`/projects/${route.params.id}/boards/${board.id}`"
                  class="flex items-center gap-2"
                >
                  <Icon name="lucide:kanban" mode="svg" class="size-4" />
                  <span class="truncate">{{ board.name }}</span>
                </NuxtLink>
              </SidebarMenuButton>
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
    </SidebarContent>
    <SidebarFooter>
      <SidebarFooterWithDialog />
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>