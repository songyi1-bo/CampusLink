from typing import Annotated, Literal
from fastapi import APIRouter, Path, Query, Response
from app.auth.dependencies import CurrentUser, DatabaseSession
from app.common.response import ApiResponse, PageData
from app.modules.quest import service
from app.modules.quest.schemas import Category, Completion, Contact, QuestContacts, QuestDetail, QuestWrite, Relation

router = APIRouter(prefix='/api/quests', tags=['quests'])
TaskId = Annotated[int, Path(gt=0, le=2**63 - 1)]
Page = Annotated[int, Query(ge=1, le=100000)]
PageSize = Annotated[int, Query(ge=1, le=50)]
FilterStatus = Literal['open', 'accepted', 'submitted', 'completed', 'cancelled', 'expired']

@router.get('', response_model=ApiResponse[PageData[QuestDetail]])
def browse(db: DatabaseSession, page: Page = 1, page_size: PageSize = 12,
           keyword: Annotated[str, Query(max_length=80)] = '', category: Category | None = None,
           status: FilterStatus | None = 'open', sort: Literal['latest', 'reward', 'deadline'] = 'latest'):
    return ApiResponse(data=service.list_tasks(db, page, page_size, keyword, category, status, sort))

@router.post('', response_model=ApiResponse[QuestDetail])
def create(payload: QuestWrite, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.write_task(db, user.id, payload))

@router.get('/mine', response_model=ApiResponse[PageData[QuestDetail]])
def mine(user: CurrentUser, db: DatabaseSession, response: Response,
         scope: Literal['published', 'accepted'] = 'published', page: Page = 1, page_size: PageSize = 12,
         status: FilterStatus | None = None):
    response.headers['Cache-Control'] = 'no-store'
    return ApiResponse(data=service.list_tasks(db, page, page_size, status=status, user_id=user.id, scope=scope))

@router.get('/{task_id}', response_model=ApiResponse[QuestDetail])
def detail(task_id: TaskId, db: DatabaseSession):
    return ApiResponse(data=service.detail(db, service.get_task(db, task_id)))

@router.put('/{task_id}', response_model=ApiResponse[QuestDetail])
def edit(task_id: TaskId, payload: QuestWrite, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.write_task(db, user.id, payload, task_id))

@router.get('/{task_id}/relation', response_model=ApiResponse[Relation])
def relation(task_id: TaskId, user: CurrentUser, db: DatabaseSession, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    return ApiResponse(data=service.relation(service.get_task(db, task_id), user.id))

@router.get('/{task_id}/contacts', response_model=ApiResponse[QuestContacts])
def contacts(task_id: TaskId, user: CurrentUser, db: DatabaseSession, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    return ApiResponse(data=service.contacts(db, task_id, user.id))

@router.post('/{task_id}/accept', response_model=ApiResponse[QuestDetail])
def accept(task_id: TaskId, payload: Contact, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, task_id, user.id, 'accept', payload))

@router.post('/{task_id}/withdraw', response_model=ApiResponse[QuestDetail])
def withdraw(task_id: TaskId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, task_id, user.id, 'withdraw'))

@router.post('/{task_id}/submit', response_model=ApiResponse[QuestDetail])
def submit(task_id: TaskId, payload: Completion, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, task_id, user.id, 'submit', payload))

@router.post('/{task_id}/confirm', response_model=ApiResponse[QuestDetail])
def confirm(task_id: TaskId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, task_id, user.id, 'confirm'))

@router.post('/{task_id}/cancel', response_model=ApiResponse[QuestDetail])
def cancel(task_id: TaskId, user: CurrentUser, db: DatabaseSession):
    return ApiResponse(data=service.act(db, task_id, user.id, 'cancel'))
