<script setup lang="ts">
import { format, parseISO } from 'date-fns'

const props = defineProps<{
  createdAt: string | null
  startedAt: string | null
  assignedAt: string | null
  submittedAt: string | null
  completedAt: string | null
}>()

const steps = computed(() => [
  {
    step: 1,
    title: 'Создана',
    description: () =>
      props.createdAt ? format(parseISO(props.createdAt), 'dd.MM.yyyy HH:mm') : 'Ожидание одобрения',
    active: props.createdAt !== null,
  },
  {
    step: 2,
    title: 'Назначена',
    description: () =>
      props.assignedAt ? format(parseISO(props.assignedAt), 'dd.MM.yyyy HH:mm') : 'Ожидание назначения',
    active: props.assignedAt !== null,
  },
  {
    step: 3,
    title: 'Начата',
    description: () =>
      props.startedAt ? format(parseISO(props.startedAt), 'dd.MM.yyyy HH:mm') : 'Ожидание начала',
    active: props.startedAt !== null,
  },
  {
    step: 4,
    title: 'Отправлена',
    description: () =>
      props.submittedAt ? format(parseISO(props.submittedAt), 'dd.MM.yyyy HH:mm') : 'Ожидание отправки',
    active: props.submittedAt !== null,
  },
  {
    step: 5,
    title: 'Завершена',
    description: () =>
      props.completedAt ? format(parseISO(props.completedAt), 'dd.MM.yyyy HH:mm') : 'Не завершена',
    active: props.completedAt !== null,
  },
])

// Находим индекс последнего активного шага
const lastActiveIndex = computed(() => {
  return steps.value.reduce((acc, step, index) => 
    step.active ? index : acc, -1
  )
})
</script>

<template>
  <div class="flex w-full items-start gap-2">
    <div
      v-for="(step, index) in steps"
      :key="index"
      class="relative flex w-full flex-col items-center justify-center"
    >
      <!-- Круг с иконкой -->
      <div
        class="z-10 rounded-full shrink-0 flex items-center justify-center w-8 h-8 border"
        :class="step.active ? 'bg-primary text-white border-primary' : 'bg-background text-muted-foreground border-muted'"
      >
        <Icon
          v-if="step.active"
          name="lucide:check"
          class="w-4 h-4"
        />
        <Icon
          v-else
          name="lucide:dot"
          class="w-4 h-4"
        />
      </div>

      <!-- Описание шага -->
      <div class="mt-5 flex flex-col items-center text-center">
        <div class="text-sm font-semibold">
          {{ step.title }}
        </div>
        <div class="text-xs text-muted-foreground">
          {{ step.description() }}
        </div>
      </div>

      <!-- Разделитель между шагами -->
      <div
        v-if="index < steps.length - 1"
        class="absolute left-[calc(50%+20px)] right-[calc(-50%+10px)] top-5 block h-0.5 shrink-0 rounded-full"
        :class="index < lastActiveIndex ? 'bg-primary' : 'bg-muted'"
      />
    </div>
  </div>
</template>