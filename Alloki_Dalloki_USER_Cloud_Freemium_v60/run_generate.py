def thumb_copy_for_offer(offer_code: str, season: str) -> dict:
    oc = (offer_code or "").upper()

    if oc == "SEASONPACK":
        # A=공감형, B=긴급형, C=프리미엄형
        season_kr = {
            "spring": "봄",
            "summer": "여름",
            "autumn": "가을",
            "winter": "겨울",
        }.get(season, season)

        return {
            "A": f"{season_kr} 시즌팩 21+3 · 오늘의 마음을 꺼내요",
            "B": f"{season_kr} 시즌팩 21+3 · 지금 안 사면 늦어요",
            "C": f"{season_kr} 시즌팩 21+3 · 프리미엄 한정",
        }

    if oc == "D7":
        return {
            "A": "7일 카드 · 오늘의 마음",
            "B": "7일 카드 · 지금 시작",
            "C": "7일 카드 · 가볍게 힐링",
        }

    if oc == "D14":
        return {
            "A": "14일 카드 · 마음 회복",
            "B": "14일 카드 · 놓치면 후회",
            "C": "14일 카드 · 프리미엄",
        }

    if oc == "D21":
        return {
            "A": "21일 카드 · 마음 루틴",
            "B": "21일 카드 · 지금이 타이밍",
            "C": "21일 카드 · 깊은 힐링",
        }

    return THUMB_COPY_DEFAULT.copy()
