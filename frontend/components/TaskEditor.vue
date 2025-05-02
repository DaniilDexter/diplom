<script setup lang="ts">
import { parseDate, type CalendarDate } from "@internationalized/date";
import { format, parseISO } from "date-fns";
import { toast } from "vue-sonner";


const projectStore = useProjectStore()

const { currentProject, selectedTask, isTaskSheetOpen, timer } = storeToRefs(projectStore)

const tags = computed(() => currentProject.value?.tags || []);
const priorities = computed(() => currentProject.value?.priorities || []);
const members = computed(() => {
  return (currentProject.value?.members || []).map((m: any) => m.user);
});

const selectedMember = ref(null);
const selectedPriority = ref(null);
const selectedTags = ref([]);

const toApiDate = (date: string | Date | CalendarDate | null | undefined) => {
  if (!date) return null;
  let dateObj = date;

  if (typeof date === "string") {
    dateObj = new Date(date);
  }

  if (dateObj instanceof Date && !isNaN(dateObj.getTime())) {
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, "0"); // Месяцы в JS начинаются с 0
    const day = String(dateObj.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
  }

  if (dateObj && "year" in dateObj && "month" in dateObj && "day" in dateObj) {
    return `${dateObj.year}-${String(dateObj.month).padStart(2, "0")}-${String(
      dateObj.day
    ).padStart(2, "0")}`;
  }

  return null;
};

const calendarDate = ref<CalendarDate | undefined>();

watch(
  () => selectedTask.value,
  (task) => {
    if (!task) return;
    selectedMember.value = task.assigned_to || null;
    selectedPriority.value = task.priority || null;
    selectedTags.value = task.tags || [];
    if (task?.due_date) {
      if (task.due_date instanceof Date) {
        calendarDate.value = parseDate(
          task.due_date.toISOString().slice(0, 10)
        );
      } else {
        calendarDate.value = parseDate(task.due_date.slice(0, 10)); // Если это уже строка
      }
    } else {
      calendarDate.value = undefined;
    }
  },
  { immediate: true }
);

watch(calendarDate, (val) => {
  if (val) {
    const jsDate = new Date(val.year, val.month - 1, val.day);
    selectedTask.value.due_date = jsDate.toISOString();
  } else {
    selectedTask.value.due_date = null;
  }
});

watch(selectedMember, (val) => {
  selectedTask.value.assigned_to =
    members.value.find((m) => m.id === val) || null;
});

watch(selectedPriority, (val) => {
  selectedTask.value.priority =
    priorities.value.find((p) => p.id === val) || null;
});

watch(selectedTags, (val) => {
  selectedTask.value.tags = tags.value.filter((tag) => val.includes(tag.id));
});
const isReportDialogOpen = ref(false);
const isCommentDialogOpen = ref(false);
const newComment = ref({
  content: "",
  is_approved: false,
});
const reportData = ref({
  comment: "",
  image: null as File | null,
  file: null as File | null,
});

const handleImageUpload = (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (input.files?.length) {
    reportData.value.image = input.files[0];
  }
};

const handleFileUpload = (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (input.files?.length) {
    reportData.value.file = input.files[0];
  }
};

const newSubtaskTitle = ref("");
const isAddingSubtask = ref(false);
const isEditingSubtask = ref(false);
const currentSubtask = ref<any>(null);

const taskApiUrl = computed(() => selectedTask.value ? `/task/${selectedTask.value.id}/` : null);
const commentApiUrl = computed(() => selectedTask.value ? `/task/${selectedTask.value.id}/add-comment/` : null);
const reportApiUrl = computed(() => selectedTask.value ? `/task/${selectedTask.value.id}/update-report/` : null);
const subtaskCreateApiUrl = computed(() => selectedTask.value ? `/task/${selectedTask.value.id}/add-subtask/` : null);
const subtaskUpdateApiUrl = computed(() => selectedTask.value ? `/task/${selectedTask.value.id}/update-subtask/` : null);
const subtaskDeleteApiUrl = computed(() => selectedTask.value ? `/task/${selectedTask.value.id}/delete-subtask/` : null);

