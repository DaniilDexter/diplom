<script setup lang="ts">
import { VueDraggableNext } from "vue-draggable-next";
import { parseDate, type CalendarDate } from "@internationalized/date";
import { format, parseISO } from "date-fns";
import { toast } from "vue-sonner";

definePageMeta({ layout: "sidebar" });

const projectStore = useProjectStore()

await projectStore.fetchProjects()

const { currentProject, currentBoard } = storeToRefs(projectStore)


const route = useRoute();
const boardId = route.params.boardID as string;

const newColumnName = ref("");
const isAddingColumn = ref(false);
const newTaskTitles = ref<Record<string, string>>({});
const isAddingTasks = ref<Record<string, boolean>>({});

const localColumns = computed(() =>
 currentBoard.value?.columns || []
);

const newColumnPayload = ref(null)
const addColumnApi = useApi(`/boards/${boardId}/add-column/`, {
  method: "POST",
  body: newColumnPayload,
  watch: false,
  immediate: false
})

const addColumn = async () => {
  if (!newColumnName.value.trim()) return;
  try {
    newColumnPayload.value = {
      name: newColumnName.value,
      order: localColumns.value.length
    }
    isAddingColumn.value = true;
    await addColumnApi.execute()
    newColumnPayload.value = null
    newColumnName.value = "";
    if(addColumnApi.data.value.id) {
      currentBoard.value.columns.push(addColumnApi.data.value)
    }
  } catch (error) {
    console.error("Ошибка при добавлении колонки:", error);
  } finally {
    isAddingColumn.value = false;
  }
};

const selectedColumnId = ref<string | null>(null);
const selectedTaskId = ref<string | null>(null);

const addTaskApiUrl = computed(() => 
  selectedColumnId.value ? `/task/add-task-to-column/${selectedColumnId.value}/` : null
);

const addTaskPayload = ref()

const addTaskApi = useApi(() => `/task/add-task-to-column/${selectedColumnId.value}/`, {
  method: "POST",
  body: addTaskPayload,
  watch: false,
  immediate: false
});

// 3. Обновленная функция addTask
const addTask = async (columnId: string) => {
  const title = newTaskTitles.value[columnId]?.trim();
  if (!title) return;

  try {
    const column = localColumns.value.find((col) => col.id === columnId);
    const order = column ? column.tasks.length : 0;
    
    // Устанавливаем ID колонки для URL
    selectedColumnId.value = columnId;
    isAddingTasks.value = { ...isAddingTasks.value, [columnId]: true };
    
    // Устанавливаем тело запроса и выполняем
    addTaskPayload.value = {
      title: title,
      order: order,
    }
    await addTaskApi.execute();

    newTaskTitles.value = { ...newTaskTitles.value, [columnId]: "" };
    
    if (addTaskApi.data.value?.id) {
      const columnIndex = currentBoard.value.columns.findIndex(col => col.id === columnId);
      if (columnIndex !== -1) {
        currentBoard.value.columns[columnIndex].tasks.push(addTaskApi.data.value);
      }
    }
  } catch (error) {
    console.error("Ошибка при добавлении задачи:", error);
    toast.error("Не удалось добавить задачу");
  } finally {
    selectedColumnId.value = null;
    addTaskPayload.value = null;
    isAddingTasks.value = { ...isAddingTasks.value, [columnId]: false };
  }
};

const columnOrderPayload = ref<{task_order: string[]} | null>(null);
const taskUpdatePayload = ref<{column_id: string, order: number} | null>(null);

const columnOrderApiUrl = computed(() => 
  selectedColumnId.value ? `/task/update-column-order/${selectedColumnId.value}/` : null
);

const taskColumnApiUrl = computed(() => 
  selectedTaskId.value ? `/task/${selectedTaskId.value}/update-column/` : null
);

// 2. Создаем API клиенты
const columnOrderApi = useApi(columnOrderApiUrl, {
  method: "POST",
  body: columnOrderPayload,
  watch: false,
  immediate: false
});

const taskColumnApi = useApi(taskColumnApiUrl, {
  method: "PATCH",
  body: taskUpdatePayload,
  watch: false,
  immediate: false
});

// 3. Обновленная функция onTaskDragEnd
const onTaskDragEnd = async (evt: any) => {
  if (!evt.moved && !evt.added) return;

  const event = evt.moved || evt.added;
  const task = event.element;
  const newIndex = event.newIndex;

  // Находим новую колонку
  const newColumn = localColumns.value.find(col => 
    col.tasks.some(t => t.id === task.id)
  );
  if (!newColumn) return;

  try {
    // Устанавливаем ID для URL
    selectedColumnId.value = newColumn.id;
    
    // 1. Обновляем порядок задач
    columnOrderPayload.value = {
      task_order: newColumn.tasks.map(t => t.id)
    };
    await columnOrderApi.execute();

    // Если задача перемещена между колонками
    if (evt.added) {
      selectedTaskId.value = task.id;
      taskUpdatePayload.value = {
        column_id: newColumn.id,
        order: newIndex
      };
      await taskColumnApi.execute();
    }

  } catch (error) {
    console.error("Ошибка при обновлении задач:", error);
    toast.error("Не удалось обновить задачу");
  } finally {
    // Сбрасываем состояния
    selectedColumnId.value = null;
    selectedTaskId.value = null;
    columnOrderPayload.value = null;
    taskUpdatePayload.value = null;
  }
};

