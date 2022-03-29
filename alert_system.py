import pandahouse as ph
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import telegram

sns.set_style("darkgrid", {"grid.color": ".6", "grid.linestyle": ":"})

connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20220320.feed_actions'}

bot = telegram.Bot(token='5109223515:AAGULsMs-W-pCPYrfNj8RlNUni7gU-UE7Do')
chat_id = 322178021
# -1001539201117 group chat_id
#  322178021 Danila chat_id

def check_feed_users():

    #Active users for the same 15-minute period for 10 last days (incliding today)
    ten_days = ph.read_clickhouse(connection=connection, query=
    ''' 
    select toStartOfFifteenMinutes(time) as ts,
        uniq(user_id) as active_users,
        toDate(ts) as date,
        formatDateTime(ts, '%R') as hm
    from simulator_20220320.feed_actions
    where (ts >=  today() - 9 and ts < toStartOfFifteenMinutes(now())) and (formatDateTime(ts, '%R') = 
        (select formatDateTime(toStartOfFifteenMinutes(time), '%R') as hm
        from simulator_20220320.feed_actions
        where toStartOfFifteenMinutes(time) >=  today() - 1 and toStartOfFifteenMinutes(time) < toStartOfFifteenMinutes(now())
        group by toStartOfFifteenMinutes(time) 
        order by toStartOfFifteenMinutes(time)  desc 
        limit 1
        ))
    group by ts
    order by ts desc 
    ''')

    #Active users since yesterday 00:00
    active_users = ph.read_clickhouse(connection=connection, query=
    '''
    SELECT
        toStartOfFifteenMinutes(time) as Time,
        toDate(Time) as date,
        formatDateTime(Time, '%R') as hm,
        uniq(user_id) as active_users
    FROM simulator_20220320.feed_actions
    WHERE Time >=  today() - 1 and Time < toStartOfFifteenMinutes(now())
    GROUP BY Time, date, hm
    ORDER BY Time desc
    ''')

    #data for comparing current value with value for previous period 
    now = ten_days.iloc[0,1]
    yesterday = ten_days.iloc[1,1]
    mean_10_days = np.mean(ten_days['active_users'])
    std_10_days = np.std(ten_days['active_users'])
    time = ten_days['hm'].iloc[0]

    #comparison
    if abs(int(now) - int(yesterday)) > (3 * std_10_days):
        alert = True
    else:
        alert = False    
        
    #sending message and graph in case of alert
    if alert:
        if yesterday < now:  
            pct_dev = f'which is {((now-yesterday)/yesterday)*100:0.2f}% higher compared to yesterday value for the same period'         
        else:
            pct_dev = f'which is {((yesterday-now)/yesterday)*100:0.2f}% lower compared to yesterday value for the same period'  

        message = f'Feed active users in last 15 minutes: {now}, {pct_dev}\nRealtime dashboard: http://superset.lab.karpov.courses/r/686'
        bot.sendMessage(chat_id=chat_id, text=message)

        fig,axes = plt.subplots(2,1, figsize=(15,12))
        plt.suptitle('Feed users', fontsize=20)
        sns.lineplot(data=ten_days, x='date', y='active_users', ax=axes[0], marker='o')
        axes[0].title.set_text(f'Number of feed active users in the same 15 minutes period ({time}) for last 10 days')

        sns.lineplot(data=active_users, x='Time', y='active_users', ax=axes[1])
        axes[1].title.set_text(f'Number of feed active users since yesterday 00:00')   
        
        fplot = io.BytesIO()
        plt.savefig(fplot)
        fplot.name = 'fplot.png'
        fplot.seek(0)
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=fplot)
        
        
def check_messenger_users():

    #Active users for the same 15-minute period for 10 last days (incliding today)
    ten_days = ph.read_clickhouse(connection=connection, query=
    ''' 
    select toStartOfFifteenMinutes(time) as ts,
        uniq(user_id) as active_users,
        toDate(ts) as date,
        formatDateTime(ts, '%R') as hm
    from simulator_20220320.message_actions
    where (ts >=  today() - 9 and ts < toStartOfFifteenMinutes(now())) and (formatDateTime(ts, '%R') = 
        (select formatDateTime(toStartOfFifteenMinutes(time), '%R') as hm
        from simulator_20220320.message_actions
        where toStartOfFifteenMinutes(time) >=  today() - 1 and toStartOfFifteenMinutes(time) < toStartOfFifteenMinutes(now())
        group by toStartOfFifteenMinutes(time) 
        order by toStartOfFifteenMinutes(time)  desc 
        limit 1
        ))
    group by ts
    order by ts desc 
    ''')

    #Active users since yesterday 00:00
    active_users = ph.read_clickhouse(connection=connection, query=
    '''
    SELECT
        toStartOfFifteenMinutes(time) as Time,
        toDate(Time) as date,
        formatDateTime(Time, '%R') as hm,
        uniq(user_id) as active_users
    FROM simulator_20220320.message_actions
    WHERE Time >=  today() - 1 and Time < toStartOfFifteenMinutes(now())
    GROUP BY Time, date, hm
    ORDER BY Time desc
    ''')
    
    #data for comparing current value with value for previous period 
    now = ten_days.iloc[0,1]
    yesterday = ten_days.iloc[1,1]
    mean_10_days = np.mean(ten_days['active_users'])
    std_10_days = np.std(ten_days['active_users'])
    time = ten_days['hm'].iloc[0]
    
    #comparison
    if abs(int(now) - int(yesterday)) > (3 * std_10_days):
        alert = True
    else:
        alert = False    

    #sending message and graph in case of alert
    if alert:
        if yesterday < now:  
            pct_dev = f'which is {((now-yesterday)/yesterday)*100:0.2f}% higher compared to yesterday value for the same period'         
        else:
            pct_dev = f'which is {((yesterday-now)/yesterday)*100:0.2f}% lower compared to yesterday value for the same period'  

        message = f'Messenger active users in last 15 minutes: {now}, {pct_dev}\nRealtime dashboard: http://superset.lab.karpov.courses/r/686'
        bot.sendMessage(chat_id=chat_id, text=message)

        fig,axes = plt.subplots(2,1, figsize=(15,12))
        plt.suptitle('Messenger users', fontsize=20)
        sns.lineplot(data=ten_days, x='date', y='active_users', ax=axes[0], marker='o')
        axes[0].title.set_text(f'Number of messenger active users in the same 15 minutes period ({time}) for last 10 days')

        sns.lineplot(data=active_users, x='Time', y='active_users', ax=axes[1])
        axes[1].title.set_text(f'Number of messenger active users since yesterday 00:00')   
        
        mplot = io.BytesIO()
        plt.savefig(mplot)
        mplot.name = 'mplot.png'
        mplot.seek(0)
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=mplot)
        

