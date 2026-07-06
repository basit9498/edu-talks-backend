def escape_braces(text: str) -> str:
    return text.replace("{", "{{").replace("}", "}}")


def build_question_format_examples(question_types: list):
    examples = []

    for item in question_types:
        qtype = item["type"]

        if qtype == "mcqs":
            example = """
        {
        "question": "string",
        "question_type": "mcqs",
        "is_fixed_answer": true,
        "question_options": {
            "a": "option 1",
            "b": "option 2",
            "c": "option 3",
            "d": "option 4"
        },
        "correct_answer": ["a"]
        }
        """
        elif qtype == "fill_in_the_blank":
                    example = """
        {
        "question": "string with a blank ___",
        "question_type": "fill_in_the_blank",
        "is_fixed_answer": true,
        "question_options": {
            "a": "correct filled text",
            "b": "wrong option",
            "c": "wrong option",
            "d": "wrong option"
        },
        "correct_answer": ["a"]
        }
        """
        elif qtype == "short_question":
                    example = """
        {
        "question": "Explain X in 2-3 sentences.",
        "question_type": "short_question",
        "is_fixed_answer": false,
        "question_options": null,
        "correct_answer": null
        }
        """
        else:  # long_answer
                    example = """
        {
        "question": "Write a detailed explanation about X.",
        "question_type": "long_answer",
        "is_fixed_answer": false,
        "question_options": null,
        "correct_answer": null
        }
        """

        examples.append(example.strip())

    # Escape braces
    safe_examples = [escape_braces(e) for e in examples]

    return ",\n".join(safe_examples)



