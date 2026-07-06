from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field,field_validator
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List



class QuestionType(str, Enum):
    fill_in_the_blank = "fill_in_the_blank"
    mcqs = "mcqs"
    short_question = "short_question"
    long_answer = "long_answer"


class PaperQuestionParser(BaseModel):
    question: str = Field(..., description="The question text.")

    question_type: QuestionType = Field(
        ..., 
        description="Question type enum: fill_in_the_blank, mcqs, short_question, long_answer"
    )

    is_fixed_answer: bool = Field(
        ..., 
        description="True for fill_in_the_blank or mcqs; False for short_question or long_answer"
    )

    question_options: Optional[Dict[str, str]] = Field(
        None,
        description="""
Options for fill_in_the_blank or mcqs.
Format:
{
    "a": "value1, value2",
    "b": "value1, value2",
    "c": "value1, value2",
    "d": "value1, value2"
}
For short_question and long_answer → must be empty / None.
"""
    )

    correct_answer: Optional[List[str]] = Field(
        None,
        description='Correct answers for fill_in_the_blank or mcqs. Example: ["a"], ["b"], ["c"].'
    )

    # ============================
    # VALIDATION RULES
    # ============================

    @field_validator("is_fixed_answer")
    def validate_is_fixed_answer(cls, v, info):
        qtype = info.data.get("question_type")

        if qtype in ["fill_in_the_blank", "mcqs"] and v is not True:
            raise ValueError("is_fixed_answer must be TRUE for fill_in_the_blank and mcqs")

        if qtype in ["short_question", "long_answer"] and v is not False:
            raise ValueError("is_fixed_answer must be FALSE for short_question and long_answer")

        return v


    @field_validator("question_options")
    def validate_question_options(cls, v, info):
        qtype = info.data.get("question_type")

        if qtype in ["short_question", "long_answer"]:
            if v not in [None, {}]:
                raise ValueError("question_options must be empty for short_question and long_answer")
            return None

        if qtype in ["fill_in_the_blank", "mcqs"]:
            if not isinstance(v, dict):
                raise ValueError("question_options must be a dictionary")

            required_keys = ["a", "b", "c", "d"]
            for key in required_keys:
                if key not in v:
                    raise ValueError(f"Missing option key: {key}")

            return v

        return v


    @field_validator("correct_answer")
    def validate_correct_answer(cls, v, info):
        qtype = info.data.get("question_type")

        if qtype in ["short_question", "long_answer"]:
            if v not in [None, []]:
                raise ValueError("correct_answer must be empty for short_question and long_answer")
            return None

        if qtype in ["fill_in_the_blank", "mcqs"]:
            if not isinstance(v, list):
                raise ValueError("correct_answer must be a list")

            for ans in v:
                if ans not in ["a", "b", "c", "d"]:
                    raise ValueError("correct_answer must contain only ['a','b','c','d']")

            return v

        return v





class PaperQuestionList(BaseModel):
    questions: List[PaperQuestionParser]

paper_question_parser = PydanticOutputParser(pydantic_object=PaperQuestionList)
