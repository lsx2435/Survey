import streamlit as st
import pandas as pd
import bt
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl
from riskprofile import RiskQuestionnaire

st.set_page_config(initial_sidebar_state="collapsed")

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "confirmation" not in st.session_state:
    st.session_state.confirmation = False
if "reset" not in st.session_state:
    st.session_state.reset = False
if "score" not in st.session_state:
    st.session_state.score = 0

font_dirs = '/customFonts'
font_files = fm.findSystemFonts(fontpaths=font_dirs)
for font_file in font_files:
    fm.fontManager.addfont(font_file)
        #plt.rcParmas['font.family'] = 'Nanum Brush Script OTF'
fm._load_fontmanager(try_read_cache=False)
plt.rcParams['font.family'] = "NanumGothic"
plt.rcParams['axes.unicode_minus'] = False
mpl.rc('font', family="NanumGothic")
plt.rc('font', family="NanumGothic")
mpl.rcParams['axes.unicode_minus'] = False

riskQuestionFile = "RiskQuestion.xlsx"
riskAnswerFile = "RiskAnswer.xlsx"
t = RiskQuestionnaire()
t.loadQuestionnaire(riskQuestionFile,riskAnswerFile)

st.header("투자자 성향 진단")
st.write("##")
selected_t = []

for i in range(len(t.questions)):
    question = t.questions[i]
    answer_1 = question.answers[0]
    answer_2 = question.answers[1]
    answer_3 = question.answers[2]   
    answer_4 = question.answers[3]
    selected = st.radio(question.questionText,[answer_1.answerText,answer_2.answerText,answer_3.answerText,answer_4.answerText], index=None)
    selected_t.append(str(selected))
    st.divider()

st.session_state.score = t.answerScore(selected_t)
#st.text(st.session_state.score)
#st.text(selected_t)
submitted = st.button(label="완료하기")

if submitted:
    if 'None' in selected_t:
        st.error("누락된 설문이 있습니다",icon = "🚨")
    else:
        st.session_state.submitted = True
        with open("saved_data.txt", "a") as file:
            file.write(str(st.session_state.score) + "\n")
        #switch_page("next")
        from portfolio import portfolio
        st.header("성향 진단 결과")
        if "status" not in st.session_state:
            st.session_state.status = "status"

        def result(score):
            if score <= 20:
                stat = "안정추구형 투자자"
            elif score > 40:
                stat = "공격투자형 투자자"
            elif score >20 & score <= 40:
                stat = "위험중립형 투자자"
            return(stat)

        def mp_vol(score):
            if score <=20:
                vol = 0.05
            elif score >= 35:
                vol = 0.3
            elif score >20 and score < 30:
                vol = 0.1
            elif score > 30 and score < 35:
                vol = 0.2
            return(vol)

        st.text(f'귀하는 "{result(st.session_state.score)}" 입니다')
        st.text(f'추천드리는 포트폴리오는 아래와 같습니다')

        t = portfolio()
        t.object(mp_vol(st.session_state.score))
        weight = t.port.to_dict()
        t.allocation_plot()
        s = t.port.index.values.tolist()
        k = t.port.values.tolist()
        fig = plt.figure(figsize=(15,5))
        plt.bar(s,k)
        st.pyplot(fig)

        st.text("월간 리밸런싱했다는 가정하에, ")
        st.text("2001년 9월부터 해당 포트폴리오에 투자했을 시 수익률 그래프는 아래와 같습니다")

        df = pd.read_excel("ASSETS.XLSX", skiprows=5, header=None, names = ["date", "북미 주식", "북미외 선진국 주식", "신흥국 주식", "글로벌 국채", "글로벌 투자등급 회사채", 
                                                                    "글로벌 하이일드 회사채",  "신흥국채권", "현금성자산"], index_col = 0 )
        df.sort_index(inplace=True)
    
        s = bt.Strategy("Recommended Portfolio", [bt.algos.RunMonthly(),
                            bt.algos.SelectAll(),
                           bt.algos.WeighSpecified(**weight),
                            bt.algos.Rebalance()])
                            #bt.algos.WeighSpecified(**weight)])
        e = bt.Strategy("Equal Weight Benchmark", [bt.algos.RunMonthly(),
                            bt.algos.SelectAll(),
                           bt.algos.WeighEqually(),
                            bt.algos.Rebalance()])
                            #bt.algos.WeighSpecified(**weight)])
        backtest_1 = bt.Backtest(s, df, initial_capital = 10000)
        backtest_2 = bt.Backtest(e, df, initial_capital = 10000)
        res = bt.run(backtest_1, backtest_2)
        g = res.plot()
        fig_2 = g.figure
        st.pyplot(fig_2)
        stats = res.stats.loc[['total_return', 'cagr', 'daily_vol', 'max_drawdown','daily_sharpe']]
        stats = stats.rename(index = {'total_return': '누적 수익률', 'cagr': '연간 수익률', 'daily_vol': '연간 변동성', 'max_drawdown': '최대낙폭', 'daily_sharpe': '샤프비율'})
        st.text("포트폴리오의 주요 특성은 아래와 같습니다")
        st.table(stats)
        st.session_state.confirmation = True                                                                                                                            

if st.session_state.confirmation:
    st.session_state.reset = st.button("성향조사 다시 하기")
    if st.session_state.reset:
        st.experimental_rerun()
