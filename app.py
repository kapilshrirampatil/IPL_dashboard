import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df=pd.read_csv(r'E:\new_project\IPL_dashboard\IPL_Ball_by_Ball_2008_2022.csv')
matches=pd.read_csv(r'E:\new_project\IPL_dashboard\IPL_Matches_2008_2022.csv')
matches['Team1Players']=matches['Team1Players'].str.strip("['").str.strip("']").str.replace("'",'').str.split(', ')
matches['Team2Players']=matches['Team2Players'].str.strip("['").str.strip("']").str.replace("'",'').str.split(', ')
matches['player']=matches[['Team1Players','Team2Players']].apply(lambda x:x['Team1Players']+x['Team2Players'],axis=1)
merge_df=df.merge(matches,how='inner',left_on='ID',right_on='ID')

def venue(city):
    return matches[matches['City']==city]['Venue'].unique()
def venue_stats(city,venue):
    match_played=matches[(matches['City']==city) & (matches['Venue']==venue)].shape[0]
    batting_first=matches[(matches['City']==city) & (matches['Venue']==venue) &
                          ((matches['TossWinner']==matches['WinningTeam']) &(matches['TossDecision']=='bat')|
                           ((matches['TossWinner']!=matches['WinningTeam']) &(matches['TossDecision']=='field')))].shape[0]
    batting_second=matches[(matches['City']==city) & (matches['Venue']==venue) &
                          ((matches['TossWinner']!=matches['WinningTeam']) &(matches['TossDecision']=='bat')|
                           ((matches['TossWinner']==matches['WinningTeam']) &(matches['TossDecision']=='field')))].shape[0]
    ds=pd.Series({'Total Match Played':match_played,'Bat First':batting_first,'Field First':batting_second})
    df=pd.DataFrame(ds)
    st.dataframe(df.T)
def graph(city,venue):
    match_played=matches[(matches['City']==city) & (matches['Venue']==venue)].shape[0]
    batting_first=matches[(matches['City']==city) & (matches['Venue']==venue) &
                          ((matches['TossWinner']==matches['WinningTeam']) &(matches['TossDecision']=='bat')|
                           ((matches['TossWinner']!=matches['WinningTeam']) &(matches['TossDecision']=='field')))].shape[0]
    batting_second=matches[(matches['City']==city) & (matches['Venue']==venue) &
                          ((matches['TossWinner']!=matches['WinningTeam']) &(matches['TossDecision']=='bat')|
                           ((matches['TossWinner']==matches['WinningTeam']) &(matches['TossDecision']=='field')))].shape[0]
    ds=pd.Series({'Bat First':batting_first,'Field First':batting_second})
    fig,ax=plt.subplots(figsize=(2,2))
    ax.pie(ds,labels=['Bat','Field'],autopct='%0.1f%%')
    ax.set_title(venue_1)
    ax.axis('equal')
    st.pyplot(fig)
def avg_first_inning_score(city,venue):
    temp_df=merge_df[(merge_df['City']==city) & (merge_df['Venue']==venue) & (merge_df['innings']==1)]
    avg_score=temp_df.groupby('ID')['total_run'].sum().reset_index()['total_run'].mean()
    st.markdown(round(avg_score))
def successfull_chase(city,venue):
    temp_df=merge_df[(merge_df['City']==city) & (merge_df['Venue']==venue) & (merge_df['innings']==2) & 
                    ((merge_df['TossWinner']==merge_df['WinningTeam']) & (merge_df['TossDecision']=='field') |
                     (merge_df['TossWinner']!=merge_df['WinningTeam']) & (merge_df['TossDecision']=='bat'))]
    chase=temp_df.groupby(['ID'])['total_run'].sum().reset_index()['total_run'].max()
    st.markdown(chase)

def player_with_most_runs(city,venue):
    temp_df=merge_df[(merge_df['City']==city) & (merge_df['Venue']==venue)].groupby('batter')['batsman_run'].sum().reset_index().sort_values(by='batsman_run',ascending=False)
    df=temp_df.set_index('batter').head(5)
    st.dataframe(df)

