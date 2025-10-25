import pytest
from datetime import datetime, timedelta
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import warnings

from app.utils.orbit_calculation import OrbitCalculator


@pytest.fixture
def calculator():
    """Create an OrbitCalculator instance."""
    return OrbitCalculator()


@pytest.fixture
def sample_observation_time():
    """Create a sample observation time."""
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def ground_location():
    """Create a sample ground location."""
    return {
        "lat": 55.7558,  # Moscow latitude
        "lon": 37.6176,  # Moscow longitude
        "alt_m": 150,    # Height above sea level in meters
    }


def test_convert_horizontal_to_equatorial_success(calculator, sample_observation_time, ground_location):
    """Test successful conversion from horizontal to equatorial coordinates."""
    # Test with known values
    ra, dec = calculator.convert_horizontal_to_equatorial(
        altitude=45.0,
        azimuth=90.0,
        obs_time=sample_observation_time,
        **ground_location
    )

    # Assertions
    assert isinstance(ra, float)
    assert isinstance(dec, float)
    # RA should be between 0 and 360 degrees
    assert 0 <= ra < 360
    # Dec should be between -90 and 90 degrees
    assert -90 <= dec <= 90


def test_convert_horizontal_to_equatorial_invalid_altitude(calculator, sample_observation_time, ground_location):
    """Test conversion with invalid altitude."""
    with pytest.raises(ValueError, match="Ошибка преобразования координат"):
        calculator.convert_horizontal_to_equatorial(
            altitude=100.0,  # Invalid altitude (> 90 degrees)
            azimuth=0.0,
            obs_time=sample_observation_time,
            **ground_location
        )


def test_convert_horizontal_to_equatorial_invalid_azimuth(calculator, sample_observation_time, ground_location):
    """Test conversion with invalid azimuth."""
    # Azimuth should be able to handle values outside 0-360 range (they should be normalized)
    ra, dec = calculator.convert_horizontal_to_equatorial(
        altitude=45.0,
        azimuth=450.0,  # Should be normalized to 90 degrees
        obs_time=sample_observation_time,
        **ground_location
    )

    # Assertions
    assert isinstance(ra, float)
    assert isinstance(dec, float)
    assert 0 <= ra < 360
    assert -90 <= dec <= 90


def test_calculate_orbit_insufficient_observations(calculator):
    """Test orbit calculation with insufficient observations."""
    observations = [
        {
            "ra": 100.0,
            "dec": 10.0,
            "observation_time": datetime(2025, 1, 1, 12, 0, 0)
        }
    ]

    with pytest.raises(ValueError, match="Требуется минимум 3 наблюдения"):
        calculator.calculate_orbit(observations)


def test_calculate_orbit_missing_keys(calculator):
    """Test orbit calculation with missing required keys."""
    observations = [
        {
            "ra": 100.0,
            "observation_time": datetime(2025, 1, 1, 12, 0, 0)  # Missing 'dec'
        },
        {
            "ra": 101.0,
            "dec": 11.0,
            "observation_time": datetime(2025, 1, 2, 12, 0, 0)
        },
        {
            "ra": 102.0,
            "dec": 12.0,
            "observation_time": datetime(2025, 1, 3, 12, 0, 0)
        }
    ]

    with pytest.raises(ValueError, match="не содержит полей"):
        calculator.calculate_orbit(observations)


def test_calculate_orbit_empty_list(calculator):
    """Test orbit calculation with empty list."""
    with pytest.raises(ValueError, match="Требуется минимум 3 наблюдения"):
        calculator.calculate_orbit([])


