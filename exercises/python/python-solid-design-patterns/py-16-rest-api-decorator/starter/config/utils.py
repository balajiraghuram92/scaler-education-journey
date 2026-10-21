class ApiUtils:
    @staticmethod
    def log_request(request_data):
        print(f"Request data: {request_data}")
    
    @staticmethod
    def apply_rate_limit(request_data):
        print(f"Rate limit applied for request: {request_data}")