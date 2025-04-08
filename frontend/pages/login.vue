<script setup lang="ts">

const user = ref({
  email: '',
  password: '',
})

const regist = ref({
  email: '',
  username: '',
  password: '',
})

const isLoginActive = ref(true)

const { data: loginData, error: loginError, execute: executeLogin } = useApi('/auth/login/', {
  method: 'POST',
  body: user.value,
  immediate: false
})

const { data: registerData, error: registerError, execute: executeRegister } = useApi('/auth/register/', {
  method: 'POST',
  body: regist.value,
  immediate: false
})

function login() {
  executeLogin().then(() => {
    if (loginData.value && loginData.value.access) {
      // Сохраняем access-токен в куки
      const authT = useCookie('authT', {
        maxAge: 60 * 60 * 24 * 7, // 7 дней (можно настроить под ваш токен)
        sameSite: 'strict',
        secure: true // если используете HTTPS
      })
      authT.value = loginData.value.access
      
      console.log('Токен сохранен:', authT.value)
      console.log('Данные пользователя:', loginData.value.data)
      
      // Перенаправляем пользователя
      navigateTo('/')
    }
  }).catch((error) => {
    console.error('Ошибка входа:', error)
    // Можно показать ошибку пользователю
  })
}

function register() {
  executeRegister().then(() => {
    if (registerData.value && registerData.value.access) {
      // Сохраняем access-токен в куки
      const authT = useCookie('authT', {
        maxAge: 60 * 60 * 24 * 7, // 7 дней (можно настроить под ваш токен)
        sameSite: 'strict',
        secure: true // если используете HTTPS
      })
      authT.value = registerData.value.access
      
      console.log('Токен сохранен:', authT.value)
      console.log('Данные пользователя:', registerData.value.data)
      
      // Перенаправляем пользователя
      navigateTo('/')
    }
  }).catch((error) => {
    console.error('Ошибка входа:', error)
    // Можно показать ошибку пользователю
  })
}

function toggleForms() {
  isLoginActive.value = !isLoginActive.value
}
</script>

<template>
  <main class="main">
    <div class="auth-container">
      <!-- Форма логина -->
      <div v-if="isLoginActive" class="form-container">
        <form @submit.prevent="login" class="form">
          <h2>Login</h2>
          <input v-model="user.email" type="text" placeholder="Email" required />
          <input v-model="user.password" type="password" placeholder="Пароль" required />
          <button type="submit">Login</button>
        </form>
      </div>
      
      <!-- Форма регистрации -->
      <div v-if="!isLoginActive" class="form-container">
        <form @submit.prevent="register" class="form">
          <h2>Register</h2>
          <input v-model="regist.username" type="text" placeholder="Имя пользователя" required />
          <input v-model="regist.email" type="email" placeholder="Email" required />
          <input v-model="regist.password" type="password" placeholder="Пароль" required />
          <button type="submit">Register</button>
        </form>
      </div>
      
      <!-- Переключение между формами -->
      <div
        :class="['switch-block', isLoginActive ? 'switch-left' : 'switch-right']"
      >
        <div class="switch-content">
          <h2>{{ isLoginActive ? 'Already have an account? Login' : "Don't have an account? Register" }}</h2>
          <button @click="toggleForms">Switch</button>
        </div>
      </div>
    </div>
  </main>
</template>



<style scoped>
.error {
  color: red;
  margin-top: 10px;
}
</style>