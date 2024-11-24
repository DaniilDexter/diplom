<template>
  <main class="main">
    <div class="auth-container">
      <div class="form-container">
        <form @submit.prevent="login" class="form">
          <h2>Login</h2>
          <input v-model="user.email" type="text" placeholder="Email" required />
          <input v-model="user.password" type="password" placeholder="Пароль" required />
          <button type="submit">Login</button>
        </form>
      </div>
      <div class="form-container">
        <form @submit.prevent="reg" class="form">
          <h2>Register</h2>
          <input v-model="regist.username" type="text" placeholder="Имя пользователя" required />
          <input v-model="regist.email" type="email" placeholder="Email" required />
          <input v-model="regist.password" type="password" placeholder="Пароль" required />
          <button type="submit">Register</button>
        </form>
      </div>
      <div
        :class="[
          'switch-block',
          isLoginActive ? 'switch-left' : 'switch-right',
        ]"
      >
        <div class="switch-content">
          <h2>{{ switchText }}</h2>
          <button @click="toggleForms">Switch</button>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import { PATHS } from "../constants";

export default {
  name: "AuthPage",

  data() {
    return {
      user: {
        email: "",
        password: "",
      },
      regist: {
        email: "",
        username: "",
        password: "",
      },
      tryCount: 0,
      isBlocked: false,
      leftTime: 10,
      isLoginActive: true,
    };
  },
  computed: {
    error() {
      return this.$store.getters.error;
    },
    switchText() {
      return this.isLoginActive ? "Already have an account? Login" : "Don't have an account? Register";
    },
  },
  methods: {
    login() {
      const self = this;

      self.$store.dispatch("auth/login", this.user).then(() => {
        self.$router.push(PATHS.HOME);
      });
    },

    reg() {
      const self = this;

      self.$store.dispatch("auth/register", this.regist).then(() => {
        self.$router.push(PATHS.HOME);
      });
    },

    toggleForms() {
      this.isLoginActive = !this.isLoginActive;
    },
  },
};
</script>

<style scoped lang="scss">

.main{
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.auth-container {
  position: relative;
  width: 800px;
  height: 400px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  display: flex;
}

.form-container {
  width: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.form {
  width: 80%;
  text-align: center;
}

input {
  margin: 10px 0;
  padding: 10px;
  width: 100%;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  margin-top: 10px;
  padding: 10px;
  width: 100%;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.3s;

  &:hover {
    background-color: #0056b3;
  }
}

.switch-block {
  position: absolute;
  top: 0;
  width: 50%;
  height: 100%;
  background-color: #007bff;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 0.6s ease-in-out;
  z-index: 2;
}

.switch-content {
  text-align: center;
  color: white;
}

.switch-content h2 {
  margin-bottom: 20px;
  font-weight: normal;
}

.switch-block button {
  background-color: white;
  color: #007bff;
  font-weight: bold;
  border-radius: 5px;
}

.switch-left {
  transform: translateX(0);
}

.switch-right {
  transform: translateX(100%);
}
</style>