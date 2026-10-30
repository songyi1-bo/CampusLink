<script setup lang="ts">
import { ref, watch } from 'vue'
import { NAlert, NButton, NEmpty, NInput, NPagination, NSelect, NSpin, NTag } from 'naive-ui'
import { categories, dateText, questsApi, statusLabels } from './api'
import type { Page } from './api'
import './quest.css'
const props = defineProps<{ mine?: boolean }>()
const keyword = ref(''), category = ref<string | null>(null), status = ref<string | null>(props.mine ? null : 'open'), sort = ref('latest'), scope = ref('published')
const page = ref(1), busy = ref(false), error = ref('')
const data = ref<Page | null>(null)
const states = Object.entries(statusLabels).map(([value, label]) => ({ value, label }))
let sequence = 0
async function load() {
  const current = ++sequence
  busy.value = true; error.value = ''; data.value = null
  try {
    const result = await questsApi.list({ page: page.value, page_size: 12, keyword: keyword.value.trim(), category: category.value || undefined, status: status.value || undefined, sort: sort.value, scope: scope.value }, props.mine)
    if (current === sequence) data.value = result
  } catch (cause) { if (current === sequence) error.value = cause instanceof Error ? cause.message : '加载失败' }
  finally { if (current === sequence) busy.value = false }
}
function search() { if (page.value !== 1) page.value = 1; else void load() }
watch(page, load)
watch(scope, search)
void load()
</script>
<template>
  <div v-if="mine" class="quest-actions"><NButton :type="scope === 'published' ? 'primary' : 'default'" @click="scope = 'published'">我发布的</NButton><NButton :type="scope === 'accepted' ? 'primary' : 'default'" @click="scope = 'accepted'">我接取的</NButton></div>
  <form class="quest-filters" @submit.prevent="search">
    <NInput v-if="!mine" v-model:value="keyword" placeholder="搜索悬赏标题或描述" :maxlength="80" aria-label="搜索关键词" />
    <NSelect v-if="!mine" v-model:value="category" :options="categories" clearable placeholder="全部分类" aria-label="悬赏分类" />
    <NSelect v-model:value="status" :options="states" clearable placeholder="全部状态" aria-label="悬赏状态" />
    <NSelect v-if="!mine" v-model:value="sort" :options="[{ label: '最新发布', value: 'latest' }, { label: '赏金从高到低', value: 'reward' }, { label: '即将截止', value: 'deadline' }]" aria-label="排序" />
    <NButton attr-type="submit" type="primary" :disabled="busy">筛选</NButton>
  </form>
  <NAlert v-if="error" type="error" class="mb-5">{{ error }} <NButton text @click="load">重试</NButton></NAlert>
  <NSpin :show="busy">
    <template v-if="data">
      <p class="text-sm text-[var(--text-secondary)]">共 {{ data.total }} 条悬赏</p>
      <div v-if="data.items.length" class="quest-grid">
        <RouterLink v-for="item in data.items" :key="item.id" :to="`/quest/${item.id}`" class="quest-card">
          <div class="quest-meta"><span>{{ categories.find(c => c.value === item.category)?.label }}</span><NTag :bordered="false" :type="item.display_status === 'open' ? 'success' : 'default'">{{ statusLabels[item.display_status] }}</NTag></div>
          <h2>{{ item.title }}</h2><p class="quest-excerpt">{{ item.description }}</p>
          <strong class="quest-reward">¥{{ item.reward }}</strong><p>{{ item.location }}</p>
          <div class="quest-meta"><span>{{ item.owner.nickname }}</span><span>截止 {{ dateText(item.deadline) }}</span></div>
        </RouterLink>
      </div>
      <NEmpty v-else description="暂无符合条件的悬赏，试试其他筛选条件" class="py-12" />
      <NPagination v-if="data.total > 12" v-model:page="page" :item-count="data.total" :page-size="12" :page-slot="5" />
    </template>
    <div v-else-if="busy" class="py-12">正在加载悬赏…</div>
  </NSpin>
</template>
