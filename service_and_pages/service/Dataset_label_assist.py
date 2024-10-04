from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import random
import yaml
import os


class Dataset_label_assist:
    @classmethod
    def __update_class_names(self, dataframe, name_of_image_dir, labels_and_names_dict):
        dataframe.loc[(dataframe['image_dir'] == name_of_image_dir),
                      'class_name'] = dataframe[dataframe['image_dir'] == name_of_image_dir]['label'].map(labels_and_names_dict)

        return dataframe

    @classmethod
    def from_yaml(self, yaml_files, dataframe: pd.DataFrame):
        for yaml_file in yaml_files:
            yaml_dir, _ = os.path.split(yaml_file)
            with open(yaml_file, 'r') as file:
                data = yaml.safe_load(file)
            # путь к изображениям, которые описываются в yaml
            image_paths = list(yaml_dir + data.get(i)
                               [2:] for i in ['test', 'train', 'val'] if data.get(i) != None)

            # словарь метка - имя
            labels_and_names_dict = {
                index: value for index, value in enumerate(data.get('names'))}

            # обновляю имена классов
            for image_path in image_paths:
                dataframe = self.__update_class_names(
                    dataframe, image_path, labels_and_names_dict)

        return dataframe

    @classmethod
    def from_dict(self, name_of_image_dir, labels_and_names_dict, dataframe: pd.DataFrame):
        dataframe = self.__update_class_names(
            dataframe, name_of_image_dir, labels_and_names_dict)

        return dataframe

    @classmethod
    def from_already_known(self, image_dir_with_known_names, name_of_image_dir_without_class_names, dataframe: pd.DataFrame):
        df_with_right_path = dataframe.loc[(
            dataframe['image_dir'] == image_dir_with_known_names), ['label', 'class_name']]
        # вормирую из них словарь
        labels_and_names_dict = df_with_right_path.drop_duplicates(
        ).dropna().set_index('label')['class_name'].to_dict()

        # обновляю имена классов
        dataframe = self.__update_class_names(
            dataframe, name_of_image_dir_without_class_names, labels_and_names_dict)

        return dataframe

    @classmethod
    def get_class_exemple_on_image(dataframe, image_path, index):
        print(image_path)
        print(index)
        # беру 10 изображений с наибольшим количеством отметок заданнго класса
        image_name_with_labels = dataframe[(dataframe['image_dir'] == image_path) & (
            dataframe['label'] == float(index))]['image_name'].value_counts().head(10).index.to_list()

        # выбираю случайное изображение из предложенных
        name_of_image = random.choice(image_name_with_labels)
        # сохраняю все строки с нужным классом для изображения
        rows = dataframe[(dataframe['image_dir'] == image_path) & (
            dataframe['image_name'] == name_of_image) & (dataframe['label'] == float(index))]

        # открываю нужное изображение
        image = Image.open(os.path.join(image_path, name_of_image))
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
        return image
