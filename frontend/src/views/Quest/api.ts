import { request } from '../../api/request'
export type Category = 'delivery' | 'study' | 'repair' | 'other'
export type Status = 'open' | 'accepted' | 'submitted' | 'completed' | 'cancelled' | 'expired'
export interface Person { id: number; nickname: string; avatar: string | null }
export interface Quest { id: number; owner: Person; assignee: Person | null; title: string; description: string; category: Category; location: string; reward: string; deadline: string; status: Status; display_status: Status; created_at: string; updated_at: string }
export interface Contact { contact_type: 'wechat' | 'qq' | 'phone'; contact_value: string }
export interface QuestWrite extends Contact { title: string; description: string; category: Category; location: string; reward: string; deadline: string }
export interface Relation { role: 'owner' | 'assignee' | 'visitor'; can_edit: boolean; can_accept: boolean; can_withdraw: boolean; can_submit: boolean; can_confirm: boolean; can_cancel: boolean; can_contact: boolean; completion_note: string | null }
export interface Contacts { owner: Contact; assignee: Contact | null }
export interface Page { items: Quest[]; total: number; page: number; page_size: number }
export const categories = [{ label: '跑腿代办', value: 'delivery' }, { label: '学习互助', value: 'study' }, { label: '维修帮忙', value: 'repair' }, { label: '其他互助', value: 'other' }]
export const statusLabels: Record<Status, string> = { open: '待接单', accepted: '进行中', submitted: '待确认', completed: '已完成', cancelled: '已取消', expired: '已过期' }
export const contactOptions = [{ label: '微信', value: 'wechat' }, { label: 'QQ', value: 'qq' }, { label: '手机', value: 'phone' }]
export const dateText = (value: string) => new Date(value).toLocaleString('zh-CN', { hour12: false })
const quiet = { silent: true }
export const questsApi = {
  list: (params: Record<string, unknown>, mine = false) => request.get<Page>(mine ? '/quests/mine' : '/quests', { ...quiet, params }),
  detail: (id: number) => request.get<Quest>(`/quests/${id}`, quiet),
  relation: (id: number) => request.get<Relation>(`/quests/${id}/relation`, quiet),
  contacts: (id: number) => request.get<Contacts>(`/quests/${id}/contacts`, quiet),
  save: (payload: QuestWrite, id?: number) => id ? request.put<Quest>(`/quests/${id}`, payload, quiet) : request.post<Quest>('/quests', payload, quiet),
  act: (id: number, action: 'accept' | 'withdraw' | 'submit' | 'confirm' | 'cancel', payload: unknown = {}) => request.post<Quest>(`/quests/${id}/${action}`, payload, quiet),
}