def check_views_number():

    #Number of views for the same 15-minute period for 10 last days (incliding today)
    ten_days = ph.read_clickhouse(connection=connection, query=
    ''' 
    select toStartOfFifteenMinutes(time) as ts,
        countIf(user_id, action = 'view') as views,
        toDate(ts) as date,
        formatDateTime(ts, '%R') as hm
    from simulator_20220320.feed_actions
    where (ts >=  today() - 9 and ts < toStartOfFifteenMinutes(now())) and (formatDateTime(ts, '%R') = 
        (select formatDateTime(toStartOfFifteenMinutes(time), '%R') as hm
        from simulator_20220320.feed_actions
        where toStartOfFifteenMinutes(time) >=  today() - 1 and toStartOfFifteenMinutes(time) < toStartOfFifteenMinutes(now())
        group by toStartOfFifteenMinutes(time) 
        order by toStartOfFifteenMinutes(time)  desc 
        limit 1
        ))
    group by ts
    order by ts desc  
    ''')

    #Number of views since yesterday 00:00
    number_of_views = ph.read_clickhouse(connection=connection, query=
    '''
    SELECT
        toStartOfFifteenMinutes(time) as Time,
        toDate(Time) as date,
        formatDateTime(Time, '%R') as hm,
        countIf(user_id, action = 'view') as views
    FROM simulator_20220320.feed_actions
    WHERE Time >=  today() - 1 and Time < toStartOfFifteenMinutes(now())
    GROUP BY Time, date, hm
    ORDER BY Time desc
    ''')

    #data for comparing current value with value for previous period 
    now = ten_days.iloc[0,1]
    yesterday = ten_days.iloc[1,1]
    mean_10_days = np.mean(ten_days['views'])
    std_10_days = np.std(ten_days['views'])
    time = ten_days['hm'].iloc[0]

    #comparison
    if abs(int(now) - int(yesterday)) > (3 * std_10_days):
        alert = True
    else:
        alert = False    
        
    #sending message and graph in case of alert
    if alert:
        if yesterday < now:  
            pct_dev = f'which is {((now-yesterday)/yesterday)*100:0.2f}% higher compared to yesterday value for the same period'         
        else:
            pct_dev = f'which is {((yesterday-now)/yesterday)*100:0.2f}% lower compared to yesterday value for the same period'  

        message = f'Number of views in last 15 minutes: {now}, {pct_dev}\nRealtime dashboard: http://superset.lab.karpov.courses/r/686'
        bot.sendMessage(chat_id=chat_id, text=message)

        fig,axes = plt.subplots(2,1, figsize=(15,12))
        plt.suptitle('Number of views', fontsize=20)
        sns.lineplot(data=ten_days, x='date', y='views', ax=axes[0], marker='o')
        axes[0].title.set_text(f'Number of views in the same 15 minutes period ({time}) for last 10 days')

        sns.lineplot(data=number_of_views, x='Time', y='views', ax=axes[1])
        axes[1].title.set_text(f'Number of views since yesterday 00:00')   
        
        vplot = io.BytesIO()
        plt.savefig(vplot)
        vplot.name = 'vplot.png'
        vplot.seek(0)
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=vplot)
       

