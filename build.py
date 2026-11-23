"""141회(2027-01-30) 역공정표 — 날짜별 배정 생성 → index.html."""
import json, datetime as dt, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, 'pred.json'), encoding='utf-8'))
Y = [p for p in P if p['id'][0] == 'Y']
S = [p for p in P if p['id'][0] == 'S']
GI = [["02 가설", 37], ["03 토공·흙막이", 29], ["04 기초", 17], ["05 거푸집", 19], ["06 철근", 27],
      ["07 콘크리트", 56], ["08 PC·모듈러", 15], ["09 커튼월·창호", 22], ["10 철골", 56], ["11 초고층·구조", 15],
      ["12 조적·미장·타일", 22], ["13 방수", 11], ["14 마감·단열·결로", 18], ["15 해체·환경·안전", 41],
      ["16 건설관리·공정·품질", 56], ["17 친환경·스마트", 24]]
TOTAL = sum(n for _, n in GI)  # 465
HOL = {dt.date(2026, 12, 25): '성탄절', dt.date(2027, 1, 1): '신정'}
START, EXAM = dt.date(2026, 11, 23), dt.date(2027, 1, 30)
PH = [('R1', '1회독 · 120선 전부 한 번 써보기', dt.date(2026, 11, 23), dt.date(2026, 12, 13)),
      ('R2', '2회독 · 뼈대 쓰기 + 모의고사', dt.date(2026, 12, 14), dt.date(2027, 1, 10)),
      ('R3', '실전 · 매일 1교시 100분 + 3회독', dt.date(2027, 1, 11), dt.date(2027, 1, 24)),
      ('R4', '압축 · 새것 없음, 1순위만', dt.date(2027, 1, 25), dt.date(2027, 1, 29))]
MOCK = {dt.date(2026, 12, 19): ('반 모의', '136회 1·2교시'), dt.date(2026, 12, 26): ('전체 모의', '137회 1~4교시'),
        dt.date(2027, 1, 2): ('반 모의', '138회 3·4교시'), dt.date(2027, 1, 9): ('전체 모의', '139회 1~4교시'),
        dt.date(2027, 1, 16): ('전체 모의', '140회 1~4교시 (실제 시험 시각)'),
        dt.date(2027, 1, 23): ('전체 모의', '예측 1순위에서 뽑은 141회 가상 시험 (실제 시각)')}


def phase(d):
    for k, n, a, b in PH:
        if a <= d <= b:
            return k
    return 'EX'


def kind(d):
    if d in HOL or d.weekday() == 5:
        return 'sat'
    return 'sun' if d.weekday() == 6 else 'wd'


def gi_range(a, b):
    """기출 465 중 a~b(0부터, b 미포함) 구간 → 공종 이름 목록."""
    out, c = [], 0
    for name, n in GI:
        lo, hi = max(a, c), min(b, c + n)
        if lo < hi:
            out.append(name if (lo, hi) == (c, c + n) else f"{name} {lo - c + 1}~{hi - c}")
        c += n
    return out


days, d = [], START
while d <= EXAM:
    days.append(d)
    d += dt.timedelta(1)

# 기출 회독 구간: R1 = 1회독(전부), R2 = 2회독(전부), R3 = ×표만 3회독
gi = {}
for key, a, b in (('R1', PH[0][2], PH[0][3]), ('R2', PH[1][2], PH[1][3])):
    seg = [x for x in days if a <= x <= b and kind(x) != 'sun']
    for i, x in enumerate(seg):
        lo, hi = TOTAL * i // len(seg), TOTAL * (i + 1) // len(seg)
        gi[x] = (f"{'1' if key == 'R1' else '2'}회독 {lo + 1}~{hi}번", gi_range(lo, hi))


def fill(seq, caps):
    q, out = list(seq), {}
    for x, n in caps:
        out[x], q = q[:n], q[n:]
    return out, q


