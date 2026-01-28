# v22 – 시즌팩(21일+보너스N)까지 run_generate에 자동 반영

## 핵심
- offer_code: D7 / D14 / D21 / SEASONPACK
- SEASONPACK이면:
  - days=21 고정
  - bonus=기본 3 ( --bonus 로 변경 가능 )
  - 썸네일 문구 A/B/C 자동 변경(21+3 표시)
  - 이미지 프롬프트 톤도 SEASONPACK 전용으로 더 프리미엄하게 자동 분기
  - BONUS01..BONUS03(또는 N) 카드까지 자동 생성

## run_generate 사용 예
```bash
python run_generate.py --season spring --platform instagram --mode paid --offer_code SEASONPACK --bonus 3   --xlsx ./day_texts.xlsx --base_url https://your-buy-link.com --utm_campaign spring_pack
```

### BONUS 텍스트는 엑셀에서 커스텀 가능
Cards 시트에 아래 key로 넣으면 자동 반영:
- BONUS01, BONUS02, BONUS03 ... (day 컬럼)

## 가격 매핑(환경변수)
```bash
export OFFER_PRICE_7=3900
export OFFER_PRICE_14=4900
export OFFER_PRICE_21=7900
export OFFER_PRICE_SEASONPACK=12900
```

## 서버
server_v22.py는 offer_code를 bonus 링크 발급 DB에 저장합니다.


## v23 추가: SEASONPACK 전용 스토리 CTA 컷
- SEASONPACK일 때만 마지막 CTA 컷 문구/프롬프트(kind) / 9:16 프리셋을 별도로 사용
- 옵션: --story_last_preset_seasonpack (기본 middle)


## v24 추가
- SEASONPACK 전용 커머스형 CTA 배경(배너/뱃지/리본)
- SEASONPACK이면 마지막 2컷 CTA(T1 티저 → T2 결제유도) 자동 생성


## v25 추가
- SEASONPACK CTA_T1: 2초 MP4 자동 생성 옵션(--cta_t1_video)
- SEASONPACK CTA: D-N 카운트다운 자동 오버레이(--countdown_days)
- 신규/재구매 segment별 CTA_T1 문구 분기(--segment new|repeat)


## v26 추가
- --deadline YYYY-MM-DD 입력 시 자동으로 D-N 계산
- deadline 없으면 기존 --countdown_days 사용


## v27 추가
- D-0/D-1/D-3/D-7 단계별 시즌팩 CTA 문구 자동 변경
- D-0: '오늘 마감', '마지막 기회' 배지 자동 전환
- 마감 이후(expired): NEXT_SEASON(+NEXT_DEADLINE)로 자동 전환 또는 시즌팩 자동 숨김(D21로 다운그레이드)
- 새 옵션: --next_season, --next_deadline


## v28 추가(긴급 옵션)
- --deadline_time HH:MM 시간 기준 남은 분 계산
- --shock_10min: 10분 전 빨간 테두리+진동(CTA_T1 MP4)
- --live_counter: 구매 수 카운터 + 구매 수에 따라 가격 폰트 자동 확대
- --auto_teaser + --teaser_url: 마감 직후 다음 시즌 티저 + 알림신청 QR 자동 생성
- CTA_T1 MP4는 *_NORMAL/H6/H3/H1/M10 으로 자동 분기


## v29 추가
- M1.mp4: 마감 1분 전 전용(더 강한 흔들림 + 경고 배너)
- live_counter_source=webhook: 스토어 주문 webhook 실데이터 기반 '지금 사는 중' 표시

### Webhook 사용법(개요)
1) `python server_webhook.py` 실행 (기본 포트 8088)
2) 스토어 webhook을 `POST /webhook/order`로 연결
3) run_generate 실행 시 `--live_counter --live_counter_source webhook --webhook_state_file ./live_counter_state.json`


## v30 추가
- 플랫폼별 webhook 파싱(스마트스토어/토스페이/카페24)
- 주문 금액 기반 고가 결제 배너 강화
- 최근 5분 + 30분 이중 카운터 표시


