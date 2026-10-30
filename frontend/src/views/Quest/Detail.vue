<script setup lang="ts">
import { onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NAlert, NButton, NCard, NFormItem, NInput, NModal, NSelect, NSpin, NTag, useDialog } from 'naive-ui'
import AppContainer from '../../components/layout/AppContainer.vue'
import PageHeader from '../../components/common/PageHeader.vue'
import { useAuthStore } from '../../stores/auth'
import { categories, contactOptions, dateText, questsApi, statusLabels } from './api'
import type { Contact, Contacts, Quest, Relation } from './api'
import './quest.css'
const route = useRoute(), router = useRouter(), auth = useAuthStore(), dialog = useDialog()
const task = ref<Quest | null>(null), relation = ref<Relation | null>(null), contacts = ref<Contacts | null>(null)
const loading = ref(false), busy = ref(false), error = ref(''), success = ref(''), showAccept = ref(false), showSubmit = ref(false), completionNote = ref('')
const contact = reactive<Contact>({ contact_type: 'wechat', contact_value: '' })
let sequence = 0
onUnmounted(() => { sequence++ })
async function load() {
  const current = ++sequence
  task.value = null; relation.value = null; contacts.value = null; error.value = ''; loading.value = true
  showAccept.value = showSubmit.value = false
  try {
    const result = await questsApi.detail(Number(route.params.id))
    const permissions = auth.isAuthenticated ? await questsApi.relation(result.id) : null
    if (current !== sequence) return
    task.value = result; relation.value = permissions
  } catch (cause) { if (current === sequence) error.value = cause instanceof Error ? cause.message : '加载失败' }
  finally { if (current === sequence) loading.value = false }
}
watch([() => route.params.id, () => auth.currentUser?.id], load, { immediate: true })
async function act(action: 'accept' | 'withdraw' | 'submit' | 'confirm' | 'cancel') {
  if (!task.value || busy.value) return
  if (action === 'accept' && contact.contact_value.trim().length < 3) { error.value = '请输入至少 3 字的联系方式'; return }
  if (action === 'submit' && completionNote.value.trim().length < 2) { error.value = '请填写至少 2 字的完成说明'; return }
  const id = task.value.id
  busy.value = true; error.value = ''; success.value = ''; contacts.value = null
  try {
    await questsApi.act(id, action, action === 'accept' ? contact : action === 'submit' ? { completion_note: completionNote.value } : {})
    await load(); success.value = '操作成功'
  } catch (cause) {
    const message = cause instanceof Error ? cause.message : '操作失败'
    await load(); error.value = message
  } finally { busy.value = false }
}
function confirmAction(action: 'withdraw' | 'confirm' | 'cancel') {
  const messages = { withdraw: '撤回后悬赏将重新开放；若已过截止时间则不能再次接取。', confirm: '确认任务已按要求完成，赏金由双方线下结算。', cancel: '取消后该悬赏将关闭，无法继续接单。' }
  dialog.warning({ title: '确认操作', content: messages[action], positiveText: '确认', negativeText: '返回', onPositiveClick: () => act(action) })
}
async function reveal() {
  if (!task.value || busy.value) return
  const current = sequence, userId = auth.currentUser?.id
  busy.value = true; error.value = ''; contacts.value = null
  try {
    const result = await questsApi.contacts(task.value.id)
    if (current === sequence && userId === auth.currentUser?.id) contacts.value = result
  }
  catch (cause) { if (current === sequence) error.value = cause instanceof Error ? cause.message : '获取失败' }
  finally { busy.value = false }
}
function login() { void router.push({ path: '/login', query: { redirect: route.fullPath } }) }
</script>
<template><AppContainer><main class="quest-page"><RouterLink to="/quest">← 返回悬赏大厅</RouterLink><div class="quest-detail">
  <NAlert v-if="error" type="error" class="mb-5">{{ error }} <NButton text @click="load">刷新</NButton></NAlert><NAlert v-if="success" type="success" class="mb-5">{{ success }}</NAlert>
  <NSpin :show="loading"><NCard v-if="task"><PageHeader :title="task.title" :description="`${categories.find(c => c.value === task?.category)?.label} · ${task.owner.nickname} 发布`" />
    <div class="quest-actions"><NTag :bordered="false" type="success">{{ statusLabels[task.display_status] }}</NTag><strong class="quest-reward">¥{{ task.reward }}</strong><span>线下结算</span></div>
    <p class="quest-description">{{ task.description }}</p>
    <dl class="quest-facts"><div><dt>交付地点</dt><dd>{{ task.location }}</dd></div><div><dt>截止时间</dt><dd>{{ dateText(task.deadline) }}</dd></div><div><dt>接单同学</dt><dd>{{ task.assignee?.nickname || '等待同学接取' }}</dd></div><div><dt>发布时间</dt><dd>{{ dateText(task.created_at) }}</dd></div></dl>
    <NAlert v-if="task.display_status === 'expired'" type="warning">这条悬赏已过期，无法接取。</NAlert>
    <NAlert v-if="relation?.completion_note" type="info" title="完成说明">{{ relation.completion_note }}</NAlert>
    <div class="quest-actions">
      <NButton v-if="!auth.isAuthenticated && task.display_status === 'open'" type="primary" @click="login">登录后接单</NButton>
      <NButton v-if="relation?.can_accept" type="primary" :disabled="busy" @click="showAccept = true">我要接单</NButton>
      <NButton v-if="relation?.can_edit" :disabled="busy" @click="router.push(`/quest/${task.id}/edit`)">编辑悬赏</NButton>
      <NButton v-if="relation?.can_submit" type="primary" :disabled="busy" @click="showSubmit = true">提交完成</NButton>
      <NButton v-if="relation?.can_confirm" type="primary" :disabled="busy" @click="confirmAction('confirm')">确认完成</NButton>
      <NButton v-if="relation?.can_withdraw" :disabled="busy" @click="confirmAction('withdraw')">撤回接单</NButton>
      <NButton v-if="relation?.can_cancel" :disabled="busy" @click="confirmAction('cancel')">取消悬赏</NButton>
      <NButton v-if="relation?.can_contact" :loading="busy" @click="reveal">查看联系方式</NButton>
    </div>
    <NAlert v-if="contacts" type="info" title="任务联系方式"><p>发布者 {{ contactOptions.find(c => c.value === contacts?.owner.contact_type)?.label }}：{{ contacts.owner.contact_value }}</p><p v-if="contacts.assignee">接单者 {{ contactOptions.find(c => c.value === contacts?.assignee?.contact_type)?.label }}：{{ contacts.assignee.contact_value }}</p></NAlert>
  </NCard></NSpin>
  <NModal v-model:show="showAccept" preset="card" title="接取悬赏" style="width: min(460px, 92vw)" :mask-closable="!busy" :closable="!busy"><p>请确认能按需求完成，并留下供发布者联系的方式。</p><NFormItem label="联系方式类型"><NSelect v-model:value="contact.contact_type" :options="contactOptions" :disabled="busy" /></NFormItem><NFormItem label="联系方式"><NInput v-model:value="contact.contact_value" :maxlength="64" :disabled="busy" /></NFormItem><NAlert v-if="error" type="error" class="mb-4">{{ error }}</NAlert><NButton type="primary" :loading="busy" @click="act('accept')">确认接单</NButton></NModal>
  <NModal v-model:show="showSubmit" preset="card" title="提交完成" style="width: min(460px, 92vw)" :mask-closable="!busy" :closable="!busy"><NFormItem label="完成说明"><NInput v-model:value="completionNote" type="textarea" :maxlength="500" :disabled="busy" placeholder="说明任务完成情况，等待发布者确认" /></NFormItem><NAlert v-if="error" type="error" class="mb-4">{{ error }}</NAlert><NButton type="primary" :loading="busy" @click="act('submit')">提交给发布者</NButton></NModal>
</div></main></AppContainer></template>
