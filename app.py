import streamlit as st
import csv
import os
from collections import Counter

st.set_page_config(page_title="3D 量化终端", page_icon="⚡", layout="centered")
st.title("⚡ 3D 量化策略终端 (实战版)")

WAN_NENG_4 = ["2579", "2678", "5689", "0368", "0679", "3789", "0178", "0489", "1479", "0159", "0258", "1289", "0126", "0239", "1369", "0134", "0247", "1237", "1245", "1358", "2348", "2356", "2469", "3459", "0357", "0456", "3467", "1468", "1567", "4578"]
DUI_MA = {'0': '5', '1': '6', '2': '7', '3': '8', '4': '9', '5': '0', '6': '1', '7': '2', '8': '3', '9': '4'}

def get_wan4_18(num_str):
    a, b, c = num_str[0], num_str[1], num_str[2]
    ta, tb, tc = a, b, c
    if a == b == c: ta, tb, tc = a, DUI_MA[b], str((int(c) + 9) % 10)
    elif a == b or a == c or b == c:
        if a == b: tb = DUI_MA[b]; tc = c if tb != c else str((int(b) + 9) % 10)
        elif b == c: tc = DUI_MA[c]; tc = str((int(c) + 9) % 10) if tc == a else tc
        elif a == c: tc = DUI_MA[c]; tc = str((int(c) + 9) % 10) if tc == b else tc
    target_3d = ta + tb + tc
    base_4d = next((code for code in WAN_NENG_4 if all(d in code for d in target_3d)), "")
    if not base_4d: return []
    remainder = [str(i) for i in range(10) if str(i) not in base_4d]
    pairs = [base_4d[i] + base_4d[j] for i in range(4) for j in range(i+1, 4)]
    groups = set()
    for code in WAN_NENG_4:
        if code == base_4d: continue
        for pair in pairs:
            if pair[0] in code and pair[1] in code:
                others = set(code) - set(pair)
                if others.issubset(set(remainder)):
                    for i in range(4):
                        for j in range(i+1, 4):
                            for k in range(j+1, 4): groups.add("".join(sorted([code[i], code[j], code[k]])))
    return sorted(list(groups))

# ================= 适配你表格的精准读取 =================
def load_data():
    file_name = "fc3d_history_full.csv"
    if not os.path.exists(file_name):
        return [], f"❌ 找不到文件：{file_name}"

    nums = []
    try:
        with open(file_name, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                # 根据你的截图，总共5列，最后三列必定是百、十、个位
                if len(row) >= 4:
                    try:
                        # 取最后三列，强转整数防止小数点干扰
                        n1 = int(float(row[-3]))
                        n2 = int(float(row[-2]))
                        n3 = int(float(row[-1]))
                        num_str = f"{n1}{n2}{n3}"
                        nums.append(num_str)
                    except:
                        pass
        return nums[-200:], f"✅ 成功读取 {len(nums)} 期数据 (展示最近 {len(nums[-200:])} 期)"
    except Exception as e:
        return [], f"❌ 读取失败：{e}"

history_nums, msg = load_data()

st.sidebar.header("输入最新开奖号")
last_num = st.sidebar.text_input("上期号码 (如 435)", "813")

if len(last_num) == 3 and last_num.isdigit():
    wan4_groups = get_wan4_18(last_num)
    
    if history_nums:
        st.sidebar.success(msg)
        digit_counts = Counter()
        for n in history_nums:
            for d in n: digit_counts[d] += 1
        sorted_counts = sorted(digit_counts.items(), key=lambda x: x[1], reverse=True)
        hot_dan = [sorted_counts[0][0], sorted_counts[1][0], sorted_counts[2][0], sorted_counts[3][0]]
        kill = [sorted_counts[-1][0], sorted_counts[-2][0]]
    else:
        st.sidebar.error(msg) 
        hot_dan = ["3", "8", "4", "5"]
        kill = ["0", "1"]

    st.subheader(f"🔥 最新预测：{last_num} 推演")
    col1, col2 = st.columns(2)
    col1.success(f"定胆：{', '.join(hot_dan)}")
    col2.error(f"杀号：{', '.join(kill)}")
    
    filtered = [g for g in wan4_groups if any(d in g for d in hot_dan) and not any(k in g for k in kill) and len(set(g))==3]
    
    st.markdown("---")
    if len(filtered) <= 15:
        st.subheader(f"🎯 刺客极简单 ({len(filtered)}注)")
        st.write("  ".join(filtered))
    else:
        st.subheader(f"⚠️ 关注单 ({len(filtered)}注)")
        st.write("  ".join(filtered))
else:
    st.warning("请在左侧输入正确的 3 位数字")
