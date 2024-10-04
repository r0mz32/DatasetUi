from dataclasses import dataclass, field
from service_and_pages.service.Dataset_class import Dataset_class
from service_and_pages.service.Dataset_label_assist import Dataset_label_assist
from typing import List
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import random
import csv
import os


@dataclass
class DatasetProcessor:
    # путь до директорий с набором данных
    path_to_the_data_directory: list[str] = field(default_factory=list)
    # датафрейм для сводной информации - директория и имя изображения, его ширина и высота, разметка связанная с изображением в формате YOLOv5\YOLOv8
    dataframe: pd.DataFrame = field(
        default_factory=lambda: pd.DataFrame(columns=['image_dir', 'image_name', 'width', 'height', 'label', 'class_name', 'x_center', 'y_center', 'width_ratio', 'height_ratio']))
    csv_file_name: str = 'dataset.csv'
    dataset_class_labels: List[Dataset_class] = field(default_factory=list)

    # Возвращает высоту и ширину изображения

    @staticmethod
    def __get_image_size(image_path):
        try:
            with Image.open(image_path) as img:
                return img.width, img.height
        except:
            return None, None

    # Ищет файл с разметкой (txt с именем изображения), в той же папке или в папке на уровень выше

    @staticmethod
    def __find_label_file(image_dir, image_name):

        image_base_name, _ = os.path.splitext(image_name)

        max_levels = 1

        # Проверяем текущую директорию
        for _ in range(max_levels + 1):
            txt_path = os.path.join(image_dir, f"{image_base_name}.txt")
            if os.path.exists(txt_path):
                return txt_path

            # Поднимаемся на уровень выше и проверяем другие директории
            parent_dir = os.path.dirname(image_dir)
            if parent_dir == image_dir:  # Достигнут корень
                break
            image_dir = parent_dir

            # Ищем во всех директориях на текущем уровне
            for folder in os.listdir(image_dir):
                current_dir = os.path.join(image_dir, folder)
                if os.path.isdir(current_dir) and current_dir != os.path.dirname(os.path.join(image_dir, image_name)):
                    txt_path = os.path.join(
                        current_dir, f"{image_base_name}.txt")
                    if os.path.exists(txt_path):
                        return txt_path

        return None

    def __image_information(self, root, file):
        # Путь к изображению
        img_path = os.path.join(root, file)
        # Разделение пути до изображения и его имени
        img_name = os.path.basename(img_path)
        img_dir = os.path.dirname(img_path)
        # Высота и ширина изображения
        width, height = self.__get_image_size(img_path)

        label_file = self.__find_label_file(
            img_dir, img_name)

        return img_dir, img_name, width, height, label_file

    def process_dataset(self, dirs=None, csv_file=None):
        if dirs != None:
            self.path_to_the_data_directory = dirs
        if csv_file != None and csv_file.endswith('.csv'):
            self.csv_file_name = csv_file

        with open(self.csv_file_name, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Заголовок
            writer.writerow(['image_dir', 'image_name', 'width', 'height',
                            'label', 'class_name', 'x_center', 'y_center', 'width_ratio', 'height_ratio'])
            for data_dir in self.path_to_the_data_directory:
                for root, _, files in os.walk(data_dir):
                    for file in files:
                        # перебор изображений только заданных форматов
                        if file.endswith(('.jpg', '.jpeg', '.png')):
                            img_dir, img_name, width, height, label_file = self. __image_information(
                                root, file)
                            if width == None or height == None:
                                continue

                            # Если файл разметки найден и он не пуст - заполняю датафрем информацией из него
                            if label_file and os.path.getsize(label_file) > 0:
                                with open(label_file, 'r') as f:
                                    for line in f:
                                        parts = line.strip().split()
                                        if len(parts) == 5:
                                            class_label = int(parts[0])
                                            x_center = float(parts[1])
                                            y_center = float(parts[2])
                                            bbox_width = float(parts[3])
                                            bbox_height = float(parts[4])

                                            writer.writerow([img_dir, img_name, width, height,
                                                            class_label, None,
                                                            x_center, y_center,
                                                            bbox_width, bbox_height])

                            # иначе заполняю информацию об изображении, а остальное None
                            else:
                                writer.writerow(
                                    [img_dir, img_name, width, height] + [None] * 6)

    # сохраняет информацию о датасете в csv

    def save_dataframe_to_csv(self, csv_file_path=None):
        if csv_file_path == None:
            csv_file_path = self.csv_file_name
        self.dataframe.to_csv(csv_file_path, index=False)
        self.dataframe = pd.DataFrame(columns=['image_dir', 'image_name', 'width', 'height',
                                               'label', 'class_name', 'x_center', 'y_center', 'width_ratio', 'height_ratio'])

    def update_names_with_yaml(self, yaml_files):
        self.dataframe = pd.read_csv(self.csv_file_name)

        Dataset_label_assist.from_yaml(yaml_files, self.dataframe)

        self.save_dataframe_to_csv()

    def update_names_with_already_known(self, image_dir_with_known_names, name_of_image_dir_without_class_names):
        self.dataframe = pd.read_csv(self.csv_file_name)

        Dataset_label_assist.from_already_known(
            image_dir_with_known_names, name_of_image_dir_without_class_names, self.dataframe)

        self.save_dataframe_to_csv()

    def update_names_with_dict(self, name_of_image_dir, labels_and_names_dict):
        self.dataframe = pd.read_csv(self.csv_file_name)

        Dataset_label_assist.from_dict(
            name_of_image_dir, labels_and_names_dict, self.dataframe)

        self.save_dataframe_to_csv()

    def update_names_manual(self, res_dict):
        for path in res_dict.keys():
            new_dict = {}
            for key, value in res_dict[path].items():
                new_key = float(key)
                new_dict[new_key] = value
            self.update_names_with_dict(path, new_dict)

    def standardize_class_names(self):
        self.dataframe = pd.read_csv(self.csv_file_name)
        # получаю уникальные имена классов
        class_names = self.dataframe['class_name'].dropna().unique()
        # создаю на их основе словарь
        labels_dict = {name: label for label, name in enumerate(class_names)}
        # меняю метки по словарю
        self.dataframe['label'] = self.dataframe['class_name'].map(labels_dict)

        self.save_dataframe_to_csv()

    def common_path(self):
        return os.path.commonpath(self.path_to_the_data_directory)

    def get_paths_labels_names(self):
        # Чтение CSV файла
        self.dataframe = pd.read_csv(self.csv_file_name)

        # Выбираем пути, для которых не заполнены имена классов
        dataset_paths = self.dataframe[self.dataframe['class_name'].isna(
        )]['image_dir'].dropna().unique()

        # Словарь: ключ - имя папки, значение - словарь, где ключ - метка класса, значение - пустая строка
        data_dict = {str(path): {str(int(label)): '' for label in self.dataframe[self.dataframe['image_dir'] == path]['label'].dropna().sort_values().unique()}
                     for path in dataset_paths}

        # Уже заполненные имена классов
        class_names = self.dataframe['class_name'].dropna().unique()

        # Пересоздаем пустую таблицу с нужными колонками
        self.dataframe = pd.DataFrame(columns=['image_dir', 'image_name', 'width', 'height',
                                               'label', 'class_name', 'x_center', 'y_center', 'width_ratio', 'height_ratio'])

        return list(dataset_paths), data_dict, list(class_names)

    def get_image_exmpl(self, dataset_path, label):
        self.dataframe = pd.read_csv(self.csv_file_name)

        image_name_with_labels = self.dataframe[(self.dataframe['image_dir'] == dataset_path) & (
            self.dataframe['label'] == float(label))]['image_name'].value_counts().head(10).index.to_list()

        # выбираю случайное изображение из предложенных
        name_of_image = random.choice(image_name_with_labels)
        # сохраняю все строки с нужным классом для изображения
        rows = self.dataframe[(self.dataframe['image_dir'] == dataset_path) & (
            self.dataframe['image_name'] == name_of_image) & (self.dataframe['label'] == float(label))]

        # открываю нужное изображение
        image = Image.open(os.path.join(dataset_path, name_of_image))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(size=40)

        for row in rows.values:
            _, _, width, height, label, _, x_center, y_center, width_ratio, height_ratio = row
            # Координаты прямоугольника (верхний левый и нижний правый угол)
            top_left = (int(width * (x_center - width_ratio / 2)),
                        int(height * (y_center - height_ratio / 2)))
            bottom_right = (int(width * (x_center + width_ratio / 2)),
                            int(height * (y_center + height_ratio / 2)))

            # Рисую ограничивающий прямоугольник
            draw.rectangle([top_left, bottom_right], outline="blue", width=2)

        # добавляю текст
        draw.text((10, 10), str(label), fill="blue", font=font)

        self.dataframe = pd.DataFrame(columns=['image_dir', 'image_name', 'width', 'height',
                                               'label', 'class_name', 'x_center', 'y_center', 'width_ratio', 'height_ratio'])

        return image

    def image_stat_from_dataframe(self):
        self.dataframe = pd.read_csv(self.csv_file_name)
        self.dataset_class_labels = Dataset_class.from_dataframe(
            self.dataframe)
        self.save_dataframe_to_csv()

    def set_dataset_class_labels(self):
        self.dataframe = pd.read_csv(self.csv_file_name)
        # Получаем уникальные метки классов
        unique_labels = self.dataframe['label'].dropna().sort_values().unique()

        # Создаем список для хранения объектов Dataset_class
        dataset_class_labels = []

        # Для каждого уникального класса фильтруем датафрейм и создаем объект Dataset_class
        for label in unique_labels:
            df_filtered = self.dataframe[(self.dataframe['label'].notna()) & (
                self.dataframe['label'] == label)]
            if not df_filtered.empty:
                dataset_class = Dataset_class.from_dataframe(
                    df_filtered, label)
                self.dataset_class_labels.append(dataset_class)

        self.save_dataframe_to_csv()

    def get_all_class_names(self):
        return [dataset_class.class_name for dataset_class in self.dataset_class_labels]

    def get_all_class_number_of_labels(self):
        return [dataset_class.class_number_of_labels for dataset_class in self.dataset_class_labels]

    def get_heatmap_by_class_name(self, class_name):
        for dataset_class in self.dataset_class_labels:
            if dataset_class.class_name == class_name:
                return dataset_class.get_heatmap()
        raise ValueError(f'Class with name "{class_name}" not found')

    def get_statistic(self):
        self.dataframe = pd.read_csv(self.csv_file_name)

        number_of_images = len(self.dataframe['image_name'].unique())
        null_annotations = len(
            self.dataframe[self.dataframe['label'].isna()]['image_name'].unique())
        number_of_labels = len(self.dataframe['label'])

        median_width = int(self.dataframe['width'].median())
        median_height = int(self.dataframe['height'].median())

        min_width = int(self.dataframe['width'].min())
        min_height = int(self.dataframe['height'].min())

        max_width = int(self.dataframe['width'].max())
        max_height = int(self.dataframe['height'].max())

        self.save_dataframe_to_csv()

        return number_of_images, null_annotations, number_of_labels, median_width, median_height, min_width, min_height, max_width, max_height
