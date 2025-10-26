from astropy.time import Time
from astropy import units as u
from astropy.coordinates import (
    SkyCoord,
    EarthLocation,
    AltAz,
    solar_system_ephemeris,
    get_body_barycentric,
)
from poliastro.bodies import Sun
from poliastro.twobody import Orbit
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
import warnings
from scipy.optimize import least_squares


class OrbitCalculator:
    """
    Калькулятор орбиты кометы по множеству наблюдений.
    Использует метод наименьших квадратов для определения орбиты по RA/Dec + времени.
    Поддерживает преобразование Alt/Az → RA/Dec.
    """

    def convert_horizontal_to_equatorial(
        self,
        altitude: float,
        azimuth: float,
        lat: float,
        lon: float,
        alt_m: float,
        obs_time: datetime,
    ) -> tuple[float, float]:
        """
        Преобразует горизонтальные координаты (высота, азимут) в экваториальные (RA, Dec).

        Параметры:
            altitude (float): высота в градусах
            azimuth (float): азимут в градусах
            lat (float): широта наблюдателя в градусах
            lon (float): долгота наблюдателя в градусах
            alt_m (float): высота над уровнем моря в метрах
            obs_time (datetime): время наблюдения

        Возвращает:
            tuple[float, float]: (RA в градусах, Dec в градусах)
        """
        try:
            location = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=alt_m * u.m)
            time = Time(obs_time)
            altaz = AltAz(obstime=time, location=location, alt=altitude * u.deg, az=azimuth * u.deg)
            coord = SkyCoord(altaz).transform_to("icrs")
            return coord.ra.deg, coord.dec.deg
        except Exception as e:
            raise ValueError(f"Ошибка преобразования координат: {e}")

    def _compute_radec_residuals(
        self,
        params: np.ndarray,
        times: Time,
        obs_ra: np.ndarray,
        obs_dec: np.ndarray,
        r_obs_list: list
    ) -> np.ndarray:
        """
        Вычисляет разницу (остатки) между наблюдаемыми и расчётными RA/Dec.
        Используется в методе наименьших квадратов.

        Параметры:
            params: [a, ecc, inc, raan, argp, nu] — параметры орбиты
            times: времена наблюдений (astropy Time)
            obs_ra, obs_dec: наблюдаемые RA/Dec (градусы)
            r_obs_list: положения Земли (в км)

        Возвращает:
            residuals: массив разниц (RA_diff, Dec_diff) в градусах
        """
        a, ecc, inc, raan, argp, nu = params

        # Проверка физичности
        if ecc >= 1 or a < 0.01 or ecc < 0:
            return np.full(len(obs_ra) * 2, np.inf)

        try:
            orbit = Orbit.from_classical(
                attractor=Sun,
                a=a * u.AU,
                ecc=ecc * u.one,
                inc=inc * u.deg,
                raan=raan * u.deg,
                argp=argp * u.deg,
                nu=nu * u.deg,
                epoch=times[0]
            )
        except Exception:
            return np.full(len(obs_ra) * 2, np.inf)

        computed_ra = []
        computed_dec = []

        with solar_system_ephemeris.set("de440s"):
            for t, r_obs_vec in zip(times, r_obs_list):
                try:
                    r_comet = orbit.propagate(t).r
                    r_comet_vec = np.array([
                        r_comet[0].to(u.km).value,
                        r_comet[1].to(u.km).value,
                        r_comet[2].to(u.km).value
                    ]) * u.km

                    r_geo_vec = r_comet_vec - r_obs_vec

                    coord = SkyCoord(
                        x=r_geo_vec[0], y=r_geo_vec[1], z=r_geo_vec[2],
                        representation_type='cartesian'
                    ).transform_to('icrs')

                    computed_ra.append(coord.ra.deg)
                    computed_dec.append(coord.dec.deg)
                except Exception:
                    computed_ra.append(np.nan)
                    computed_dec.append(np.nan)

        computed_ra = np.array(computed_ra)
        computed_dec = np.array(computed_dec)

        # Более точное вычисление разницы углов RA с учетом цикличности
        ra_diff = computed_ra - obs_ra
        # Корректируем разницу, учитывая цикличность (0-360 градусов)
        ra_diff = (ra_diff + 180) % 360 - 180
        dec_diff = computed_dec - obs_dec

        residuals = np.hstack([ra_diff, dec_diff])
        residuals[np.isnan(residuals)] = 1e6

        return residuals
    
    def calculate_orbit(
    self,
    observations: List[Dict],
) -> Dict[str, Optional[float]]:
        """
        Определяет орбиту по множеству наблюдений методом наименьших квадратов.
        Используются все доступные наблюдения (RA/Dec + время).
        
        Параметры:
            observations (List[Dict]): Список наблюдений с полями:
                - 'ra': float, прямое восхождение в градусах
                - 'dec': float, склонение в градусах
                - 'observation_time': datetime

        Возвращает:
            Dict: Орбитальные элементы или None при ошибке
                - semi_major_axis: AU (None для гипербол)
                - eccentricity: -
                - inclination: градусы
                - longitude_ascending_node: градусы
                - argument_periapsis: градусы
                - periapsis_time: datetime
        """
        if len(observations) < 3:
            raise ValueError("Требуется минимум 3 наблюдения для определения орбиты")

        required_keys = {"ra", "dec", "observation_time"}
        for i, obs in enumerate(observations):
            if not required_keys.issubset(obs.keys()):
                missing = required_keys - obs.keys()
                raise ValueError(f"Наблюдение {i} не содержит полей: {missing}")

        # Сортируем по времени
        sorted_obs = sorted(observations, key=lambda x: x["observation_time"])
        times = Time([o["observation_time"] for o in sorted_obs])
        obs_ra = np.array([o["ra"] for o in sorted_obs])  # градусы
        obs_dec = np.array([o["dec"] for o in sorted_obs])  # градусы

        # Получаем положения Земли (геоцентрические векторы)
        with solar_system_ephemeris.set("de440s"):
            r_obs_list = []
            for t in times:
                r = get_body_barycentric("earth", t)
                r_obs_list.append(np.array([
                    r.x.to(u.km).value,
                    r.y.to(u.km).value,
                    r.z.to(u.km).value
                ]) * u.km)

        x0 = [
            3.0,    # a: большая полуось, AU
            0.6,    # ecc: эксцентриситет
            20.0,   # inc: наклонение (град)
            45.0,   # raan: долгота восходящего узла
            30.0,   # argp: аргумент перицентра
            0.0     # nu: истинная аномалия
        ]

        bounds = (
            [0.1, 0.0, 0.0, -180.0, -180.0, -180.0],
            [100.0, 1.0, 180.0, 360.0, 360.0, 360.0]
        )

        result = least_squares(
            self._compute_radec_residuals,
            x0,
            args=(times, obs_ra, obs_dec, r_obs_list),
            bounds=bounds,
            ftol=1e-6,
            xtol=1e-6,
            gtol=1e-6,
            method='trf',
            loss='linear',
            max_nfev=1000,
            verbose=0
        )

        if not result.success:
            warnings.warn(f"Оптимизация не сошлась: {result.message}. Используется начальное приближение.")
            a, ecc, inc, raan, argp, nu = x0
        else:
            a, ecc, inc, raan, argp, nu = result.x

        if ecc >= 1:
            is_elliptic = False
            a = None
        elif a < 0.01:
            is_elliptic = False
            a = None
            ecc = min(ecc, 0.99)
        else:
            is_elliptic = True

        try:
            orbit_a = (a * u.AU) if is_elliptic else (1e6 * u.km)
            orbit = Orbit.from_classical(
                attractor=Sun,
                a=orbit_a,
                ecc=float(ecc) * u.one,
                inc=float(inc) * u.deg,
                raan=float(raan) * u.deg,
                argp=float(argp) * u.deg,
                nu=float(nu) * u.deg,
                epoch=times[0]
            )
            time_to_peri = orbit.time_to_anomaly(0 * u.deg)
            periapsis_time = (times[0] + time_to_peri).datetime
        except Exception as e:
            warnings.warn(f"Не удалось вычислить время перигелия: {e}")
            periapsis_time = sorted_obs[0]["observation_time"]

        return {
            "semi_major_axis": float(a) if is_elliptic else None,
            "eccentricity": float(ecc),
            "inclination": float(inc),
            "longitude_ascending_node": float(raan),
            "argument_periapsis": float(argp),
            "periapsis_time": periapsis_time,
        }

    def calculate_closest_approach(
        self,
        orbit_elements: Dict,
        start_time: datetime,
        end_time: datetime,
        time_steps: int = 1000
    ) -> Dict:
        """
        Рассчитывает ближайшее сближение кометы с Землёй.

        Параметры:
            orbit_elements: результат calculate_orbit
            start_time, end_time: временной диапазон поиска
            time_steps: число шагов дискретизации

        Возвращает:
            {"time": datetime, "distance_au": float, "distance_km": float}
        """
        times = Time(
            np.linspace(start_time.timestamp(), end_time.timestamp(), time_steps),
            format="unix"
        )

        try:
            a = orbit_elements["semi_major_axis"]
            if a is None or a <= 0:
                a_val = 1e6 * u.km
            else:
                a_val = a * u.AU

            # Создаем орбиту с использованием времени перигелия как эпохи и nu=0
            orbit = Orbit.from_classical(
                attractor=Sun,
                a=a_val,
                ecc=orbit_elements["eccentricity"] * u.one,
                inc=orbit_elements["inclination"] * u.deg,
                raan=orbit_elements["longitude_ascending_node"] * u.deg,
                argp=orbit_elements["argument_periapsis"] * u.deg,
                nu=0 * u.deg,  # nu=0, потому что эпоха - это время перигелия
                epoch=Time(orbit_elements["periapsis_time"])
            )
        except Exception as e:
            warnings.warn(f"Не удалось создать орбиту для расчёта сближения: {e}")
            return {
                "time": start_time,
                "distance_au": 1.0,
                "distance_km": 149_597_870.7,
            }

        min_distance_au = float("inf")
        closest_time = None

        with solar_system_ephemeris.set("de440s"):
            try:
                # Распространяем орбиту на все временные точки
                cartesian = orbit.propagate(times)
                r_comet_list = cartesian.cartesian.xyz.T
                r_comet_list = r_comet_list * u.km

                # Получаем позиции Земли для всех временных точек
                r_earth_list = []
                for t in times:
                    r = get_body_barycentric("earth", t)
                    r_earth_list.append([r.x.to(u.km).value, r.y.to(u.km).value, r.z.to(u.km).value])
                r_earth_list = np.array(r_earth_list) * u.km

                # Вычисляем векторы разности и расстояния
                r_diff = r_comet_list - r_earth_list
                distances_au = np.linalg.norm(r_diff, axis=1) * u.km.to(u.AU)

                # Находим минимальное расстояние
                idx_min = np.argmin(distances_au)
                min_distance_au = float(distances_au[idx_min])
                closest_time = times[idx_min].datetime

            except Exception as e:
                warnings.warn(f"Ошибка при расчёте сближения: {e}")
                closest_time = start_time
                min_distance_au = 1.0

        return {
            "time": closest_time,
            "distance_au": min_distance_au,
            "distance_km": min_distance_au * 149_597_870.7,
        }
