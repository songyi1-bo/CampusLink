from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import func, or_, select
from app.modules.quest.models import QuestTask
from app.user.models import User

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def get_task(db, task_id, lock=False):
    query = select(QuestTask).where(QuestTask.id == task_id)
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    task = db.scalar(query)
    if task is None:
        raise HTTPException(404, '悬赏不存在')
    return task

def person(user):
    return dict(id=user.id, nickname=user.nickname, avatar=user.avatar) if user else None

def detail(db, task):
    return dict(id=task.id, owner=person(db.get(User, task.owner_id)),
                assignee=person(db.get(User, task.assignee_id)) if task.assignee_id else None,
                title=task.title, description=task.description, category=task.category,
                location=task.location, reward=f'{task.reward:.2f}',
                deadline=task.deadline.replace(tzinfo=timezone.utc), status=task.status,
                display_status='expired' if task.status == 'open' and task.deadline <= now() else task.status,
                created_at=task.created_at.replace(tzinfo=timezone.utc),
                updated_at=task.updated_at.replace(tzinfo=timezone.utc))

def list_tasks(db, page, page_size, keyword='', category=None, status=None, sort='latest', user_id=None, scope=None):
    query = select(QuestTask)
    if scope == 'published':
        query = query.where(QuestTask.owner_id == user_id)
    elif scope == 'accepted':
        query = query.where(QuestTask.assignee_id == user_id)
    if keyword:
        query = query.where(or_(QuestTask.title.contains(keyword, autoescape=True), QuestTask.description.contains(keyword, autoescape=True)))
    if category:
        query = query.where(QuestTask.category == category)
    if status == 'expired':
        query = query.where(QuestTask.status == 'open', QuestTask.deadline <= now())
    elif status:
        query = query.where(QuestTask.status == status)
        if status == 'open':
            query = query.where(QuestTask.deadline > now())
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    ordering = {'latest': QuestTask.created_at.desc(), 'reward': QuestTask.reward.desc(), 'deadline': QuestTask.deadline.asc()}
    tasks = db.scalars(query.order_by(ordering[sort], QuestTask.id.desc()).offset((page - 1) * page_size).limit(page_size))
    return dict(items=[detail(db, t) for t in tasks], total=total, page=page, page_size=page_size)

def relation(task, user_id):
    owner, assignee = task.owner_id == user_id, task.assignee_id == user_id
    available = task.status == 'open' and task.deadline > now()
    return dict(role='owner' if owner else 'assignee' if assignee else 'visitor',
                can_edit=owner and available, can_accept=not owner and available,
                can_withdraw=assignee and task.status == 'accepted', can_submit=assignee and task.status == 'accepted',
                can_confirm=owner and task.status == 'submitted', can_cancel=owner and task.status == 'open',
                can_contact=owner or (assignee and task.status in ('accepted', 'submitted', 'completed')),
                completion_note=task.completion_note if owner or assignee else None)

def write_task(db, user_id, payload, task_id=None):
    try:
        values = payload.model_dump()
        values['deadline'] = payload.deadline.astimezone(timezone.utc).replace(tzinfo=None)
        if task_id is None:
            task = QuestTask(owner_id=user_id, **values)
            db.add(task)
        else:
            task = get_task(db, task_id, True)
            if task.owner_id != user_id:
                raise HTTPException(403, '只能编辑自己发布的悬赏')
            if not relation(task, user_id)['can_edit']:
                raise HTTPException(409, '仅未过期且无人接单的悬赏可以编辑')
            for key, value in values.items():
                setattr(task, key, value)
        if task.deadline <= now():
            raise HTTPException(409, '截止时间已过，请重新选择')
        db.commit()
        db.refresh(task)
        return detail(db, task)
    except Exception:
        db.rollback()
        raise

def act(db, task_id, user_id, action, payload=None):
    try:
        task = get_task(db, task_id, True)
        permissions = relation(task, user_id)
        role = 'owner' if action in ('cancel', 'confirm') else 'assignee'
        if action == 'accept':
            if task.owner_id == user_id:
                raise HTTPException(403, '不能接取自己发布的悬赏')
        elif permissions['role'] != role:
            raise HTTPException(403, '你无权执行此操作')
        if not permissions['can_' + action]:
            raise HTTPException(409, '悬赏状态已变化，请刷新后重试')
        if action == 'accept':
            task.assignee_id = user_id
            task.assignee_contact_type = payload.contact_type
            task.assignee_contact_value = payload.contact_value
            task.status = 'accepted'
        elif action == 'withdraw':
            task.assignee_id = None
            task.assignee_contact_type = task.assignee_contact_value = None
            task.completion_note = ''
            task.status = 'open'
        elif action == 'submit':
            task.completion_note = payload.completion_note
            task.status = 'submitted'
        elif action == 'confirm':
            task.status = 'completed'
        elif action == 'cancel':
            task.status = 'cancelled'
        db.commit()
        db.refresh(task)
        return detail(db, task)
    except Exception:
        db.rollback()
        raise

def contacts(db, task_id, user_id):
    task = get_task(db, task_id, True)
    if not relation(task, user_id)['can_contact']:
        raise HTTPException(403, '仅发布者和当前接单者可查看联系方式')
    return dict(owner=dict(contact_type=task.contact_type, contact_value=task.contact_value),
                assignee=dict(contact_type=task.assignee_contact_type, contact_value=task.assignee_contact_value) if task.assignee_id else None)
