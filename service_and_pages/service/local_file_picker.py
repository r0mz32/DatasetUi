from pathlib import Path
from typing import Optional

from nicegui import events, ui


class local_file_picker(ui.dialog):

    def __init__(self, directory: str, *,
                 upper_limit: Optional[str] = ..., multiple: bool = False, show_hidden_files: bool = False, chose_yaml: bool = False) -> None:
        """Local File Picker

        Простой диалог для выбора файлов из локальной файловой системы, где работает NiceGUI.

        :param directory: Директория, в которой начинается выбор.
        :param upper_limit: Директория, выше которой нельзя подниматься (None: нет ограничения, по умолчанию: та же директория, что и начальная).
        :param multiple: Позволяет ли выбирать несколько файлов.
        :param show_hidden_files: Показывать ли скрытые файлы.
        :param chose_yaml: Показывать ли только .yaml файлы и директории или только директории.
        """
        super().__init__()

        # Устанавливаем начальный путь и верхний предел (если указан)
        self.path = Path(directory).expanduser()
        if upper_limit is None:
            self.upper_limit = None
        else:
            self.upper_limit = Path(
                directory if upper_limit == ... else upper_limit).expanduser()

        # Сохраняем флаги показа скрытых файлов и фильтрации по yaml
        self.show_hidden_files = show_hidden_files
        self.chose_yaml = chose_yaml  # Установка параметра chose_yaml

        # Создаем интерфейс с таблицей и кнопками "Cancel" и "Ok"
        with self, ui.card():
            self.grid = ui.aggrid({
                'columnDefs': [{'field': 'name', 'headerName': self.get_shortened_path()}],
                'rowSelection': 'multiple' if multiple else 'single',
            }, html_columns=[0]).classes('w-96').on('cellDoubleClicked', self.handle_double_click)
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=self.close).props('outline')
                ui.button('Ok', on_click=self._handle_ok)
        self.update_grid()

    def get_shortened_path(self) -> str:
        """Возвращает укороченный путь, если он слишком длинный."""
        path_str = str(self.path)
        max_length = 50  # Максимальная длина для отображения пути
        if len(path_str) > max_length:
            parts = self.path.parts
            while len(str(Path(*parts))) > max_length and len(parts) > 1:
                parts = parts[1:]
            return f'..{Path(*parts)}'
        return path_str

    def update_drive(self):
        """Обновление текущей директории при смене диска."""
        self.path = Path(self.drives_toggle.value).expanduser()
        self.update_grid()

    def update_grid(self) -> None:
        """Обновление содержимого таблицы в зависимости от текущего пути."""
        # Обновляем заголовок с учетом текущего пути
        self.grid.options['columnDefs'][0]['headerName'] = self.get_shortened_path()

        paths = list(self.path.glob('*'))

        # Фильтрация скрытых файлов, если флаг show_hidden_files выключен
        if not self.show_hidden_files:
            paths = [p for p in paths if not p.name.startswith('.')]

        # Фильтрация файлов в зависимости от параметра chose_yaml
        if self.chose_yaml:
            # Если chose_yaml = True, показываем папки и .yaml файлы
            paths = [p for p in paths if p.is_dir() or (
                p.is_file() and p.suffix == '.yaml')]
        else:
            # Если chose_yaml = False, показываем только папки
            paths = [p for p in paths if p.is_dir()]

        # Сортировка: сначала папки, затем файлы
        paths.sort(key=lambda p: p.name.lower())
        paths.sort(key=lambda p: not p.is_dir())

        # Обновляем данные для таблицы с отображением файлов и папок
        self.grid.options['rowData'] = [
            {
                'name': f'📁 <strong>{p.name}</strong>' if p.is_dir() else p.name,
                'path': str(p),
            }
            for p in paths
        ]

        # Добавляем возможность вернуться на уровень выше, если это не корневая директория
        if self.upper_limit is None and self.path != self.path.parent or \
                self.upper_limit is not None and self.path != self.upper_limit:
            self.grid.options['rowData'].insert(0, {
                'name': '📁 <strong>..</strong>',
                'path': str(self.path.parent),
            })

        # Обновляем таблицу интерфейса
        self.grid.update()

    def handle_double_click(self, e: events.GenericEventArguments) -> None:
        """Обработка двойного щелчка по элементу таблицы."""
        self.path = Path(e.args['data']['path'])
        if self.path.is_dir():
            # Если выбранная запись — папка, обновляем таблицу для этой папки
            self.update_grid()
        else:
            # Если выбран файл, передаем его путь
            self.submit([str(self.path)])

    async def _handle_ok(self):
        """Обработка кнопки Ok — выбор файла/файлов."""
        rows = await self.grid.get_selected_rows()
        self.submit([r['path'] for r in rows])
