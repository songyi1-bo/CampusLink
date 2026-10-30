<script setup lang="ts">
import { NButton } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import QuestList from './QuestList.vue'
</script>
<template><AppContainer><main class="quest-page"><PageHeader title="我的悬赏" description="查看发布与接取的任务，跟进每一次校园互助。" /><div class="quest-actions"><RouterLink to="/quest"><NButton>悬赏大厅</NButton></RouterLink><RouterLink to="/quest/new"><NButton type="primary">发布悬赏</NButton></RouterLink></div><QuestList mine /></main></AppContainer></template>
