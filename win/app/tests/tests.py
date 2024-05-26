from win.app.back.model_wrapper import Detector


def test_model_categories():
    print()
    for tolerance in range(0, 4):
        for no_face in [False, True]:
            print(f'Tolerance: {tolerance}, No Face: {no_face}\n\t{Detector.__generate_categories__(tolerance, no_face)}\n')