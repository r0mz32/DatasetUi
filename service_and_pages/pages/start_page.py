from nicegui import ui


def start_page_content(app):
    def to_new_project(app):
        # Переход к странице создания датасета
        ui.navigate.to('/new_project')

    def open_existing_project():
        # ui.navigate.to('/existing_project')
        ui.notify('Пришельцы украли код. Функция в разработке', color='negative')

    with ui.column().classes('justify-center items-center'):
        with ui.card().classes('absolute-center'):
            # Название страницы
            ui.label('Начало работы').style(
                'font-size: 36px; font-family: Arial; text-align: center;').classes('font-bold')
            # Кнопка для перехода к созданию датасета
            ui.button('Новый проект', on_click=to_new_project).classes(
                'w-full').style(
                'font-size: 24px; font-family: Arial; text-align: center;')
            ui.button('Открыть проект',
                      on_click=open_existing_project).classes('w-full').style(
                'font-size: 24px; font-family: Arial; text-align: center;')
