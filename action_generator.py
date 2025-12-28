from typing import List, Dict, Tuple
from functools import cmp_to_key
from card import Card

class ActionGenerator:
    def __init__(self):
        self.RANK_ORDER: List[str] = []
        self.RANK_TO_VAL: Dict[str, int] = {}
        self.MAX_STRAIGHT_RANK: str = "A"
        self.MIN_STRAIGHT_RANK: str = "3"

    @classmethod
    def NewActionGenerator(cls) -> 'ActionGenerator':
        ag = cls()
        ag.RANK_ORDER = ["3","4","5","6","7","8","9","T","J","Q","K","A","2","B","R"]
        # Faster lookups
        ag.RANK_TO_VAL = {}
        for i in range(0, len(ag.RANK_ORDER)):
            ag.RANK_TO_VAL[ ag.RANK_ORDER[i] ] = i

        # For "straight/pair-chain/airplane" the highest allowed rank is "A"
        ag.MAX_STRAIGHT_RANK = "A"   # cannot include "2","B","R"
        ag.MIN_STRAIGHT_RANK = "3"

        return ag

    def RankBefore(self, r: str):
        idx = self.RANK_TO_VAL[r]
        if idx <= 0:
            return None
        return self.RANK_ORDER[idx - 1]

    def RankAfter(self, r: str):
        idx = self.RANK_TO_VAL[r]
        if idx >= len(self.RANK_ORDER) - 1:
            return None
        return self.RANK_ORDER[idx + 1]

    def IsRankInStraightRange(self, r: str) -> bool:
        # Straight/PairChain/Airplane core allow only 3..A
        val = self.RANK_TO_VAL[r]
        return (self.RANK_TO_VAL[self.MIN_STRAIGHT_RANK] <= val) and (val <= self.RANK_TO_VAL[self.MAX_STRAIGHT_RANK])

    def CountRanks(self, hand_cards: List[Card]) -> Dict[str, int]:
        m: Dict[str, int] = {}
        for c in hand_cards:
            m[c.rank] = m.get(c.rank, 0) + 1
        return m

    def CountRanksFromString(self, s: str) -> Dict[str, int]:
        m: Dict[str, int] = {}
        for ch in s:
            m[ch] = m.get(ch, 0) + 1
        return m

    def CloneCounts(self, m: Dict[str, int]) -> Dict[str, int]:
        n: Dict[str, int] = {}
        for k, v in m.items():
            n[k] = v
        return n

    def SubCounts(self, a: Dict[str, int], b: Dict[str, int]) -> Dict[str, int]:
        # returns (a - b), assumes a has enough
        n = self.CloneCounts(a)
        for k, v in b.items():
            n[k] = n.get(k, 0) - v
            if n[k] <= 0:
                del n[k]
        return n

    def MakeUseMap(self, ranks: List[str], times: int) -> Dict[str, int]:
        m: Dict[str, int] = {}
        for r in ranks:
            m[r] = m.get(r, 0) + times
        return m

    def CountTotal(self, m: Dict[str, int]) -> int:
        s = 0
        for _, c in m.items():
            s = s + c
        return s

    def NumberOfKeys(self, cnt: Dict[str, int]) -> int:
        n = 0
        for _ in cnt.items():
            n = n + 1
        return n

    def AllSameCount(self, cnt: Dict[str, int], value: int) -> bool:
        if self.NumberOfKeys(cnt) == 0:
            return False
        for _, c in cnt.items():
            if c != value:
                return False
        return True

    def AllCountsMax(self, cnt: Dict[str, int], maxv: int) -> bool:
        for _, c in cnt.items():
            if c > maxv:
                return False
        return True

    def ContainsCount(self, cnt: Dict[str, int], target: int) -> bool:
        for _, c in cnt.items():
            if c == target:
                return True
        return False

    def GetRankWithCount(self, cnt: Dict[str, int], target: int):
        for r, c in cnt.items():
            if c == target:
                return r
        return None

    def SortRanks(self, ranks: List[str]) -> List[str]:
        ranks.sort(key=lambda rank: self.RANK_TO_VAL[rank])
        return ranks

    def SortedRanks(self, cnt: Dict[str, int]) -> List[str]:
        ranks: List[str] = []
        for r, _ in cnt.items():
            ranks.append(r)
        return self.SortRanks(ranks)

    def IsConsecutive(self, ranks_sorted: List[str]) -> bool:
        if len(ranks_sorted) <= 1:
            return True
        for i in range(0, len(ranks_sorted) - 1):
            if self.RANK_TO_VAL[ranks_sorted[i+1]] != self.RANK_TO_VAL[ranks_sorted[i]] + 1:
                return False
        return True

    def AllWithinStraightRange(self, ranks_sorted: List[str]) -> bool:
        for r in ranks_sorted:
            if not self.IsRankInStraightRange(r):
                return False
        return True

    def ListSingleRanksFromCounts(self, cnt: Dict[str, int]) -> List[str]:
        # Each rank appears as many times as multiplicity (so we can choose two different copies if available)
        out: List[str] = []
        for r, c in cnt.items():
            for _ in range(1, c + 1):
                out.append(r)
        # Keep stable order by rank value
        out = self.SortRanks(out)
        return out

    def ListPairRanksFromCounts(self, cnt: Dict[str, int]) -> List[str]:
        # Each rank appears floor(c/2) times; picking it once consumes 2 cards
        out: List[str] = []
        for r, c in cnt.items():
            k = c // 2
            for _ in range(1, k + 1):
                # Jokers cannot form pairs naturally; counts for "B"/"R" will be 0/1, so no entry added
                if r != "B" and r != "R":
                    out.append(r)
        out = self.SortRanks(out)
        return out

    def CombinationsByIndex(self, A: List, k: int) -> List[List[int]]:
        result: List[List[int]] = []
        cur: List[int] = []

        def dfs(start: int, remain: int):
            if remain == 0:
                result.append(list(cur))
                return
            for i in range(start, len(A) - remain + 1):
                cur.append(i)
                dfs(i + 1, remain - 1)
                cur.pop()

        if k <= len(A) and k >= 0:
            dfs(0, k)
        return result

    def StringFromCounts(self, cnt: Dict[str, int]) -> str:
        s = ""
        ranks_sorted = self.SortRanks(self.SortedRanks(cnt))
        for r in ranks_sorted:
            for _ in range(1, cnt.get(r, 0) + 1):
                s = s + r
        return s

    def FindAirplaneCores(self, counts: Dict[str, int]) -> List[List[str]]:
        cores: List[List[str]] = []
        # ranks eligible for core (>=3 and within straight range)
        elig: List[str] = []
        for r, c in counts.items():
            if (c >= 3) and self.IsRankInStraightRange(r):
                elig.append(r)
        elig = self.SortRanks(elig)

        # consecutive blocks length >=2
        i = 0
        while i < len(elig):
            j = i
            while (j + 1 < len(elig)) and (self.RANK_TO_VAL[elig[j+1]] == self.RANK_TO_VAL[elig[j]] + 1):
                j = j + 1
            block_len = j - i + 1
            if block_len >= 2:
                for L in range(2, block_len + 1):
                    for start in range(i, j - L + 2):
                        core: List[str] = []
                        for t in range(start, start + L):
                            core.append(elig[t])
                        cores.append(core)
            i = j + 1

        return cores

    def TryExtractAirplaneCore(self, cnt: Dict[str, int]) -> Dict:
        # Brute-force: try all possible cores (as IdentifyPatternFromString is called on already-fixed string)
        cores = self.FindAirplaneCores(cnt)
        for core_ranks in cores:
            # check if cnt has at least 3 of each core rank
            ok = True
            for r in core_ranks:
                if cnt.get(r, 0) < 3:
                    ok = False
                    break
            if ok:
                use = self.MakeUseMap(core_ranks, 3)  # r -> 3
                return {"success": True, "core_ranks": core_ranks, "core_use": use}
        return {"success": False}

    def RepeatRanks(self, core_ranks: List[str], times: int) -> str:
        s = ""
        for r in core_ranks:
            for _ in range(1, times + 1):
                s = s + r
        return s

    def IsValidAirplaneAttachmentCounts(self, core_ranks: List[str], attach_cnt: Dict[str, int], attach_type: str) -> bool:
        # rule: if single attachments → 不允许双王
        if attach_type == "single":
            if (attach_cnt.get("B", 0) == 1) and (attach_cnt.get("R", 0) == 1):
                return False

        # 组合后的总计数 = core(每核3张) + attach_cnt
        total: Dict[str, int] = {}
        for r in core_ranks:
            total[r] = total.get(r, 0) + 3
        for r, c in attach_cnt.items():
            total[r] = total.get(r, 0) + c

        # 不允许组合中出现炸弹（任何点数计数==4）
        for _, c in total.items():
            if c == 4:
                return False

        # 边缘检查：附件不得在核心左/右边界点数上达到 >=3（会构成更大飞机）
        # 获取核心最小/最大点数
        min_r = core_ranks[0]
        max_r = core_ranks[len(core_ranks) - 1]

        # 左边缘 = 前一位，必须在 [3..A] 范围内才检查
        left_edge = self.RankBefore(min_r)
        if (left_edge is not None) and self.IsRankInStraightRange(left_edge):
            if total.get(left_edge, 0) >= 3:
                return False

        # 右边缘 = 后一位，必须在 [3..A] 范围内才检查
        right_edge = self.RankAfter(max_r)
        if (right_edge is not None) and self.IsRankInStraightRange(right_edge):
            if total.get(right_edge, 0) >= 3:
                return False

        return True

    def IsValidAirplaneAttachmentString(self, core_str: str, attach_cnt: Dict[str, int], attach_type: str) -> bool:
        # derive core_ranks from core_str (every 3 contiguous chars per rank)
        core_rank_cnt = self.CountRanksFromString(core_str)
        core_ranks = self.SortedRanks(core_rank_cnt)
        return self.IsValidAirplaneAttachmentCounts(core_ranks, attach_cnt, attach_type)

    def IdentifyPatternFromString(self, action_str: str) -> Dict:
        info = {"kind": "invalid", "main_value": -1}

        if action_str == "" or action_str == "pass":
            return info

        # Count by rank
        cnt = self.CountRanksFromString(action_str)

        # Rocket
        if (len(action_str) == 2) and (cnt.get("B", 0) == 1) and (cnt.get("R", 0) == 1):
            info["kind"] = "rocket"
            info["main_value"] = 999
            return info

        # Bomb
        if len(action_str) == 4:
            # exactly four of a kind
            for rank, c in cnt.items():
                if c == 4:
                    info["kind"] = "bomb"
                    info["main_value"] = self.RANK_TO_VAL[rank]
                    return info

        # Solo / Pair / Trio
        if len(action_str) == 1:
            r = action_str[0]
            info["kind"] = "solo"
            info["main_value"] = self.RANK_TO_VAL[r]
            return info

        if len(action_str) == 2:
            # could be pair (not jokers, since "BR" already returned rocket)
            if self.AllSameCount(cnt, 2) and (self.NumberOfKeys(cnt) == 1):
                r = self.GetRankWithCount(cnt, 2)
                info["kind"] = "pair"
                info["main_value"] = self.RANK_TO_VAL[r]
                return info

        if len(action_str) == 3:
            if self.AllSameCount(cnt, 3) and (self.NumberOfKeys(cnt) == 1):
                r = self.GetRankWithCount(cnt, 3)
                info["kind"] = "trio"
                info["main_value"] = self.RANK_TO_VAL[r]
                info["core_count"] = 1
                return info

        # Trio with single (4 cards): trio(3) + single(1), single rank must differ from trio rank
        if len(action_str) == 4:
            if self.ContainsCount(cnt, 3) and self.ContainsCount(cnt, 1) and (self.NumberOfKeys(cnt) == 2):
                trio_rank = self.GetRankWithCount(cnt, 3)
                single_rank = self.GetRankWithCount(cnt, 1)
                if trio_rank != single_rank:
                    info["kind"] = "trio_single"
                    info["main_value"] = self.RANK_TO_VAL[trio_rank]
                    info["core_count"] = 1
                    return info

        # Trio with pair (5 cards): trio(3) + pair(2)
        if len(action_str) == 5:
            if self.ContainsCount(cnt, 3) and self.ContainsCount(cnt, 2) and (self.NumberOfKeys(cnt) == 2):
                trio_rank = self.GetRankWithCount(cnt, 3)
                pair_rank = self.GetRankWithCount(cnt, 2)
                if (trio_rank != pair_rank) and (pair_rank != "B") and (pair_rank != "R"):
                    info["kind"] = "trio_pair"
                    info["main_value"] = self.RANK_TO_VAL[trio_rank]
                    info["core_count"] = 1
                    return info

        # Four with two singles (6 cards): four(4) + two singles (can be same or different); no rocket among these two 
        if len(action_str) == 6:
            if self.ContainsCount(cnt, 4):
                four_rank = self.GetRankWithCount(cnt, 4)
                # Collect the remaining 2 cards
                rem_ranks: List[str] = []
                for rank, c in cnt.items():
                    if rank != four_rank:
                        for _ in range(1, c + 1):
                            rem_ranks.append(rank)
                # Must be exactly 2 remaining cards
                if len(rem_ranks) == 2:
                    # Check they are not rocket (B + R)
                    if not (("B" in rem_ranks) and ("R" in rem_ranks)):
                        info["kind"] = "four_two_single"
                        info["main_value"] = self.RANK_TO_VAL[four_rank]
                        return info

        # Four with two pairs (8 cards): four(4) + two pairs(2,2)
        if len(action_str) == 8:
            if self.ContainsCount(cnt, 4):
                four_rank = self.GetRankWithCount(cnt, 4)
                # Check remaining are exactly two pairs (no jokers can make pair anyway)
                pairs_count = 0
                ok = True
                for rank, c in cnt.items():
                    if rank == four_rank:
                        continue
                    if c == 2:
                        pairs_count = pairs_count + 1
                    else:
                        ok = False
                if ok and (pairs_count == 2):
                    info["kind"] = "four_two_pair"
                    info["main_value"] = self.RANK_TO_VAL[four_rank]
                    return info

        # Straight: length>=5, all single, consecutive in [3..A]
        if (len(action_str) >= 5) and self.AllSameCount(cnt, 1):
            ranks_sorted = self.SortedRanks(cnt)
            if self.AllWithinStraightRange(ranks_sorted) and self.IsConsecutive(ranks_sorted):
                # main value = highest rank in straight
                top = ranks_sorted[len(ranks_sorted) - 1]
                info["kind"] = "straight"
                info["main_value"] = self.RANK_TO_VAL[top]
                info["length"] = len(action_str)
                return info

        # Pair Chain: total length >=6 and divisible by 2, all counts==2, consecutive in [3..A]
        if (len(action_str) >= 6) and (len(action_str) % 2 == 0) and self.AllSameCount(cnt, 2):
            ranks_sorted = self.SortedRanks(cnt)
            if self.AllWithinStraightRange(ranks_sorted) and self.IsConsecutive(ranks_sorted):
                top = ranks_sorted[len(ranks_sorted) - 1]
                info["kind"] = "pair_chain"
                info["main_value"] = self.RANK_TO_VAL[top]
                info["pair_len"] = len(action_str) // 2
                return info

        # Airplane (pure): length divisible by 3, >= 6, all counts==3, consecutive in [3..A]
        if (len(action_str) >= 6) and (len(action_str) % 3 == 0):
            if self.AllSameCount(cnt, 3):
                ranks_sorted = self.SortedRanks(cnt)
                if self.AllWithinStraightRange(ranks_sorted) and self.IsConsecutive(ranks_sorted):
                    top = ranks_sorted[len(ranks_sorted) - 1]
                    info["kind"] = "airplane"
                    info["main_value"] = self.RANK_TO_VAL[top]
                    info["trio_len"] = len(action_str) // 3
                    info["core_count"] = info["trio_len"]
                    return info

        # Airplane with attachments:
        #   - with singles: total = 4*k, composed of k trios (consecutive) + k singles
        #   - with pairs  : total = 5*k, composed of k trios (consecutive) + k pairs
        # Identification strategy: try to extract a maximal consecutive trio-core.
        core = self.TryExtractAirplaneCore(cnt)
        if core.get("success", False):
            k = len(core["core_ranks"])            # number of trios
            top = core["core_ranks"][k - 1]
            remain = self.SubCounts(cnt, core["core_use"])  # remove exactly 3 of each core rank
            total_len = len(action_str)

            # with singles: 4*k
            if total_len == 4 * k:
                # remaining must be k single cards; additionally must satisfy "no rocket inside", "no bomb in final"
                if self.CountTotal(remain) == k:
                    # Validate attachments vs constraints (double-joker forbidden; no bombs in final; no adjacent-core extension by 3)
                    airplane_cards_str = self.RepeatRanks(core["core_ranks"], 3)   # 3 of each in order
                    if self.IsValidAirplaneAttachmentString(airplane_cards_str, remain, "single"):
                        info["kind"] = "airplane_single"
                        info["main_value"] = self.RANK_TO_VAL[top]
                        info["trio_len"] = k
                        info["core_count"] = k
                        return info

            # with pairs: 5*k
            if total_len == 5 * k:
                # remaining must be k pairs (counts all ==2)
                if self.CountTotal(remain) == 2 * k and self.AllSameCount(remain, 2):
                    airplane_cards_str = self.RepeatRanks(core["core_ranks"], 3)
                    if self.IsValidAirplaneAttachmentString(airplane_cards_str, remain, "pair"):
                        info["kind"] = "airplane_pair"
                        info["main_value"] = self.RANK_TO_VAL[top]
                        info["trio_len"] = k
                        info["core_count"] = k
                        return info

        return info

    def LexRankLess(self, a: str, b: str) -> bool:
        # compare char by char using rank order map
        i = 0
        while (i < len(a)) and (i < len(b)):
            va = self.RANK_TO_VAL[a[i]]
            vb = self.RANK_TO_VAL[b[i]]
            if va != vb:
                return va < vb
            i = i + 1
        return len(a) < len(b)

    def SortUnique(self, seq: List[str]) -> List[str]:
        # Deduplicate first
        seen = set()
        tmp: List[str] = []
        for s in seq:
            if s not in seen:
                seen.add(s)
                tmp.append(s)

        # Sort by:
        # 1) length ascending
        # 2) by main pattern value (if identifiable), otherwise lexicographic by rank order

        def compare_actions(a: str, b: str) -> int:
            if a == "pass" and b == "pass": return 0
            if a == "pass": return -1  # pass 排最前
            if b == "pass": return 1
            if len(a) != len(b):
                return -1 if len(a) < len(b) else 1
            ia = self.IdentifyPatternFromString(a)
            ib = self.IdentifyPatternFromString(b)
            if (ia["kind"] != "invalid") and (ib["kind"] != "invalid"):
                if ia["main_value"] != ib["main_value"]:
                    return -1 if ia["main_value"] < ib["main_value"] else 1
                # tie-break by lexicographic in rank-order
                return -1 if self.LexRankLess(a, b) else (1 if self.LexRankLess(b, a) else 0)
            else:
                return -1 if self.LexRankLess(a, b) else (1 if self.LexRankLess(b, a) else 0)

        tmp.sort(key=cmp_to_key(compare_actions))
        return tmp

    def FindSolos(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 1:
                result.append(r)
        return self.SortUnique(result)

    def FindPairs(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 2 and r != "B" and r != "R":
                result.append(r + r)
        return self.SortUnique(result)

    def FindTrios(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 3 and r != "B" and r != "R":
                result.append(r + r + r)
        return self.SortUnique(result)

    def FindTrioWithSingle(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)

        for r, c in counts.items():
            if c >= 3 and r != "B" and r != "R":
                # build remaining counts after taking trio rrr
                remain = self.CloneCounts(counts)
                remain[r] = remain.get(r, 0) - 3

                # singles cannot be same rank as trio, and cannot be empty
                for s_rank, s_cnt in remain.items():
                    if s_cnt >= 1 and s_rank != r:
                        result.append(r + r + r + s_rank)
        return self.SortUnique(result)

    def FindTrioWithPair(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)

        for r, c in counts.items():
            if c >= 3 and r != "B" and r != "R":
                remain = self.CloneCounts(counts)
                remain[r] = remain.get(r, 0) - 3
                for p_rank, p_cnt in remain.items():
                    if (p_cnt >= 2) and (p_rank != "B") and (p_rank != "R") and (p_rank != r):
                        result.append(r + r + r + p_rank + p_rank)
        return self.SortUnique(result)

    def FindStraights(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)

        # collect ranks eligible for straight (>=1, 3..A)
        elig: List[str] = []
        for r, c in counts.items():
            if (c >= 1) and self.IsRankInStraightRange(r):
                elig.append(r)
        elig = self.SortRanks(elig)  # ascending by RANK_TO_VAL

        # find all consecutive windows of length >= 5
        i = 0
        while i < len(elig):
            j = i
            while (j + 1 < len(elig)) and (self.RANK_TO_VAL[elig[j+1]] == self.RANK_TO_VAL[elig[j]] + 1):
                j = j + 1
            # elig[i..j] is a consecutive block
            block_len = j - i + 1
            if block_len >= 5:
                # output all sub-windows of length >= 5
                for L in range(5, block_len + 1):
                    for start in range(i, j - L + 2):
                        s = ""
                        for t in range(start, start + L):
                            s = s + elig[t]
                        result.append(s)
            i = j + 1

        return self.SortUnique(result)

    def FindPairChains(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)

        # eligible ranks: count>=2 and in straight range
        elig: List[str] = []
        for r, c in counts.items():
            if (c >= 2) and self.IsRankInStraightRange(r):
                elig.append(r)
        elig = self.SortRanks(elig)

        # consecutive blocks, each contributes 2 of that rank
        i = 0
        while i < len(elig):
            j = i
            while (j + 1 < len(elig)) and (self.RANK_TO_VAL[elig[j+1]] == self.RANK_TO_VAL[elig[j]] + 1):
                j = j + 1
            block_len = j - i + 1
            if block_len >= 3:
                # sub-windows length >=3
                for L in range(3, block_len + 1):
                    for start in range(i, j - L + 2):
                        s = ""
                        for t in range(start, start + L):
                            s = s + elig[t] + elig[t]
                        result.append(s)
            i = j + 1

        return self.SortUnique(result)

    def FindAirplanes(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)

        # eligible ranks: count>=3 and in straight range
        elig: List[str] = []
        for r, c in counts.items():
            if (c >= 3) and self.IsRankInStraightRange(r):
                elig.append(r)
        elig = self.SortRanks(elig)

        # find consecutive blocks of length >=2
        i = 0
        while i < len(elig):
            j = i
            while (j + 1 < len(elig)) and (self.RANK_TO_VAL[elig[j+1]] == self.RANK_TO_VAL[elig[j]] + 1):
                j = j + 1
            block_len = j - i + 1
            if block_len >= 2:
                for L in range(2, block_len + 1):
                    for start in range(i, j - L + 2):
                        s = ""
                        for t in range(start, start + L):
                            s = s + elig[t] + elig[t] + elig[t]
                        result.append(s)
            i = j + 1

        return self.SortUnique(result)

    def FindAirplanesWithAttachments(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)

        # 先找所有飞机核心
        cores = self.FindAirplaneCores(counts)  # list of core_ranks (ascending) each

        for core_ranks in cores:
            k = len(core_ranks)
            # 构造核心牌串
            core_str = self.RepeatRanks(core_ranks, 3)
            # 剩余牌计数
            remain = self.SubCounts(counts, self.MakeUseMap(core_ranks, 3))

            # --- 带单牌：需要 k 个单牌 ---
            single_slots = k
            single_candidates = self.ListSingleRanksFromCounts(remain)  # ranks repeated by multiplicity
            # 组合从 single_candidates 中选 k 个不同“实例”（允许同点数多张，只要剩余中有多张）
            for pick in self.CombinationsByIndex(single_candidates, single_slots):
                # 构造附件计数
                attach_cnt: Dict[str, int] = {}
                for idx in pick:
                    r = single_candidates[idx]
                    attach_cnt[r] = attach_cnt.get(r, 0) + 1

                # 校验：不允许双王
                if (attach_cnt.get("B", 0) == 1) and (attach_cnt.get("R", 0) == 1):
                    continue

                # 校验：最终无炸弹 && 不从大飞机拆出小飞机（边缘检查）
                if not self.IsValidAirplaneAttachmentCounts(core_ranks, attach_cnt, "single"):
                    continue

                # 通过：拼接字符串
                attach_str = self.StringFromCounts(attach_cnt)
                result.append(core_str + attach_str)

            # --- 带对子：需要 k 个对子 ---
            pair_slots = k
            pair_candidates = self.ListPairRanksFromCounts(remain)  # rank appears floor(count/2) times
            for pick in self.CombinationsByIndex(pair_candidates, pair_slots):
                # 构造附件计数（每个被选中的索引贡献2张）
                attach_cnt: Dict[str, int] = {}
                for idx in pick:
                    r = pair_candidates[idx]
                    attach_cnt[r] = attach_cnt.get(r, 0) + 2

                # 校验：最终无炸弹 && 不从大飞机拆出小飞机（边缘检查）
                if not self.IsValidAirplaneAttachmentCounts(core_ranks, attach_cnt, "pair"):
                    continue

                attach_str = self.StringFromCounts(attach_cnt)
                result.append(core_str + attach_str)

        return self.SortUnique(result)

    def FindFourWithTwo(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)

        for r, c in counts.items():
            if c >= 4:
                # take four r as core
                core_str = r + r + r + r
                remain = self.CloneCounts(counts)
                remain[r] = remain.get(r, 0) - 4

                # --- two singles (distinct ranks; cannot be BR as rocket) ---
                singles = self.ListSingleRanksFromCounts(remain)
                for pick in self.CombinationsByIndex(singles, 2):
                    rank1 = singles[pick[0]]
                    rank2 = singles[pick[1]]
                    if ((rank1 == "B" and rank2 == "R") or (rank1 == "R" and rank2 == "B")):
                        continue  # 不允许附件组成火箭
                    s = core_str + rank1 + rank2
                    result.append(s)

                # --- two pairs (distinct or same rank? 必须是两对 → 两个不同点数的对子) ---
                pairs = self.ListPairRanksFromCounts(remain)
                for pick in self.CombinationsByIndex(pairs, 2):
                    rankA = pairs[pick[0]]
                    rankB = pairs[pick[1]]
                    if rankA == rankB:
                        continue
                    # jokers不会形成对子；
                    s = core_str + rankA + rankA + rankB + rankB
                    result.append(s)

        return self.SortUnique(result)

    def FindBombs(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 4 and r != "B" and r != "R":
                result.append(r + r + r + r)
        return self.SortUnique(result)

    def FilterHigherBombs(self, hand_cards: List[Card], last_bomb_value: int) -> List[str]:
        bombs = self.FindBombs(hand_cards)
        out: List[str] = []
        for b in bombs:
            r = b[0]
            if self.RANK_TO_VAL[r] > last_bomb_value:
                out.append(b)
        return self.SortUnique(out)

    def HasRocket(self, hand_cards: List[Card]) -> bool:
        counts = self.CountRanks(hand_cards)
        return (counts.get("B", 0) >= 1) and (counts.get("R", 0) >= 1)

    def FindSamePatternStronger(self, hand_cards: List[Card], last_info: Dict) -> List[str]:
        out: List[str] = []

        kind = last_info["kind"]

        if kind == "solo":
            candidates = self.FindSolos(hand_cards)
            for s in candidates:
                val = self.RANK_TO_VAL[s[0]]
                if val > last_info["main_value"]:
                    out.append(s)

        elif kind == "pair":
            candidates = self.FindPairs(hand_cards)
            for s in candidates:
                val = self.RANK_TO_VAL[s[0]]
                if val > last_info["main_value"]:
                    out.append(s)

        elif kind == "trio":
            candidates = self.FindTrios(hand_cards)
            for s in candidates:
                trio_rank = s[0]
                if self.RANK_TO_VAL[trio_rank] > last_info["main_value"]:
                    out.append(s)

        elif kind == "trio_single":
            candidates = self.FindTrioWithSingle(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "trio_single") and (info.get("core_count", 0) == last_info.get("core_count", 0)) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)

        elif kind == "trio_pair":
            candidates = self.FindTrioWithPair(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "trio_pair") and (info.get("core_count", 0) == last_info.get("core_count", 0)) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)

        elif kind == "straight":
            candidates = self.FindStraights(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "straight") and (info.get("length", 0) == last_info.get("length", 0)) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)

        elif kind == "pair_chain":
            candidates = self.FindPairChains(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "pair_chain") and (info.get("pair_len", 0) == last_info.get("pair_len", 0)) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)

        elif kind == "airplane":
            candidates = self.FindAirplanes(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "airplane") and (info.get("trio_len", 0) == last_info.get("trio_len", 0)) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)

        elif kind == "airplane_single":
            candidates = self.FindAirplanesWithAttachments(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "airplane_single") and (info.get("trio_len", 0) == last_info.get("trio_len", 0)) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)

        elif kind == "airplane_pair":
            candidates = self.FindAirplanesWithAttachments(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "airplane_pair") and (info.get("trio_len", 0) == last_info.get("trio_len", 0)) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)

        elif kind == "four_two_single":
            candidates = self.FindFourWithTwo(hand_cards)   # both forms returned; filter in identify
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "four_two_single") and (info["main_value"] > last_info["main_value"]):
                    out.append(s)

        elif kind == "four_two_pair":
            candidates = self.FindFourWithTwo(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "four_two_pair") and (info["main_value"] > last_info["main_value"]):
                    out.append(s)

        else:
            # "bomb" handled outside; default do nothing
            pass

        return self.SortUnique(out)

    def GenerateAllPatterns(self, hand_cards: List[Card]) -> List[str]:
        result: List[str] = []

        solos = self.FindSolos(hand_cards)
        for s in solos: result.append(s)

        pairs = self.FindPairs(hand_cards)
        for s in pairs: result.append(s)

        trios = self.FindTrios(hand_cards)
        for s in trios: result.append(s)

        trio_single = self.FindTrioWithSingle(hand_cards)
        for s in trio_single: result.append(s)

        trio_pair = self.FindTrioWithPair(hand_cards)
        for s in trio_pair: result.append(s)

        straights = self.FindStraights(hand_cards)
        for s in straights: result.append(s)

        pair_chains = self.FindPairChains(hand_cards)
        for s in pair_chains: result.append(s)

        airplanes = self.FindAirplanes(hand_cards)
        for s in airplanes: result.append(s)

        airplane_wings = self.FindAirplanesWithAttachments(hand_cards)
        for s in airplane_wings: result.append(s)

        four_two = self.FindFourWithTwo(hand_cards)
        for s in four_two: result.append(s)

        bombs = self.FindBombs(hand_cards)
        for s in bombs: result.append(s)

        if self.HasRocket(hand_cards):
            result.append("BR")

        return self.SortUnique(result)

    def GetLegalActions(self, player, round_context) -> List[str]:
        actions: List[str] = []
        hand_cards = player.GetHand()

        # Retrieve last non-pass play
        last = round_context.GetLastValidPlay()  # (player_id, action_str) or null

        if (last is None) or (last[0] == player.GetId()):
            # Free play: generate everything
            all_patterns = self.GenerateAllPatterns(hand_cards)
            for s in all_patterns:
                actions.append(s)
            return self.SortUnique(actions)

        # Follow case
        actions.append("pass")
        last_str = last[1]
        last_info = self.IdentifyPatternFromString(last_str)

        # If last was invalid (shouldn't happen), treat as free play (minus duplication)
        if last_info["kind"] == "invalid":
            all_patterns = self.GenerateAllPatterns(hand_cards)
            for s in all_patterns:
                actions.append(s)
            return self.SortUnique(actions)

        # If last was rocket, nothing can beat it; only "pass"
        if last_info["kind"] == "rocket":
            return self.SortUnique(actions)

        # 1) Same pattern but stronger (same size & type)
        stronger = self.FindSamePatternStronger(hand_cards, last_info)
        for s in stronger:
            actions.append(s)

        # 2) Any bomb beats non-bomb
        if last_info["kind"] != "bomb":
            bombs = self.FindBombs(hand_cards)
            for b in bombs:
                actions.append(b)
        else:
            # last is bomb → only higher bomb allowed
            higher_bombs = self.FilterHigherBombs(hand_cards, last_info["main_value"])
            for b in higher_bombs:
                actions.append(b)

        # 3) Rocket always allowed if present
        if self.HasRocket(hand_cards):
            actions.append("BR")

        return self.SortUnique(actions)