def check_likes_number():
    #Number of likes for the same 15-minute period for 10 last days (incliding today)    
    ten_days = ph.read_clickhouse(connection=connection, query=
    ''' 
    select toStartOfFifteenMinutes(time) as ts,
        countIf(user_id, action = 'like') as likes,
        toDate(ts) as date,
        formatDateTime(ts, '%R') as hm
    from simulator_20220320.feed_actions
    where (ts >=  today() - 9 and ts < toStartOfFifteenMinutes(now())) and (formatDateTime(ts, '%R') = 
        (select formatDateTime(toStartOfFifteenMinutes(time), '%R') as hm
        from simulator_20220320.feed_actions
        where toStartOfFifteenMinutes(time) >=  today() - 1 and toStartOfFifteenMinutes(time) < toStartOfFifteenMinutes(now())
        group by toStartOfFifteenMinutes(time) 
        order by toStartOfFifteenMinutes(time)  desc 
        limit 1
        ))
    group by ts
    order by ts desc  
    ''')

    #Number of views since yesterday 00:00
    number_of_likes = ph.read_clickhouse(connection=connection, query=
    '''
    SELECT
        toStartOfFifteenMinutes(time) as Time,
        toDate(Time) as date,
        formatDateTime(Time, '%R') as hm,
        countIf(user_id, action = 'like') as likes
    FROM simulator_20220320.feed_actions
    WHERE Time >=  today() - 1 and Time < toStartOfFifteenMinutes(now())
    GROUP BY Time, date, hm
    ORDER BY Time desc
    ''')

    #data for comparing current value with value for previous period 
    now = ten_days.iloc[0,1]
    yesterday = ten_days.iloc[1,1]
    mean_10_days = np.mean(ten_days['likes'])
    std_10_days = np.std(ten_days['likes'])
    time = ten_days['hm'].iloc[0]

    #comparison
    if abs(int(now) - int(yesterday)) > (3 * std_10_days):
        alert = True
    else:
        alert = False    

    #sending message and graph in case of alert
    if alert:
        if yesterday < now:  
            pct_dev = f'which is {((now-yesterday)/yesterday)*100:0.2f}% higher compared to yesterday value for the same period'         
        else:
            pct_dev = f'which is {((yesterday-now)/yesterday)*100:0.2f}% lower compared to yesterday value for the same period'  

        message = f'Number of likes in last 15 minutes: {now}, {pct_dev}\nRealtime dashboard: http://superset.lab.karpov.courses/r/686'
        bot.sendMessage(chat_id=chat_id, text=message)

        fig,axes = plt.subplots(2,1, figsize=(15,12))
        plt.suptitle('Number of likes', fontsize=20)
        sns.lineplot(data=ten_days, x='date', y='likes', ax=axes[0], marker='o')
        axes[0].title.set_text(f'Number of likes in the same 15 minutes period ({time}) for last 10 days')

        sns.lineplot(data=number_of_likes, x='Time', y='likes', ax=axes[1])
        axes[1].title.set_text(f'Number of likes since yesterday 00:00')   

        lplot = io.BytesIO()
        plt.savefig(lplot)
        lplot.name = 'vplot.png'
        lplot.seek(0)
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=lplot)
        

