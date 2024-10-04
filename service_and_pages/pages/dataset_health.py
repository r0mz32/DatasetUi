from nicegui import ui
from typing import List
import pandas as pd
from service_and_pages.service.Dataset_class import Dataset_class
import numpy as np
import matplotlib.pyplot as plt

selected_options = []


def dataset_health_content(app):
    # Имена классов для выбора
    options = app.dataset.get_all_class_names()
    number_of_options = app.dataset.get_all_class_number_of_labels()

    def to_previous_page():
        ui.navigate.to('/manual_enter')

    # Функция для обновления тепловой карты

    def update_heatmap():
        heatmap_card.clear()
        if not selected_options:
            with heatmap_card:
                ui.label('Тепловая карта не выбрана.').classes(
                    'absolute-center').style('font-size: 20px; font-family: Arial;')
        else:
            # Получение тепловых карт для выбранных классов
            selected_heatmaps = [app.dataset.get_heatmap_by_class_name(
                option) for option in selected_options]

            # Усреднение тепловых карт
            avg_heatmap = np.mean(selected_heatmaps, axis=0)

            # Построение и отображение тепловой карты
            with heatmap_card:
                with ui.pyplot(figsize=(10, 10), tight_layout=True):  # Задаем размеры графика
                    plt.imshow(avg_heatmap, cmap='hot',
                               interpolation='nearest', aspect='auto')
                    # Убираем оси для более чистого отображения
                    plt.axis('off')
                    # Настройка для полного заполнения области
                    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Функция для обновления выбранных классов

    def update_selected_options(option):
        if option in selected_options:
            selected_options.remove(option)
        else:
            selected_options.append(option)
        update_heatmap()

    number_of_images, null_annotations, number_of_labels, median_width, median_height, min_width, min_height, max_width, max_height = app.dataset.get_statistic()

    with ui.row().classes('justify-start items-start'):
        ui.button('Назад', on_click=to_previous_page).classes('m-4')

    ui.label('Аналитика набора данных').classes(
        'text-lg ml-4').style('font-size: 24px; font-family: Arial;').classes('font-bold')

    with ui.row().classes('w-full flex items-center'):
        # Карточка 1: выбор пути
        with ui.card().style('width: 32.75%').props('flat bordered'):
            ui.label('Количество изображений').style(
                'font-size: 20px; font-family: Arial; text-align: center;').classes('font-bold')
            ui.label(number_of_images).style(
                'font-size: 20px; font-family: Arial; text-align: center;').classes('font-bold')

            ui.label('∅ Без меток').style(
                'font-size: 18px; font-family: Arial; text-align: center;')
            ui.label(null_annotations).style(
                'font-size: 18px; font-family: Arial; text-align: center;')
        # Карточка 1: выбор пути
        with ui.card().style('width: 32.75%').props('flat bordered'):
            ui.label('Количество меток').style(
                'font-size: 20px; font-family: Arial; text-align: center;').classes('font-bold')
            ui.label(number_of_labels).style(
                'font-size: 20px; font-family: Arial; text-align: center;').classes('font-bold')

            per_image = round(number_of_labels / number_of_images, 2)
            ui.label('В среднем на одно изображение').style(
                'font-size: 18px; font-family: Arial; text-align: center;')
            ui.label(per_image).style(
                'font-size: 18px; font-family: Arial; text-align: center;')

        # Карточка 1: выбор пути
        with ui.card().style('width: 32.75%').props('flat bordered'):
            ui.label('Медианный размер').style(
                'font-size: 20px; font-family: Arial; text-align: center;').classes('font-bold')

            ui.label(f'{median_width}x{median_height}').style(
                'font-size: 20px; font-family: Arial; text-align: center;').classes('font-bold')

            ui.label(f'От {min_width}x{min_height}').style(
                'font-size: 18px; font-family: Arial; text-align: center;')
            ui.label(f'До {max_width}x{max_height}').style(
                'font-size: 18px; font-family: Arial; text-align: center;')

    ui.label('Распределение классов').classes(
        'text-lg ml-4').style('font-size: 20px; font-family: Arial;').classes('font-bold')

    chart = ui.highchart({
        'title': False,
        'chart': {'type': 'bar'},
        'xAxis': {'categories': options},  # Используем категории из массива
        'series': [
            # Используем значения из массива
            {'name': 'Количество меток', 'data': number_of_options},
        ],
    }).classes('w-full height: 32vw')

    ui.label('епловая карта').classes(
        'text-lg ml-4').style('font-size: 20px; font-family: Arial;').classes('font-bold')

    with ui.row().classes('w-full flex items-center'):
        # Карточка с хитмапом
        with ui.card().style('width: 32vw; height: 32vw;').props('flat bordered') as heatmap_card:
            ui.label('Тепловая карта не выбрана.').classes(
                'absolute-center').style('font-size: 20px; font-family: Arial;')

        # Карточка с выбором классов
        with ui.card().style('width: 64.72vw; height: 32vw;').props('flat bordered'):
            with ui.scroll_area().style('height: 32vw;'):
                ui.label('Выберите элементы:')
                for option in options:
                    ui.checkbox(option, on_change=lambda e,
                                option=option: update_selected_options(option)).style('font-size: 20px; font-family: Arial;')
