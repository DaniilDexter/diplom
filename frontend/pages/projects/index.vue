<script setup lang="ts">
const projectStore = useProjectStore()

await projectStore.fetchProjects()

const {projects} = storeToRefs(projectStore)

const newProject = ref({
  name: "",
  description: "",
  members: [],
});

const selectedUsers = ref([])

const userStore = useUserStore()

await userStore.fetchFriends()

const { userFriends } = storeToRefs(userStore)

const { data: projectData, error: projectError, execute: executeCreateProject } = useApi('/project/create-project/', {
  method: 'POST',
  body: newProject.value,
  watch: false,
  immediate: false, // Запрос не выполняется автоматически
});

async function createProject() {
  try {
    console.log('Запрос на создание проекта');

    newProject.value.members = selectedUsers.value.map(user => user.id);
    
    const payload = {
      name: newProject.value.name,
      description: newProject.value.description,
      members: newProject.value.members.map(m => m.id) // отправляем только ID
    };
    
    await executeCreateProject({
      body: payload
    });

    if (projectData.value?.id) {
      projects.value.push(projectData.value)
      
    }
  } catch (error) {
    console.error('Ошибка создания проекта:', error);
  }
}


</script>

<template>
  <main class="container mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold mb-6">Мои проекты</h1>

    <Sheet ref="sheet">
      <SheetTrigger as-Child>
      <Button class="mb-6 flex items-center">
        <Icon name="lucide:plus" class="size-4 mr-2" /> Новый проект
      </Button>
      </SheetTrigger>
      <SheetContent >
        <SheetHeader>
          <SheetTitle>Создать новый проект</SheetTitle>
        </SheetHeader>
        <div class="space-y-4 mt-4">
          <Input v-model="newProject.name" placeholder="Название проекта" class="w-full" />
          <Textarea v-model="newProject.description" placeholder="Описание" class="w-full" />
          
          <Combobox v-model="selectedUsers" multiple by="id">
            <ComboboxAnchor as-child>
              <ComboboxTrigger as-child>
                <Button variant="outline" class="w-full justify-between">
                  {{ selectedUsers.length > 0 ? selectedUsers.map(m => m.username).join(', ') : "Выберите участников" }}
                  <Icon name="lucide:chevrons-up-down" class="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
              </ComboboxTrigger>
            </ComboboxAnchor>

            <ComboboxList>
              <div class="relative w-full max-w-sm items-center">
                <ComboboxInput class="pl-9 focus-visible:ring-0 border-0 border-b rounded-none h-10" placeholder="Выберите участников..." />
                <span class="absolute start-0 inset-y-0 flex items-center justify-center px-3">
                  <Icon name="lucide:search" class="size-4 text-muted-foreground" />
                </span>
              </div>

              <ComboboxEmpty>
                Не найдено участников.
              </ComboboxEmpty>

              <ComboboxGroup>
                <ComboboxItem
                  v-for="friend in userFriends"
                  :key="friend.id"
                  :value="friend"
                >
                  <Icon name="lucide:user" class="size-4 mr-2" />
                  {{ friend.username }}

                  <ComboboxItemIndicator>
                    <Icon name="lucide:check" class="ml-auto h-4 w-4'" />
                  </ComboboxItemIndicator>
                </ComboboxItem>
              </ComboboxGroup>
            </ComboboxList>
          </Combobox>
        </div>
        <SheetFooter>
          <Button @click="createProject" class="flex items-center">
            <Icon name="lucide:sparkles" class="size-4 mr-2 text-sky-300 group-hover:text-white transition-colors" />
            Создать проект
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
    
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card v-for="project in projects" :key="project.id">
        <CardHeader>
          <CardTitle>
            <NuxtLink :to="`/projects/${project.id}/boards`">
              {{ project.name }}
            </NuxtLink>
          </CardTitle>
          <p class="text-muted-foreground text-sm">{{ project.description }}</p>
        </CardHeader>
        <CardContent>
          <p class="text-xs text-gray-500">Участники:</p>
          <ul class="text-sm">
            <li v-for="member in project.members" :key="member.id" class="flex items-center gap-2">
              <Icon name="lucide:user" class="size-4 text-sky-500" />
              {{ member.user.username }}
            </li>
          </ul>
          <p class="text-xs text-gray-500">Ключ: {{ project.key }}</p>
        </CardContent>
      </Card>
    </div>
  </main>
</template>
