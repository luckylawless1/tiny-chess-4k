# 4k chess: 0x88 board, PESTO tapered eval, PVS+NMP+LMR+TT, fixed node budget.
import json, os, random, urllib.request
_Q = b'FFFFFFFFBFDCDIKCCFFEFFJDCFEHHGGCDHGIIHHCEGIJNMIDRWNRNVJEFFFFFFFFFFFFFFFFHGGGHFFEFGEFFEFEHGFEEEFFJIHGFFHHRRQNMMPP\\\\ZWXV[]FFFFFFFF9C?BDBDCB?DFFHDDCEHGHHIDDFHHJHIEEHHMKOHI@NKNPVOL=AOJINGD1;B@N:D9B@CDCD@>ADEEFDC@CFFHGFDCDEHIHHFDDFIIIGGDCDGGFEDACECFECC@?ADBBC>:BFDCDDACFHHFGIJFFHHHHIHGEHHIJHGFFGHLKKGFDKKKJLKFCHDDJMH@BF<ACAGECECEEDEDDDEFFEDCDFGGHFEDEFHHGGFEFGHGHGFFFEFFFGFFEFGDFDFDDCEEEEDCDDFHHGAC@DDEFGE=@CDDFFEBBCDFGEGCCEGIIJEDEHIJHLNHIJMNPNILJKJLNGJKEFFFEDFFEEFFEEEFFFFFEDEDFGGFEEEEFFHFFFFFGGGGFFEFGHHGFFGFHGHHHHGGFDEGDCB@BEGFGHFFDFEFEFHGECEEFFFFCCDDFHFFDDGGJMLMCAEFDMJMBFJHMLKLBBCAEBDACCBDDCBBDCHGGHGGDJHLJJKIFIILMKMJDGGLLJHGDHJKMIJFEIIIIHGHDJH?GBIHFGE>ADGGDDC@@BDC@FCA@@B@DDDCBCDBEIFDDGICJFDEEFAB>IHD?BFH?BCEBDCACEFHHFEDDFGIIHGEDFIIIIGEEIIIIJIFGHIHHLLHDHHHHKIG=BDDEHFD'
PST = [[[(_Q[t * 128 + k * 64 + s] - 70) * 8 for s in range(64)] for k in (0, 1)] for t in range(6)]
VAL = ((82, 94), (337, 281), (365, 297), (477, 512), (1025, 936), (0, 0))
PHW = (0, 1, 1, 2, 4, 0)
MVV = (0, 94, 281, 297, 512, 936, 0)
KN = (31, 33, 14, 18, -31, -33, -14, -18)
KG = (1, -1, 16, -16, 15, 17, -15, -17)
BD = (15, 17, -15, -17)
RD = (1, -1, 16, -16)
MATE = 100000
INF = 10 ** 9
SQ = [r * 16 + f for r in range(8) for f in range(8)]
CM = {0: 13, 7: 14, 4: 12, 112: 7, 119: 11, 116: 3}
CD = {6: (7, 5), 2: (0, 3), 118: (119, 117), 114: (112, 115)}
PB_ = (0, 5, 10, 20, 35, 60, 100, 0)
C9 = [0] + [0x0101010101010101 << f for f in range(8)] + [0]
FU = (1 << 64) - 1
C3 = [C9[i] | C9[i + 1] | C9[i + 2] for i in range(8)]
PW_ = [C3[s % 8] & (-1 << (8 * (s >> 3) + 8)) & FU for s in range(64)]
PBM = [C3[s % 8] & ((1 << (8 * (s >> 3))) - 1) for s in range(64)]
random.seed(20261124)
ZK = [random.getrandbits(64) for _ in range(2073)]
ZP = ZK[:2048]; ZS = ZK[2048]; ZC = ZK[2049:2065]; ZE = ZK[2065:2073]
CK = [0]
for _c in range(1, 16):
    CK.append(CK[_c & _c - 1] ^ ZC[(_c & -_c).bit_length() - 1])
B = [0] * 128; SD = 0; CA = 0; EP = -1; HM = 0
MG = 0; EG = 0; PH = 0; KY = 0; KS = [0, 0]; PB = [0, 0]

