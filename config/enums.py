import enum


class ToneEnum(str, enum.Enum):
    VP = 'Very Positive'
    P = 'Positive'
    N = 'Neutral'
    NEG = 'Negative'
    VNEG = 'Very Negative'
