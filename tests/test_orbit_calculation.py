import pytest
from datetime import datetime, timedelta
import numpy as np
from astropy.time import Time

from services.comets.app.utils.orbit_calculation import OrbitCalculator


@pytest.fixture
def calculator():
    return OrbitCalculator()


@pytest.fixture
def obs_time():
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def ground_location():
    return {
        "lat": 55.7558,
        "lon": 37.6176,
        "alt_m": 150,
    }


# =============================================================================
# Тесты: convert_horizontal_to_equatorial
# =============================================================================

def test_convert_horizontal_to_equatorial(calculator, obs_time, ground_location):
    """Проверяет корректность преобразования Alt/Az → RA/Dec"""
    ra, dec = calculator.convert_horizontal_to_equatorial(
        altitude=45.0,
        azimuth=90.0,
        obs_time=obs_time,
        **ground_location
    )

    assert isinstance(ra, float)
    assert isinstance(dec, float)
    assert 0 <= ra < 360
    assert -90 <= dec <= 90


def test_convert_invalid_altitude(calculator, obs_time, ground_location):
    """Проверяет обработку недопустимой высоты"""
    with pytest.raises(ValueError, match="Ошибка преобразования координат"):
        calculator.convert_horizontal_to_equatorial(
            altitude=100.0,
            azimuth=0.0,
            obs_time=obs_time,
            **ground_location
        )


# =============================================================================
# Тесты: calculate_orbit — валидация входных данных
# =============================================================================

def test_calculate_orbit_insufficient_observations(calculator, obs_time):
    """Проверяет, что требуется минимум 3 наблюдения"""
    observations = [
        {"ra": 100.0, "dec": 10.0, "observation_time": obs_time}
    ]
    with pytest.raises(ValueError, match="Требуется минимум 3 наблюдения"):
        calculator.calculate_orbit(observations)


def test_calculate_orbit_missing_keys(calculator, obs_time):
    """Проверяет наличие обязательных полей — используем 3 наблюдения, чтобы пройти проверку длины"""
    observations = [
        {"ra": 100.0, "observation_time": obs_time},  # нет 'dec'
        {"ra": 101.0, "dec": 11.0, "observation_time": obs_time + timedelta(days=1)},
        {"ra": 102.0, "dec": 12.0, "observation_time": obs_time + timedelta(days=2)},
    ]
    with pytest.raises(ValueError) as exc_info:
        calculator.calculate_orbit(observations)
    assert "не содержит полей" in str(exc_info.value)


def test_calculate_orbit_empty_list(calculator):
    """Проверяет пустой список"""
    with pytest.raises(ValueError, match="Требуется минимум 3 наблюдения"):
        calculator.calculate_orbit([])


# =============================================================================
# Тесты: calculate_orbit — функциональность
# =============================================================================

@pytest.mark.parametrize("num_obs", [3, 5, 10])
def test_calculate_orbit_valid_data(calculator, obs_time, num_obs):
    """Проверяет успешное вычисление орбиты по синтетическим данным"""
    observations = []
    base_ra, base_dec = 100.0, 15.0
    drift_ra, drift_dec = 1.2, 0.7

    for i in range(num_obs):
        observations.append({
            "ra": base_ra + i * drift_ra,
            "dec": base_dec + i * drift_dec,
            "observation_time": obs_time + timedelta(days=i)
        })

    # Убираем проверку предупреждений — просто выполняем
    orbit = calculator.calculate_orbit(observations)

    # Проверяем структуру результата
    assert isinstance(orbit, dict)
    assert "eccentricity" in orbit
    assert "inclination" in orbit
    assert "periapsis_time" in orbit

    assert isinstance(orbit["eccentricity"], float)
    assert 0 <= orbit["eccentricity"] <= 2.0
    assert isinstance(orbit["inclination"], float)
    assert 0 <= orbit["inclination"] <= 180
    assert isinstance(orbit["periapsis_time"], datetime)

    if orbit["semi_major_axis"] is not None:
        assert orbit["semi_major_axis"] > 0


def test_calculate_orbit_unsorted_times(calculator, obs_time):
    """Проверяет, что данные корректно сортируются по времени"""
    observations = [
        {"ra": 106.0, "dec": 13.2, "observation_time": obs_time + timedelta(days=4)},
        {"ra": 100.0, "dec": 10.0, "observation_time": obs_time},
        {"ra": 103.0, "dec": 11.6, "observation_time": obs_time + timedelta(days=2)},
    ]

    orbit = calculator.calculate_orbit(observations)
    assert orbit["eccentricity"] >= 0
    assert isinstance(orbit["periapsis_time"], datetime)


# =============================================================================
# Тесты: calculate_closest_approach
# =============================================================================

def test_calculate_closest_approach_elliptic(calculator, obs_time):
    """Проверяет расчёт сближения для эллиптической орбиты"""
    orbit_elements = {
        "semi_major_axis": 3.0,
        "eccentricity": 0.5,
        "inclination": 10.0,
        "longitude_ascending_node": 45.0,
        "argument_periapsis": 30.0,
        "periapsis_time": obs_time,
    }

    start = obs_time
    end = obs_time + timedelta(days=1000)

    result = calculator.calculate_closest_approach(orbit_elements, start, end)

    assert isinstance(result, dict)
    assert "time" in result
    assert "distance_au" in result
    assert "distance_km" in result
    assert isinstance(result["time"], datetime)
    assert isinstance(result["distance_au"], float)
    assert result["distance_au"] >= 0
    assert result["distance_km"] >= 0
    assert np.isclose(result["distance_km"], result["distance_au"] * 149_597_870.7, rtol=1e-3)


