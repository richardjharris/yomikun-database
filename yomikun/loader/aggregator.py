from yomikun.models import Gender, NameData, NamePart


class Aggregator:
    """
    Legacy interface to code that now exists in NameData.
    """

    @staticmethod
    def copy_data_to_subreadings(data: NameData):
        data.copy_pseudo_data_to_subreadings()

    @staticmethod
    def extract_name_parts(data: NameData) -> list[tuple[NamePart, Gender | None]]:
        return data.extract_name_parts()
