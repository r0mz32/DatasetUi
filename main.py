from nicegui import ui
from service_and_pages.pages.start_page import start_page_content
from service_and_pages.pages.new_project import new_project_content
from service_and_pages.pages.configure_names_with_yaml import configure_names_with_yaml_content
from service_and_pages.pages.manual_enter import manual_enter_content
from service_and_pages.pages.dataset_health import dataset_health_content
from service_and_pages.pages.page3 import page3_content
from service_and_pages.service.DatasetProcessor import DatasetProcessor


class MultiPageApp:
    def __init__(self):
        self.dataset = DatasetProcessor()
        # Инициализация страниц
        self.create_routes()

    def create_routes(self):
        # маршруты для страниц
        ui.page('/')(self.start_page)
        ui.page('/new_project')(self.new_project)
        ui.page('/configure_names_with_yaml')(self.configure_names_with_yaml)
        ui.page('/manual_enter')(self.manual_enter)
        ui.page('/dataset_health')(self.dataset_health)
        ui.page('/page3')(self.page3)

    def start_page(self):
        # Начальная страница
        start_page_content(self)

    async def new_project(self):
        # включение директорий в датасет
        await new_project_content(self)

    async def configure_names_with_yaml(self):
        # включение директорий в датасет
        await configure_names_with_yaml_content(self)

    async def manual_enter(self):
        # Начальная страница
        await manual_enter_content(self)

    def dataset_health(self):
        # аналитика датасета
        dataset_health_content(self)

    def page3(self):
        """Третья страница."""
        page3_content(self)


if __name__ in {"__main__", "__mp_main__"}:
    app = MultiPageApp()
    ui.run()