def check_ctr():

    #CTR for the same 15-minute period for 10 last days (incliding today)    
    ten_days = ph.read_clickhouse(connection=connection, query=
    ''' 
    select toStartOfFifteenMinutes(time) as ts,
        countIf(user_id, action = 'like') / countIf(user_id, action = 'view') as ctr,
        toDate(ts) as date,
        formatDateTime(ts, '%R') as hm
    from simulator_20220320.feed_actions
    where (ts >=  today() - 9 and ts < toStartOfFifteenMinutes(now())) and (formatDateTime(ts, '%R') = 
        (select formatDateTime(toStartOfFifteenMinutes(time), '%R') as hm
        from simulator_20220320.feed_actions
        where toStartOfFifteenMinutes(time) >=  today() - 1 and toStartOfFifteenMinutes(time) < toStartOfFifteenMinutes(now())
        group by toStartOfFifteenMinutes(time) 
        order by toStartOfFifteenMinutes(time)  desc 
        limit 1
        ))
    group by ts
    order by ts desc  
    ''')

    #CTR since yesterday 00:00
    ctr = ph.read_clickhouse(connection=connection, query=
    '''
    SELECT
        toStartOfFifteenMinutes(time) as Time,
        toDate(Time) as date,
        formatDateTime(Time, '%R') as hm,
        countIf(user_id, action = 'like') / countIf(user_id, action = 'view') as ctr
    FROM simulator_20220320.feed_actions
    WHERE Time >=  today() - 1 and Time < toStartOfFifteenMinutes(now())
    GROUP BY Time, date, hm
    ORDER BY Time desc
    ''')

    #data for comparing current value with value for previous period 
    now = ten_days.iloc[0,1]
    yesterday = ten_days.iloc[1,1]
    mean_10_days = np.mean(ten_days['ctr'])
    std_10_days = np.std(ten_days['ctr'])
    time = ten_days['hm'].iloc[0]

    #comparison
    if abs(int(now) - int(yesterday)) > (3 * std_10_days):
        alert = True
    else:
        alert = False    

    #sending message and graph in case of alert
    if alert:
        if yesterday < now:  
            pct_dev = f'which is {((now-yesterday)/yesterday)*100:0.2f}% higher compared to yesterday value for the same period'         
        else:
            pct_dev = f'which is {((yesterday-now)/yesterday)*100:0.2f}% lower compared to yesterday value for the same period'  

        message = f'CTR in last 15 minutes: {now:0.2f}, {pct_dev}\nRealtime dashboard: http://superset.lab.karpov.courses/r/686'
        bot.sendMessage(chat_id=chat_id, text=message)

        fig,axes = plt.subplots(2,1, figsize=(15,12))
        plt.suptitle('CTR', fontsize=20)
        sns.lineplot(data=ten_days, x='date', y='ctr', ax=axes[0], marker='o')
        axes[0].title.set_text(f'CTR in the same 15 minutes period ({time}) for last 10 days')

        sns.lineplot(data=ctr, x='Time', y='ctr', ax=axes[1])
        axes[1].title.set_text(f'CTR since yesterday 00:00')   

        ctrplot = io.BytesIO()
        plt.savefig(ctrplot)
        ctrplot.name = 'ctrplot.png'
        ctrplot.seek(0)
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=ctrplot)
        
