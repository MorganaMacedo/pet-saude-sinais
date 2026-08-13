import numpy as np

from training.train import fit_temperature, grouped_three_way_split, temperature_scale


def test_grouped_split_keeps_participants_separate():
    labels = np.asarray((["normal"] * 30 + ["alterado"] * 30) * 2)
    groups = np.asarray([f"p-{index}" for index in range(60) for _ in range(2)])
    train, calibration, test = grouped_three_way_split(labels, groups, 0.2, 0.15, 42)
    train_groups = set(groups[train])
    calibration_groups = set(groups[calibration])
    test_groups = set(groups[test])
    assert train_groups.isdisjoint(calibration_groups)
    assert train_groups.isdisjoint(test_groups)
    assert calibration_groups.isdisjoint(test_groups)


def test_temperature_calibration_preserves_distributions():
    classes = np.asarray(["alterado", "normal"])
    labels = np.asarray(["alterado", "normal", "alterado", "normal"])
    probabilities = np.asarray([[0.8, 0.2], [0.3, 0.7], [0.65, 0.35], [0.1, 0.9]])
    temperature = fit_temperature(labels, probabilities, classes)
    calibrated = temperature_scale(probabilities, temperature)
    assert 0.2 <= temperature <= 5
    assert np.allclose(calibrated.sum(axis=1), 1)
    assert np.all(calibrated >= 0)
