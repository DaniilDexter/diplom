<script setup lang="ts">
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

definePageMeta({ layout: "sidebar" });


// Получаем store и нужные значения
const projectStore = useProjectStore()
const { currentProject } = storeToRefs(projectStore)

// Форматирование даты
const formatDate = (dateString: string) => {
  return format(new Date(dateString), 'dd MMM yyyy', { locale: ru })
}

// Проверка на просроченность задачи
const isOverdue = (task: any) => {
  if (!task.due_date || task.is_completed) return false
  return new Date(task.due_date) < new Date()
}

// Проверка, что задача на сегодня
const isDueToday = (task: any) => {
  if (!task.due_date) return false
  const today = new Date()
  const dueDate = new Date(task.due_date)
  return dueDate.toDateString() === today.toDateString()
}

// Расчет прогресса по подзадачам
const calculateProgress = (task: any) => {
  if (!task.subtasks?.length) return 0
  const completed = task.subtasks.filter((st: any) => st.is_completed).length
  return (completed / task.subtasks.length) * 100
}

// Получение статуса задачи
const getTaskStatus = (task: any) => {
  if (task.is_completed) return 'completed'
  if (task.submitted_at) return 'submitted'
  if (task.started_at) return 'in_progress'
  return 'todo'
}

const statusLabels = {
  todo: 'К выполнению',
  in_progress: 'В работе',
  submitted: 'На проверке',
  completed: 'Завершено'
}

const statusIcons = {
  todo: 'lucide:circle',
  in_progress: 'lucide:refresh-cw',
  submitted: 'lucide:send',
  completed: 'lucide:check-circle'
}

const statusClasses = {
  todo: 'bg-gray-100 text-gray-800',
  in_progress: 'bg-blue-100 text-blue-800',
  submitted: 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800'
}

// Получение инициалов пользователя
const getInitials = (username: string) => {
  return username.split(' ').map(n => n[0]).join('').toUpperCase()
}

// Получение топ-5 задач по приоритету
const getTopPriorityTasks = (board: any) => {
  if (!board?.columns) return []
  const allTasks = board.columns.flatMap((col: any) => col.tasks || [])
  return allTasks
    .filter((task: any) => task?.priority && !task.is_completed)
    .sort((a: any, b: any) => (a.priority?.order || 0) - (b.priority?.order || 0))
    .slice(0, 5)
}

// Получение спринтовых досок
const getSprintBoards = () => {
  return currentProject.value?.boards?.filter((board: any) => board.is_sprint) || []
}

// Получение обычных досок
const getRegularBoards = () => {
  return currentProject.value?.boards?.filter((board: any) => !board.is_sprint) || []
}
</script>

