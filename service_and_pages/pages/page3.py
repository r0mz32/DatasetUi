from nicegui import ui


def page3_content(app):
    def to_previous_page():
        app.navigate_to('/page2', -1)

    """Контент для третьей страницы."""
    ui.label(f'Это страница {type(app.dataset)}')
    ui.notification(f'Текущий номер страницы: {
                    app.dataset.path_to_the_data_directory}')
    with ui.row():
        ui.button('Предыдущая страница',
                  on_click=to_previous_page)
