<script setup lang="ts">
import { NConfigProvider, NDialogProvider, NGlobalStyle, NMessageProvider, zhCN, dateZhCN } from 'naive-ui'
import RequestFeedback from './components/common/RequestFeedback.vue'
import AppHeader from './components/layout/AppHeader.vue'
import { theme } from './theme'
</script>

<template>
  <NConfigProvider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="theme">
    <NGlobalStyle />
    <NMessageProvider>
      <NDialogProvider><RequestFeedback><AppHeader /><RouterView :key="$route.path" /></RequestFeedback></NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>
