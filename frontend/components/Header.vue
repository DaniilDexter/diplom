<script lang="ts" setup>
import { navigationMenuTriggerStyle } from '@/components/ui/navigation-menu'

</script>

<template>
  <header class="max-w-3xl w-full mx-auto my-2 border-[1px] rounded-3xl p-3 flex justify-between">
    <NuxtLink to="/">
        <img src="/logo.svg" class="h-12"/>
    </NuxtLink>
    <NavigationMenu>
      <NavigationMenuList>
        <NavigationMenuItem>
          <NuxtLink v-slot="{ isActive, href, navigate }" to="/login" custom>
            <NavigationMenuLink :active="isActive" :href :class="navigationMenuTriggerStyle()" @click="navigate">
              Login
            </NavigationMenuLink>
          </NuxtLink>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NuxtLink v-slot="{ isActive, href, navigate }" to="/about" custom>
            <NavigationMenuLink :active="isActive" :href :class="navigationMenuTriggerStyle()" @click="navigate">
              About
            </NavigationMenuLink>
          </NuxtLink>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NuxtLink v-slot="{ isActive, href, navigate }" to="/projects" custom>
            <NavigationMenuLink :active="isActive" :href :class="navigationMenuTriggerStyle()" @click="navigate">
              Projects
            </NavigationMenuLink>
          </NuxtLink>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>    
  </header>
</template>
