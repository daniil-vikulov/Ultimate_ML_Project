from nudenet import NudeDetector


class Detector:
    def __init__(self, tolerance=0, no_face=False):
        """
            Creates an instance of the Nude Detector model.

            Args:
                no_face (bool): If True, faces will be censored; if False, they will not.
                tolerance (int): Specifies the sensitivity of nudity detection, where each level includes more body parts considered explicit. The default value is 0.
                    - 0 (low): Includes basic nudity detection:
                        * BUTTOCKS_EXPOSED
                        * FEMALE_GENITALIA_EXPOSED
                        * MALE_GENITALIA_EXPOSED
                        * ANUS_EXPOSED
                    - 1 (medium): Includes level 0 plus:
                        * FEMALE_BREAST_EXPOSED
                    - 2 (high): Includes level 1 plus:
                        * FEMALE_GENITALIA_COVERED
                        * MALE_BREAST_EXPOSED
                        * FEET_EXPOSED
                        * BELLY_EXPOSED
                        * ANUS_COVERED
                        * BUTTOCKS_COVERED
                        * ARMPITS_EXPOSED
                    - 3 (overdrive): Includes all previous levels plus:
                        * BELLY_COVERED
                        * FEET_COVERED
                        * ARMPITS_COVERED
                        * FEMALE_BREAST_COVERED

            Returns:
                None
            """

        self.detector = NudeDetector()
        self.explicit_categories = self.generate_categories(tolerance, no_face)

    @staticmethod
    def generate_categories(tolerance, no_face) -> []:
        explicit_categories = []
        if no_face:
            explicit_categories.append('FACE_FEMALE')
            explicit_categories.append('FACE_MALE')

        explicit_categories.append('BUTTOCKS_EXPOSED')
        explicit_categories.append('FEMALE_GENITALIA_EXPOSED')
        explicit_categories.append('MALE_GENITALIA_EXPOSED')
        explicit_categories.append('MALE_GENITALIA_EXPOSED')

        if tolerance > 0:
            explicit_categories.append('FEMALE_BREAST_EXPOSED')

        if tolerance > 1:
            explicit_categories.append('FEMALE_GENITALIA_COVERED')
            explicit_categories.append('MALE_BREAST_EXPOSED')
            explicit_categories.append('FEET_EXPOSED')
            explicit_categories.append('BELLY_EXPOSED')
            explicit_categories.append('ANUS_COVERED')
            explicit_categories.append('BUTTOCKS_COVERED')
            explicit_categories.append('ARMPITS_EXPOSED')

        if tolerance == 3:
            explicit_categories.append('BELLY_COVERED')
            explicit_categories.append('FEET_COVERED')
            explicit_categories.append('ARMPITS_COVERED')
            explicit_categories.append('FEMALE_BREAST_COVERED')

        return explicit_categories
