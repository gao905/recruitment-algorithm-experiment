# ===================== 1. 导入所需库 =====================
import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

# ===================== 2. 全局配置与实验设计定义 =====================
# 页面基础配置
st.set_page_config(
    page_title="招聘算法模拟实验平台",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 核心实验设计：2×2×2被试间分组定义（严格匹配开题变量操作化）
# 分组规则：group_id 1-8，对应【统计公平/偏见-透明度高/低-有申诉/无申诉】
GROUP_CONFIG = {
    1: {"stat_fair": "公平", "transparency": "高透明", "appeal": "有申诉"},
    2: {"stat_fair": "公平", "transparency": "高透明", "appeal": "无申诉"},
    3: {"stat_fair": "公平", "transparency": "低透明", "appeal": "有申诉"},
    4: {"stat_fair": "公平", "transparency": "低透明", "appeal": "无申诉"},
    5: {"stat_fair": "偏见", "transparency": "高透明", "appeal": "有申诉"},
    6: {"stat_fair": "偏见", "transparency": "高透明", "appeal": "无申诉"},
    7: {"stat_fair": "偏见", "transparency": "低透明", "appeal": "有申诉"},
    8: {"stat_fair": "偏见", "transparency": "低透明", "appeal": "无申诉"},
}

# Likert 7级计分选项（全量表统一）
LIKERT7_OPTIONS = [1, 2, 3, 4, 5, 6, 7]
LIKERT7_LABELS = {
    1: "非常不同意",
    2: "比较不同意",
    3: "略微不同意",
    4: "中立",
    5: "略微同意",
    6: "比较同意",
    7: "非常同意"
}

# 数据保存文件路径（自动生成，无需修改）
DATA_FILE = "experiment_data.xlsx"

# ===================== 3. 会话状态初始化（页面跳转+数据持久化） =====================
# 初始化所有需要保存的变量，避免页面刷新数据丢失
def init_session_state():
    # 页面流程控制
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1  # 1=知情同意，2=前测，3=简历填报，4=分组与结果，5=后测，6=提交完成
    # 被试基础信息
    if "subject_id" not in st.session_state:
        st.session_state.subject_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(np.random.randint(1000,9999))  # 匿名被试编号
    if "informed_consent" not in st.session_state:
        st.session_state.informed_consent = False
    # 前测数据
    if "demographic" not in st.session_state:
        st.session_state.demographic = {}
    if "tech_trust" not in st.session_state:
        st.session_state.tech_trust = {}
    # 简历信息
    if "resume_info" not in st.session_state:
        st.session_state.resume_info = {}
    # 实验分组
    if "group_id" not in st.session_state:
        st.session_state.group_id = None
    if "group_config" not in st.session_state:
        st.session_state.group_config = {}
    # 算法结果
    if "algorithm_result" not in st.session_state:
        st.session_state.algorithm_result = "不通过"
    if "result_score" not in st.session_state:
        st.session_state.result_score = {}
    # 后测数据
    if "manipulation_check" not in st.session_state:
        st.session_state.manipulation_check = {}
    if "perceived_fairness" not in st.session_state:
        st.session_state.perceived_fairness = {}
    if "acceptance" not in st.session_state:
        st.session_state.acceptance = {}
    # 提交状态
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

# 执行初始化
init_session_state()

# ===================== 4. 工具函数：数据保存 =====================
def save_experiment_data():
    """将被试所有实验数据保存到Excel文件，适配SPSS分析格式"""
    # 构建单条数据字典
    data_row = {
        "被试编号": st.session_state.subject_id,
        "分组编号": st.session_state.group_id,
        "统计公平水平": st.session_state.group_config.get("stat_fair", ""),
        "透明度水平": st.session_state.group_config.get("transparency", ""),
        "申诉机制水平": st.session_state.group_config.get("appeal", ""),
        "算法最终结果": st.session_state.algorithm_result,
        # 人口学控制变量
        "性别": st.session_state.demographic.get("gender", ""),
        "年龄": st.session_state.demographic.get("age", ""),
        "教育背景": st.session_state.demographic.get("education", ""),
        "当前身份": st.session_state.demographic.get("identity", ""),
        "求职经历": st.session_state.demographic.get("job_hunt_exp", ""),
        "互联网熟练程度": st.session_state.demographic.get("internet_skill", ""),
        # 技术信任倾向量表（T1-T5）
        "T1": st.session_state.tech_trust.get("T1", None),
        "T2": st.session_state.tech_trust.get("T2", None),
        "T3": st.session_state.tech_trust.get("T3", None),
        "T4": st.session_state.tech_trust.get("T4", None),
        "T5": st.session_state.tech_trust.get("T5", None),
        # 操控检验量表（F1-F3,P1-P3,C1-C3）
        "F1": st.session_state.manipulation_check.get("F1", None),
        "F2": st.session_state.manipulation_check.get("F2", None),
        "F3": st.session_state.manipulation_check.get("F3", None),
        "P1": st.session_state.manipulation_check.get("P1", None),
        "P2": st.session_state.manipulation_check.get("P2", None),
        "P3": st.session_state.manipulation_check.get("P3", None),
        "C1": st.session_state.manipulation_check.get("C1", None),
        "C2": st.session_state.manipulation_check.get("C2", None),
        "C3": st.session_state.manipulation_check.get("C3", None),
        # 感知公平量表（PF1-PF6）
        "PF1": st.session_state.perceived_fairness.get("PF1", None),
        "PF2": st.session_state.perceived_fairness.get("PF2", None),
        "PF3": st.session_state.perceived_fairness.get("PF3", None),
        "PF4": st.session_state.perceived_fairness.get("PF4", None),
        "PF5": st.session_state.perceived_fairness.get("PF5", None),
        "PF6": st.session_state.perceived_fairness.get("PF6", None),
        # 接受度量表（A1-A9）
        "A1": st.session_state.acceptance.get("A1", None),
        "A2": st.session_state.acceptance.get("A2", None),
        "A3": st.session_state.acceptance.get("A3", None),
        "A4": st.session_state.acceptance.get("A4", None),
        "A5": st.session_state.acceptance.get("A5", None),
        "A6": st.session_state.acceptance.get("A6", None),
        "A7": st.session_state.acceptance.get("A7", None),
        "A8": st.session_state.acceptance.get("A8", None),
        "A9": st.session_state.acceptance.get("A9", None),
        "提交时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 转换为DataFrame
    new_data = pd.DataFrame([data_row])

    # 若文件不存在，创建新文件；若存在，追加数据
    if os.path.exists(DATA_FILE):
        existing_data = pd.read_excel(DATA_FILE)
        final_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        final_data = new_data

    # 保存到Excel
    final_data.to_excel(DATA_FILE, index=False)
    st.session_state.submitted = True

# ===================== 5. 页面流程渲染（核心实验流程） =====================
# 步骤1：知情同意书（伦理要求，必须勾选才能进入实验）
if st.session_state.current_step == 1:
    st.title("招聘领域算法决策模拟实验")
    st.divider()
    st.subheader("知情同意书")
    st.markdown("""
    您好！欢迎参与本次学术研究实验。本实验由哈尔滨工业大学社会学系开展，旨在探究公众对招聘领域算法决策的认知与态度。

    **实验说明**：
    1.  本实验全程匿名，不会收集您的姓名、手机号、身份证号等任何可识别个人身份的信息，所有数据仅用于学术研究，严格保密。
    2.  实验总时长约8分钟，包含模拟招聘流程体验和问卷填写，无任何风险与不适。
    3.  您可以在实验过程中随时退出，无需承担任何责任；只有完成全部流程的有效问卷，可获得5元现金报酬。
    4.  实验内容仅用于学术研究，结果无对错之分，请您根据自身真实感受填写。

    如您已阅读并同意以上内容，请勾选下方选项进入实验。
    """)

    # 知情同意勾选
    consent = st.checkbox("我已阅读并同意上述知情同意书内容，自愿参与本次实验")
    st.session_state.informed_consent = consent

    # 下一步按钮
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        if st.button("进入实验", type="primary", use_container_width=True, disabled=not consent):
            st.session_state.current_step = 2
            st.rerun()

# 步骤2：前测问卷（人口学控制变量+技术信任倾向量表）
elif st.session_state.current_step == 2:
    st.title("前测问卷")
    st.divider()

    # 第一部分：人口学与控制变量
    st.subheader("一、基本信息")
    gender = st.radio("1. 您的性别：", options=["男", "女", "其他"], horizontal=True)
    age = st.radio("2. 您的年龄：", options=["18-22岁", "23-30岁", "31-45岁"], horizontal=True)
    education = st.radio("3. 您的最高教育背景：", options=["高中/中专及以下", "大专", "本科", "硕士及以上"], horizontal=True)
    identity = st.radio("4. 您当前的身份：", options=["在校大学生", "应届毕业生", "在职人员", "待业/求职中"], horizontal=True)
    job_hunt_exp = st.radio("5. 您是否有过线上平台求职/招聘的经历？", options=["从未有过", "1-2次", "3次及以上"], horizontal=True)
    internet_skill = st.radio("6. 您日常使用互联网/智能系统的熟练程度：", options=["非常不熟练", "比较不熟练", "一般", "比较熟练", "非常熟练"], horizontal=True)

    # 保存人口学数据
    st.session_state.demographic = {
        "gender": gender,
        "age": age,
        "education": education,
        "identity": identity,
        "job_hunt_exp": job_hunt_exp,
        "internet_skill": internet_skill
    }

    st.divider()
    # 第二部分：技术信任倾向量表
    st.subheader("二、技术信任倾向调查")
    st.markdown("请根据您对以下陈述的同意程度，选择对应的分数：1=非常不同意，7=非常同意")

    t1 = st.select_slider("T1. 我通常相信自动化算法系统能够做出公正的决策", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    t2 = st.select_slider("T2. 我认为算法系统比人工决策更能避免主观偏见", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    t3 = st.select_slider("T3. 我对新技术、新的智能系统持有开放和信任的态度", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    t4 = st.select_slider("T4. 我担心算法系统会隐藏不为人知的偏见，带来不公平的结果", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    t5 = st.select_slider("T5. 除非经过人工验证，否则我不会轻易相信算法的决策结果", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)

    # 保存技术信任数据
    st.session_state.tech_trust = {
        "T1": t1, "T2": t2, "T3": t3, "T4": t4, "T5": t5
    }

    # 上一步/下一步按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("上一步", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    with col2:
        if st.button("下一步", type="primary", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()

# 步骤3：虚拟简历填报（匹配实验自变量操控）
elif st.session_state.current_step == 3:
    st.title("模拟简历填报")
    st.divider()
    st.markdown("""
    接下来，您将进入模拟招聘场景。请您填写一份虚拟简历，体验企业招聘中的算法简历筛选流程。
    本次招聘岗位为【市场专员】，招聘要求为：本科及以上学历，具备相关实习/工作经验，良好的沟通能力。
    """)

    # 简历信息填写（核心用于偏见组的变量操控）
    name = st.text_input("虚拟姓名（可随意填写，仅用于模拟）", placeholder="例如：张三")
    gender_resume = st.radio("简历性别：", options=["男", "女"], horizontal=True)
    education_resume = st.radio("最高学历：", options=["本科", "硕士"], horizontal=True)
    school_type = st.radio("毕业院校类型：", options=["985/211院校", "普通本科院校"], horizontal=True)
    work_exp = st.radio("相关工作/实习经验：", options=["1年及以上", "无相关经验"], horizontal=True)
    skill_desc = st.text_area("个人技能与优势描述（可随意填写）", placeholder="例如：具备市场调研、新媒体运营能力，良好的沟通协调能力")

    # 保存简历信息
    st.session_state.resume_info = {
        "name": name,
        "gender_resume": gender_resume,
        "education_resume": education_resume,
        "school_type": school_type,
        "work_exp": work_exp,
        "skill_desc": skill_desc
    }

    # 上一步/下一步按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("上一步", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    with col2:
        if st.button("提交简历，进入筛选流程", type="primary", use_container_width=True, disabled=len(name)==0):
            # 随机分配实验组（关键！均等概率分配8个组）
            st.session_state.group_id = np.random.choice(list(GROUP_CONFIG.keys()), p=[1/8]*8)
            st.session_state.group_config = GROUP_CONFIG[st.session_state.group_id]

            # 算法结果生成（严格匹配开题的统计公平操作化）
            group_config = st.session_state.group_config
            # 基础通过规则：有相关经验+本科及以上，基础通过率80%
            base_pass = (work_exp == "1年及以上") and (education_resume in ["本科", "硕士"])
            pass_rate = 0.8 if base_pass else 0.2

            # 偏见组操控：女性/普通本科院校，通过率降低30%
            if group_config["stat_fair"] == "偏见":
                if gender_resume == "女" or school_type == "普通本科院校":
                    pass_rate = max(pass_rate - 0.3, 0.05)

            # 生成最终结果
            st.session_state.algorithm_result = "通过" if np.random.random() < pass_rate else "不通过"

            # 高透明组评分生成
            st.session_state.result_score = {
                "岗位匹配度": np.random.randint(30, 95),
                "能力胜任度": np.random.randint(30, 95),
                "简历完整度": np.random.randint(80, 100)
            }

            st.session_state.current_step = 4
            st.rerun()

# 步骤4：算法筛选结果展示（核心自变量操控环节）
elif st.session_state.current_step == 4:
    st.title("算法简历筛选结果")
    st.divider()
    group_config = st.session_state.group_config
    result = st.session_state.algorithm_result

    # 结果标题
    if result == "通过":
        st.success(f"📌 您的简历筛选结果：{result}，进入面试环节")
    else:
        st.error(f"📌 您的简历筛选结果：{result}，未进入面试环节")

    st.divider()
    # 高透明组：展示评分+详细解释；低透明组：仅展示结果
    if group_config["transparency"] == "高透明":
        st.subheader("算法评分详情")
        score_col1, score_col2, score_col3 = st.columns(3)
        with score_col1:
            st.metric("岗位匹配度", f"{st.session_state.result_score['岗位匹配度']}分")
        with score_col2:
            st.metric("能力胜任度", f"{st.session_state.result_score['能力胜任度']}分")
        with score_col3:
            st.metric("简历完整度", f"{st.session_state.result_score['简历完整度']}分")

        st.markdown("""
        **算法决策规则说明**：
        本次简历筛选算法基于岗位匹配度、能力胜任度、简历完整度三个维度进行综合评分，评分维度权重均等，最终结果由综合得分决定，所有候选人采用统一评分标准。
        """)
    else:
        st.markdown("本次简历筛选结果由企业招聘算法系统综合评定，为最终筛选结果。")

    st.divider()
    # 申诉机制操控：有申诉组/无申诉组
    if group_config["appeal"] == "有申诉":
        st.info("""
        **结果申诉说明**：
        如您对本次算法筛选结果有异议，可提交申诉申请，我们将在24小时内安排人工对您的简历进行复核，复核结果将第一时间反馈给您。申诉邮箱：experiment_hr@163.com
        """)
    else:
        st.warning("本次算法筛选结果为最终评定结果，无申诉与复核渠道。")

    # 上一步/下一步按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("上一步", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    with col2:
        if st.button("填写后续问卷", type="primary", use_container_width=True):
            st.session_state.current_step = 5
            st.rerun()

# 步骤5：后测核心问卷（操控检验+感知公平+接受度+注意力检验）
elif st.session_state.current_step == 5:
    st.title("实验后测问卷")
    st.divider()
    st.markdown("请根据您本次模拟实验的真实体验，填写以下问卷，所有问题无对错之分，请如实选择。")

    # 注意力检验题（关键！筛选无效样本）
    st.divider()
    st.subheader("一、注意力检验")
    attention_check = st.select_slider(
        "为确保您认真阅读本次实验，请本题选择「略微不同意」选项",
        options=LIKERT7_OPTIONS,
        format_func=lambda x: LIKERT7_LABELS[x],
        value=4
    )

    # 操控检验量表
    st.divider()
    st.subheader("二、实验体验评价")
    st.markdown("请根据您对以下陈述的同意程度，选择对应的分数：1=非常不同意，7=非常同意")

    f1 = st.select_slider("F1. 我认为该招聘算法对不同性别、不同院校背景的候选人存在明显的偏见", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    f2 = st.select_slider("F2. 在相同胜任力下，该算法对所有候选人的通过标准是一致的", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    f3 = st.select_slider("F3. 该算法的招聘结果没有偏向特定的社会群体", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)

    p1 = st.select_slider("P1. 我清楚地了解该招聘算法的决策依据和评分规则", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    p2 = st.select_slider("P2. 该算法向我充分解释了最终招聘结果的产生原因", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    p3 = st.select_slider("P3. 该算法的决策过程像一个“黑箱”，我完全无法理解", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)

    c1 = st.select_slider("C1. 我认为自己有渠道对该算法的招聘结果提出申诉和复核", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    c2 = st.select_slider("C2. 面对该算法的决策结果，我没有任何反驳和干预的机会", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    c3 = st.select_slider("C3. 即使对算法结果不满意，我也有对应的解决途径", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)

    # 保存操控检验数据
    st.session_state.manipulation_check = {
        "F1": f1, "F2": f2, "F3": f3,
        "P1": p1, "P2": p2, "P3": p3,
        "C1": c1, "C2": c2, "C3": c3,
        "attention_check": attention_check
    }

    # 感知公平量表
    st.divider()
    st.subheader("三、公平性感知调查")
    st.markdown("请根据您对以下陈述的同意程度，选择对应的分数：1=非常不同意，7=非常同意")

    pf1 = st.select_slider("PF1. 我认为本次招聘算法的决策过程是公平的", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    pf2 = st.select_slider("PF2. 我认为该算法对所有求职者都做到了一视同仁", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    pf3 = st.select_slider("PF3. 该算法的决策结果与求职者的个人能力是匹配的", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    pf4 = st.select_slider("PF4. 我认为该算法的决策规则没有包含任何歧视性内容", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    pf5 = st.select_slider("PF5. 面对该算法的决策，我感受到了被公平对待", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    pf6 = st.select_slider("PF6. 我认为该算法的招聘决策存在明显的不公平之处", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)

    # 保存感知公平数据
    st.session_state.perceived_fairness = {
        "PF1": pf1, "PF2": pf2, "PF3": pf3,
        "PF4": pf4, "PF5": pf5, "PF6": pf6
    }

    # 公众接受度量表
    st.divider()
    st.subheader("四、算法接受度调查")
    st.markdown("请根据您对以下陈述的同意程度，选择对应的分数：1=非常不同意，7=非常同意")

    a1 = st.select_slider("A1. 我认为该招聘算法能够有效提升招聘流程的效率", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    a2 = st.select_slider("A2. 我认为该招聘算法的决策比人工招聘更具客观性", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    a3 = st.select_slider("A3. 我能够轻松理解该算法的运作逻辑和决策方式", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)

    a4 = st.select_slider("A4. 面对该算法的招聘决策，我感到安心和信任", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    a5 = st.select_slider("A5. 我对该算法在招聘中的应用感到反感和抵触", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    a6 = st.select_slider("A6. 我对该算法能否公平对待所有求职者感到担忧", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)

    a7 = st.select_slider("A7. 如果未来求职遇到该类算法招聘系统，我愿意使用其完成求职流程", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    a8 = st.select_slider("A8. 我会向身边的求职者推荐使用这类公平的算法招聘平台", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)
    a9 = st.select_slider("A9. 我支持企业在招聘中广泛应用这类算法系统", options=LIKERT7_OPTIONS, format_func=lambda x: LIKERT7_LABELS[x], value=4)

    # 保存接受度数据
    st.session_state.acceptance = {
        "A1": a1, "A2": a2, "A3": a3,
        "A4": a4, "A5": a5, "A6": a6,
        "A7": a7, "A8": a8, "A9": a9
    }

    # 上一步/提交按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("上一步", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()
    with col2:
        if st.button("提交问卷，完成实验", type="primary", use_container_width=True):
            save_experiment_data()
            st.session_state.current_step = 6
            st.rerun()

# 步骤6：实验完成致谢页面
elif st.session_state.current_step == 6:
    st.balloons()
    st.title("实验完成，感谢您的参与！")
    st.divider()
    st.markdown("""
    您已完成本次实验的全部流程，非常感谢您的支持与配合！

    **报酬领取说明**：
    请您将下方的被试编号截图，添加微信：15543660190，发送截图即可领取5元现金报酬，我们将在24小时内完成发放。

    本次实验的匿名被试编号：
    """)
    st.code(st.session_state.subject_id)
    st.divider()
    st.info("如您对本次实验有任何疑问，可随时通过上述联系方式与我们联系，再次感谢您的参与！")

# 侧边栏：实验数据查看（仅开发者可见，被试端无影响）
with st.sidebar:
    st.title("实验后台管理")
    st.divider()
    st.metric("累计有效样本量", value=len(pd.read_excel(DATA_FILE)) if os.path.exists(DATA_FILE) else 0)
    if os.path.exists(DATA_FILE):
        st.download_button(
            label="下载全部实验数据",
            data=open(DATA_FILE, "rb").read(),
            file_name="招聘算法实验全量数据.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    st.divider()
    st.markdown("**当前被试分组信息**")
    st.write(f"分组编号：{st.session_state.group_id}")
    st.write(f"分组配置：{st.session_state.group_config}")