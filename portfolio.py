class portfolio:
    def __init__(self):
        self.port = []

    def object(self,vol):
        import pandas as pd 
        from pypfopt.efficient_frontier import EfficientFrontier
        from pypfopt import risk_models
        from pypfopt import expected_returns
        from pypfopt import objective_functions

        df = pd.read_excel("ASSETS.xlsx", skiprows=5, header=None, names = ["date", "북미 주식", "북미외 선진국 주식", "신흥국 주식", "글로벌 국채", "글로벌 투자등급 회사채", 
                                                                    "글로벌 하이일드 회사채",  "신흥국채권", "현금성자산"], index_col = 0 )
        df.sort_index(inplace=True)
        #df_return = df.pct_change().dropna()
        #df = df.drop("금", axis=1)
        mu = expected_returns.mean_historical_return(df, frequency=52)
        S = risk_models.sample_cov(df, frequency=52)

        ef = EfficientFrontier(mu, S)
        ef.add_constraint(lambda x: x >= 0.01)
        ef.add_constraint(lambda x: x <= 0.4)
        #ef.add_constraint(lambda x: x[3] + x[4]+ x[5]+ x[6] <=0.8)
        ef.add_constraint(lambda x: x[3] + x[4]+ x[5]+ x[6] + x[7]>=0.3)
        #ef.add_constraint(lambda x: x[6] <= 0.3)
        if vol <= 0.1:
            ef.add_constraint(lambda x: x[3] + x[4]+ x[5]+ x[6] + x[7]>= 0.7)
        elif vol >= 0.2 and vol < 0.3: 
            ef.add_constraint(lambda x: x[0]+x[1]+x[2] >= 0.5)
            ef.add_constraint(lambda x: x[7] <= 0.05)   
        elif vol >= 0.3:
            ef.add_constraint(lambda x: x[0]+x[1]+x[2] >= 0.6)
            ef.add_constraint(lambda x: x[7] <= 0.05)
        #ef.add_constraint(lambda x: x[5] <= 0.2)
        #ef.add_constraint(lambda x: x[7] <= 0.8)
        ef.add_objective(objective_functions.L2_reg, gamma = 0.1)
        ef.efficient_risk(vol)
        weight = ef.clean_weights()
        self.port = pd.DataFrame(weight, index = weight.keys()).iloc[0]

    def allocation_plot(self):
        import matplotlib
        import matplotlib.pyplot as plt
        matplotlib.rcParams['font.family'] ='Malgun Gothic'
        matplotlib.rcParams['axes.unicode_minus'] = False
        t = self.port.index.values.tolist()
        k = self.port.values.tolist()
        plt.bar(t,k)
        plt.legend(fontsize=20)
        plt.show()
    
    def backtest(self):
        import pandas as pd
        import bt
        df = pd.read_excel("ASSETS.xlsx", skiprows=5, header=None, names = ["date", "북미 주식", "북미외 선진국 주식", "신흥국 주식", "글로벌 국채", "글로벌 투자등급 회사채", 
                                                                    "글로벌 하이일드 회사채",  "신흥국채권", "초단기채"], index_col = 0 )
        df.sort_index(inplace=True)
        s = bt.Strategy("s", [bt.algos.RunMonthly(),
                            bt.algos.SelectAll(),
                            bt.algos.Rebalnce(),
                            br.algos.WeighSapecified(self.port)])
        backtest = bt.Backtest(s,df)
        res = bt.run(backtest)
        stats = res.stats.loc[['total_return', 'cagr', 'daily_vol', 'max_drawdown', 'calmar', 'daily_sharpe']]
