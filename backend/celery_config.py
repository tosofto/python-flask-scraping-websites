from celery.schedules import crontab

imports = 'backend.celery_tasks'
result_expires = 30
timezone = 'UTC'

accept_content = ['json', 'msgpack', 'yaml']
task_serializer = 'json'
result_serializer = 'json'

beat_schedule = {
    'fetch-all-store-menus-every-month': {
        'task': 'backend.celery_tasks.fetch_all_stores_menu_items',
        'schedule': crontab(day_of_month=1, hour=0, minute=0)
    }
}
