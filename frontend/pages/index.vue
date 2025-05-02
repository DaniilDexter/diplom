<script setup lang="ts">

const userStore = useUserStore()

const {user} =storeToRefs(userStore)

const features = [
  {
    title: "Ориентированность на веб-разработку",
    description: "Специальные шаблоны и интеграции для разработчиков",
    icon: "lucide:code-2",
  },
  {
    title: "Аналитика работы команды",
    description: "Подробные отчеты и метрики продуктивности",
    icon: "lucide:bar-chart-4",
  },
  {
    title: "Электронные уведомления",
    description: "Своевременные оповещения о новых задачах",
    icon: "lucide:mail",
  },
  {
    title: "Командная работа",
    description: "Удобное взаимодействие между участниками проекта",
    icon: "lucide:users",
  },
];
</script>

<template>
  <main class="container mx-auto px-4 py-12">
    <!-- Hero секция -->
    <section
      class="mb-16 text-center relative overflow-hidden py-20 rounded-xl bg-gradient-to-br from-sky-50 to-white dark:from-sky-900/30 dark:to-gray-900"
    >
      <!-- Фоновые элементы -->
      <div class="absolute inset-0 opacity-10 dark:opacity-20">
        <div
          class="absolute top-20 left-20 w-32 h-32 rounded-full bg-sky-300 blur-3xl"
        ></div>
        <div
          class="absolute bottom-10 right-20 w-40 h-40 rounded-full bg-sky-200 blur-3xl"
        ></div>
      </div>

      <div class="relative z-10">
        <h1
          class="text-4xl font-bold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-sky-500 to-sky-600 dark:from-sky-400 dark:to-sky-300"
        >
          Ваш современный таск-менеджер
        </h1>
        <p class="text-lg text-muted-foreground max-w-2xl mx-auto">
          Оптимизируйте процессы веб-разработки
          <Icon
            name="lucide:arrow-right"
            class="size-5 inline ml-1 text-sky-500 animate-pulse"
          />
        </p>

        <Button size="lg" class="mt-8 group">
          Начать работу
          <Icon
            name="lucide:sparkles"
            class="size-4 ml-2 text-sky-300 group-hover:text-white transition-colors"
          />
        </Button>
      </div>
    </section>

    <!-- Преимущества -->
    <section class="mb-16">
      <h2 class="text-2xl font-semibold mb-8 text-center">Наши преимущества</h2>

      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card
          v-for="feature in features"
          :key="feature.title"
          class="group hover:border-sky-300 transition-colors hover:shadow-lg dark:hover:shadow-sky-900/30"
        >
          <CardHeader class="pb-2">
            <div class="p-2 rounded-lg bg-sky-50 dark:bg-sky-900/20 w-fit">
              <Icon
                :name="feature.icon"
                class="w-6 h-6 text-sky-500 group-hover:text-sky-600 dark:text-sky-400 dark:group-hover:text-sky-300 transition-colors"
              />
            </div>
            <CardTitle
              class="group-hover:text-sky-600 dark:group-hover:text-sky-400 transition-colors"
            >
              {{ feature.title }}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p class="text-sm text-muted-foreground">
              {{ feature.description }}
            </p>
          </CardContent>
        </Card>
      </div>
    </section>

    <!-- Как это работает (табы) -->
    <section class="mb-16">
      <h2 class="text-2xl font-semibold mb-8 text-center">Как это работает</h2>

      <Tabs default-value="web" class="max-w-3xl mx-auto">
        <TabsList class="grid w-full grid-cols-3 bg-sky-50 dark:bg-sky-900/10 p-1 rounded-lg">
          <TabsTrigger 
            value="web"
            class="data-[state=active]:bg-sky-500 data-[state=active]:text-white data-[state=active]:shadow-sm"
          >
            <Icon name="lucide:code" class="size-4 mr-2" />
            Веб-разработка
          </TabsTrigger>
          <TabsTrigger 
            value="analytics"
            class="data-[state=active]:bg-green-500 data-[state=active]:text-white data-[state=active]:shadow-sm"
          >
            <Icon name="lucide:pie-chart" class="size-4 mr-2" />
            Аналитика
          </TabsTrigger>
          <TabsTrigger 
            value="notifications"
            class="data-[state=active]:bg-yellow-500 data-[state=active]:text-white data-[state=active]:shadow-sm"
          >
            <Icon name="lucide:bell" class="size-4 mr-2" />
            Уведомления
          </TabsTrigger>
        </TabsList>
        
        <!-- Веб-разработка -->
        <TabsContent value="web">
          <Card class="border-sky-100 dark:border-sky-900/50">
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Icon name="lucide:code" class="size-5 text-sky-500" />
                Интеграция с инструментами разработки
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <p class="text-muted-foreground">
                Специальные шаблоны задач для фронтенд и бэкенд разработки.
              </p>
              <ul class="space-y-2 text-sm">
                <li class="flex items-center gap-2">
                  <Icon name="lucide:check-circle" class="size-4 text-sky-500" />
                  Интеграция с Git и GitHub
                </li>
                <li class="flex items-center gap-2">
                  <Icon name="lucide:check-circle" class="size-4 text-sky-500" />
                  Поддержка CI/CD пайплайнов
                </li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- Аналитика -->
        <TabsContent value="analytics">
          <Card class="border-green-100 dark:border-green-900/50">
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Icon name="lucide:pie-chart" class="size-5 text-green-500" />
                Подробная аналитика работы команды
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <p class="text-muted-foreground">
                Визуализация данных, мониторинг производительности и анализ эффективности.
              </p>
              <ul class="space-y-2 text-sm">
                <li class="flex items-center gap-2">
                  <Icon name="lucide:check-circle" class="size-4 text-green-500" />
                  Диаграммы прогресса по проектам
                </li>
                <li class="flex items-center gap-2">
                  <Icon name="lucide:check-circle" class="size-4 text-green-500" />
                  Оценка загруженности разработчиков
                </li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <!-- Уведомления -->
        <TabsContent value="notifications">
          <Card class="border-yellow-100 dark:border-yellow-900/50">
            <CardHeader>
              <CardTitle class="flex items-center gap-2">
                <Icon name="lucide:bell" class="size-5 text-yellow-500" />
                Своевременные уведомления
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <p class="text-muted-foreground">
                Мгновенные оповещения о важных изменениях в проекте.
              </p>
              <ul class="space-y-2 text-sm">
                <li class="flex items-center gap-2">
                  <Icon name="lucide:check-circle" class="size-4 text-yellow-500" />
                  Push-уведомления о новых задачах
                </li>
                <li class="flex items-center gap-2">
                  <Icon name="lucide:check-circle" class="size-4 text-yellow-500" />
                  Напоминания о дедлайнах
                </li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

    </section>

    <!-- CTA секция -->
    <section class="text-center relative py-16 rounded-xl overflow-hidden">
      <!-- Фоновые элементы -->
      <div
        class="absolute inset-0 bg-gradient-to-br from-sky-50 to-white dark:from-sky-900/10 dark:to-gray-900 -z-10"
      ></div>
      <div
        class="absolute -bottom-20 -right-20 w-64 h-64 rounded-full bg-sky-200 blur-3xl opacity-30 dark:opacity-20 -z-10"
      ></div>

      <div class="relative z-10">
        <h2 class="text-2xl font-semibold mb-4">Готовы попробовать?</h2>
        <p class="text-muted-foreground mb-6 max-w-2xl mx-auto">
          Начните использовать наш таск-менеджер уже сегодня
        </p>
        <Button
          size="lg"
          class="bg-sky-600 hover:bg-sky-700 shadow-lg shadow-sky-500/20"
        >
          Начать бесплатно
          <Icon name="lucide:rocket" class="size-4 ml-2 animate-bounce" />
        </Button>

        <div
          class="mt-4 text-xs text-sky-500 dark:text-sky-400 flex items-center justify-center gap-2"
        >
          <Icon name="lucide:zap" class="size-3" />
          Без кредитной карты • 14 дней бесплатно
        </div>
      </div>
    </section>
  </main>
</template>
