from nicegui import ui
from ..service import local_file_picker
import asyncio


async def configure_names_with_yaml_content(app):
    columns = [
        {'field': 'Выбрано:', 'editable': False, 'sortable': False},
    ]
    rows = []

    def to_previous_page():
        ui.navigate.to('/new_project')

    async def to_next_page():
        # Переход к странице загрузки файлов конфигурации
        loading_dialog.open()

        # Запускаем длительный процесс в отдельном потоке
        await asyncio.to_thread(execute_long_process)

        # Переход к следующей странице после завершения обработки
        ui.navigate.to('/manual_enter')

    def execute_long_process():
        # Вызов инициализации датасета
        yamls = [d['Выбрано:'] for d in rows]
        app.dataset.update_names_with_yaml(yaml_files=yamls)

    async def add_row():
        new_yamls = await local_file_picker.local_file_picker(directory=f'{app.dataset.common_path()}', upper_limit='/', multiple=True, chose_yaml=True)
        if new_yamls != None:
            existing_rows = {d['Выбрано:'] for d in rows}
            for value in new_yamls:
                if value in existing_rows:
                    ui.notify(f'Элемент "{value}" уже добавлен')
                elif not value.endswith('.yaml'):
                    ui.notify(f'not yaml')
                else:
                    rows.append({'Выбрано:': value})
            aggrid.update()

    async def delete_selected():
        selected_yaml = [row['Выбрано:'] for row in await aggrid.get_selected_rows()]
        rows[:] = [row for row in rows if row['Выбрано:'] not in selected_yaml]
        aggrid.update()

    # колесо загрузки
    loading_dialog = ui.dialog()

    with loading_dialog:
        with ui.card():
            ui.spinner(size='lg')

    # Кнопка "Назад"
    with ui.row().classes('justify-start items-start'):
        ui.button('Назад', on_click=to_previous_page).classes('m-4')

    # Заголовок
    ui.label('Выбор выбор конфигурационных файлов').classes(
        'text-lg ml-4').style('font-size: 24px; font-family: Arial;').classes('font-bold')

    ui.label(f'Для следующих директорий:').classes(
        'text-lg ml-8').style('font-size: 20px; font-family: Arial;')

    with ui.card().style('width: 100%').props('flat bordered'):
        with ui.scroll_area():
            with ui.list() as l:
                dataset_dirs, _, _ = app.dataset.get_paths_labels_names()
                for item in dataset_dirs:
                    ui.label(item).classes(
                        'text-lg ml-12').style('font-size: 16px; font-family: Arial;')

    # Таблица с выбранными элементами
    aggrid = ui.aggrid({
        'columnDefs': columns,
        'rowData': rows,
        'rowSelection': 'multiple',
    })

    # Панель с кнопками "Добавить", "Удалить" и "Далее"
    with ui.row().classes('justify-between w-full m-4'):
        with ui.row().classes('justify-start'):
            ui.button('Добавить',  on_click=add_row,
                      icon='folder').classes('mr-2')
            ui.button('Удалить', on_click=delete_selected,
                      icon='delete_outline')

        ui.button('Далее', on_click=to_next_page).classes('mr-8')
