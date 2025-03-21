import enum


class ToneEnum(str, enum.Enum):
    VP = 'Very positive'
    P = 'Positive'
    N = 'Neutral'
    NEG = 'Negative'
    VNEG = 'Very negative'
