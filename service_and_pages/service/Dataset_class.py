from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class Dataset_class:
    class_label: str
    class_name: str
    class_number_of_labels: int
    class_heatmap: np.ndarray

    @classmethod
    def from_dataframe(cls, df_filtered: pd.DataFrame, label, heatmap_size=640):
        # Инициализация тепловой карты
        heatmap = np.zeros((heatmap_size, heatmap_size))

        # Подсчитываем количество элементов с указанным label
        class_number_of_labels = len(df_filtered)

        # Получаем имя класса из первой строки отфильтрованного датафрейма
        class_name = df_filtered['class_name'].iloc[0] if class_number_of_labels > 0 else ""

        # Заполнение тепловой карты
        for _, row in df_filtered.iterrows():
            x_center = int(row['x_center'] * heatmap_size)
            y_center = int(row['y_center'] * heatmap_size)
            width = int(row['width_ratio'] * heatmap_size)
            height = int(row['height_ratio'] * heatmap_size)

            x1 = int(x_center - width / 2)
            x2 = int(x_center + width / 2)
            y1 = int(y_center - height / 2)
            y2 = int(y_center + height / 2)

            heatmap[y1:y2, x1:x2] += 1

        # Возвращаем экземпляр Dataset_class с заполненными полями
        return cls(
            class_label=str(int(label)),
            class_name=str(class_name),
            class_number_of_labels=int(class_number_of_labels),
            class_heatmap=heatmap
        )

    def get_heatmap(self):
        return self.class_heatmap/self.class_number_of_labels

    def get_number_of_labels(self):
        return self.class_number_of_labels