<template>
  <div class="flex flex-1 flex-col gap-6 p-6 pt-0" v-if="currentProject">
    <!-- Заголовок проекта -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">{{ currentProject.name }}</h1>
        <p class="text-muted-foreground">{{ currentProject.description || 'Описание проекта отсутствует' }}</p>
      </div>
      <div class="flex items-center gap-2">
        <Badge variant="outline" class="px-3 py-1">
          <Icon name="lucide:key" class="size-4 mr-2" />
          {{ currentProject.key }}
        </Badge>
      </div>
    </div>

    <!-- Статистика проекта -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Всего задач</CardTitle>
          <Icon name="lucide:list-checks" class="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">
            {{ currentProject.boards?.flatMap(b => b.columns?.flatMap(c => c.tasks || [])).length || 0 }}
          </div>
          <p class="text-xs text-muted-foreground">во всех досках</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Завершено</CardTitle>
          <Icon name="lucide:check-circle" class="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">
            {{ currentProject.boards?.flatMap(b => b.columns?.flatMap(c => c.tasks?.filter(t => t.is_completed) || []))?.length || 0 }}
          </div>
          <p class="text-xs text-muted-foreground">задач выполнено</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Участники</CardTitle>
          <Icon name="lucide:users" class="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ currentProject.members?.length || 0 }}</div>
          <p class="text-xs text-muted-foreground">человек в проекте</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Досок</CardTitle>
          <Icon name="lucide:layout-dashboard" class="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ currentProject.boards?.length || 0 }}</div>
          <p class="text-xs text-muted-foreground">
            {{ getSprintBoards().length }} спринтовых, {{ getRegularBoards().length }} обычных
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- Доски и приоритетные задачи -->
    <div class="grid gap-6 lg:grid-cols-2">
      <!-- Список досок -->
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Icon name="lucide:layout-dashboard" class="size-5" />
            Доски проекта
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="board in currentProject.boards" :key="board.id" class="border rounded-lg p-4">
              <div class="flex items-center gap-3">
                <Icon :name="board.icon" class="size-5" />
                <div>
                  <h3 class="font-medium">{{ board.name }}</h3>
                  <p class="text-sm text-muted-foreground">
                    {{ board.is_sprint ? 'Спринтовая доска' : 'Обычная доска' }}
                  </p>
                </div>
              </div>
              <div class="mt-3 grid grid-cols-4 gap-2">
                <div v-for="column in board.columns" :key="column.id" class="text-center">
                  <div class="text-sm font-medium">{{ column.name }}</div>
                  <div class="text-lg font-bold">{{ column.tasks?.length || 0 }}</div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Приоритетные задачи -->
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Icon name="lucide:alert-octagon" class="size-5" />
            Приоритетные задачи
          </CardTitle>
          <CardDescription>Самые важные задачи во всех досках</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <template v-for="board in currentProject.boards" :key="board.id">
              <div v-if="getTopPriorityTasks(board).length > 0">
                <h4 class="text-sm font-medium flex items-center gap-2 mb-2">
                  <Icon :name="board.icon" class="size-4" />
                  {{ board.name }}
                </h4>
                <div class="space-y-2">
                  <div
                    v-for="task in getTopPriorityTasks(board)"
                    :key="task.id"
                    class="rounded border p-3 text-sm space-y-2 relative"
                    :style="{ 'border-left': `4px solid ${task.priority?.color || '#e5e7eb'}` }"
                  >
                    <div class="flex flex-col gap-2">
                      <h4 class="font-medium break-words">{{ task.title || "Нет title" }}</h4>
                      <div class="flex flex-wrap gap-1">
                        <Badge 
                          v-if="isOverdue(task)"
                          class="bg-red-100 text-red-800 flex items-center gap-1"
                        >
                          <Icon name="lucide:alert-circle" class="w-3 h-3" />
                          Просрочено
                        </Badge>
                        <Badge 
                          v-if="getTaskStatus(task) !== 'todo'"
                          :class="statusClasses[getTaskStatus(task)]"
                          class="flex items-center gap-1"
                        >
                          <Icon :name="statusIcons[getTaskStatus(task)]" class="w-3 h-3" />
                          {{ statusLabels[getTaskStatus(task)] }}
                        </Badge>
                        <Badge 
                          v-if="task.priority"
                          variant="outline"
                          class="flex items-center gap-1"
                          :style="{ color: task.priority.color }"
                        >
                          <Icon name="lucide:flag" class="w-3 h-3" />
                          {{ task.priority.name }}
                        </Badge>
                      </div>
                    </div>
                    <div v-if="task.due_date" class="flex items-center gap-1 text-xs mt-1"
                      :class="{
                        'text-red-500': isOverdue(task) && !task.is_completed,
                        'text-yellow-500': isDueToday(task) && !task.is_completed,
                        'text-green-500': task.is_completed
                      }"
                    >
                      <Icon name="lucide:calendar" class="size-3" />
                      {{ formatDate(task.due_date) }}
                    </div>
                  </div>
                </div>
              </div>
            </template>
            <p v-if="currentProject.boards?.flatMap(b => getTopPriorityTasks(b))?.length === 0" class="text-sm text-muted-foreground text-center py-4">
              Нет задач с приоритетами
            </p>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Участники и теги -->
    <div class="grid gap-6 lg:grid-cols-2">
      <!-- Участники проекта -->
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Icon name="lucide:users" class="size-5" />
            Участники проекта
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="member in currentProject.members" :key="member.user.id" class="flex items-center gap-3">
              <Avatar class="size-10">
                <AvatarImage v-if="member.user.photo" :src="`http://127.0.0.1:8000${member.user.photo}`" />
                <AvatarFallback>{{ getInitials(member.user.username) }}</AvatarFallback>
              </Avatar>
              <div>
                <h4 class="font-medium">{{ member.user.username }}</h4>
                <p class="text-sm text-muted-foreground">{{ member.role.name }}</p>
              </div>
              <Badge variant="outline" class="ml-auto">
                {{ formatDate(member.joined_at) }}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Теги проекта -->
      <Card>
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Icon name="lucide:tags" class="size-5" />
            Теги проекта
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div class="flex flex-wrap gap-2">
            <Badge
              v-for="tag in currentProject.tags"
              :key="tag.id"
              variant="outline"
              class="px-3 py-1"
            >
              <Icon name="lucide:tag" class="size-4 mr-2" :style="{ color: tag.color }" />
              {{ tag.name }}
              <span v-if="tag.is_default" class="ml-2 text-xs text-muted-foreground">по умолчанию</span>
            </Badge>
            <p v-if="currentProject.tags?.length === 0" class="text-sm text-muted-foreground">
              В проекте нет тегов
            </p>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Приоритеты проекта -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Icon name="lucide:signal" class="size-5" />
          Приоритеты проекта
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid gap-4 md:grid-cols-4">
          <div v-for="priority in currentProject.priorities?.sort((a, b) => a.order - b.order)" :key="priority.id" class="flex items-center gap-3">
            <div class="size-3 rounded-full" :style="{ backgroundColor: priority.color }"></div>
            <span class="font-medium">{{ priority.name }}</span>
            <span class="text-sm text-muted-foreground ml-auto">порядок: {{ priority.order }}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
</template>