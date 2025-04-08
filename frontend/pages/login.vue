<script setup lang="ts">
import { ref } from 'vue';
import { useApi } from '@/composables/useApi';
import { vAutoAnimate } from '@formkit/auto-animate/vue'


const user = ref({
  email: '',
  password: '',
});

const regist = ref({
  email: '',
  username: '',
  password: '',
});

// Убедитесь, что запросы выполняются только по запросу
const { data: loginData, error: loginError, execute: executeLogin } = useApi('/auth/login/', {
  method: 'POST',
  body: user.value,
  watch: false,
  immediate: false,  // Запрос не выполняется автоматически
});

const { data: registerData, error: registerError, execute: executeRegister } = useApi('/auth/register/', {
  method: 'POST',
  body: regist.value,
  watch: false,
  immediate: false,  // Запрос не выполняется автоматически
});

// Функция для логина
async function login() {
  try {
    console.log('Запрос на логин');
    await executeLogin();  // Запрос выполняется только при вызове этой функции
    if (loginData.value?.access) {
      const authT = useCookie('authT', { maxAge: 60 * 60 * 24 * 7, sameSite: 'strict', secure: true });
      authT.value = loginData.value.access;
      navigateTo('/');
    }
  } catch (error) {
    console.error('Ошибка входа:', error);
  }
}

// Функция для регистрации
async function register() {
  try {
    console.log('Запрос на регистрацию');
    await executeRegister();  // Запрос выполняется только при вызове этой функции
    if (registerData.value?.access) {
      const authT = useCookie('authT', { maxAge: 60 * 60 * 24 * 7, sameSite: 'strict', secure: true });
      authT.value = registerData.value.access;
      navigateTo('/');
    }
  } catch (error) {
    console.error('Ошибка регистрации:', error);
  }
}
</script>

<template>
  <div v-auto-animate class="max-w-md mx-auto p-6 bg-white dark:bg-gray-900 rounded-lg shadow-md">
    <Tabs default-value="login" class="w-full">
      <TabsList class="grid w-full grid-cols-2 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
        <TabsTrigger value="login" class="data-[state=active]:bg-sky-500 data-[state=active]:text-white">Вход</TabsTrigger>
        <TabsTrigger value="register" class="data-[state=active]:bg-sky-500 data-[state=active]:text-white">Регистрация</TabsTrigger>
      </TabsList>
      
      <TabsContent value="login">
        <form @submit.prevent="login" class="space-y-4 mt-4">
          <Label>Email</Label>
          <Input v-model="user.email" type="email" placeholder="Введите email" required />
          
          <Label>Пароль</Label>
          <Input v-model="user.password" type="password" placeholder="Введите пароль" required />
          
          <Button type="submit" class="w-full bg-sky-500 hover:bg-sky-600">Войти</Button>
          <p v-if="loginError" class="text-red-500 text-sm">
            Ошибка: {{ loginError?.data?.error }}
          </p>
        </form>
      </TabsContent>
      
      <TabsContent value="register">
        <form @submit.prevent="register" class="space-y-4 mt-4">
          <Label>Email</Label>
          <Input v-model="regist.email" type="email" placeholder="Введите email" required />
          
          <Label>Имя пользователя</Label>
          <Input v-model="regist.username" type="text" placeholder="Введите имя пользователя" required />
          
          <Label>Пароль</Label>
          <Input v-model="regist.password" type="password" placeholder="Введите пароль" required />
          
          <Button type="submit" class="w-full bg-sky-500 hover:bg-sky-600">Зарегистрироваться</Button>
          <p v-if="registerError" class="text-red-500 text-sm">Ошибка: {{ registerError }}</p>
        </form>
      </TabsContent>
    </Tabs>
  </div>
</template>