def check_sent_messages():

    #Number of sent messages in the same 15-minute period for 10 last days (incliding today)
    ten_days = ph.read_clickhouse(connection=connection, query=
    ''' 
    select toStartOfFifteenMinutes(time) as ts,
        count(user_id) as msg,
        toDate(ts) as date,
        formatDateTime(ts, '%R') as hm
    from simulator_20220320.message_actions
    where (ts >=  today() - 9 and ts < toStartOfFifteenMinutes(now())) and (formatDateTime(ts, '%R') = 
        (select formatDateTime(toStartOfFifteenMinutes(time), '%R') as hm
        from simulator_20220320.message_actions
        where toStartOfFifteenMinutes(time) >=  today() - 1 and toStartOfFifteenMinutes(time) < toStartOfFifteenMinutes(now())
        group by toStartOfFifteenMinutes(time) 
        order by toStartOfFifteenMinutes(time)  desc 
        limit 1
        ))
    group by ts
    order by ts desc 
    ''')

    ##Number of sent messages since yesterday 00:00
    active_users = ph.read_clickhouse(connection=connection, query=
    '''
    SELECT
        toStartOfFifteenMinutes(time) as Time,
        toDate(Time) as date,
        formatDateTime(Time, '%R') as hm,
        count(user_id) as msg
    FROM simulator_20220320.message_actions
    WHERE Time >=  today() - 1 and Time < toStartOfFifteenMinutes(now())
    GROUP BY Time, date, hm
    ORDER BY Time desc
    ''')
    
    #data for comparing current value with value for previous period 
    now = ten_days.iloc[0,1]
    yesterday = ten_days.iloc[1,1]
    mean_10_days = np.mean(ten_days['msg'])
    std_10_days = np.std(ten_days['msg'])
    time = ten_days['hm'].iloc[0]
    
    #comparison
    if abs(int(now) - int(yesterday)) > (3 * std_10_days):
        alert = True
    else:
        alert = False    

    #sending message and graph in case of alert
    if alert:
        if yesterday < now:  
            pct_dev = f'which is {((now-yesterday)/yesterday)*100:0.2f}% higher compared to yesterday value for the same period'         
        else:
            pct_dev = f'which is {((yesterday-now)/yesterday)*100:0.2f}% lower compared to yesterday value for the same period'  

        message = f'Number of sent messages in last 15 minutes: {now}, {pct_dev}\nRealtime dashboard: http://superset.lab.karpov.courses/r/686'
        bot.sendMessage(chat_id=chat_id, text=message)

        fig,axes = plt.subplots(2,1, figsize=(15,12))
        plt.suptitle('Number of sent messages', fontsize=20)
        sns.lineplot(data=ten_days, x='date', y='msg', ax=axes[0], marker='o')
        axes[0].title.set_text(f'Number of sent messages in the same 15 minutes period ({time}) for last 10 days')

        sns.lineplot(data=active_users, x='Time', y='msg', ax=axes[1])
        axes[1].title.set_text(f'Number of sent messages since yesterday 00:00')   
        
        mplot = io.BytesIO()
        plt.savefig(mplot)
        mplot.name = 'mplot.png'
        mplot.seek(0)
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=mplot)
        
        
check_feed_users()
check_messenger_users()
check_views_number()
check_likes_number()
check_ctr()
check_sent_messages()