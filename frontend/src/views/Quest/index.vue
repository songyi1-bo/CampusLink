<script setup lang="ts">
import { NButton } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import QuestList from './QuestList.vue'
</script>
<template>
  <AppContainer><main class="quest-page"><PageHeader title="校园悬赏" description="把小事交给顺路的同学，把擅长变成一次互助。" />
    <div class="quest-actions"><RouterLink to="/quest/new"><NButton type="primary">发布悬赏</NButton></RouterLink><RouterLink to="/quest/mine"><NButton>我的悬赏</NButton></RouterLink></div>
    <QuestList />
  </main></AppContainer>
</template>