def player_with_most_wickets(city,venue):
    temp_df=merge_df[(merge_df['City']==city) & (merge_df['Venue']==venue) &
                     ~(merge_df['kind'].isin(['run out','not out','retired hurt','retired out','obstructing the field']))].groupby('bowler')['isWicketDelivery'].count().reset_index()
    temp_df=temp_df.rename(columns={'isWicketDelivery':'Total Wickets'}).set_index('bowler').sort_values(by='Total Wickets',ascending=False).head()
    st.dataframe(temp_df)

def number_of_six_per_match(city,venue):
    a=merge_df[(merge_df['City']==city)
                    & (merge_df['Venue']==venue)
                    &(merge_df['non_boundary']==0)
                    & (merge_df['batsman_run']==6)].groupby('ID')['batsman_run'].count().reset_index()['batsman_run'].mean()
    st.markdown(round(a))


def team_stat(team):
    matches_played=matches[(matches['Team1']==team) | (matches['Team2']==team)].shape[0]
    win=matches[((matches['Team1']==team) | (matches['Team2']==team)) & (matches['WinningTeam']==team)].shape[0]
    loss=matches[((matches['Team1']==team) | (matches['Team2']==team)) & (matches['WinningTeam']!=team) & ~(matches['WinningTeam']=='No Result')].shape[0]
    tie=matches_played-win-loss
    ds=pd.Series({'Match Played':matches_played,'Win':win,'Loss':loss,'No Result':tie})
    df=pd.DataFrame(ds)
    df=df.T.set_index('Match Played')
    st.dataframe(df)
    ds_1=pd.Series({'Win':win,'Loss':loss,'No Result':tie})
    fig,ax=plt.subplots(figsize=(2,2))
    ax.pie(ds_1,autopct='%0.1f%%',labels=['Win','Loss','Tie'])
    ax.set_title(f'Team Record {team}')
    st.pyplot(fig)
def most_runs_and_wickets(team):
    temp_df=merge_df[(merge_df['Team1']==team) | (merge_df['Team2']==team)].groupby('batter')['batsman_run'].sum().reset_index().sort_values(by='batsman_run',ascending=False).set_index('batter').head()
    st.markdown(f'Top 5 Batsman of {team_1}')
    st.dataframe(temp_df)
    temp_df_1=merge_df[((merge_df['Team1']==team) | (merge_df['Team2']==team)) & (merge_df['isWicketDelivery']==1)].groupby('bowler')['isWicketDelivery'].sum().reset_index().sort_values(by='isWicketDelivery',ascending=False).set_index('bowler').rename(columns={'isWicketDelivery':'Total Wickets'}).head()
    st.markdown(f'Top 5 Bowler of {team_1}')
    st.dataframe(temp_df_1)


def player_list(player):
    l=[]
    for i in matches[player]:
        l=l+i
    return list(set(l))
def player_stats(player):
    if player not in merge_df['batter'].unique():
        st.markdown(f"{player} didn't bat")
    else:
        merge_df['player_in']=merge_df['player'].apply(lambda x: 1 if player in x else 0)
        merge_df['islegalball']=merge_df['extra_type'].apply(lambda x:1 if x in ['legal ball','legbyes','byes','penalty'] else 0)
        match_played=merge_df[merge_df['player_in']==1]['ID'].nunique()
        innings_df=merge_df[merge_df['player_in']==1].groupby(['ID','batter'])['innings'].count().reset_index()
        innings=innings_df[innings_df['batter']==player].shape[0]
        runs=merge_df[merge_df['player_in']==1].groupby('batter').get_group(player)['batsman_run'].sum()
        best=merge_df[(merge_df['player_in']==1) & (merge_df['batter']==player)].groupby('ID')['batsman_run'].sum().reset_index()['batsman_run'].max()
        out=merge_df[(merge_df['player_in']==1) & (merge_df['isWicketDelivery']==1) & (merge_df['player_out']==player)].shape[0]
        not_out=innings-out
        average=round(runs/out,2)
        ball_faced=merge_df[(merge_df['islegalball']==1) & (merge_df['batter']==player)].shape[0]
        strike_rate=round(runs/ball_faced*100,2)
        score=merge_df[merge_df['batter']==player].groupby(['ID'])['batsman_run'].sum().reset_index()
        hundreds=score[score['batsman_run']>99].shape[0]
        fifty=score[score['batsman_run'].between(50,98,inclusive = True)].shape[0]
        ds=pd.Series({'Match Played':match_played,'Innings':innings,'Run Scored':runs,'Best':best,
                        "Not Out's":not_out,'Average':average,'Ball Played':ball_faced,'Strike Rate':strike_rate,'Hundreds':hundreds,
                        'Fifties':fifty})
        df=pd.DataFrame(ds,columns=['values'])
        st.dataframe(df)