## v31 추가
- webhook state 기반 가격/혜택 실시간 변동(--dynamic_offer)
- 고가 결제 직후(high_amount_recent) CTA 배너 문구 즉시 강화
- CTA 영상에 '실시간 구매 그래프' 렌더링(--graph_in_video)


## v32 추가
- 고가 결제 직후(theme=gold) 배너/리본 색상 금색 테마로 자동 전환
- 주문 금액 구간별 BONUS/쿠폰 자동 스위칭(CTA 이미지에 쿠폰 리본 자동 노출)
- BONUS_RULES.txt로 선택된 혜택 스냅샷 출력


## v33 추가
- 티어별 BONUS DAY10/DAY11 실제 카드 이미지 자동 생성(--generate_bonus_cards)
- 쿠폰코드 랜덤 발급(local_random) + message_payload.json 자동 출력
- server_loyalty.py: 쿠폰 발급/사용 이벤트 수집(/coupon/issue, /coupon/used) + 방문 이벤트(/event/visit)

### 예시
python run_generate.py ... --generate_bonus_cards --coupon_mode local_random

python server_loyalty.py  # 이벤트 수집 서버


## v34 추가
- 보너스 카드 생성 후 S3/Google Drive 자동 업로드(--upload_backend s3|gdrive)
- 업로드된 URL을 message_payload.json에 자동 삽입(무인)

### S3 예시
export S3_BUCKET=your-bucket
export S3_PREFIX=alloki/bonus/
# (옵션) public/CloudFront base URL
export S3_PUBLIC_URL_BASE=https://cdn.example.com/alloki/bonus
python run_generate.py ... --upload_backend s3

### Google Drive(서비스계정) 예시
export GDRIVE_SA_JSON=./service_account.json
export GDRIVE_FOLDER_ID=your_folder_id
# folder must be shared with service account email
python run_generate.py ... --upload_backend gdrive


## v35 추가
- message_payload.json 생성 후 발송 API 자동 호출(--send_messages --sender ...)
- CloudFront/공개 URL 기반 고정 링크 강제(--require_stable_urls + S3_PUBLIC_URL_BASE)

### CloudFront 고정 URL 방식(권장)
S3 업로드 시 Presigned URL 대신 CloudFront(또는 public base URL)를 반드시 사용하도록 강제:
- export S3_PUBLIC_URL_BASE=https://cdn.example.com/alloki/bonus
- run_generate.py ... --upload_backend s3 --require_stable_urls

### 발송 백엔드
- kakao_i_alimtalk: BizMessage AlimTalk (OAuth2 선행 필요)
- solapi_sms: SOLAPI SMS
- instagram_dm: Meta IG Messaging send

※ 실제 운영 시 각 플랫폼 권한/템플릿 심사/메시지 정책 준수 필요.


## v36 추가
- 발송 성공/실패 로그를 XLSX로 자동 반영(--log_xlsx)
- 카카오 알림톡 실패 시 SMS(솔라피) 자동 대체발송(--fallback_sms_on_fail)
- 인스타/틱톡은 DM 대신 댓글/자동응답/링크 랜딩 퍼널로 자동화(--funnel_mode comment_landing)

### 예시
python run_generate.py ... --send_messages --sender kakao_i_alimtalk --fallback_sms_on_fail --log_xlsx ./performance_log.xlsx

# 인스타/틱톡 안정형 퍼널
python run_generate.py ... --funnel_mode comment_landing --landing_destination_url "https://smartstore.naver.com/..."
(출력: comment_reply_payload.json + landing.html)


## v37 추가
- landing.html을 S3/CloudFront에 자동 업로드(--upload_landing)
- 프로필 링크용 고정 URL(profile_link_url)을 message_payload.json에 자동 삽입

### 사용
export S3_BUCKET=your-bucket
export S3_PUBLIC_URL_BASE=https://cdn.example.com/
python run_generate.py ... --funnel_mode comment_landing --upload_landing


## v38 추가
- landing.html A/B/C 자동 생성(--landing_variants 2|3) + 쿠폰 복사 버튼 내장
- 랜딩 방문 추적 endpoint(--landing_track_url) 지원
- server_loyalty.py에 /report (A/B 전환율) + /event/purchase + /retarget/list 추가
- retarget_worker.py: 방문 후 미구매 리타겟 자동 발송(크론 권장)

