import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def load_data():
    return pd.read_csv('Data/olympics_dataset.csv', encoding='utf-8')

def apply_filters(df, selected_years, selected_sports, selected_countries, selected_athletes):
    if selected_years:
        df = df[df['Year'].isin(selected_years)]
    if selected_sports:
        df = df[df['Sport'].isin(selected_sports)]
    if selected_countries:
        df = df[df['Team'].isin(selected_countries)]
    if selected_athletes:
        df = df[df['Name'].isin(selected_athletes)]
    return df

def plot_medals_by_country(filtered_df):
    medals_by_country = (
        filtered_df[filtered_df['Medal'] != 'No medal']
        .drop_duplicates(subset=['Team', 'Sport', 'Event', 'Medal'])
        .groupby('Team')['Medal']
        .count()
        .sort_values(ascending=False)
        .head(10)
        .astype(int)
    )
    fig1 = go.Figure([go.Bar(x=medals_by_country.index, y=medals_by_country.values, text=medals_by_country.values, textposition='auto', marker_color='#003F88')])
    fig1.update_layout(
        yaxis_title='Total Medals',
        xaxis_title='Country',
        title='Medal Distribution by Country'
    )
    st.plotly_chart(fig1)

def plot_athletes_by_sport(filtered_df):
    athletes_by_sport = filtered_df['Sport'].value_counts().head(10).astype(int)
    fig2 = go.Figure([go.Bar(x=athletes_by_sport.index, y=athletes_by_sport.values, text=athletes_by_sport.values, textposition='auto', marker_color='#003F88')])
    fig2.update_layout(
        yaxis_title='Number of Athletes',
        xaxis_title='Sport',
        title='Athletes Distribution by Sport',
    )
    st.plotly_chart(fig2)

def plot_medals_over_time(filtered_df):
    medals_by_year = (
        filtered_df[filtered_df['Medal'] != 'No medal']
        .drop_duplicates(subset=['Year', 'Sport', 'Event', 'Medal'])
        .groupby('Year')['Medal']
        .count()
        .astype(int)
    )
    fig4 = go.Figure([go.Scatter(x=medals_by_year.index, y=medals_by_year.values, mode='lines+markers', text=medals_by_year.values, textposition='top center', line=dict(color='#003F88'))])
    fig4.update_layout(
        xaxis=dict(
            type='category',
            tickangle=45,
            tickvals=[medals_by_year.index[i] for i in range(0, len(medals_by_year), max(1, len(medals_by_year) // 10))],
            ticktext=[str(medals_by_year.index[i]) for i in range(0, len(medals_by_year), max(1, len(medals_by_year) // 10))],
        ),
        yaxis_title='Total Medals',
        xaxis_title='Year',
        title='Medals Over Time',
        font=dict(color='#03045E')
    )
    st.plotly_chart(fig4)

def plot_gender_distribution(filtered_df):
    gender_distribution = filtered_df['Sex'].value_counts().reset_index()
    gender_distribution.columns = ['Gender', 'Count']
    col1, col2 = st.columns(2)
    for index, row in gender_distribution.iterrows():
        with col1 if index == 0 else col2:
            st.metric(label=row['Gender'], value=row['Count'], delta=None)

def plot_medal_distribution(filtered_df):
    required_columns = ['Team', 'Medal', 'Event']
    
    if not all(column in filtered_df.columns for column in required_columns):
        st.error(f"Missing required columns: {', '.join([col for col in required_columns if col not in filtered_df.columns])}")
        return
    
    unique_medals = filtered_df[filtered_df['Medal'] != 'No medal'].drop_duplicates(subset=['Team', 'Event', 'Medal'])
    
    medal_counts = unique_medals.groupby('Medal').size().reset_index(name='Count')
    medal_counts = medal_counts.set_index('Medal').reindex(['Gold', 'Silver', 'Bronze']).fillna(0).reset_index()
    
    medal_emojis = {
        'Gold': '🥇',
        'Silver': '🥈',
        'Bronze': '🥉'
    }
    
    st.subheader("Total Medal Distribution")
    col1, col2, col3 = st.columns(3)
    
    for index, row in medal_counts.iterrows():
        emoji = medal_emojis.get(row['Medal'], '')
        if index == 0:
            with col1:
                st.metric(label=f"{emoji} {row['Medal']}", value=int(row['Count']))
        elif index == 1:
            with col2:
                st.metric(label=f"{emoji} {row['Medal']}", value=int(row['Count']))
        else:
            with col3:
                st.metric(label=f"{emoji} {row['Medal']}", value=int(row['Count']))

def show_athletes_medals(filtered_df):
    st.title("Athletes and Medals")
    
    if not filtered_df.empty:        
        medal_counts = (
            filtered_df[filtered_df['Medal'] != 'No medal']
            .groupby(['Name', 'NOC', 'Team','Sport'])['Medal']
            .value_counts()
            .unstack(fill_value=0)
            .reset_index()
        )
        
        medal_counts['Gold'] = medal_counts.get('Gold', 0)
        medal_counts['Silver'] = medal_counts.get('Silver', 0)
        medal_counts['Bronze'] = medal_counts.get('Bronze', 0)
        
        medal_counts = medal_counts.sort_values(by=['Gold', 'Silver', 'Bronze'], ascending=False)
        
        st.dataframe(medal_counts[['Name', 'NOC', 'Team', 'Sport' ,'Gold', 'Silver', 'Bronze']].reset_index(drop=True))

        medal_counts = filtered_df['Medal'].value_counts().reset_index()
        medal_counts.columns = ['Medal Type', 'Count']
        medal_counts = medal_counts.set_index('Medal Type').reindex(['Gold', 'Silver', 'Bronze']).reset_index()
        

def generate_insights(df):
    st.sidebar.title("Filters")
    
    selected_years = st.sidebar.multiselect(
        'Year', 
        sorted(df['Year'].unique())
    )
    
    selected_sports = st.sidebar.multiselect(
        'Sport', 
        sorted(df['Sport'].unique())
    )
    
    selected_countries = st.sidebar.multiselect(
        'Country', 
        sorted(df['Team'].unique())
    )
    
    selected_athletes = st.sidebar.multiselect(
        'Athlete Name', 
        sorted(df['Name'].unique())
    )
    
    filtered_df = apply_filters(df, selected_years, selected_sports, selected_countries, selected_athletes)
    
    filtered_df.loc[:, 'Sex'] = filtered_df['Sex'].replace({'M': 'Male', 'F': 'Female'})
    
    st.title("Olympic Games Data Analysis")

    page = st.selectbox("Select Page", ["Overview", "Athletes and Medals"])

    if page == "Overview":
        plot_medals_by_country(filtered_df)
        plot_athletes_by_sport(filtered_df)
        plot_medals_over_time(filtered_df)
        plot_gender_distribution(filtered_df)
        plot_medal_distribution(filtered_df)
    
    elif page == "Athletes and Medals":
        show_athletes_medals(filtered_df)

if __name__ == "__main__":
    
    st.title('Interactive Olympic Games Analysis')
    st.write("This dashboard allows you to explore historical data from the Olympic Games from 1896 to 2024.")
    st.write("This dataset encompasses a comprehensive record of Summer Olympic Games from the inaugural 1896 Athens Olympics to the most recent 2024 Paris Olympics. It provides a rich source of information about athletes, their performances, and the medals awarded over a span of more than a century.")
    st.write("The medal counts are based on the medals received by each athlete from the country")
    
    df = load_data()
    generate_insights(df)