const taskPayload = ref();
const commentPayload = ref();
const reportPayload = ref<FormData>();
const subtaskCreatePayload = ref();
const subtaskUpdatePayload = ref();
const subtaskDeletePayload = ref();

// 2. API клиенты
const taskApi = useApi(taskApiUrl, {
  method: "PATCH",
  body: taskPayload,
  watch: false,
  immediate: false
});

const commentApi = useApi(commentApiUrl, {
  method: "POST",
  body: commentPayload,
  watch: false,
  immediate: false
});

const reportApi = useApi(reportApiUrl, {
  method: "POST",
  body: reportPayload,
  headers: { "Content-Type": "multipart/form-data" },
  watch: false,
  immediate: false
});

const subtaskCreateApi = useApi(subtaskCreateApiUrl, {
  method: "POST",
  body: subtaskCreatePayload,
  watch: false,
  immediate: false
});

const subtaskUpdateApi = useApi(subtaskUpdateApiUrl, {
  method: "PATCH",
  body: subtaskUpdatePayload,
  watch: false,
  immediate: false
});

const subtaskDeleteApi = useApi(subtaskDeleteApiUrl, {
  method: "DELETE",
  body: subtaskDeletePayload,
  watch: false,
  immediate: false
});

// 3. Основные методы
const updateTask = async () => {
  if (timer.value.isRunning) {
    toast.warning("Остановите таймер перед сохранением");
    return;
  }

  if (!selectedTask.value) return;

  try {
    taskPayload.value = {
      title: selectedTask.value.title,
      description: selectedTask.value.description,
      assigned_to_id: selectedMember.value?.id || null,
      priority_id: selectedPriority.value?.id || null,
      due_date: toApiDate(selectedTask.value.due_date),
      tags_ids: selectedTags.value.map(tag => tag.id),
    };

    await taskApi.execute();
    projectStore.updateSelectedTask();
    isTaskSheetOpen.value = false;
    toast.success("Задача обновлена");
  } catch (error) {
    console.error("Ошибка при обновлении задачи:", error);
    toast.error("Не удалось обновить задачу");
  } finally {
    taskPayload.value = null;
  }
};

const addComment = async () => {
  if (!newComment.value.content.trim() || !selectedTask.value) return;

  try {
    commentPayload.value = { ...newComment.value };
    await commentApi.execute();
    
    projectStore.updateSelectedTask();
    newComment.value = { content: "", is_approved: false };
    isCommentDialogOpen.value = false;
    toast.success("Комментарий добавлен");
  } catch (error) {
    console.error("Ошибка при добавлении комментария:", error);
    toast.error("Не удалось добавить комментарий");
  }
};

const submitReport = async () => {
  if (!selectedTask.value) return;

  try {
    reportPayload.value = new FormData();
    reportPayload.value.append("comment", reportData.value.comment);
    if (reportData.value.image) reportPayload.value.append("image", reportData.value.image);
    if (reportData.value.file) reportPayload.value.append("file", reportData.value.file);

    await reportApi.execute();
    
    projectStore.updateSelectedTask();
    reportData.value = { comment: "", image: null, file: null };
    isReportDialogOpen.value = false;
    toast.success("Отчет отправлен");
  } catch (error) {
    console.error("Ошибка при отправке отчёта:", error);
    toast.error("Не удалось отправить отчёт");
  } finally {
    reportPayload.value = undefined;
  }
};

// 4. Методы для подзадач
const addSubtask = async () => {
  if (!newSubtaskTitle.value.trim() || !selectedTask.value) return;

  try {
    isAddingSubtask.value = true;
    subtaskCreatePayload.value = { title: newSubtaskTitle.value };
    await subtaskCreateApi.execute();

    if (subtaskCreateApi.data.value?.id) {
      projectStore.updateSelectedTask();
      newSubtaskTitle.value = "";
      toast.success("Подзадача добавлена");
    }
  } catch (error) {
    console.error("Ошибка при добавлении подзадачи:", error);
    toast.error("Не удалось добавить подзадачу");
  } finally {
    isAddingSubtask.value = false;
    subtaskCreatePayload.value = null;
  }
};

