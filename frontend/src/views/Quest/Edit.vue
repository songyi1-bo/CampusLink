<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NDatePicker, NForm, NFormItem, NInput, NInputNumber, NSelect, NSpin } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import { categories, contactOptions, questsApi } from './api'
import type { QuestWrite } from './api'
import './quest.css'
const route = useRoute(), router = useRouter()
const loading = ref(false), busy = ref(false), ready = ref(false), error = ref('')
const deadline = ref<number | null>(Date.now() + 86400000), reward = ref<number | null>(5)
const model = reactive<QuestWrite>({ title: '', description: '', category: 'delivery', location: '', reward: '5.00', deadline: '', contact_type: 'wechat', contact_value: '' })
let sequence = 0
watch(() => route.params.id, async () => {
  const current = ++sequence
  error.value = ''; ready.value = false; loading.value = true
  Object.assign(model, { title: '', description: '', category: 'delivery', location: '', contact_type: 'wechat', contact_value: '' })
  deadline.value = Date.now() + 86400000; reward.value = 5
  try {
    if (route.params.id) {
      const id = Number(route.params.id)
      const [task, relation] = await Promise.all([questsApi.detail(id), questsApi.relation(id)])
      if (current !== sequence) return
      if (!relation.can_edit) throw new Error('仅能编辑自己发布、未过期且无人接单的悬赏')
      const contact = await questsApi.contacts(id)
      if (current !== sequence) return
      Object.assign(model, { title: task.title, description: task.description, category: task.category, location: task.location, ...contact.owner })
      deadline.value = new Date(task.deadline).getTime(); reward.value = Number(task.reward)
    }
    ready.value = true
  } catch (cause) { if (current === sequence) error.value = cause instanceof Error ? cause.message : '加载失败' }
  finally { if (current === sequence) loading.value = false }
}, { immediate: true })
async function save() {
  if (busy.value || !ready.value) return
  error.value = ''
  if (model.title.trim().length < 2 || model.description.trim().length < 5 || model.location.trim().length < 2 || model.contact_value.trim().length < 3) {
    error.value = '请填写完整：标题和地点至少 2 字、需求描述至少 5 字、联系方式至少 3 字'; return
  }
  if (reward.value === null || !deadline.value || deadline.value <= Date.now() || deadline.value > Date.now() + 30 * 86400000) {
    error.value = '请输入赏金，并选择未来 30 天内的截止时间'; return
  }
  busy.value = true
  try {
    const result = await questsApi.save({ ...model, reward: reward.value.toFixed(2), deadline: new Date(deadline.value).toISOString() }, route.params.id ? Number(route.params.id) : undefined)
    await router.push(`/quest/${result.id}`)
  } catch (cause) { error.value = cause instanceof Error ? cause.message : '保存失败' }
  finally { busy.value = false }
}
</script>
<template><AppContainer><main class="quest-page"><PageHeader :title="route.params.id ? '编辑悬赏' : '发布悬赏'" description="说清需求、地点与时间，让同学更容易帮上忙。" /><div class="quest-form"><NAlert v-if="error" type="error" class="mb-5">{{ error }}</NAlert><NSpin :show="loading"><NCard v-if="ready"><NForm :disabled="busy" @submit.prevent="save">
  <NFormItem label="悬赏标题"><NInput v-model:value="model.title" :maxlength="80" show-count placeholder="例如：帮取一份快递到宿舍楼下" /></NFormItem>
  <NFormItem label="分类"><NSelect v-model:value="model.category" :options="categories" /></NFormItem>
  <NFormItem label="需求描述"><NInput v-model:value="model.description" type="textarea" :maxlength="1500" show-count :autosize="{ minRows: 4 }" placeholder="请说明具体事项、交付要求及注意事项" /></NFormItem>
  <NFormItem label="交付地点"><NInput v-model:value="model.location" :maxlength="160" placeholder="例如：南区三号宿舍楼下" /></NFormItem>
  <NFormItem label="赏金 元"><NInputNumber v-model:value="reward" :min="0" :max="9999.99" :precision="2" class="w-full" /></NFormItem>
  <NFormItem label="截止时间"><NDatePicker v-model:value="deadline" type="datetime" clearable class="w-full" /></NFormItem>
  <NFormItem label="联系方式类型"><NSelect v-model:value="model.contact_type" :options="contactOptions" /></NFormItem>
  <NFormItem label="联系方式"><NInput v-model:value="model.contact_value" :maxlength="64" placeholder="仅向接单者展示" /></NFormItem>
  <NAlert type="info">每条悬赏由一位同学接取。赏金由双方线下协商结算，请勿在需求描述中公开联系方式。</NAlert>
  <div class="quest-actions"><NButton type="primary" attr-type="submit" :loading="busy">保存悬赏</NButton><NButton :disabled="busy" @click="router.push(route.params.id ? `/quest/${route.params.id}` : '/quest')">返回</NButton></div>
</NForm></NCard></NSpin></div></main></AppContainer></template>
