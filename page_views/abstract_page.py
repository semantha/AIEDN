from abc import ABC, abstractmethod


class AbstractPage(ABC):
    def __init__(self, page_id):
        self.page_id = page_id

    def get_page_id(self):
        return self.page_id

    @abstractmethod
    def display_page(self):
        pass
