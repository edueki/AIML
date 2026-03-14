from abc import ABC, abstractmethod

class UserBase(ABC):
    def __init__(self, username):
        self.username = username

    @abstractmethod
    def user_validation(self):
        pass




