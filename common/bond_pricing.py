from datetime import datetime
from typing import Optional

from scipy import optimize


def estimate_years_to_maturity(
    maturity_date: datetime, from_date: Optional[datetime] = None
):
    current_date = from_date or datetime.now()
    delta = maturity_date - current_date
    return delta.days / 360


def calc_bond_price_from_ytm(
    ytm: float,
    coupon: float,
    years_to_maturity: float,
    freq: int = 2,
    face_amount: float = 100.0,
    calc_dirty=False,
) -> float:
    ytm = ytm / 100
    coupon = coupon / 100
    bond_price = 0.0

    full_periods = int(years_to_maturity * freq)
    coupon_payment = face_amount * (coupon / freq)
    y_div_frq = ytm / freq

    for i in range(1, full_periods + 1):
        bond_price += coupon_payment / ((1 + y_div_frq) ** i)

    bond_price += face_amount / ((1 + y_div_frq) ** full_periods)

    if calc_dirty:
        fractional = years_to_maturity % 1
        coupon_per_period = coupon / freq
        accrued_rate = coupon_per_period * (
            (1 - fractional) / ((1 - fractional) * freq)
        )
        accrued_interest = accrued_rate * face_amount
        return bond_price + accrued_interest

    return bond_price


def calc_bond_ytm_from_price(
    curr_bond_price: float,
    face_amount: float,
    coupon: float,
    years_to_maturity: int,
    freq: int = 2,
    estimate: float = 0.05,
    calc_dirty=False,
) -> float:
    try:
        get_yield = (
            lambda curr_yield: calc_bond_price_from_ytm(
                coupon=coupon,
                face_amount=face_amount,
                ytm=curr_yield,
                years_to_maturity=years_to_maturity,
                freq=freq,
                calc_dirty=calc_dirty,
            )
            - curr_bond_price
        )
        return optimize.newton(get_yield, estimate)
    except Exception as e:
        print(e)
        return None


def calc_bond_duration(
    ytm: float,
    coupon: float,
    years_to_maturity: int,
    curr_bond_price: Optional[float] = None,
    face_amount: float = 100,
    freq: int = 2,
    modified=False,
    calc_dirty=False,
):
    bond_price = curr_bond_price or calc_bond_price_from_ytm(
        ytm=ytm,
        coupon=coupon,
        years_to_maturity=years_to_maturity,
        freq=freq,
        face_amount=face_amount,
        calc_dirty=calc_dirty,
    )

    ytm /= 100
    coupon_rate = coupon / 100
    coupon_payment = coupon_rate * face_amount
    n = int(years_to_maturity * freq)
    y = ytm / freq

    duration = 0
    for t in range(1, n + 1):
        duration += (t * coupon_payment / freq) / ((1 + y) ** t)
    duration += (n * face_amount) / ((1 + y) ** n)
    duration = (duration / bond_price) / freq
    duration = duration / (1 + y) if modified else duration

    return (duration, bond_price)