const handleTaskClick = (task: any) => {
  projectStore.openTaskEditor(task);
};

// Форматирование даты
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

// Получение инициалов для аватара
const getInitials = (name) => {
  if (!name) return ''
  return name.split(' ').map(n => n[0]).join('').toUpperCase()
}

// Проверка просроченности
const isOverdue = (task) => {
  if (!task.due_date) return false
  const dueDate = new Date(task.due_date)
  const today = new Date()
  return dueDate < today && !isSameDay(dueDate, today)
}

// Проверка что срок истекает сегодня
const isDueToday = (task) => {
  if (!task.due_date) return false
  const dueDate = new Date(task.due_date)
  const today = new Date()
  return isSameDay(dueDate, today)
}

// Проверка что две даты - один и тот же день
const isSameDay = (date1, date2) => {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  )
}

const getStatusText = (task) => {
  if (task.is_completed) return 'Завершено'
  
  switch(task.status) {
    case 'in_progress': return 'В работе'
    case 'in_review': return 'На проверке'
    case 'todo': return 'К выполнению'
    default: return 'К выполнению'
  }
}

const getTaskStatus = (task) => {
  if (task.is_completed) return 'completed'
  if (task.completed_at) return 'completed'
  if (task.submitted_at) return 'submitted'
  if (task.started_at) return 'in_progress'
  if (task.assigned_at) return 'assigned'
  return 'todo'
}

const statusLabels = {
  todo: 'К выполнению',
  assigned: 'Назначена',
  in_progress: 'В работе',
  submitted: 'На проверке',
  completed: 'Завершено'
}

const statusClasses = {
  todo: 'bg-gray-100 text-gray-800',
  assigned: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-amber-100 text-amber-800',
  submitted: 'bg-purple-100 text-purple-800',
  completed: 'bg-emerald-100 text-emerald-800'
}

const statusIcons = {
  todo: 'lucide:circle',
  assigned: 'lucide:user',
  in_progress: 'lucide:play',
  submitted: 'lucide:eye',
  completed: 'lucide:check'
}

const calculateProgress = (task) => {
  if (!task.subtasks?.length) return 0
  const completed = task.subtasks.filter(st => st.is_completed).length
  return Math.round((completed / task.subtasks.length) * 100)
}

</script>