def player_stats_bowling(player):
    if player not in merge_df['bowler'].unique():
        st.markdown(f"{player} didn't bowled")
    else:
        merge_df['player_in']=merge_df['player'].apply(lambda x: 1 if player in x else 0)
        merge_df['islegalball']=merge_df['extra_type'].apply(lambda x:1 if x in ['legal ball','legbyes','byes','penalty'] else 0)
        match_played=merge_df[merge_df['player_in']==1]['ID'].nunique()
        innings_df=merge_df[merge_df['player_in']==1].groupby(['ID','bowler'])['innings'].count().reset_index()
        innings=innings_df[innings_df['bowler']==player].shape[0]
        run_1=merge_df[merge_df['player_in']==1].groupby('bowler').get_group(player)['total_run'].sum()
        b=merge_df[(merge_df['extra_type'].isin(['byes','penelty','legbyes']))&(merge_df['bowler']==player)]['extras_run'].sum()
        runs=run_1-b
        best_df=merge_df[(merge_df['bowler']==player) &(merge_df['kind']!='run out')].groupby('ID').agg({'total_run':'sum','isWicketDelivery':'sum'}).sort_values(by=['isWicketDelivery','total_run'],ascending=[False,True])
        best_df_1=best_df.astype(str)
        best_df_1['BBF']=best_df_1.apply(lambda x:x['isWicketDelivery']+'/'+x['total_run'],axis=1)
        bbf=best_df_1['BBF'].values[0]
        wickets=merge_df[(merge_df['bowler']==player) & (merge_df['isWicketDelivery']==1) &(merge_df['kind']!='run out')].shape[0]
        average=round(runs/wickets,2)
        ball_bowled=merge_df[(merge_df['islegalball']==1) & (merge_df['bowler']==player)].shape[0]
        strike_rate=round(ball_bowled/wickets,2)
        five_wicket_hall=best_df[best_df['isWicketDelivery']>=5].shape[0]
        ds=pd.Series({'Match Played':match_played,'Innings':innings,'Run':runs,'Wickets':wickets,'Best Bowling fig':bbf,
                        'Average':average,'Ball Bowled':ball_bowled,'Strike Rate':strike_rate,'5WH':five_wicket_hall})
        df=pd.DataFrame(ds,columns=['values'])
        st.dataframe(df)

st.sidebar.title('IPL Analysis')
option=st.sidebar.selectbox('select one',['Venue','Team','Player'])
if option=='Venue':
    st.title('Venue Record')
    city_1=st.sidebar.selectbox('Select City',matches['City'].unique())
    venue_1=st.sidebar.selectbox('Select Venue',venue(city_1))
    btn_1=st.sidebar.button('Venue Stats')
    if btn_1:
        st.subheader(venue_1)
        venue_stats(city_1,venue_1)
        graph(city_1,venue_1)
        st.write('Average 1st inning Score')
        avg_first_inning_score(city_1,venue_1)
        st.write('Successfull Run chase')
        successfull_chase(city_1,venue_1)
        st.write('Top 5 batsman with most runs')
        player_with_most_runs(city_1,venue_1)
        st.write('Top 5  with bowlers most Wickets')
        player_with_most_wickets(city_1,venue_1)
        st.write('Average number of sixes per match')
        number_of_six_per_match(city_1,venue_1)
elif option=='Team':
    st.title('Team Records')
    team_1=st.sidebar.selectbox('Select Team',matches['Team1'].unique())
    btn_2=st.sidebar.button('Team stat')
    if btn_2:
        st.markdown(team_1)
        team_stat(team_1)
        most_runs_and_wickets(team_1)

else:
    st.title('Player Record')
    player_1=st.sidebar.selectbox('select player',player_list('player'))
    btn_3=st.sidebar.button('Show Stats')
    if btn_3:
        st.markdown(f'{player_1} batting stats')
        player_stats(player_1)
        st.markdown(f'{player_1} bowling stats')
        player_stats_bowling(player_1)