const updateSubtask = async () => {
  if (!currentSubtask.value || !selectedTask.value) return;

  try {
    isEditingSubtask.value = true;
    subtaskUpdatePayload.value = {
      id: currentSubtask.value.id,
      title: currentSubtask.value.title,
      is_completed: currentSubtask.value.is_completed,
    };

    await subtaskUpdateApi.execute();
    projectStore.updateSelectedTask();
    currentSubtask.value = null;
    toast.success("Подзадача обновлена");
  } catch (error) {
    console.error("Ошибка при обновлении подзадачи:", error);
    toast.error("Не удалось обновить подзадачу");
  } finally {
    isEditingSubtask.value = false;
    subtaskUpdatePayload.value = null;
  }
};

const deleteSubtask = async (subtaskId: number) => {
  if (!selectedTask.value) return;

  try {
    subtaskDeletePayload.value = { id: subtaskId };
    await subtaskDeleteApi.execute();
    projectStore.updateSelectedTask();
    toast.success("Подзадача удалена");
  } catch (error) {
    console.error("Ошибка при удалении подзадачи:", error);
    toast.error("Не удалось удалить подзадачу");
  } finally {
    subtaskDeletePayload.value = null;
  }
};

const toggleSubtaskCompletion = async (subtask: any, event: Event) => {
  event.stopPropagation();

  try {
    subtaskUpdatePayload.value = {
      id: subtask.id,
      is_completed: !subtask.is_completed
    };
    await subtaskUpdateApi.execute();
    projectStore.updateSelectedTask();
  } catch (error) {
    console.error("Ошибка при обновлении подзадачи:", error);
    toast.error("Не удалось обновить статус подзадачи");
  } finally {
    subtaskUpdatePayload.value = null;
  }
};
</script>