def test_calculate_orbit_success_elliptic(calculator):
    """Test successful orbit calculation for elliptic orbit."""
    # Mock the least_squares function to return a successful result
    with patch('app.utils.orbit_calculation.least_squares') as mock_least_squares:
        # Create a mock result that simulates successful optimization
        mock_result = Mock()
        mock_result.success = True
        mock_result.x = [2.5, 0.1, 5.0, 45.0, 30.0, 0.0]  # a, ecc, inc, raan, argp, nu
        mock_least_squares.return_value = mock_result

        # Mock solar system ephemeris and orbit propagation
        with patch('app.utils.orbit_calculation.solar_system_ephemeris'), \
             patch('app.utils.orbit_calculation.get_body_barycentric'), \
             patch('app.utils.orbit_calculation.Orbit') as mock_orbit_class:
            
            # Mock the orbit object and its methods
            mock_orbit = Mock()
            mock_orbit_class.from_classical.return_value = mock_orbit
            mock_orbit.time_to_anomaly.return_value = 15 * 24 * 3600 * u.second  # 15 days

            observations = [
                {
                    "ra": 100.0,
                    "dec": 10.0,
                    "observation_time": datetime(2025, 1, 1, 12, 0, 0)
                },
                {
                    "ra": 101.0,
                    "dec": 10.5,
                    "observation_time": datetime(2025, 1, 2, 12, 0, 0)
                },
                {
                    "ra": 102.0,
                    "dec": 11.0,
                    "observation_time": datetime(2025, 1, 3, 12, 0, 0)
                }
            ]

            result = calculator.calculate_orbit(observations)

            # Assertions
            assert isinstance(result, dict)
            assert "semi_major_axis" in result
            assert "eccentricity" in result
            assert "inclination" in result
            assert "longitude_ascending_node" in result
            assert "argument_periapsis" in result
            assert "periapsis_time" in result

            # Check data types and values
            assert isinstance(result["semi_major_axis"], float)
            assert result["semi_major_axis"] > 0
            assert isinstance(result["eccentricity"], float)
            assert 0 <= result["eccentricity"] < 1  # Elliptic orbit
            assert isinstance(result["inclination"], float)
            assert 0 <= result["inclination"] <= 180
            assert isinstance(result["longitude_ascending_node"], float)
            assert 0 <= result["longitude_ascending_node"] <= 360
            assert isinstance(result["argument_periapsis"], float)
            assert 0 <= result["argument_periapsis"] <= 360
            assert isinstance(result["periapsis_time"], datetime)


def test_calculate_orbit_success_hyperbolic(calculator):
    """Test successful orbit calculation for hyperbolic orbit."""
    # Mock the least_squares function to return a successful result with hyperbolic orbit
    with patch('app.utils.orbit_calculation.least_squares') as mock_least_squares:
        # Create a mock result that simulates successful optimization
        mock_result = Mock()
        mock_result.success = True
        mock_result.x = [2.5, 1.2, 5.0, 45.0, 30.0, 0.0]  # a, ecc (>1 for hyperbolic), inc, raan, argp, nu
        mock_least_squares.return_value = mock_result

        # Mock solar system ephemeris and orbit propagation
        with patch('app.utils.orbit_calculation.solar_system_ephemeris'), \
             patch('app.utils.orbit_calculation.get_body_barycentric'), \
             patch('app.utils.orbit_calculation.Orbit') as mock_orbit_class:
            
            # Mock the orbit object and its methods
            mock_orbit = Mock()
            mock_orbit_class.from_classical.return_value = mock_orbit
            mock_orbit.time_to_anomaly.return_value = 15 * 24 * 3600 * u.second  # 15 days

            observations = [
                {
                    "ra": 100.0,
                    "dec": 10.0,
                    "observation_time": datetime(2025, 1, 1, 12, 0, 0)
                },
                {
                    "ra": 101.0,
                    "dec": 10.5,
                    "observation_time": datetime(2025, 1, 2, 12, 0, 0)
                },
                {
                    "ra": 102.0,
                    "dec": 11.0,
                    "observation_time": datetime(2025, 1, 3, 12, 0, 0)
                }
            ]

            result = calculator.calculate_orbit(observations)

            # Assertions
            assert isinstance(result, dict)
            # For hyperbolic orbits, semi_major_axis should be None
            assert result["semi_major_axis"] is None
            assert isinstance(result["eccentricity"], float)
            assert result["eccentricity"] >= 1  # Hyperbolic orbit


