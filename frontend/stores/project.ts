import { toast } from "vue-sonner";


export const useProjectStore = defineStore(
  'Project',
  () => {
    
    const projects = ref(null)
    const currentProject = ref(null)
    const currentBoard = ref(null)
    const isLoading = ref(false)
    const error = ref(null)

    const isTaskSheetOpen = ref(false);
    const selectedTask = ref<any | null>(null);

    const timer = reactive({
      isRunning: false,
      startTime: null as Date | null,
      elapsed: 0,
      total: 0,
      currentTaskId: null as number | null,
      intervalId: null as NodeJS.Timeout | null
    });

    watch(
      () => selectedTask.value?.id,
      (newTaskId, oldTaskId) => {
        if (newTaskId !== oldTaskId) {
          resetTimer();
          
          // Восстанавливаем время если открыли ту же задачу
          if (selectedTask.value?.time) {
            const [h, m, s] = selectedTask.value.time.split(":").map(Number);
            timer.total = h * 3600 + m * 60 + s;
          }
        }
      }
    );
    
    // 2. Упрощаем метод openTaskEditor
    const openTaskEditor = (task: any) => {
      if (timer.isRunning && task.id !== timer.currentTaskId) {
        toast("Невозможно открыть другую задачу", {
          description: "Пожалуйста, остановите таймер перед открытием другой задачи.",
        });
        return;
      }
    
      selectedTask.value = {
        ...task,
        due_date: task.due_date ? new Date(task.due_date) : null
      };
      isTaskSheetOpen.value = true;
      
    };
  
    // 1. Computed URL для таймера
    const timerApiUrl = computed(() => 
      selectedTask.value ? `/task/${selectedTask.value.id}/track-time/` : null
    );

    // 2. API клиент для таймера (без body)
    const timerApi = useApi(timerApiUrl, {
      method: "POST",
      watch: false,
      immediate: false
    });

    // 4. Основные методы
    const toggleTimer = async () => {
      if (!selectedTask.value) return;
      
      clearTimerInterval();
      
      try {
        await timerApi.execute();
        const status = timerApi.data.value?.status;
        
        if (status === "timer_started") {
          startTimer();
        } else if (status === "timer_stopped") {
          stopTimer(timerApi.data.value?.total_time);
        }
      } catch (error) {
        console.error("Ошибка таймера:", error);
        toast.error("Ошибка управления таймером");
      }
    };

    const startTimer = () => {
      timer.isRunning = true;
      timer.startTime = new Date();
      timer.currentTaskId = selectedTask.value?.id || null;
      timer.elapsed = 0;
      startTimerInterval();
    };

    const stopTimer = (totalTime?: string) => {
      timer.isRunning = false;
      if (totalTime) {
        const [h, m, s] = totalTime.split(":").map(Number);
        timer.total = h * 3600 + m * 60 + s;
      }
      updateSelectedTask();
    };

    const startTimerInterval = () => {
      timer.intervalId = setInterval(() => {
        if (timer.isRunning && timer.startTime) {
          timer.elapsed = Math.floor(
            (Date.now() - timer.startTime.getTime()) / 1000
          );
        }
      }, 1000);
    };

    const clearTimerInterval = () => {
      if (timer.intervalId) {
        clearInterval(timer.intervalId);
        timer.intervalId = null;
      }
    };

    const resetTimer = () => {
      clearTimerInterval();
      timer.isRunning = false;
      timer.startTime = null;
      timer.elapsed = 0;
      timer.total = 0;
      timer.currentTaskId = selectedTask.value?.id || null;
    };

    const formatTime = (totalSeconds: number) => {
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;
      return `${hours.toString().padStart(2, "0")}:${minutes
        .toString()
        .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
    };

    const userStore = useUserStore()
    
    const route = useRoute()
    const projectsApi = useApi('/project/', { method: "GET" })


    const updateCurrentProjectAndBoard = async () => {
      const projectId = route.params.id
      const boardId = route.params.boardID
      
      currentProject.value = projectId && projects.value 
        ? projects.value.find(p => p.id == projectId) || null
        : null
      
      currentBoard.value = boardId && currentProject.value?.boards
        ? currentProject.value.boards.find(b => b.id == boardId) || null
        : null
    }

    // 1. Добавляем computed URL и payload ref
    const getTaskApiUrl = computed(() => selectedTask.value ? `/task/${selectedTask.value.id}/` : null);

    // 2. Создаем API клиент
    const getTaskApi = useApi(getTaskApiUrl, {
      method: "GET",
      watch: false,
      immediate: false
    });

    // 3. Обновленная функция
    const updateSelectedTask = async () => {
      if (!selectedTask.value) return;

      try {
        await getTaskApi.execute();
        
        if (getTaskApi.data.value) {
          const updatedTask = {
            ...getTaskApi.data.value,
            due_date: getTaskApi.data.value.due_date ? new Date(getTaskApi.data.value.due_date) : null
          };
          
          selectedTask.value = updatedTask;
          updateTaskInStore(updatedTask);
        }
      } catch (error) {
        console.error("Ошибка при обновлении задачи:", error);
        toast.error("Не удалось обновить данные задачи");
      }
    };

    const fetchProjects = async () => {
      if (projects.value || isLoading.value) return
      
      isLoading.value = true
      error.value = null
      
      try {
        await projectsApi.execute()
        projects.value = projectsApi.data.value || []
        updateCurrentProjectAndBoard()
      } catch (e) {
        error.value = e as Error
        console.error('Ошибка загрузки проектов:', e)
      } finally {
        isLoading.value = false
      }
    }

    const resetProjects = () => {
      projects.value = null
      currentProject.value = null
      currentBoard.value = null
    }

    const updateTaskInStore = (updatedTask: any) => {
      if (!updatedTask?.id) return;
    
      // 1. Обновляем selectedTask если это текущая задача
      if (selectedTask.value?.id === updatedTask.id) {
        selectedTask.value = updatedTask;
      }
    
      // 2. Обновляем в основном массиве projects
      if (!projects.value) return;
    
      // Мутируем напрямую (Vue reactivity сделает свое дело)
      for (const project of projects.value) {
        for (const board of project.boards || []) {
          for (const column of board.columns || []) {
            const task = column.tasks?.find(t => t.id === updatedTask.id);
            if (task) {
              Object.assign(task, updatedTask);
              return; // Выходим после первого обновления
            }
          }
        }
      }
    };

    watch(
      () => userStore.user,
      (newUser) => {
        if (newUser) {
          resetProjects()
          fetchProjects()
        } else {
          resetProjects()
        }
      },
      { immediate: true }
    )

    watch(
      () => route.params.id,
      async (newId) => {
        if (!projects.value) {
          await fetchProjects()
        }
        updateCurrentProjectAndBoard()
      },
      { immediate: true }
    )

    watch(
      () => route.params.boardID,
      async (newId) => {
        if (!projects.value) {
          await fetchProjects()
        }
        updateCurrentProjectAndBoard()
      },
      { immediate: true }
    )

    return {
      projects,
      currentProject,
      currentBoard,
      isLoading,
      error,
      isTaskSheetOpen,
      selectedTask,
      timer,
      openTaskEditor,
      toggleTimer,
      formatTime,
      fetchProjects,
      updateTaskInStore,
      updateSelectedTask
    }
  }
)