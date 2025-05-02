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

const addTask = async (columnId: string) => {
  const title = newTaskTitles.value[columnId]?.trim();
  if (!title) return;

  try {
    const column = localColumns.value.find((col) => col.id === columnId);
    const order = column ? column.tasks.length : 0;
    
    isAddingTasks.value = { ...isAddingTasks.value, [columnId]: true };
    
    const { data } = await useApi(`/task/add-task-to-column/${columnId}/`, {
      method: "POST",
      body: {
        title: title,
        order: order
      }
    });

    newTaskTitles.value = { ...newTaskTitles.value, [columnId]: "" };
    
    if (data.value?.id) {
      const columnIndex = currentBoard.value.columns.findIndex(col => col.id === columnId);
      if (columnIndex !== -1) {
        currentBoard.value.columns[columnIndex].tasks.push(data.value);
      }
    }
  } catch (error) {
    console.error("Ошибка при добавлении задачи:", error);
    toast.error("Не удалось добавить задачу");
  } finally {
    isAddingTasks.value = { ...isAddingTasks.value, [columnId]: false };
  }
};

const columnOrderPayload = ref<{task_order: string[]} | null>(null);
const taskUpdatePayload = ref<{column_id: string, order: number} | null>(null);

const updateColumnOrderApi = (columnId: string) => useApi(
  `/task/update-column-order/${columnId}/`, 
  {
    method: "POST",
    body: columnOrderPayload,
    watch: false,
    immediate: false
  }
);

const updateTaskColumnApi = (taskId: string) => useApi(
  `/task/${taskId}/update-column/`, 
  {
    method: "PATCH",
    body: taskUpdatePayload,
    watch: false,
    immediate: false
  }
);

const onTaskDragEnd = async (evt: any) => {
  if (!evt.moved && !evt.added) return;

  const event = evt.moved || evt.added;
  const task = event.element;
  const newIndex = event.newIndex;

  // Находим новую колонку
  const newColumn = localColumns.value.find((col) =>
    col.tasks.some((t) => t.id === task.id)
  );
  if (!newColumn) return;

  try {
    // 1. Обновляем порядок задач в колонке
    columnOrderPayload.value = {
      task_order: newColumn.tasks.map((t) => t.id)
    };
    
    await updateColumnOrderApi(newColumn.id).execute();

    if (evt.added) {
      taskUpdatePayload.value = {
        column_id: newColumn.id,
        order: newIndex
      };
      
      await updateTaskColumnApi(task.id).execute();
    }

  } catch (error) {
    console.error("Ошибка при обновлении задач:", error);
    toast.error("Не удалось обновить задачу");
  } finally {
    // Сбрасываем payload
    columnOrderPayload.value = null;
    taskUpdatePayload.value = null;
  }
};

const handleTaskClick = (task: any) => {
  projectStore.openTaskEditor(task);
};
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
      <span>Время: {{ projectStore.formatTime(projectStore.timer.total) }}</span>
    </div>
    <ClientOnly>
      <TransitionGroup
        name="columns"
        tag="div"
        class="flex gap-4 overflow-x-auto pb-4"
      >
        <div
          v-for="column in localColumns"
          :key="column.id"
          class="min-w-[300px] shrink-0 rounded-lg border bg-card p-4"
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
                class="rounded border p-3 text-sm cursor-move"
                @click="handleTaskClick(task)"
              >
                {{ task.title || "Нет title" }}
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
</style>