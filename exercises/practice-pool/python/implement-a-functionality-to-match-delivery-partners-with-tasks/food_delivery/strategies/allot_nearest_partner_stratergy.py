from .match_partner_task_stratergy import MatchPartnerTaskStrategy
from food_delivery.models import Location


class AllotNearestPartnerStrategy(MatchPartnerTaskStrategy):

    def match_partners_and_tasks(self, partners, tasks):
        partner_set = set(partners)
        mapping = []

        for task in tasks:
            nearest_partner = AllotNearestPartnerStrategy.__find_nearest_partner(partner_set, task)
            partner_set.remove(nearest_partner)
            mapping.append((nearest_partner, task))

        return mapping

    @staticmethod
    def __find_nearest_partner(partners, task):
        closest_partner = None
        closest_distance = None

        for partner in partners:
            task_location = task.location
            partner_location = partner.location
            distance = AllotNearestPartnerStrategy.__calculate_distance(task_location, partner_location)
            if (not closest_distance) or (distance < closest_distance):
                closest_partner = partner
                closest_distance = distance

        return closest_partner

    @staticmethod
    def __calculate_distance(task_location: Location, partner_location: Location):
        distance = ((
                           (task_location.latitude - partner_location.latitude) ** 2 +
                           (task_location.longitude - partner_location.longitude) ** 2)
                    ** 0.5)
        return distance