# R1: 평일 서술2·용어3 / 토·휴일 서술8·용어5 / 일 서술2
r1 = [x for x in days if phase(x) == 'R1']
capS = [(x, {'wd': 2, 'sat': 8, 'sun': 2}[kind(x)]) for x in r1]
capY = [(x, {'wd': 3, 'sat': 5, 'sun': 0}[kind(x)]) for x in r1]
w1S, leftS = fill(S, capS)
w1Y, leftY = fill(Y, capY)
assert not leftS and not leftY, (len(leftS), len(leftY))
# R2: 뼈대 — 평일 서술4·용어3 / 휴일 서술8·용어8 / 모의 토요일은 모의만
r2 = [x for x in days if phase(x) == 'R2' and kind(x) != 'sun' and x not in MOCK]
w2S, _ = fill(S, [(x, 8 if kind(x) == 'sat' else 4) for x in r2])
w2Y, _ = fill(Y, [(x, 8 if kind(x) == 'sat' else 3) for x in r2])
# R3: 평일 밤 한 교시씩 1→2→3→4 돌림
r3 = [x for x in days if phase(x) == 'R3' and kind(x) == 'wd']
y1, s1 = Y[:30] + Y[30:], S[:30] + S[30:]
yi = si = 0
r3plan = {}
for i, x in enumerate(r3):
    k = i % 4 + 1
    if k == 1:
        r3plan[x] = (k, [p['id'] for p in y1[yi:yi + 10]]); yi += 10
    else:
        r3plan[x] = (k, [p['id'] for p in s1[si:si + 4]]); si += 4
# R4: 1순위 30+30을 5일에 6+6
r4 = [x for x in days if phase(x) == 'R4']
r4plan = {x: ([p['id'] for p in Y[i * 6:i * 6 + 6]], [p['id'] for p in S[i * 6:i * 6 + 6]]) for i, x in enumerate(r4)}

