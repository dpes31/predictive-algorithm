# Gate 2-3P-M4F-1 Public Source Feasibility Snapshot

작성일: 2026-07-01  
범위: 공개 공식원천의 존재와 역할만 확인. 데이터 수집·다운로드·구조화는 수행하지 않음.

## 1. MBC 공식 로또 프로그램

확인된 공개범위:

- 정규 생방송 시각 안내
- 회차별 다시보기와 추첨영상
- 방송시간 변경 공지
- 추첨방송 참관 절차
- MBC 상암사옥 집결 및 준비과정 안내
- 경찰공무원, 방송관계자, 동행복권 관계자가 함께 진행한다는 공식 설명

공식 페이지:

- https://program.imbc.com/lotto
- https://program.imbc.com/Concept/lotto
- https://program.imbc.com/Info/lotto?seq=607
- https://program.imbc.com/Info/1003945100000100000?seq=1886

판정:

- 방송시각·장소·일정변경: 공식 Grade B
- actual machine/ball/pretest structured archive: 공개 확인 불가
- VOD 기반 수기추출: Grade C diagnostic-only

## 2. 동행복권 공식원천

확인된 공개범위:

- 공식 운영주체·추첨 관련 공지와 보도자료
- 공식 당첨결과
- 공개 참관행사 및 엄격한 절차·관리 설명

예시 공식 페이지:

- https://m.dhlottery.co.kr/happy.do?method=fundPressPrView&txtNo=2116

판정:

- 공식 결과·공지: Grade B
- 회차별 machine_id, ball_set_id, 장비정비, ball measurement, pre-draw test raw log: 공개 구조화 archive 확인 불가
- primary M4 pilot에는 별도 원기록 접근 필요

## 3. 기상청 기상자료개방포털

확인된 공개범위:

- ASOS 시간·분·일 자료
- AWS 시간·분·일 자료와 파일셋
- 관측지점 정보와 위치변경 유의사항
- 온도, 습도, 기압 등 기상요소

공식 페이지:

- https://data.kma.go.kr/data/grnd/selectAsosList.do?pgmNo=36
- https://data.kma.go.kr/data/grnd/selectAwsRltmList.do
- https://apihub.kma.go.kr/apiList.do
- https://www.data.go.kr/data/15057210/openapi.do

판정:

- 공식 외부환경 자료: Grade B
- 스튜디오 실내·장비 내부상태의 직접측정이 아니므로 diagnostic-only
- 지점 위경도 변경이력을 함께 보존해야 함

## 4. 현재 결론

공개 공식원천만으로 확보 가능한 것은 방송 일정·영상·외부 기상·공식 결과다.

M4 primary evidence에 필요한 다음 자료는 공개 구조화 archive가 확인되지 않았다.

- machine identity and generation
- ball-set identity and generation
- machine maintenance and usage history
- number-preserving ball measurements
- pre-draw test and operational logs
- local indoor environmental sensor data
- exact selection and availability timestamps

따라서 공개정보만으로 실제 M4 evidence pilot을 시작하면 안 된다. 먼저 운영기관 또는 방송사 원기록의 존재, 520회 이상 coverage, timestamp와 연구사용권한을 확인해야 한다.