def ar(sq, p, d):
    global MG, EG, PH, KY
    t = (p & 7) - 1; c = p >> 3; s = (sq >> 4) * 8 + (sq & 7)
    if c: s ^= 56
    v = VAL[t]; q = PST[t]; w = v[0] + q[0][s]; z = v[1] + q[1][s]
    sg = d * (1 - 2 * c)
    MG += sg * w; EG += sg * z
    PH += d * PHW[t]
    if t == 0:
        bit = 1 << ((sq >> 4) * 8 + (sq & 7))
        PB[c] = PB[c] | bit if d > 0 else PB[c] & ~bit
    KY ^= ZP[(p - 1) * 128 + sq]

def st():
    global B, SD, CA, EP, HM, MG, EG, PH, KY
    B = [0] * 128; MG = EG = PH = KY = 0
    PB[0] = PB[1] = 0
    SD = 0; CA = 15; EP = -1; HM = 0
    for i, ch in enumerate("rnbqkbnr" + "p" * 8 + "." * 32 + "P" * 8 + "RNBQKBNR"):
        if ch == ".": continue
        t = "pnbrqk".index(ch.lower()); c = 1 if ch.islower() else 0
        sq = (7 - i // 8) * 16 + i % 8; p = t + 1 + 8 * c
        B[sq] = p; ar(sq, p, 1)
        if t == 5: KS[c] = sq
    KY ^= CK[15]

def at(sq, by):
    for d in ((-15, -17) if by == 0 else (15, 17)):
        t = sq + d
        if not t & 0x88 and B[t] == 1 + 8 * by: return True
    for dirs, w in ((KN, 2), (KG, 6)):
        for d in dirs:
            t = sq + d
            if not t & 0x88 and B[t] == w + 8 * by: return True
    for dirs, tys in ((BD, (3, 5)), (RD, (4, 5))):
        for d in dirs:
            t = sq + d
            while not t & 0x88:
                q = B[t]
                if q:
                    if q >> 3 == by and q & 7 in tys: return True
                    break
                t += d
    return False

def ic():
    return at(KS[SD], SD ^ 1)

D2 = ((), KN, BD, RD, KG, KG)

def gm():
    ms = []; ap = ms.append
    for sq in SQ:
        p = B[sq]
        if not p or p >> 3 != SD: continue
        t = p & 7
        if t == 1:
            up = 16 - 32 * SD
            r = sq >> 4; one = sq + up
            pr = 6 - 5 * SD
            tg = []
            if not B[one]:
                tg.append(one)
                if r == 1 + 5 * SD and not B[sq + 2 * up]: ap(sq | (sq + 2 * up) << 7 | 1 << 21)
            for d in (up - 1, up + 1):
                to = sq + d
                if to & 0x88: continue
                q = B[to]
                if q and q >> 3 != SD: tg.append(to)
                elif to == EP: ap(sq | to << 7 | 1 << 20)
            for to in tg:
                if r == pr:
                    for x in (5, 4, 3, 2): ap(sq | to << 7 | x << 14)
                else: ap(sq | to << 7)
        else:
            for d in D2[t - 1]:
                to = sq + d
                while not to & 0x88:
                    q = B[to]
                    if q:
                        if q >> 3 != SD: ap(sq | to << 7)
                        break
                    ap(sq | to << 7)
                    if t < 3 or t > 5: break
                    to += d
            if t == 6 and sq == 112 * SD + 4:
                base = 112 * SD
                for bit, rf, dest, mid in ((1 << (2 * SD), base + 7, base + 6, (base + 5, base + 6)), (2 << (2 * SD), base, base + 2, (base + 1, base + 2, base + 3))):
                    if CA & bit and B[rf] == 4 + 8 * SD and all(not B[x] for x in mid) and not any(at(x, SD ^ 1) for x in (sq, (sq + dest) // 2, dest)):
                        ap(sq | dest << 7 | 1 << 19)
    return ms

def kx():
    global KY
    KY ^= CK[CA]
    if EP >= 0: KY ^= ZE[EP & 7]

def mk(m):
    global CA, EP, HM, SD, KY
    fr = m & 127; to = m >> 7 & 127; pr = m >> 14 & 7
    p = B[fr]; sd = SD; cp = B[to]; es = -1; cs = to
    if m & 1 << 20:
        es = cs = to - 16 if sd == 0 else to + 16; cp = B[es]
    u = (cp, CA, EP, HM, es)
    kx(); EP = -1
    HM = 0 if p & 7 == 1 or cp else HM + 1
    if cp:
        ar(cs, cp, -1)
        if es >= 0: B[es] = 0
    ar(fr, p, -1); B[fr] = 0
    if pr:
        np_ = pr + 8 * sd; ar(to, np_, 1); B[to] = np_
    else:
        ar(to, p, 1); B[to] = p
    if p & 7 == 6:
        KS[sd] = to
        if m & 1 << 19:
            rf, rt = CD[to]
            r = B[rf]; ar(rf, r, -1); B[rf] = 0; ar(rt, r, 1); B[rt] = r
    if m & 1 << 21:
        EP = fr + 16 if sd == 0 else fr - 16; KY ^= ZE[EP & 7]
    CA &= CM.get(fr, 15) & CM.get(to, 15); KY ^= CK[CA]
    SD ^= 1; KY ^= ZS
    if at(KS[sd], sd ^ 1):
        um(m, u); return None
    return u

def um(m, u):
    global CA, EP, HM, SD, KY
    cp, CA0, EP0, HM0, es = u
    SD ^= 1; KY ^= ZS
    sd = SD; fr = m & 127; to = m >> 7 & 127; pr = m >> 14 & 7
    kx()
    p = B[to]
    if pr:
        ar(to, p, -1); p = 1 + 8 * sd; ar(fr, p, 1); B[fr] = p; B[to] = 0
    else:
        ar(to, p, -1); ar(fr, p, 1); B[fr] = p; B[to] = 0
    if p & 7 == 6:
        KS[sd] = fr
        if m & 1 << 19:
            rf, rt = CD[to]
            r = B[rt]; ar(rt, r, -1); B[rt] = 0; ar(rf, r, 1); B[rf] = r
    if cp:
        cs = es if es >= 0 else to
        ar(cs, cp, 1); B[cs] = cp
    CA = CA0; EP = EP0; HM = HM0
    kx()

def ev():
    ph = PH if PH <= 24 else 24
    a = MG; b = EG
    for c in (0, 1):
        sg = 1 - 2 * c
        w = PB[c]; o = PB[c ^ 1]; ms = PW_ if c == 0 else PBM
        while w:
            l = w & -w; s = l.bit_length() - 1
            if not o & ms[s]:
                x = PB_[s >> 3] if c == 0 else PB_[7 - (s >> 3)]
                a += sg * (x // 2); b += sg * x
            w ^= l
    sc = (a * ph + b * (24 - ph)) // 24
    return sc if SD == 0 else -sc

TT = {}
HC = {}
NB = 55000
ND = [0, False]
NL = [False]

def om(ms, tm):
    sc = []
    for m in ms:
        to = m >> 7 & 127; cp = B[to]
        if m & 1 << 20: cp = 1
        if m == tm: s = 1 << 28
        elif cp: s = (1 << 24) + MVV[cp & 7] * 16 - (B[m & 127] & 7)
        elif m >> 14 & 7: s = (1 << 24) + 900
        else: s = 0
        sc.append((s, m))
    return [m for _, m in sorted(sc, reverse=True)]

def sr(d, a, b, ply):
    global EP, KY, SD
    if ply > 0 and (HC.get(KY, 0) >= 2 or (HM >= 100 and not ic())):
        return 0
    ND[0] += 1
    if ND[0] & 1023 == 0 and ND[0] > NB: ND[1] = True
    if ND[1]: return a
    if d <= 0:
        chk = ic()
        bst = -INF
        if not chk:
            bst = ev()
            if bst >= b: return bst
            if bst > a: a = bst
        legal = 0; best = bst
        for m in om(gm(), 0):
            if not chk and not (B[m >> 7 & 127] or m & 1 << 20 or m >> 14 & 7): continue
            u = mk(m)
            if u is None: continue
            legal += 1
            s = -sr(0, -b, -a, ply + 1)
            um(m, u)
            if ND[1]: return a
            if s > best: best = s
            if s >= b: return s
            if s > a: a = s
        if chk and legal == 0: return -MATE + ply
        return best
    a0 = a
    e = TT.get(KY); tm = e[0] if e else 0
    if e and e[1] >= d and (e[2] == 0 or (e[2] == 1 and e[3] >= b) or (e[2] == 2 and e[3] <= a)): return e[3]
    chk = ic()
    cd = d - 1 + (1 if chk else 0)
    if d >= 3 and not chk and ply and PH and not NL[0] and b < MATE - 1000 and ev() >= b:
        NL[0] = True
        ep0 = EP
        if EP >= 0: KY ^= ZE[EP & 7]
        EP = -1; SD ^= 1; KY ^= ZS
        s = -sr(d - 3, -b, -b + 1, ply + 1)
        SD ^= 1; KY ^= ZS; EP = ep0
        if ep0 >= 0: KY ^= ZE[ep0 & 7]
        NL[0] = False
        if ND[1]: return a
        if s >= b: return s
    legal = 0; best = -INF; bm = 0
    for i, m in enumerate(om(gm(), tm)):
        u = mk(m)
        if u is None: continue
        legal += 1
        HC[KY] = HC.get(KY, 0) + 1
        if i == 0:
            s = -sr(cd, -b, -a, ply + 1)
        else:
            s = -sr(cd, -a - 1, -a, ply + 1)
            if a < s < b: s = -sr(cd, -b, -a, ply + 1)
        HC[KY] -= 1
        um(m, u)
        if ND[1]: return a
        if s > best: best = s; bm = m
        if s > a: a = s
        if a >= b: break
    if legal == 0:
        return -MATE + ply if chk else 0
    TT[KY] = (bm, d, 2 if best <= a0 else 1 if best >= b else 0, best)
    return best

def choose(hist):
    global HC
    HC = {}
    for k in hist: HC[k] = HC.get(k, 0) + 1
    legal = [m for m in gm() if (u := mk(m)) is not None and um(m, u) is None]
    if len(legal) == 1: return legal[0]
    ND[0] = 0; ND[1] = False
    bm = legal[0]; d = 1
    while d <= 64 and not ND[1] and ND[0] <= NB // 2:
        a = -INF; best = -INF
        tm = TT.get(KY, (0,))[0]
        for i, m in enumerate(om(legal, tm)):
            u = mk(m)
            HC[KY] = HC.get(KY, 0) + 1
            if i == 0: s = -sr(d - 1, -INF, INF, 1)
            else:
                s = -sr(d - 1, -a - 1, -a, 1)
                if a < s: s = -sr(d - 1, -INF, -a, 1)
            HC[KY] -= 1
            um(m, u)
            if ND[1]: break
            if s > best: best = s; bm = m
            if s > a: a = s
        if not ND[1]:
            TT[KY] = (bm, d, 0, best)
        d += 1
    return bm

def uci(m):
    f = m & 127; t = m >> 7 & 127; p = m >> 14 & 7
    return chr(97 + (f & 7)) + str(f // 16 + 1) + chr(97 + (t & 7)) + str(t // 16 + 1) + ("nbrq"[p - 2] if p else "")

def main():
    env = os.environ["MAKEFUN_ENV_URL"]
    def post(p, b):
        with urllib.request.urlopen(urllib.request.Request(env + p, json.dumps(b).encode(), {"content-type": "application/json"})) as r: return json.load(r)
    while True:
        g = post("/game", {})
        if g["status"] == "done": break
        TT.clear()
        while g["status"] == "your_move":
            st(); hist = [KY]
            for u in g["moves"]:
                fr = (int(u[1]) - 1) * 16 + ord(u[0]) - 97
                to = (int(u[3]) - 1) * 16 + ord(u[2]) - 97
                for m in gm():
                    if m & 127 == fr and m >> 7 & 127 == to and (len(u) < 5 or m >> 14 & 7 == 5 - "qrbn".index(u[4])):
                        mk(m); break
                hist.append(KY)
            g = post("/move", {"game": g["game"], "move": uci(choose(hist))})

main()
