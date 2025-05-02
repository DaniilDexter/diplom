<script setup lang="ts">
import { SIDEBAR_COOKIE_NAME } from '@/components/ui/sidebar/utils'
import { useBreadcrumbs } from '@/composables/useBreadcrumbs'

const { breadcrumbs } = useBreadcrumbs()

const userStore = useUserStore()

await userStore.fetchUser()

const sidebarState = useCookie<boolean>(SIDEBAR_COOKIE_NAME)

</script>

<template>
  <div>
    <SidebarProvider :default-open="sidebarState">
      <SidebarCustom />
      <SidebarInset>
        <header
          class="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12"
        >
          <div class="flex items-center gap-2 px-4">
            <SidebarTrigger class="-ml-1" />
            <Separator orientation="vertical" class="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem v-for="(crumb, index) in breadcrumbs" :key="index" as-child>
                  <BreadcrumbLink 
                    v-if="crumb.href"
                    class="hover:text-primary"
                  >
                    <NuxtLink :to="crumb.href">
                      {{ crumb.title }}
                    </NuxtLink>
                  </BreadcrumbLink>
                  <BreadcrumbPage v-else>
                    {{ crumb.title }}
                  </BreadcrumbPage>
                  <BreadcrumbSeparator v-if="index < breadcrumbs.length - 1" />
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div class="mx-auto flex min-h-[calc(100vh-64px)] w-full flex-col px-4 pb-4">
          <slot />
        </div>
      </SidebarInset>
    </SidebarProvider>
  </div>
</template>
