from typing import List
from .registry import ObserverRegistry
from .observer import Observer

class Publisher(ObserverRegistry):
    def __init__(self):
        self.observers: List[Observer] = []
    
    def add_observer(self, observer: Observer) -> None:
        self.observers.append(observer)
        
    def remove_observer(self, observer: Observer) -> None:
        self.observers.remove(observer)
        
    def notify_observers(self, stock_name: str, new_price: float) -> None:
        for observer in list(self.observers):
            observer.send_notification(stock_name, new_price)
