from src.legal_archive import ArchiveDecision, MatterIntake, review_matter


class StubClient:
    def parse_pdf(self, pdf):
        return {"text": "Patient contact: a@clinic.example"}


def test_matter_with_parsed_text_is_ready_for_archive():
    decision = review_matter(MatterIntake("m-1", "encoded", True), StubClient())
    assert decision == ArchiveDecision("m-1", "Patient contact: a@clinic.example", ("email", "phone", "person_name", "address"), True)
