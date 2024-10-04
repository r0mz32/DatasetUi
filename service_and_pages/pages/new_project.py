import asyncio
from nicegui import ui
from ..service import local_file_picker


async def new_project_content(app):
    columns = [
        {'field': 'Выбрано:', 'editable': False, 'sortable': False},
    ]
    rows = []

    def to_previous_page():
        # Переход к начальной странице
        ui.navigate.to('/')

    async def to_next_page():
        # Переход к странице загрузки файлов конфигурации
        loading_dialog.open()

        # Запускаем длительный процесс в отдельном потоке
        await asyncio.to_thread(execute_long_process)

        # Переход к следующей странице после завершения обработки
        ui.navigate.to('/configure_names_with_yaml')

    def execute_long_process():
        # Вызов инициализации датасета
        dataset_dirs = [d['Выбрано:'] for d in rows]
        app.dataset.process_dataset(dirs=dataset_dirs)

    async def add_row():
        # Добавление директории к датасету
        new_dirs = await local_file_picker.local_file_picker('/', multiple=True)
        if new_dirs is not None:
            existing_rows = {d['Выбрано:'] for d in rows}
            for value in new_dirs:
                if value in existing_rows:
                    ui.notify(f'Элемент "{value}" уже добавлен')
                else:
                    rows.append({'Выбрано:': value})
            aggrid.update()

    async def delete_selected():
        # Удаление директории из списка
        selected_dir = [row['Выбрано:'] for row in await aggrid.get_selected_rows()]
        rows[:] = [row for row in rows if row['Выбрано:'] not in selected_dir]
        aggrid.update()

    # колесо загрузки
    loading_dialog = ui.dialog()

    with loading_dialog:
        with ui.card():
            ui.spinner(size='lg')

    # Кнопка для возвращения на начальный экран
    with ui.row().classes('justify-start items-start'):
        ui.button('Назад', on_click=to_previous_page).classes('m-4')

    # Название страницы
    ui.label('Выбор директорий, которые будут включены в набор данных').classes(
        'text-lg ml-4').style('font-size: 24px; font-family: Arial;').classes('font-bold')

    # Таблица с выбранными директориями
    aggrid = ui.aggrid({
        'columnDefs': columns,
        'rowData': rows,
        'rowSelection': 'multiple',
    })

    # Панель с кнопками "Добавить", "Удалить" и "Далее"
    with ui.row().classes('justify-between w-full m-4'):
        with ui.row().classes('justify-start'):
            # Кнопка для добавления папки
            ui.button('Добавить',  on_click=add_row,
                      icon='folder').classes('mr-2')
            # Кнопка для удаления
            ui.button('Удалить', on_click=delete_selected,
                      icon='delete_outline')

        ui.button('Далее', on_click=to_next_page).classes('mr-8')
