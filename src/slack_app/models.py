"""Slack /fb モーダル用のデータモデル"""

from dataclasses import dataclass


@dataclass
class CandidateData:
    """候補者・マスタ保存用のフォームデータ"""

    transcript: str = ""
    candidate_name: str = ""
    ca_person: str = ""
    qualifications: str = ""
    experience: str = ""
    age: str = ""
    desired_salary: str = ""
    proposed_company: str = ""
    appeal_to_needs: str = ""
    current_evaluation: str = ""

    def to_master_kwargs(self) -> dict:
        """save_candidate_to_master に渡す kwargs"""
        return {
            "candidate": self.candidate_name,
            "ca_person": self.ca_person,
            "qualifications": self.qualifications,
            "experience": self.experience,
            "age": self.age,
            "desired_salary": self.desired_salary,
            "proposed_company": self.proposed_company,
            "appeal_to_needs": self.appeal_to_needs,
            "current_evaluation": self.current_evaluation,
        }
