<script setup lang="ts">
import { useSidebar } from '@/components/ui/sidebar'

const { isMobile } = useSidebar()

const userStore = useUserStore()

const {user} =storeToRefs(userStore)

const avatarText = computed<string>(() => {
  return user.value?.username?.[0] || ''
})
</script>

<template>
  <SidebarMenu>
  <SidebarMenuItem>
    <DropdownMenu>
      <DropdownMenuTrigger as-child>
        <SidebarMenuButton size="lg" class="sidebar-footer data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground">
          <Avatar class="avatar size-8 rounded-md bg-neutral-200">
            <AvatarFallback class="avatar-fallback rounded-md font-medium text-neutral-950">
              {{ avatarText }}
            </AvatarFallback>
          </Avatar>
          <Icon name="lucide:chevrons-up-down" mode="svg" class="ml-auto size-4" />
        </SidebarMenuButton>
      </DropdownMenuTrigger>
        <DropdownMenuContent
          class="w-[--reka-dropdown-menu-trigger-width] min-w-56 rounded-lg"
          :side="isMobile ? 'bottom' : 'right'"
          align="end"
          :side-offset="4"
        >
          <DropdownMenuLabel class="p-0 font-normal">
            <div class="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
              <Avatar class="size-9 rounded-md">
                <AvatarFallback class="rounded-md font-medium text-neutral-950">
                  {{ avatarText }}
                </AvatarFallback>
              </Avatar>
              <div class="grid flex-1 text-left text-sm leading-tight">
                <span class="truncate font-medium text-neutral-950">
                  {{ user?.username || 'Гость' }} <!-- Если user отсутствует, покажем "Гость" -->
                </span>
              </div>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem class="dropdown-item" as-child>
              <NuxtLink to="#">
                <Icon name="lucide:shopping-bag" mode="svg" class="size-4" />
                {{ 'components.sidebar.footer.shop' }}
                <Icon name="lucide:arrow-up-right" mode="svg" class="absolute right-2 size-4" />
              </NuxtLink>
            </DropdownMenuItem>
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuItem class="dropdown-item">
            <Icon name="lucide:log-out" mode="svg" class="size-4" />
            {{ 'components.sidebar.footer.logOut' }}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  </SidebarMenu>
</template>