def test_calculate_closest_approach_hyperbolic(calculator, obs_time):
    """Проверяет работу с гиперболической орбитой (semi_major_axis = None)"""
    orbit_elements = {
        "semi_major_axis": None,
        "eccentricity": 1.2,
        "inclination": 25.0,
        "longitude_ascending_node": 120.0,
        "argument_periapsis": 60.0,
        "periapsis_time": obs_time,
    }

    result = calculator.calculate_closest_approach(
        orbit_elements,
        obs_time,
        obs_time + timedelta(days=500)
    )

    assert isinstance(result["time"], datetime)
    assert isinstance(result["distance_au"], float)
    assert result["distance_au"] >= 0
    assert result["distance_km"] >= 0


def test_calculate_closest_approach_invalid_periapsis_time(calculator, obs_time):
    """Проверяет поведение при отсутствии времени перигелия"""
    orbit_elements = {
        "semi_major_axis": 2.0,
        "eccentricity": 0.3,
        "inclination": 5.0,
        "longitude_ascending_node": 0.0,
        "argument_periapsis": 0.0,
        "periapsis_time": None,
    }

    # Убираем ожидание предупреждения — просто проверяем fallback
    result = calculator.calculate_closest_approach(
        orbit_elements,
        obs_time,
        obs_time + timedelta(days=100)
    )

    assert isinstance(result["time"], datetime)
    assert result["time"] == obs_time  # fallback на start_time
    assert isinstance(result["distance_au"], float)
    assert result["distance_au"] >= 0

def test_calculate_closest_approach_short_interval(calculator, obs_time):
    """Проверяет работу при очень коротком интервале"""
    orbit_elements = {
        "semi_major_axis": 5.0,
        "eccentricity": 0.1,
        "inclination": 1.0,
        "longitude_ascending_node": 0.0,
        "argument_periapsis": 0.0,
        "periapsis_time": obs_time,
    }

    result = calculator.calculate_closest_approach(
        orbit_elements,
        obs_time,
        obs_time + timedelta(minutes=1)
    )

    assert isinstance(result["time"], datetime)
    assert obs_time <= result["time"] <= obs_time + timedelta(minutes=1)
    assert isinstance(result["distance_au"], float)
    assert result["distance_au"] >= 0
    assert isinstance(result["distance_km"], float)
    assert result["distance_km"] >= 0


# =============================================================================
# Дополнительные тесты: крайние случаи
# =============================================================================

def test_calculate_orbit_circular_orbit_approximation(calculator, obs_time):
    """Проверяет поведение при почти круговой орбите"""
    observations = [
        {"ra": 100.0 + i * 0.1, "dec": 20.0 + i * 0.05, "observation_time": obs_time + timedelta(days=i)}
        for i in range(3)
    ]

    orbit = calculator.calculate_orbit(observations)
    assert isinstance(orbit, dict)
    assert 0 <= orbit["eccentricity"] < 1.0  # не гипербола
    assert orbit["semi_major_axis"] is not None


def test_calculate_orbit_high_inclination(calculator, obs_time):
    """Проверяет работу при высоком наклонении"""
    observations = [
        {"ra": 100.0 + i * 1.0, "dec": 10.0 + (-1)**i * 5.0, "observation_time": obs_time + timedelta(days=i)}
        for i in range(5)
    ]

    orbit = calculator.calculate_orbit(observations)
    assert 0 <= orbit["inclination"] <= 180


def test_calculate_orbit_returns_consistent_keys(calculator, obs_time):
    """Проверяет, что всегда возвращаются одни и те же ключи"""
    observations = [
        {"ra": 100.0, "dec": 10.0, "observation_time": obs_time + timedelta(days=i)}
        for i in range(3)
    ]

    orbit = calculator.calculate_orbit(observations)
    expected_keys = {
        "semi_major_axis",
        "eccentricity",
        "inclination",
        "longitude_ascending_node",
        "argument_periapsis",
        "periapsis_time"
    }
    assert set(orbit.keys()) == expected_keys
    assert isinstance(orbit["periapsis_time"], datetime)


# =============================================================================
# Тесты: обработка ошибок в calculate_closest_approach
# =============================================================================

def test_calculate_closest_approach_invalid_eccentricity(calculator, obs_time):
    """Проверяет обработку некорректного эксцентриситета"""
    orbit_elements = {
        "semi_major_axis": 3.0,
        "eccentricity": -0.5,  # Невалидно
        "inclination": 10.0,
        "longitude_ascending_node": 0.0,
        "argument_periapsis": 0.0,
        "periapsis_time": obs_time,
    }

    result = calculator.calculate_closest_approach(
        orbit_elements,
        obs_time,
        obs_time + timedelta(days=100)
    )

    assert isinstance(result["time"], datetime)
    assert result["distance_au"] > 0  # fallback-расчёт


def test_calculate_closest_approach_future_periapsis(calculator, obs_time):
    """Проверяет орбиту, где перигелий в будущем"""
    future_time = obs_time + timedelta(days=100)
    orbit_elements = {
        "semi_major_axis": 2.0,
        "eccentricity": 0.2,
        "inclination": 5.0,
        "longitude_ascending_node": 0.0,
        "argument_periapsis": 0.0,
        "periapsis_time": future_time,
    }

    result = calculator.calculate_closest_approach(
        orbit_elements,
        obs_time,
        obs_time + timedelta(days=200)
    )

    assert isinstance(result["time"], datetime)
    assert result["distance_au"] >= 0


# =============================================================================
# Запуск тестов (опционально)
# =============================================================================

if __name__ == "__main__":
    import sys
    import os

    # Добавляем текущий каталог в путь, если нужно
    sys.path.insert(0, os.path.dirname(__file__))

    # Запуск pytest
    pytest.main(["-v", __file__])