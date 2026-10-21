"""Stand-in vendor SDK clients. Provided; do not edit.

AcmeClient.create_completion(*, messages, max_tokens) returns
    {"choices": [{"message": {"content": str}}],
     "usage": {"prompt_tokens": int, "completion_tokens": int}}
NimbusClient.generate(text, max_output_tokens) returns an object with the
    attributes ``output``, ``tokens_in`` and ``tokens_out``.
Both may raise ConnectionError or TimeoutError.
"""


class AcmeClient:
    def create_completion(self, *, messages: list[dict], max_tokens: int) -> dict:
        raise NotImplementedError


class NimbusClient:
    def generate(self, text: str, max_output_tokens: int):
        raise NotImplementedError
