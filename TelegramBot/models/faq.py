from dataclasses import dataclass

@dataclass
class FAQ:
    id: int
    question: str
    answer: str

    @classmethod
    def from_dict(cls, data: dict) -> "FAQ":
        return cls(
            id=data["id"],
            question=data["question"],
            answer=data["answer"],
        )