<template>
  <Sheet v-model:open="isTaskSheetOpen">
    <SheetContent class="sm:max-w-[600px] overflow-y-auto">
      <SheetHeader>
        <SheetTitle>Редактирование задачи</SheetTitle>
        <SheetDescription>
          Внесите изменения и нажмите "Сохранить"
        </SheetDescription>
      </SheetHeader>

      <div class="grid gap-4 py-4">
        <TaskStepper
          :createdAt="selectedTask.created_at"
          :assignedAt="selectedTask.assigned_at"
          :startedAt="selectedTask.started_at"
          :submittedAt="selectedTask.submitted_at"
          :completedAt="selectedTask.completed_at"
        />

        <div
          class="timer-container flex items-center gap-4 p-4 bg-gray-50 rounded-lg border"
        >
          <Button
            @click="projectStore.toggleTimer()"
            :variant="timer.isRunning ? 'destructive' : 'default'"
            :disabled="!selectedTask"
            class="timer-button px-4 py-2 rounded-md transition-colors"
          >
            <Icon
              :name="timer.isRunning ? 'lucide:square' : 'lucide:play'"
              class="h-4 w-4 mr-2"
            />
            {{ timer.isRunning ? "Остановить" : "Запустить" }}
          </Button>

          <div class="timer-display flex flex-col">
            <div
              v-if="timer.isRunning"
              class="current-session text-sm text-gray-600 mb-1"
            >
              Текущая сессия:
              <span class="font-mono">{{ projectStore.formatTime(timer.elapsed) }}</span>
            </div>
            <div class="total-time text-base font-medium">
              Всего:
              <span class="font-mono text-primary-600">{{
                projectStore.formatTime(
                  timer.total + (timer.isRunning ? timer.elapsed : 0)
                )
              }}</span>
            </div>
          </div>
        </div>
        <!-- Название задачи -->
        <div class="grid grid-cols-4 items-center gap-4">
          <label for="title" class="text-right">Название</label>
          <Input id="title" v-model="selectedTask.title" class="col-span-3" />
        </div>

        <!-- Описание -->
        <div class="grid grid-cols-4 items-center gap-4">
          <label for="description" class="text-right">Описание</label>
          <Textarea
            id="description"
            v-model="selectedTask.description"
            class="col-span-3"
            rows="4"
          />
        </div>

        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="font-medium">Отчёт</h4>
            <Dialog v-model:open="isReportDialogOpen">
              <DialogTrigger as-child>
                <Button variant="outline" size="sm">
                  {{
                    selectedTask.report ? "Редактировать" : "Добавить"
                  }}
                  отчёт
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle
                    >{{
                      selectedTask.report ? "Редактирование" : "Создание"
                    }}
                    отчёта</DialogTitle
                  >
                </DialogHeader>
                <div class="grid gap-4 py-4">
                  <Textarea
                    v-model="reportData.comment"
                    placeholder="Комментарий к отчёту"
                    rows="3"
                  />
                  <div>
                    <label class="block mb-2 text-sm font-medium"
                      >Изображение</label
                    >
                    <input
                      type="file"
                      accept="image/*"
                      @change="handleImageUpload"
                      class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
                    />
                  </div>
                  <div>
                    <label class="block mb-2 text-sm font-medium">Файл</label>
                    <input
                      type="file"
                      @change="handleFileUpload"
                      class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
                    />
                  </div>
                  <Button @click="submitReport" class="mt-2">
                    Сохранить отчёт
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          <div v-if="selectedTask.report" class="rounded border p-3 text-sm">
            <p>{{ selectedTask.report.comment }}</p>
            <div v-if="selectedTask.report.image" class="mt-2">
              <img
                :src="selectedTask.report.image"
                alt="Изображение отчёта"
                class="max-h-40 rounded"
              />
            </div>
            <div v-if="selectedTask.report.file" class="mt-2">
              <a
                :href="selectedTask.report.file"
                target="_blank"
                class="text-primary underline flex items-center gap-2"
              >
                <Icon name="lucide:file" class="h-4 w-4" />
                Скачать прикреплённый файл
              </a>
            </div>
          </div>
          <p v-else class="text-sm text-muted-foreground">
            Отчёт не добавлен
          </p>
        </div>

        <!-- Блок комментариев -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="font-medium">Комментарии</h4>
            <Dialog v-model:open="isCommentDialogOpen">
              <DialogTrigger as-child>
                <Button variant="outline" size="sm">
                  Добавить комментарий
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Добавление комментария</DialogTitle>
                </DialogHeader>
                <div class="grid gap-4 py-4">
                  <Textarea
                    v-model="newComment.content"
                    placeholder="Введите ваш комментарий"
                    rows="3"
                  />

                  <!-- Чекбокс для "Принятой задачи" -->
                  <div class="flex items-center gap-2">
                    <Checkbox
                      v-model="newComment.is_approved"
                      id="isApproved"
                      class="text-green-500"
                    />
                    <label
                      for="isApproved"
                      class="text-sm text-muted-foreground"
                      >Задача одобрена</label
                    >
                  </div>

                  <Button @click="addComment"> Отправить </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          <div v-if="selectedTask.comments?.length" class="space-y-2">
            <div
              v-for="comment in selectedTask.comments"
              :key="comment.id"
              class="rounded border p-3 text-sm"
            >
              <div class="flex items-center gap-2 mb-1">
                <span class="font-medium">{{ comment.author.username }}</span>
                <Icon
                  v-if="comment.is_approved === true"
                  name="lucide:check-circle"
                  mode="svg"
                  class="size-4 text-green-500"
                />
                <Icon
                  v-else-if="comment.is_approved === false"
                  name="lucide:x-circle"
                  mode="svg"
                  class="size-4 text-red-500"
                />
                <span class="text-muted-foreground text-xs">
                  {{
                    format(new Date(comment.created_at), "dd.MM.yyyy HH:mm")
                  }}
                </span>
              </div>
              <p>{{ comment.content }}</p>
            </div>
          </div>
          <p v-else class="text-sm text-muted-foreground">
            Комментариев пока нет
          </p>
        </div>

        <div class="grid grid-cols-4 items-center gap-4">
          <label class="text-right">Теги</label>
          <Combobox
            v-model="selectedTags"
            multiple
            by="id"
            class="col-span-3"
          >
            <ComboboxAnchor as-child>
              <ComboboxTrigger as-child>
                <Button variant="outline" class="w-full justify-between">
                  {{
                    selectedTags?.length
                      ? selectedTags.map((t) => t.name).join(", ")
                      : "Выберите теги"
                  }}
                  <Icon
                    name="lucide:chevrons-up-down"
                    class="ml-2 h-4 w-4 opacity-50"
                  />
                </Button>
              </ComboboxTrigger>
            </ComboboxAnchor>

            <ComboboxList>
              <div class="relative w-full max-w-sm items-center">
                <ComboboxInput
                  class="pl-9 focus-visible:ring-0 border-0 border-b rounded-none h-10"
                  placeholder="Выберите участников..."
                />
                <span
                  class="absolute start-0 inset-y-0 flex items-center justify-center px-3"
                >
                  <Icon
                    name="lucide:search"
                    class="size-4 text-muted-foreground"
                  />
                </span>
              </div>

              <ComboboxEmpty> Не найдено участников. </ComboboxEmpty>

              <ComboboxGroup>
                <ComboboxItem v-for="tag in tags" :key="tag.id" :value="tag">
                  <Icon name="lucide:user" class="size-4 mr-2" />
                  {{ tag.name }}

                  <ComboboxItemIndicator>
                    <Icon name="lucide:check" class="ml-auto h-4 w-4'" />
                  </ComboboxItemIndicator>
                </ComboboxItem>
              </ComboboxGroup>
            </ComboboxList>
          </Combobox>
        </div>

        <div class="grid grid-cols-4 items-center gap-4">
          <label class="text-right">Приоритет</label>
          <Combobox v-model="selectedPriority" by="id" class="col-span-3">
            <ComboboxAnchor as-child>
              <ComboboxTrigger as-child>
                <Button variant="outline" class="w-full justify-between">
                  {{ selectedPriority?.name || "Укажите приоритет" }}
                  <Icon
                    name="lucide:chevrons-up-down"
                    class="ml-2 h-4 w-4 opacity-50"
                  />
                </Button>
              </ComboboxTrigger>
            </ComboboxAnchor>

            <ComboboxList>
              <div class="relative w-full max-w-sm items-center">
                <ComboboxInput
                  class="pl-9 focus-visible:ring-0 border-0 border-b rounded-none h-10"
                  placeholder="Выберите участников..."
                />
                <span
                  class="absolute start-0 inset-y-0 flex items-center justify-center px-3"
                >
                  <Icon
                    name="lucide:search"
                    class="size-4 text-muted-foreground"
                  />
                </span>
              </div>

              <ComboboxEmpty>Приоритетов не найдено</ComboboxEmpty>

              <ComboboxGroup>
                <ComboboxItem
                  v-for="priority in priorities"
                  :key="priority.id"
                  :value="priority"
                >
                  <Icon name="lucide:user" class="size-4 mr-2" />
                  {{ priority.name }}
                  <ComboboxItemIndicator>
                    <Icon name="lucide:check" class="ml-auto h-4 w-4" />
                  </ComboboxItemIndicator>
                </ComboboxItem>
              </ComboboxGroup>
            </ComboboxList>
          </Combobox>
        </div>

        <div class="grid grid-cols-4 items-center gap-4">
          <label class="text-right">Назначено</label>
          <Combobox v-model="selectedMember" by="id" class="col-span-3">
            <ComboboxAnchor as-child>
              <ComboboxTrigger as-child>
                <Button variant="outline" class="w-full justify-between">
                  {{ selectedMember?.username || "Выберите участника" }}
                  <Icon
                    name="lucide:chevrons-up-down"
                    class="ml-2 h-4 w-4 opacity-50"
                  />
                </Button>
              </ComboboxTrigger>
            </ComboboxAnchor>

            <ComboboxList>
              <div class="relative w-full max-w-sm items-center">
                <ComboboxInput
                  class="pl-9 focus-visible:ring-0 border-0 border-b rounded-none h-10"
                  placeholder="Выберите участников..."
                />
                <span
                  class="absolute start-0 inset-y-0 flex items-center justify-center px-3"
                >
                  <Icon
                    name="lucide:search"
                    class="size-4 text-muted-foreground"
                  />
                </span>
              </div>

              <ComboboxEmpty>Участник не найден</ComboboxEmpty>

              <ComboboxGroup>
                <ComboboxItem
                  v-for="member in members"
                  :key="member.id"
                  :value="member"
                >
                  <Icon name="lucide:user" class="size-4 mr-2" />
                  {{ member.username }}
                  <ComboboxItemIndicator>
                    <Icon name="lucide:check" class="ml-auto h-4 w-4" />
                  </ComboboxItemIndicator>
                </ComboboxItem>
              </ComboboxGroup>
            </ComboboxList>
          </Combobox>
        </div>

        <!-- Срок выполнения -->
        <div class="grid grid-cols-4 items-center gap-4">
          <label for="due_date" class="text-right">Срок выполнения</label>
          <Popover>
            <PopoverTrigger as-child>
              <Button
                variant="outline"
                class="col-span-3 justify-start text-left font-normal"
              >
                <Icon name="lucide:calendar" class="mr-2 h-4 w-4" />
                {{
                  selectedTask.due_date
                    ? format(new Date(selectedTask.due_date), "dd.MM.yyyy")
                    : "Выберите дату"
                }}
              </Button>
            </PopoverTrigger>
            <PopoverContent class="w-auto p-0">
              <Calendar v-model="calendarDate" mode="single" initial-focus />
            </PopoverContent>
          </Popover>
        </div>

        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="font-medium">Подзадачи</h4>
            <div class="flex gap-2">
              <Input
                v-model="newSubtaskTitle"
                placeholder="Новая подзадача"
                class="w-[200px]"
                @keyup.enter="addSubtask"
              />
              <Button
                size="sm"
                :disabled="!newSubtaskTitle.trim() || isAddingSubtask"
                @click="addSubtask"
              >
                <Icon
                  :name="
                    isAddingSubtask ? 'svg-spinners:180-ring' : 'lucide:plus'
                  "
                  class="h-4 w-4"
                />
              </Button>
            </div>
          </div>

          <div v-if="selectedTask.subtasks?.length" class="space-y-2">
            <div
              v-for="subtask in selectedTask.subtasks"
              :key="subtask.id"
              class="flex items-center gap-3 rounded border p-3 text-sm"
              @dblclick="currentSubtask = { ...subtask }"
            >
              <Checkbox
                v-model="subtask.is_completed"
                @click.stop="toggleSubtaskCompletion(subtask, $event)"
                class="pointer-events-auto"
              />

              <div class="flex-1">
                <Input
                  v-if="currentSubtask?.id === subtask.id"
                  v-model="currentSubtask.title"
                  @keyup.enter="updateSubtask"
                  @blur="updateSubtask"
                  @click.stop
                />
                <span
                  v-else
                  :class="{
                    'line-through text-muted-foreground':
                      subtask.is_completed,
                  }"
                >
                  {{ subtask.title }}
                </span>
              </div>

              <Button
                variant="ghost"
                size="sm"
                @click.stop="deleteSubtask(subtask.id)"
              >
                <Icon
                  name="lucide:trash-2"
                  class="h-4 w-4 text-destructive"
                />
              </Button>
            </div>
          </div>
          <p v-else class="text-sm text-muted-foreground">
            Подзадач пока нет
          </p>
        </div>

        <!-- Кнопки сохранения/отмены -->
        <div class="flex justify-end gap-2 mt-6">
          <Button variant="outline" @click="isTaskSheetOpen = false">
            Отмена
          </Button>
          <Button @click="updateTask"> Сохранить </Button>
        </div>
      </div>
    </SheetContent>
  </Sheet>
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