"""Helpers that turn structured LLM findings into guided questions."""

from typing import List

from app.services.interaction.contracts import InteractionQuestion


def build_questions_from_missing(missing_blocks: List[str]) -> List[InteractionQuestion]:
    """Builds the guided questions associated with one missing-group analysis result."""

    questions: List[InteractionQuestion] = []
    for missing in missing_blocks:
        if missing == "Algorithm":
            questions.append(
                InteractionQuestion(
                    id="q_algorithm",
                    text="What type of algorithm will be used?",
                    scope="missing_information",
                    options=[
                        "Greedy",
                        "Dynamic Programming",
                        "Quantum Search",
                        "Other",
                    ],
                )
            )
        elif missing == "Programming":
            questions.append(
                InteractionQuestion(
                    id="q_programming",
                    text="Which framework/language will be used for development?",
                    scope="missing_information",
                    options=["Python", "Rust", "Q#", "Other"],
                )
            )
        elif missing == "Integration_model":
            questions.append(
                InteractionQuestion(
                    id="q_integration",
                    text="Which integration model will be used? (SOA, middleware, etc.)",
                    scope="missing_information",
                    options=["Middleware/API", "Microservices", "Quantum-SOA"],
                )
            )
        elif missing == "Quantum_HW_constraint":
            questions.append(
                InteractionQuestion(
                    id="q_hw",
                    text="Which hardware constraint is the most relevant?",
                    scope="missing_information",
                    options=[
                        "Qubits",
                        "Shots",
                        "Circuit depth",
                        "Error rate",
                        "Connectivity",
                        "Other",
                    ],
                )
            )
        elif missing == "Functionality":
            questions.append(
                InteractionQuestion(
                    id="q_functionality",
                    text="What main functionality should the system cover?",
                    scope="missing_information",
                )
            )
    return questions