<template>
  <div class="flex flex-1 flex-col gap-4 p-4 pt-0">
    <!-- Форма добавления колонки -->
    <div class="flex items-center gap-2">
      <Input
        v-model="newColumnName"
        placeholder="Введите название колонки"
        class="max-w-[300px]"
        @keyup.enter="addColumn"
      />
      <Button
        :disabled="!newColumnName.trim() || isAddingColumn"
        @click="addColumn"
      >
        <Icon
          :name="isAddingColumn ? 'svg-spinners:180-ring' : 'lucide:plus'"
          class="h-4 w-4"
        />
        <span class="ml-2">Добавить колонку</span>
      </Button>
    </div>
    <div v-if="projectStore.selectedTask" class="page-timer">
      <span>Текущая задача: {{ projectStore.selectedTask.title }}</span>
      <span>Время: {{ projectStore.formatTime(projectStore.timer.elapsed) }}</span>
    </div>
    <ClientOnly>
      <TransitionGroup
        name="columns"
        tag="div"
        class="flex gap-4 overflow-x-auto pb-4 h-full scrollbar-container"
      >
        <div
          v-for="column in localColumns"
          :key="column.id"
          class="max-w-[360px] w-full shrink-0 rounded-lg border bg-card p-4"
        >
          <h3 class="mb-3 text-lg font-semibold">{{ column.name }}</h3>

          <!-- Форма добавления задачи -->
          <div class="mb-3 flex gap-2">
            <Input
              v-model="newTaskTitles[column.id]"
              placeholder="Новая задача"
              @keyup.enter="addTask(column.id)"
            />
            <Button
              size="sm"
              :disabled="
                !newTaskTitles[column.id]?.trim() || isAddingTasks[column.id]
              "
              @click="addTask(column.id)"
            >
              <Icon
                :name="
                  isAddingTasks[column.id]
                    ? 'svg-spinners:180-ring'
                    : 'lucide:plus'
                "
                class="h-4 w-4"
              />
            </Button>
          </div>

          <!-- Список задач с drag-and-drop -->
          <VueDraggableNext
            :list="column.tasks"
            :group="{ name: 'tasks', pull: true, put: true }"
            class="space-y-2"
            item-key="id"
            @change="onTaskDragEnd"
            :animation="150"
            ghost-class="ghost-task"
          >
          <template v-for="task in column.tasks">
            <div
              class="rounded border p-3 text-sm cursor-move space-y-2 relative"
              :style="{ 'border-left': `4px solid ${task.priority?.color || '#e5e7eb'}` }"
              @click="handleTaskClick(task)"
            >
              <!-- Заголовок и статус - теперь в колонку -->
              <div class="flex flex-col gap-2">
                <!-- Заголовок на всю ширину -->
                <h4 class="font-medium break-words">{{ task.title || "Нет title" }}</h4>
                
                <!-- Бейджи - переносятся на новую строку -->
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
                </div>
              </div>

              <!-- Теги -->
              <div class="flex flex-wrap gap-1" v-if="task.tags?.length">
                <Badge
                  v-for="tag in task.tags"
                  :key="tag.id"
                  variant="outline"
                  class="text-xs"
                >
                  <Icon name="lucide:tag" class="size-3 mr-1" :style="{ color: tag.color }"/>
                  {{ tag.name }}
                </Badge>
              </div>

              <!-- Подзадачи (прогресс) -->
              <div v-if="task.subtasks?.length" class="text-xs text-muted-foreground">
                <div class="flex items-center gap-1">
                  <Icon name="lucide:list-checks" class="size-3" />
                  <span>
                    {{ task.subtasks.filter(st => st.is_completed).length }}/{{ task.subtasks.length }}
                  </span>
                </div>
                <Progress 
                  :model-value="calculateProgress(task)" 
                  class="h-1 mt-1"
                />
              </div>

              <!-- Дата выполнения и назначенный -->
              <div class="flex justify-between items-center pt-1">
                <div class="flex items-center gap-2">
                  <!-- Дата выполнения -->
                  <div 
                    v-if="task.due_date" 
                    class="flex items-center gap-1 text-xs"
                    :class="{
                      'text-red-500': isOverdue(task) && !task.is_completed,
                      'text-yellow-500': isDueToday(task) && !task.is_completed,
                      'text-green-500': task.is_completed
                    }"
                  >
                    <Icon name="lucide:calendar" class="size-3" />
                    {{ formatDate(task.due_date) }}
                  </div>

                  <!-- Время выполнения -->
                  <div v-if="task.time" class="flex items-center gap-1 text-xs text-muted-foreground">
                    <Icon name="lucide:clock" class="size-3" />
                    {{ task.time }}
                  </div>
                </div>

                <!-- Аватар назначенного -->
                <Avatar v-if="task.assigned_to" class="size-6">
                  <AvatarImage v-if="task.assigned_to.photo" :src="task.assigned_to.photo" />
                  <AvatarFallback v-else>
                    {{ getInitials(task.assigned_to.username) }}
                  </AvatarFallback>
                </Avatar>
              </div>
            </div>
          </template>
          </VueDraggableNext>
        </div>
      </TransitionGroup>
      <TaskEditor />
      <div
        v-if="!localColumns?.length"
        class="flex flex-col items-center justify-center py-12 text-center"
      >
        <Icon
          name="lucide:columns"
          class="mb-4 h-12 w-12 text-muted-foreground"
        />
        <h3 class="mb-2 text-lg font-medium">Нет колонок</h3>
        <p class="text-muted-foreground">Начните с добавления первой колонки</p>
      </div>
    </ClientOnly>
    </div>
  <ClientOnly>
    <Toaster />
  </ClientOnly>
</template>

<style scoped>
.columns-move,
.columns-enter-active,
.columns-leave-active {
  transition: all 0.3s ease;
}

.columns-enter-from,
.columns-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.columns-leave-active {
  position: absolute;
}

/* Стили для drag-and-drop */
.ghost-task {
  opacity: 0.5;
  background: #c8ebfb;
}

.sortable-chosen {
  cursor: grabbing;
}

.subtask-enter-active,
.subtask-leave-active {
  transition: all 0.3s ease;
}
.subtask-enter-from,
.subtask-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
.subtask-item {
  user-select: none;
}
.subtask-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.timer-container {
  transition: all 0.3s ease;
  user-select: none;
}

.timer-button {
  min-width: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.timer-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.timer-display {
  font-variant-numeric: tabular-nums; /* Для ровных цифр */
}

.current-session {
  opacity: 0.8;
}

.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

/* Анимация пульсации при работе таймера */
.timer-button[data-running="true"] {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
  }
}

.scrollbar-container {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 transparent;
}

/* Для Chrome/Safari */
.scrollbar-container::-webkit-scrollbar {
  height: 8px;
}

.scrollbar-container::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 4px;
  margin: 0 16px;
}

.scrollbar-container::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 4px;
  border: 2px solid transparent;
  background-clip: content-box;
}

.scrollbar-container::-webkit-scrollbar-thumb:hover {
  background-color: #a8a8a8;
}

/* Анимация появления скролла */
.scrollbar-container {
  transition: scrollbar-color 0.3s ease;
}
</style>