### 랜딩 A/B 생성 + 업로드
python run_generate.py ... --funnel_mode comment_landing --landing_variants 3 --upload_landing --require_stable_urls

### 전환율 리포트
python server_loyalty.py
curl http://127.0.0.1:8090/report

### 리타겟(60분 후)
python retarget_worker.py --server_base http://127.0.0.1:8090 --minutes 60 --sender solapi_sms --config ./sender_config.json


# v39 통합 실행
이제 하나의 엔트리포인트로 실행합니다.

## 1) 생성(기존 run_generate 옵션 그대로)
python app.py generate -- <run_generate.py 옵션들>

예:
python app.py generate -- --funnel_mode comment_landing --landing_destination_url "https://..." --upload_landing --require_stable_urls

## 2) 서버 실행
python app.py serve

## 3) AB 리포트
python app.py report --server_base http://127.0.0.1:8090

## 4) 리타겟 워커
python app.py retarget --minutes 60 --sender solapi_sms --config ./sender_config.json


## v40: 원클릭 run_week
python app.py run_week --landing_destination_url "https://smartstore.naver.com/..." --upload_landing --require_stable_urls --send_messages --sender kakao_i_alimtalk --fallback_sms_on_fail

- 실행 순서: generate → (upload/URL 삽입) → (send) → log(xlsx) → report(가능하면 weekly_report.json 저장)
- 리포트는 server_loyalty.py가 실행 중일 때만 자동 저장됩니다.


## v41: run_week (7일치 × 플랫폼별) + 서버 자동 백그라운드
예:
python app.py run_week --season spring --platforms instagram,tiktok --landing_destination_url "https://smartstore.naver.com/..." --upload_landing --require_stable_urls --auto_server

