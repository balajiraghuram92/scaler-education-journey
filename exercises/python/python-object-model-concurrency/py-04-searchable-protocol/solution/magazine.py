class Magazine:
    def __init__(self, title, issue):
        self.title = title
        self.issue = issue
        self.is_available = True

    def matches(self, query: str) -> bool:
        return query.lower() in self.title.lower()