W = '월화수목금토일'
out = []
for x in days:
    ph, k = phase(x), kind(x)
    e = {'d': x.isoformat(), 'w': W[x.weekday()], 'ph': ph, 'k': k, 'dday': (EXAM - x).days,
         'hol': HOL.get(x, ''), 'tasks': []}
    T = e['tasks']
    if x == EXAM:
        e['k'] = 'exam'
        T += [['07:30', '입실 전', '앞글자 카드 1순위만 훑기 — 새 문항 보지 않기'],
              ['09:00', '1교시 용어', '13문항 중 10 · 아는 것부터, 1문항 10분 · 1쪽'],
              ['11:00', '2교시 서술', '6문항 중 4 · 25분씩 · 키플랜 띠 먼저'],
              ['13:40', '3교시 서술', '점심은 가볍게 · 쉬는 시간에 앞 교시 생각 금지'],
              ['15:40', '4교시 서술', '마지막까지 4문항 다 채우기 — 빈 문항이 가장 큰 감점']]
        out.append(e); continue
    if k == 'wd' or (k == 'sat' and x in HOL):
        pass
    g = gi.get(x)
    bus_am = (f"90 기출 자가테스트 {g[0]} · " + ', '.join(g[1])) if g else \
        ('기출 ×표 문항만 3회독 (90 전자책)' if ph == 'R3' else '1순위 앞글자 카드만 (A6·크레마)')
    if ph == 'R1':
        sY, sS = w1Y.get(x, []), w1S.get(x, [])
        ids = [p['id'] for p in sS + sY]
        if k == 'wd':
            T += [['06–08', '버스', bus_am],
                  ['12:30', '점심 30분', '용어 쇼츠 2~3편 또는 어제 ×표 A6 카드'],
                  ['18–20', '버스', f"95 영상으로 오늘 밤 쓸 {len(ids)}문항 미리보기 → 눈 감고 대제목 떠올리기"],
                  ['21–23', '도서관 쓰기', f"서술 {len(sS)}문항 25분씩 + 용어 {len(sY)}문항 10분씩 (93·94 작성표 1회 칸)"],
                  ['23–24', '채점·암기', '97 전자책과 대조 → 빠진 키워드 빨간펜 → ×표 A6 카드로']]
        elif k == 'sat':
            T += [['09–12', '서술 쓰기', f"서술 {len(sS)}문항 중 앞 4개 — 100분 1교시처럼 이어 쓰기"],
                  ['13–15', '서술 쓰기', f"나머지 서술 {max(0, len(sS) - 4)} + 용어 {len(sY)}"],
                  ['15–17', '기출 읽기', bus_am],
                  ['19–21', '주간 ×표 정리', '이번 주 ×표 문항 다시 쓰기 · 앞글자 카드 만들기']]
        else:
            T += [['09–12', '복습 반나절', f"서술 {len(sS)}문항 새로 + 이번 주 ×표 다시 읽기"],
                  ['오후', '쉼', '산책·운동 — 공부하지 않기 (번아웃 방지)']]
        e['Y'], e['S'] = [p['id'] for p in sY], [p['id'] for p in sS]
    elif ph == 'R2':
        if x in MOCK:
            m = MOCK[x]
            T += [['09–12:40', m[0], m[1] + ' — 실제 답안지 양식·시간 그대로'],
                  ['14–17', '채점', '모범답안(87)과 대조, 문항별 점수 매기기 · 시간 부족했던 교시 기록'],
                  ['19–21', '×표 정리', '틀린 공종을 내일·다음 주 뼈대 쓰기 앞으로']]
        elif k == 'sun':
            T += [['09–12', '복습 반나절', '이번 주 뼈대에서 ×표 난 문항만 다시 쓰기'],
                  ['오후', '쉼', '산책·운동 — 공부하지 않기']]
        else:
            sY, sS = w2Y.get(x, []), w2S.get(x, [])
            e['Y'], e['S'] = [p['id'] for p in sY], [p['id'] for p in sS]
            if k == 'wd':
                T += [['06–08', '버스', bus_am],
                      ['12:30', '점심 30분', '×표 A6 카드'],
                      ['18–20', '버스', '97 전자책으로 오늘 밤 문항 대제목·키워드 확인'],
                      ['21–22:30', '뼈대 쓰기', f"서술 {len(sS)}문항 뼈대 15분씩 (키플랜·대제목·그림·표만)"],
                      ['22:30–23:10', '용어 완성', f"용어 {len(sY)}문항 10분씩 1쪽 완성"],
                      ['23:10–24', '채점·암기', '×표만 앞글자 카드에 옮기기']]
            else:
                T += [['09–12', '뼈대 쓰기', f"서술 {len(sS)}문항 뼈대"],
                      ['13–15', '용어 완성', f"용어 {len(sY)}문항"],
                      ['15–17', '기출 읽기', bus_am], ['오후 늦게', '쉼', '휴일은 저녁 쉬기']]
    elif ph == 'R3':
        if x in MOCK:
            m = MOCK[x]
            T += [['09:00–17:20', m[0], m[1] + ' · 09:00 / 11:00 / 13:40 / 15:40 시작'],
                  ['19–21', '채점', '교시별 점수 · 시간 배분 점검']]
        elif k == 'sun':
            T += [['09–12', '×표 다시 쓰기', '이번 주 실전에서 막힌 문항만'], ['오후', '쉼', '']]
        else:
            n, ids = r3plan[x]
            e['exam'] = n
            e['Y' if n == 1 else 'S'] = ids
            what = f"용어 {len(ids)}문항 100분 (1문항 10분·1쪽)" if n == 1 else f"서술 {len(ids)}문항 100분 (25분씩)"
            T += [['06–08', '버스', bus_am],
                  ['18–20', '버스', '오늘 밤 교시 문항 키플랜만 머릿속으로'],
                  ['21–22:40', f'{n}교시 실전', what],
                  ['22:40–24', '채점·암기', '97 전자책 대조 · ×표 앞글자 카드']]
    elif ph == 'R4':
        yy, ss = r4plan[x]
        e['Y'], e['S'] = yy, ss
        last = x == dt.date(2027, 1, 29)
        T += [['06–08', '버스', '1순위 앞글자 카드만 — 새 자료 금지'],
              ['18–20', '버스', f"오늘 몫 용어 {len(yy)} + 서술 {len(ss)} 대제목 떠올리기"],
              ['21–23' if not last else '21–22', 'A3 한 장 요약' if not last else '준비물',
               '오늘 몫을 A3 한 장에 키워드만' if not last else '수험표·신분증·검정펜 여러 자루·시계·도시락 챙기고 22시 취침'],
              ]
        if not last:
            T.append(['23–24', '일찍 자기', '수면이 점수다 — 24시 전 취침'])
    out.append(e)

pred = {p['id']: [p['t'], p['g']] for p in P}
data = {'days': out, 'pred': pred, 'phases': [[k, n, a.isoformat(), b.isoformat()] for k, n, a, b in PH],
        'mock': {k.isoformat(): v for k, v in MOCK.items()}}
api = open(os.path.join(HERE, 'api_url.txt'), encoding='utf-8').read().strip() if os.path.exists(os.path.join(HERE, 'api_url.txt')) else ''
html = open(os.path.join(HERE, 'tpl.html'), encoding='utf-8').read().replace('/*DATA*/null', json.dumps(data, ensure_ascii=False)).replace("/*API*/''", json.dumps(api))
os.makedirs(os.path.join(HERE, 'docs'), exist_ok=True)
open(os.path.join(HERE, 'docs', 'index.html'), 'w', encoding='utf-8').write(html)
# 점검
print('R1 S', sum(len(v) for v in w1S.values()), 'Y', sum(len(v) for v in w1Y.values()))
print('R2 S', sum(len(v) for v in w2S.values()), 'Y', sum(len(v) for v in w2Y.values()), 'days', len(r2))
print('R3', [(x.isoformat(), r3plan[x][0], len(r3plan[x][1])) for x in r3])
print('days', len(out))
