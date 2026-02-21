"""Slack /fb モーダル用のデータモデル"""

from dataclasses import dataclass


@dataclass
class CandidateData:
    """候補者・マスタ保存用のフォームデータ（書き起こし・候補者名・担当者名）"""

    transcript: str = ""
    candidate_name: str = ""
    ca_person: str = ""

    def to_master_kwargs(self) -> dict:
        """save_candidate_to_master に渡す kwargs"""
        return {
            "candidate": self.candidate_name,
            "ca_person": self.ca_person,
        }
