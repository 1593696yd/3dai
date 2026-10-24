import streamlit as st
import csv
import os
import pandas as pd
from collections import Counter

st.set_page_config(page_title="3D 量化终端", page_icon="⚡", layout="wide")
st.title("⚡ 3D 量化策略终端 (大满贯版)")

# ================= 核心算法 =================
WAN_NENG_4 = ["2579", "2678", "5689", "0368", "0679", "3789", "0178", "0489", "1479", "0159", "0258", "1289", "0126", "0239", "1369", "0134", "0247", "1237", "1245", "1358", "2348", "2356", "2469", "3459", "0357", "0456", "3467", "1468", "1567", "4578"]
DUI_MA = {'0': '5', '1': '6', '2': '7', '3': '8', '4': '9', '5': '0', '6': '1', '7': '2', '8': '3', '9': '4'}
MAPPING_TABLE = {"0134": ["2579", "2678", "5689"], "1245": ["0368", "0679", "3789"], "2356": ["0178", "0489", "1479"], "3467": ["0159", "0258", "1289"], "4578": ["0126", "0239", "1369"], "5689": ["0134", "0247", "1237"], "6790": ["1245", "1358", "2348"], "7801": ["2356", "2469", "3459"], "8912": ["0357", "0456", "3467"], "9023": ["1468", "1567", "4578"]}

def convert_number(num_str):
    a, b, c = num_str[0], num_str[1], num_str[2]
    ta, tb, tc = a, b, c
    if a == b == c: ta, tb, tc = a, DUI_MA[b], str((int(c) + 9) % 10)
    elif a == b or a == c or b == c:
        if a == b: tb = DUI_MA[b]; tc = c if tb != c else str((int(b) + 9) % 10)
        elif b == c: tc = DUI_MA[c]; tc = str((int(c) + 9) % 10) if tc == a else tc
        elif a == c: tc = DUI_MA[c]; tc = str((int(c) + 9) % 10) if tc == b else tc
    return ta + tb + tc

def get_wan4_18(num_str):
    target_3d = convert_number(num_str)
    base_4d = next((code for code in WAN_NENG_4 if all(d in code for d in target_3d)), "")
    if not base_4d: return []
    remainder = [str(i) for i in range(10) if str(i) not in base_4d]
    pairs = [base_4d[i] + base_4d[j] for i in range(4) for j in range(i+1, 4)]
    candidates = set([base_4d])
    for code in WAN_NENG_4:
        if code == base_4d: continue
        for pair in pairs:
            if pair[0] in code and pair[1] in code:
                others = set(code) - set(pair)
                if others.issubset(set(remainder)):
                    candidates.add(code)
                    break
    return sorted(list(candidates))

def get_break_groups(num_str):
    target = convert_number(num_str)
    base4 = next((code for code in WAN_NENG_4 if all(d in code for d in target)), "")
    wan10 = next((key for key in MAPPING_TABLE if MAPPING_TABLE[key].count(base4) > 0 or key == base4), "")
    if not wan10: return []
    remainder = [str(i) for i in range(10) if str(i) not in wan10]
    B = [d for d in remainder if d in ['0','2','4','6','8']]
    C = [d for d in remainder if d not in ['0','2','4','6','8']]
    return [wan10, "".join(B), "".join(C)]

# ================= 数据读取 =================
def load_data():
    file_name = "fc3d_history_full.csv"
    if not os.path.exists(file_name): return []
    nums = []
    with open(file_name, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 4:
                try:
                    n1, n2, n3 = int(float(row[-3])), int(float(row[-2])), int(float(row[-1]))
                    nums.append(f"{n1}{n2}{n3}")
                except: pass
    return nums[-50:] # 取最近50期用于展示和计算

history_nums = load_data()

# ================= 核心逻辑 =================
st.sidebar.header("🎯 输入最新开奖号")
last_num = st.sidebar.text_input("上期号码 (如 435)", "813")

if len(last_num) == 3 and last_num.isdigit():
    
    # 1. 算冷热 AI
    digit_counts = Counter()
    for n in history_nums:
        for d in n: digit_counts[d] += 1
    sorted_counts = sorted(digit_counts.items(), key=lambda x: x[1], reverse=True)
    hot_dan = [sorted_counts[0][0], sorted_counts[1][0], sorted_counts[2][0], sorted_counts[3][0]]
    kill = [sorted_counts[-1][0], sorted_counts[-2][0]]

    # 2. 基础推演
    wan4_list = get_wan4_18(last_num)
    duan_groups = get_break_groups(last_num)

    # --- 第一部分：下期核心预测 ---
    st.subheader("🔥 下期核心预测")
    col1, col2, col3 = st.columns(3)
    col1.success(f"**定胆**：{', '.join(hot_dan)}")
    col2.error(f"**杀号**：{', '.join(kill)}")
    col3.info(f"**断组**：A组({duan_groups[0]}) B组({duan_groups[1]}) C组({duan_groups[2]})")

    # --- 第二部分：万四大底与刺客缩水 ---
    st.markdown("---")
    st.subheader("🎯 万四推演与缩水")
    
    # 找出万四的组选
    wan4_pool = set()
    for code in wan4_list:
        for i in range(4):
            for j in range(i+1, 4):
                for k in range(j+1, 4):
                    wan4_pool.add("".join(sorted([code[i], code[j], code[k]])))
    wan4_pool = sorted(list(wan4_pool))

    # 刺客缩水 (中定胆，避开杀号)
    filtered = [g for g in wan4_pool if any(d in g for d in hot_dan) and not any(k in g for k in kill)]
    
    with st.expander(f"📦 展开查看 18组万四底池 (共生成 {len(wan4_pool)} 注组六)"):
        st.write("  ".join(wan4_pool))

    if len(filtered) <= 15:
        st.success(f"**触发刺客！极简单 ({len(filtered)}注)**")
    else:
        st.warning(f"**关注单 ({len(filtered)}注)**")
    st.code("  ".join(filtered), language="text")

    # --- 第三部分：历史走势复盘 --
