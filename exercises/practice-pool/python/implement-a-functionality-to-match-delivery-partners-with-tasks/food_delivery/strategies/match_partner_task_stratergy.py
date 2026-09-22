from abc import ABC, abstractmethod


class MatchPartnerTaskStrategy(ABC):

    @abstractmethod
    def match_partners_and_tasks(self, partners, tasks):
        pass