def test_calculate_orbit_optimization_failure(calculator):
    """Test orbit calculation when optimization fails."""
    # Mock the least_squares function to return a failed result
    with patch('app.utils.orbit_calculation.least_squares') as mock_least_squares:
        # Create a mock result that simulates failed optimization
        mock_result = Mock()
        mock_result.success = False
        mock_result.message = "Optimization failed to converge"
        mock_least_squares.return_value = mock_result

        # Mock solar system ephemeris and orbit propagation
        with patch('app.utils.orbit_calculation.solar_system_ephemeris'), \
             patch('app.utils.orbit_calculation.get_body_barycentric'), \
             patch('app.utils.orbit_calculation.Orbit') as mock_orbit_class:
            
            # Mock the orbit object and its methods
            mock_orbit = Mock()
            mock_orbit_class.from_classical.return_value = mock_orbit
            mock_orbit.time_to_anomaly.return_value = 15 * 24 * 3600 * u.second  # 15 days

            observations = [
                {
                    "ra": 100.0,
                    "dec": 10.0,
                    "observation_time": datetime(2025, 1, 1, 12, 0, 0)
                },
                {
                    "ra": 101.0,
                    "dec": 10.5,
                    "observation_time": datetime(2025, 1, 2, 12, 0, 0)
                },
                {
                    "ra": 102.0,
                    "dec": 11.0,
                    "observation_time": datetime(2025, 1, 3, 12, 0, 0)
                }
            ]

            with pytest.warns(UserWarning, match="Оптимизация не сошлась"):
                result = calculator.calculate_orbit(observations)

            # Should still return a result with initial approximation values
            assert isinstance(result, dict)
            assert "eccentricity" in result
            assert "inclination" in result


def test_calculate_orbit_periapsis_time_failure(calculator):
    """Test orbit calculation when periapsis time calculation fails."""
    # Mock the least_squares function to return a successful result
    with patch('app.utils.orbit_calculation.least_squares') as mock_least_squares:
        # Create a mock result that simulates successful optimization
        mock_result = Mock()
        mock_result.success = True
        mock_result.x = [2.5, 0.1, 5.0, 45.0, 30.0, 0.0]
        mock_least_squares.return_value = mock_result

        # Mock solar system ephemeris and orbit propagation
        with patch('app.utils.orbit_calculation.solar_system_ephemeris'), \
             patch('app.utils.orbit_calculation.get_body_barycentric'), \
             patch('app.utils.orbit_calculation.Orbit') as mock_orbit_class:
            
            # Mock the orbit object to raise an exception when from_classical is called
            mock_orbit_class.from_classical.side_effect = Exception("Orbit creation failed")

            observations = [
                {
                    "ra": 100.0,
                    "dec": 10.0,
                    "observation_time": datetime(2025, 1, 1, 12, 0, 0)
                },
                {
                    "ra": 101.0,
                    "dec": 10.5,
                    "observation_time": datetime(2025, 1, 2, 12, 0, 0)
                },
                {
                    "ra": 102.0,
                    "dec": 11.0,
                    "observation_time": datetime(2025, 1, 3, 12, 0, 0)
                }
            ]

            with pytest.warns(UserWarning, match="Не удалось вычислить время перигелия"):
                result = calculator.calculate_orbit(observations)

            # Should still return a result with fallback periapsis time
            assert isinstance(result, dict)
            assert "periapsis_time" in result
            assert result["periapsis_time"] == observations[0]["observation_time"]


