from .model import AutoProtectStatus


class AutoProtectApi:
    def add_claim(self, amount):
        print("Submitting claim to AutoProtect")

    def get_status(self, claim_id):
        print("Getting claim status from AutoProtect")
        return AutoProtectStatus.APPROVED


class TravelGuardApi:
    def submit_claim(self, claim_id, amount):
        print("Submitting claim to TravelGuard")

    def get_claim_status(self, claim_id):
        print("Getting claim status from TravelGuard")
        return "SUCCESS"
