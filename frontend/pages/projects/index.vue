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
    
    await executeCreateProject();

    if (projectData.value?.id) {
      projects.value.unshift(projectData.value)
      
      newProject.value = ({
        name: "",
        description: "",
        members: [],
      });
      selectedUsers.value = []
    }
  } catch (error) {
    console.error('Ошибка создания проекта:', error);
  }
}

const projectKey = ref("");
const isAddingProject = ref(false);
const keyError = ref(null)
const projectKeyPayload = ref(null)
const projectKeyApi = useApi(`/project/add-member-by-key/`, {
  method: "POST",
  body: projectKeyPayload,
  watch: false,
  immediate: false
})

const addProjectKey = async () => {
  if (!projectKey.value.trim()) return;
  try {
    projectKeyPayload.value = {
      key: projectKey.value,
      user_id: userStore.user.id
    }
    isAddingProject.value = true;
    await projectKeyApi.execute()
    projectKeyPayload.value = null
    projectKey.value = "";
    if(projectKeyApi.error.value){
      keyError.value = projectKeyApi.error.value.data.detail
    }
    else if(projectKeyApi.data.value.id) {
      projects.value.unshift(projectKeyApi.data.value)
    }
  } catch (error) {
    console.error("Ошибка при добавлении колонки:", error);
  } finally {
    isAddingProject.value = false;
  }
};
</script>

<template>
  <main class="container mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold mb-6">Мои проекты</h1>

    <Sheet ref="sheet">
      <div class="flex justify-between">
        <SheetTrigger as-Child>
          <Button class="mb-6 flex items-center h-10">
            <Icon name="lucide:plus" class="size-4 mr-2" /> Новый проект
          </Button>
        </SheetTrigger>
        <div>
          <div class="flex justify-items-start gap-2">
            <Input
              v-model="projectKey"
              placeholder="Введите ключ проекта"
              class="max-w-[300px] h-10"
              @keyup.enter="addProjectKey"
            />
            <Button
              :disabled="!projectKey.trim() || isAddingProject"
              @click="addProjectKey"
              class="h-10"
            >
              <Icon
                :name="isAddingProject ? 'svg-spinners:180-ring' : 'lucide:plus'"
                class="h-4 w-4"
              />
              <span class="ml-2">Добавить проект</span>
            </Button>
          </div>
          <p v-if="keyError" class="text-red-500 text-sm">Ошибка: {{ keyError }}</p>
        </div>
      </div>
      <SheetContent >
        <SheetHeader>
          <SheetTitle>Создать новый проект</SheetTitle>
        </SheetHeader>
        <div class="space-y-4 mt-4">
          <Input v-model="newProject.name" placeholder="Название проекта" class="w-full" />
          <Textarea v-model="newProject.description" placeholder="Описание" class="w-full" />
          
          <Select v-model="selectedUsers" :multiple="true">
            <SelectTrigger class="w-full justify-between">
              <span v-if="selectedUsers.length > 0">
                {{ selectedUsers.map(user => user.username).join(', ') }}
              </span>
              <span v-else>Выберите участников</span>
            </SelectTrigger>

            <SelectContent class="w-full">

              <SelectGroup>
                <SelectLabel>Друзья</SelectLabel>

                <SelectItem
                  v-for="friend in userFriends"
                  :key="friend.id"
                  :value="friend"
                >
                  <div class="flex items-center justify-between w-full">
                    <Icon name="lucide:user" class="size-4 mr-2" />
                    <span>{{ friend.username }}</span>
                    <Badge variant="outline" class="ml-2">{{ friend.role.name }}</Badge>
                  </div>
                </SelectItem>
              </SelectGroup>

              <div v-if="userFriends.length === 0" class="px-4 py-2 text-sm text-muted-foreground">
                Не найдено участников.
              </div>
            </SelectContent>
          </Select>

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