def test_calculate_closest_approach_elliptic_orbit(calculator, sample_observation_time):
    """Test closest approach calculation for elliptic orbit."""
    # Define orbit elements
    orbit_elements = {
        "semi_major_axis": 2.5,  # AU
        "eccentricity": 0.1,
        "inclination": 5.0,
        "longitude_ascending_node": 45.0,
        "argument_periapsis": 30.0,
        "periapsis_time": sample_observation_time
    }

    start_time = sample_observation_time
    end_time = sample_observation_time + timedelta(days=365)
    
    # Mock the orbit propagation and calculations
    with patch('app.utils.orbit_calculation.solar_system_ephemeris'), \
         patch('app.utils.orbit_calculation.get_body_barycentric'), \
         patch('app.utils.orbit_calculation.Orbit') as mock_orbit_class:
        
        # Mock the orbit object and its methods
        mock_orbit = Mock()
        mock_orbit_class.from_classical.return_value = mock_orbit
        
        # Mock the propagate method to return a CartesianRepresentation
        mock_cartesian = Mock()
        mock_cartesian.cartesian.xyz.T = np.array([[1e8, 1e8, 1e8]] * 1000) * u.km
        mock_orbit.propagate.return_value = mock_cartesian

        result = calculator.calculate_closest_approach(
            orbit_elements=orbit_elements,
            start_time=start_time,
            end_time=end_time,
            time_steps=100
        )

        # Assertions
        assert isinstance(result, dict)
        assert "time" in result
        assert "distance_au" in result
        assert "distance_km" in result
        
        assert isinstance(result["time"], datetime)
        assert isinstance(result["distance_au"], float)
        assert isinstance(result["distance_km"], float)
        
        assert result["distance_au"] >= 0
        assert result["distance_km"] >= 0
        assert result["distance_km"] == result["distance_au"] * 149_597_870.7


def test_calculate_closest_approach_hyperbolic_orbit(calculator, sample_observation_time):
    """Test closest approach calculation for hyperbolic orbit."""
    # Define orbit elements for hyperbolic orbit (semi_major_axis = None)
    orbit_elements = {
        "semi_major_axis": None,
        "eccentricity": 1.2,
        "inclination": 5.0,
        "longitude_ascending_node": 45.0,
        "argument_periapsis": 30.0,
        "periapsis_time": sample_observation_time
    }

    start_time = sample_observation_time
    end_time = sample_observation_time + timedelta(days=365)
    
    # Mock the orbit propagation and calculations
    with patch('app.utils.orbit_calculation.solar_system_ephemeris'), \
         patch('app.utils.orbit_calculation.get_body_barycentric'), \
         patch('app.utils.orbit_calculation.Orbit') as mock_orbit_class:
        
        # Mock the orbit object and its methods
        mock_orbit = Mock()
        mock_orbit_class.from_classical.return_value = mock_orbit
        
        # Mock the propagate method to return a CartesianRepresentation
        mock_cartesian = Mock()
        mock_cartesian.cartesian.xyz.T = np.array([[1e8, 1e8, 1e8]] * 1000) * u.km
        mock_orbit.propagate.return_value = mock_cartesian

        result = calculator.calculate_closest_approach(
            orbit_elements=orbit_elements,
            start_time=start_time,
            end_time=end_time,
            time_steps=100
        )

        # Assertions
        assert isinstance(result, dict)
        assert "time" in result
        assert "distance_au" in result
        assert "distance_km" in result


def test_calculate_closest_approach_orbit_creation_failure(calculator, sample_observation_time):
    """Test closest approach calculation when orbit creation fails."""
    # Define orbit elements
    orbit_elements = {
        "semi_major_axis": 2.5,
        "eccentricity": 0.1,
        "inclination": 5.0,
        "longitude_ascending_node": 45.0,
        "argument_periapsis": 30.0,
        "periapsis_time": sample_observation_time
    }

    start_time = sample_observation_time
    end_time = sample_observation_time + timedelta(days=365)
    
    # Mock the Orbit.from_classical to raise an exception
    with patch('app.utils.orbit_calculation.Orbit') as mock_orbit_class:
        mock_orbit_class.from_classical.side_effect = Exception("Orbit creation failed")
        
        with pytest.warns(UserWarning, match="Не удалось создать орбиту для расчёта сближения"):
            result = calculator.calculate_closest_approach(
                orbit_elements=orbit_elements,
                start_time=start_time,
                end_time=end_time
            )

        # Should return fallback values
        assert isinstance(result, dict)
        assert result["time"] == start_time
        assert result["distance_au"] == 1.0
        assert result["distance_km"] == 149_597_870.7


