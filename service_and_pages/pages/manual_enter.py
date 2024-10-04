from nicegui import ui
import asyncio


async def manual_enter_content(app):

    dataset_paths, data_dict, class_names = app.dataset.get_paths_labels_names()

    # Показ диалога с изображением
    def show_image_dialog(selected_path, key):
        img_data = app.dataset.get_image_exmpl(selected_path, key)
        image_dialog.clear()

        with image_dialog:
            ui.image(img_data).style('max-width: 80%; max-height: 80%;')
        image_dialog.open()

    def execute_long_process():

        app.dataset.update_names_manual(data_dict)
        app.dataset.standardize_class_names()
        app.dataset.set_dataset_class_labels()

    # Переход на следующую страницу

    async def to_next_page():
        all_filled = True
        for path in dataset_paths:
            data = data_dict[path]
            # Находим ключи с пустыми значениями
            missing_values = [key for key, value in data.items() if not value]

            if missing_values:
                all_filled = False
                for key in missing_values:
                    ui.notify(f"Заполните класс {key} для {path}")

        if all_filled:
            # Переход к странице загрузки файлов конфигурации
            loading_dialog.open()

            # Запускаем длительный процесс в отдельном потоке
            await asyncio.to_thread(execute_long_process)

            ui.navigate.to('/dataset_health')
    # Переход на предыдущую страницу

    def to_previous_page():
        ui.navigate.to('/configure_names_with_yaml')

    # Обновление карточки 2 на основе выбора в карточке 1
    def update_card2(selected_path):
        card2.clear()
        if selected_path:
            data = data_dict[selected_path]

            with card2:
                with ui.scroll_area():
                    with ui.grid(columns='auto 1fr').classes('w-full gap-1'):

                        ui.label('Метка').classes('font-bold')
                        ui.label('Имя').classes('font-bold')

                        for key in data.keys():
                            ui.button(str(key), on_click=lambda key=key: show_image_dialog(
                                selected_path, key))
                            ui.input(value=data[key], on_change=lambda e, key=key: update_value(
                                selected_path, key, e.value))

    # Обновление значения в словаре
    def update_value(path, key, value):
        data_dict[path][key] = value

    loading_dialog = ui.dialog()

    with loading_dialog:
        with ui.card():
            ui.spinner(size='lg')

    # Интерфейс страницы
    with ui.row().classes('justify-start items-start'):
        ui.button('Назад', on_click=to_previous_page).classes('m-4')

    ui.label('Ввод имен классов').classes(
        'text-lg ml-4').style('font-size: 24px; font-family: Arial;').classes('font-bold')

    if len(class_names) > 0:
        with ui.row():
            ui.label('Известные классы:').classes('text-lg ml-4')
            for class_name in class_names:
                ui.label(f'{class_name}').classes('text-lg ml-4')

    with ui.row().classes('w-full flex items-center'):
        # Карточка 1: выбор пути
        with ui.card().style('width: 49%').props('flat bordered'):
            with ui.scroll_area():
                ui.label('Выберите путь:')
                global radio_group
                radio_group = ui.radio(options=dataset_paths,
                                       on_change=lambda e: update_card2(e.value))
        # Карточка 2: отображение словаря
        with ui.card().style('width: 49%').props('flat bordered') as card2:
            with ui.scroll_area():
                ui.label(
                    'Выберите элемент из списка выше, чтобы увидеть результат.')

    with ui.row().classes('w-full justify-end'):
        ui.button('Далее', on_click=to_next_page).classes('mr-1')

# Создание диалога для показа изображения
    image_dialog = ui.dialog()