- 결과 폴더: out_dir/instagram/*, out_dir/tiktok/* 로 분리 저장
- --auto_server 사용 시 server_loyalty를 백그라운드로 띄우고 작업 끝나면 자동 종료


## v42: 신규/재구매 동시 + 이번 주 자동 요일톤 문구
- run_week가 XLSX를 자동 생성합니다(엑셀 없이도 실행 가능).
- week_start 미지정 시: '이번 주 월요일' 기준으로 DAY01~DAY07에 날짜/요일/톤이 자동 반영됩니다.
- segments 기본값: new,repeat → 신규/재구매 세트 동시 생성
- 출력: out_dir/new/instagram, out_dir/repeat/tiktok 처럼 분리

예:
python app.py run_week --season spring --auto_server --landing_destination_url "https://smartstore.naver.com/..." --upload_landing --require_stable_urls


## v43: 업로드 시간대(오전/저녁/밤) 톤 반영 + 플랫폼별 시즌 팔레트 최적화
- run_week가 timeband를 플랫폼별로 자동 적용합니다(기본: instagram=morning, tiktok=evening)
- 랜딩/카드 문구에 '오전 톤/저녁 톤/밤 톤'이 반영됩니다.
- season 팔레트는 instagram(파스텔) / tiktok(대비강)으로 자동 분기됩니다.

예:
python app.py run_week --season spring --timebands instagram:morning,tiktok:evening --auto_server --landing_destination_url "https://..." --upload_landing --require_stable_urls


## v44: 실제 업로드 시간(HH:MM) 훅 자동 반영
- run_week에 --upload_times 추가(기본: instagram 09:00 / tiktok 18:30)
- 문구에 짧은 훅 자동 삽입(예: '출근 전 10초', '퇴근 후 10초', '자기 전 10초')

예:
python app.py run_week --season spring --upload_times instagram:09:00,tiktok:18:30 --timebands instagram:morning,tiktok:evening --auto_server --landing_destination_url "https://..." --upload_landing --require_stable_urls


## v45: 플랫폼별 훅 공격성 분기
- TikTok 훅 예시: '지금 안 보면 놓쳐요 (10초)', '퇴근하자마자 딱 10초'
- Instagram 훅 예시: '출근 전 10초', '퇴근 후 10초'
- 동일한 업로드 시간/타임밴드라도 플랫폼에 따라 훅 톤이 자동 분기됩니다.


## v46: 훅 A/B 테스트 + TikTok 10초↔5초 자동 전환 + 다음 주 자동 승격
- 훅은 platform×timeband별로 A/B 2종이 랜덤 적용됩니다(--hook_policy random)
- TikTok은 hooks_stats.json의 최근 성과(best_conv_rate)가 임계값보다 약하면 '10초' → '5초'로 자동 전환합니다.
- 성과 좋은 훅 승격: hooks_stats.json에 best_hook_id를 저장하고 --hook_policy promote로 실행하면 다음 주부터 그 훅만 사용합니다.

### 사용 예시
1) 이번 주 AB 랜덤
python app.py run_week --season spring --hook_policy random --auto_server --landing_destination_url "https://..." --upload_landing --require_stable_urls

2) (선택) 성과 계산 결과를 JSON으로 넣어 승격 업데이트
python app.py hooks_promote --from_json hook_eval.json --hooks_stats ./hooks_stats.json

3) 다음 주엔 자동 승격 모드
python app.py run_week --season spring --hook_policy promote --auto_server --landing_destination_url "https://..." --upload_landing --require_stable_urls

* hook_eval.json 형식 예:
{
  "tiktok:evening": {"A": 0.12, "B": 0.08},
  "instagram:morning": {"A": 0.05, "B": 0.07}
}


## v48: 훅 + CTA + 가격(3900/4900) + 카드 수(7/14/21) 자동 승격
- run_week가 platform×timeband별로 CTA(A/B), price(3900/4900), offer_days(7/14/21)을 랜덤/승격 정책으로 선택합니다.
- 무인 승격: 성과 시트(xlsx)에서 자동 추출 → eval json 생성 → stats 갱신

### 1) 이번 주 랜덤 테스트
python app.py run_week --season spring --hook_policy random --cta_policy random --price_policy random --offer_policy random --auto_server

### 2) 월말/주말 무인 승격
python app.py auto_promote --xlsx ./performance_log.xlsx --out_dir ./promote_out

### 3) 다음 주 승격 고정(플랫폼별 자동)
python app.py run_week --season spring --hook_policy promote --cta_policy promote --price_policy promote --offer_policy promote --auto_server


## v49: 상품 정책 룰 엔진 + 플랫폼×요일×시즌 분리 승격 + 조합 멀티암 밴딧
- RULE: 21일 오퍼는 product_type=seasonpack일 때만 허용 (--product_type seasonpack)
- CTA/가격/훅은 platform×season×weekday×timeband 기준으로 best 값을 따로 저장/승격
- combo_policy=bandit이면 (훅+CTA+가격+오퍼) 조합 전체를 하나의 arm으로 UCB1 탐색/승격( combo_stats.json )

### 시즌팩만 21일 허용
python app.py run_week --season spring --product_type standard   # offer=7/14만
python app.py run_week --season spring --product_type seasonpack # offer=7/14/21 가능

### 조합 밴딧 모드
python app.py run_week --season spring --product_type seasonpack --combo_policy bandit --auto_server

### 무인 승격(개별 + 조합 통계 업데이트)
python app.py auto_promote --xlsx ./performance_log.xlsx --out_dir ./promote_out --combo_stats ./combo_stats.json


## v50: 밴딧 룰 금지 + segment 차원 분리 + 밴딧 reward=EV
- RULE(예시): 4,900원은 7일 구성에서만 허용 (--rule_price4900_only_d7, 기본 True)
- 승격/통계 키는 platform×season×segment(new/repeat)×weekday×timeband 로 완전 분리
- combo_stats 밴딧 reward는 기본 EV(=price×conv_rate×margin). auto_promote에서 --bandit_reward ev/conv_rate 선택 가능

### 밴딧 + 룰 적용
python app.py run_week --season spring --product_type seasonpack --combo_policy bandit --rule_price4900_only_d7 --auto_server

### EV 기준 combo 통계 업데이트
python app.py auto_promote --xlsx ./performance_log.xlsx --out_dir ./promote_out --combo_stats ./combo_stats.json --bandit_reward ev --ev_margin 1.0


## v51: 순이익 EV(환불/쿠폰/보너스 원가) + 플랫폼별 EV 식 분리
- bandit_reward=profit_ev(기본): net_profit_per_conversion * metric
  net_profit_per_conversion = (price*margin)*(1-refund_rate) - coupon_cost - bonus_cost
- platform_ev_config.json로 플랫폼별 metric 선택
  - instagram/tiktok: click_cvr (없으면 conv_rate fallback)
  - smartstore/cafe24/toss: purchase_cvr (없으면 conv_rate fallback)

### 사용 예시(무인 갱신)
python app.py auto_promote --xlsx ./performance_log.xlsx --out_dir ./promote_out --combo_stats ./combo_stats.json \
  --bandit_reward profit_ev --ev_margin 1.0 --refund_rate 0.03 --coupon_cost 200 --bonus_cost 150 \
  --platform_ev_config ./platform_ev_config.json


## v52: 플랫폼별 비용 구조 + 시즌팩 보너스 원가 가중 + 재구매 LTV 가중
- platform_ev_config.json에 플랫폼별 refund_rate/coupon_cost/bonus_cost/ltv_weight 설정 가능
- default.seasonpack_bonus_cost_mult로 시즌팩 보너스 원가를 더 높게 반영
- default.segment_ltv_mult로 new/repeat별 LTV 가중(예: repeat=1.25)

### 무인 갱신(순이익 EV + LTV 가중)
python app.py auto_promote --xlsx ./performance_log.xlsx --out_dir ./promote_out --combo_stats ./combo_stats.json \
  --bandit_reward profit_ev --ev_margin 1.0 --platform_ev_config ./platform_ev_config.json

(비용은 platform_ev_config.json에서 플랫폼별로 자동 적용)


## v53: 시즌별 비용 오버라이드 + 실데이터 기반 LTV 월간 자동 업데이트
### 1) 시즌별 비용 구조(by_season)
platform_ev_config.json에서 default 또는 플랫폼별로 by_season을 지정하면 자동 반영됩니다.
예: 연말(yearend)에 쿠폰비 증가

### 2) LTV 월간 자동 업데이트
성과 xlsx를 읽어서 플랫폼별 ltv_weight와 repeat 배수를 자동 갱신:
python app.py update_ltv --xlsx ./performance_log.xlsx --platform_ev_config ./platform_ev_config.json --month 2026-01
(월 필터는 선택)

이후 auto_promote를 실행하면 profit_ev reward에 최신 ltv_weight가 적용됩니다.


## v54: 현실적 LTV 모델(재구매 매출/쿠폰 할인율/시즌팩 영향) + promo 라벨 시즌 세분화
### 프로모션 기간명도 season 라벨로 사용 가능
--season promo_d-3 처럼 사용하면 platform_ev_config.json의 by_season.promo_d-3 오버라이드가 적용됩니다.

### LTV 업데이트(실데이터 기반)
update_ltv는 아래 컬럼이 있으면 더 현실적으로 갱신합니다:
- revenue, repurchase_revenue, coupon_discount_rate(0~1 또는 %), product_type
없으면 기존 repurchase_rate/coupon_use_rate 기반으로 fallback.

platform_ev_config.json -> default.ltv_model로 가중치 조정:
- alpha_repurchase_rev_ratio
- beta_coupon_discount
- gamma_seasonpack_uplift


# ✅ One Program Entry Point
Use **app.py** for everything.

## One-click weekly generation
```bash
python app.py run_week --season spring --platforms instagram,tiktok --segments new,repeat --auto_server
```

## LTV monthly update
```bash
python app.py update_ltv --xlsx ./performance_log.xlsx --platform_ev_config ./platform_ev_config.json --month 2026-01
```

## Forward advanced flags to run_generate.py
```bash
python app.py run_week --season promo_d-3 --platforms tiktok --segments new -- --shock_10min --urgency_video
```