def test_calculate_closest_approach_propagation_failure(calculator, sample_observation_time):
    """Test closest approach calculation when orbit propagation fails."""
    # Define orbit elements
    orbit_elements = {
        "semi_major_axis": 2.5,
        "eccentricity": 0.1,
        "inclination": 5.0,
        "longitude_ascending_node": 45.0,
        "argument_periapsis": 30.0,
        "periapsis_time": sample_observation_time
    }

    start_time = sample_observation_time
    end_time = sample_observation_time + timedelta(days=365)
    
    # Mock the orbit propagation to raise an exception
    with patch('app.utils.orbit_calculation.solar_system_ephemeris'), \
         patch('app.utils.orbit_calculation.get_body_barycentric'), \
         patch('app.utils.orbit_calculation.Orbit') as mock_orbit_class:
        
        # Mock the orbit object and its methods
        mock_orbit = Mock()
        mock_orbit_class.from_classical.return_value = mock_orbit
        
        # Mock the propagate method to raise an exception
        mock_orbit.propagate.side_effect = Exception("Propagation failed")

        with pytest.warns(UserWarning, match="Ошибка при расчёте сближения"):
            result = calculator.calculate_closest_approach(
                orbit_elements=orbit_elements,
                start_time=start_time,
                end_time=end_time
            )

        # Should return fallback values
        assert isinstance(result, dict)
        assert result["time"] == start_time
        assert result["distance_au"] == 1.0
        assert result["distance_km"] == 149_597_870.7


def test_calculate_closest_approach_minimum_distance(calculator, sample_observation_time):
    """Test that closest approach finds the minimum distance."""
    # Define orbit elements
    orbit_elements = {
        "semi_major_axis": 2.5,
        "eccentricity": 0.1,
        "inclination": 5.0,
        "longitude_ascending_node": 45.0,
        "argument_periapsis": 30.0,
        "periapsis_time": sample_observation_time
    }

    start_time = sample_observation_time
    end_time = sample_observation_time + timedelta(days=365)
    
    # Mock the orbit propagation and calculations with specific distances
    with patch('app.utils.orbit_calculation.solar_system_ephemeris'), \
         patch('app.utils.orbit_calculation.get_body_barycentric'), \
         patch('app.utils.orbit_calculation.Orbit') as mock_orbit_class:
        
        # Mock the orbit object and its methods
        mock_orbit = Mock()
        mock_orbit_class.from_classical.return_value = mock_orbit
        
        # Mock the propagate method to return a CartesianRepresentation
        mock_cartesian = Mock()
        # Create distances that have a clear minimum at index 50
        distances = np.ones(1000)
        distances[50] = 0.5  # Minimum distance
        mock_cartesian.cartesian.xyz.T = np.array([[1e8, 1e8, 1e8]] * 1000) * u.km
        mock_orbit.propagate.return_value = mock_cartesian

        # Mock get_body_barycentric to return consistent values
        with patch('app.utils.orbit_calculation.get_body_barycentric') as mock_get_body:
            mock_get_body.return_value.x.to.return_value.value = 0
            mock_get_body.return_value.y.to.return_value.value = 0
            mock_get_body.return_value.z.to.return_value.value = 0

            result = calculator.calculate_closest_approach(
                orbit_elements=orbit_elements,
                start_time=start_time,
                end_time=end_time,
                time_steps=1000
            )

        # Assertions
        assert isinstance(result, dict)
        assert result["distance_au"] == 0.5  # Should find the minimum distance
