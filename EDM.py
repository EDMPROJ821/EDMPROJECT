import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import numpy as np
from datetime import datetime

class GDPAnalysisDashboard:
    def __init__(self, excel_file='cleaned_data.xlsx'):
        """
        Initialize the GDP Analysis Dashboard
        Reads data from Excel file and prepares it for analysis
        """
        self.df = pd.read_excel(excel_file)
        self.prepare_data()
        
    def prepare_data(self):
        """
        Clean and prepare data for analysis
        """
        # Convert Year columns to numeric if they're not already
        self.df['Start_Year'] = pd.to_numeric(self.df['Start_Year'], errors='coerce')
        self.df['End_Year'] = pd.to_numeric(self.df['End_Year'], errors='coerce')
        self.df['Value'] = pd.to_numeric(self.df['Value'], errors='coerce')
        
        # Remove rows with missing critical data
        self.df = self.df.dropna(subset=['Value', 'Start_Year'])
        
        print(f"Data loaded successfully: {len(self.df)} records")
        print(f"Regions: {self.df['Region'].unique()}")
        print(f"Industries: {self.df['Industry'].unique()}")
        
    # ==================== BY REGION TAB - 8 CHARTS ====================
    
    def region_chart_1_top_thriving_industries(self):
        """
        Region Chart 1: Top Thriving Industries in Each Region
        Shows the leading industries by GDP value in each region
        """
        latest_year = self.df['Start_Year'].max()
        latest_data = self.df[self.df['Start_Year'] == latest_year]
        
        # Get top 3 industries per region by GDP value
        top_industries = latest_data.groupby('Region').apply(
            lambda x: x.nlargest(3, 'Value')
        ).reset_index(drop=True)
        
        fig = px.bar(
            top_industries,
            x='Region',
            y='Value',
            color='Industry',
            title='Top Thriving Industries by Region (Latest Year)',
            labels={'Value': 'GDP Value (Billions)', 'Region': 'Region'},
            barmode='group'
        )
        
        fig.update_layout(xaxis_tickangle=-45, height=600, showlegend=True)
        return fig
    
    def region_chart_2_gdp_contribution_pie(self):
        """
        Region Chart 2: GDP Contribution per Region (Pie Chart)
        Shows each region's contribution to total national GDP
        """
        latest_year = self.df['Start_Year'].max()
        regional_gdp = self.df[self.df['Start_Year'] == latest_year].groupby('Region')['Value'].sum().reset_index()
        
        fig = px.pie(
            regional_gdp,
            values='Value',
            names='Region',
            title=f'Regional GDP Contribution ({latest_year})',
            hole=0.3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=600)
        return fig
    
    def region_chart_3_gdp_contribution_stacked_bar(self):
        """
        Region Chart 3: GDP Contribution per Region (Stacked Bar Chart)
        Alternative visualization showing regional GDP contribution over time
        """
        yearly_regional_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        
        fig = px.bar(
            yearly_regional_gdp,
            x='Start_Year',
            y='Value',
            color='Region',
            title='Regional GDP Contribution Over Time (Stacked Bar)',
            labels={'Value': 'GDP Value (Billions)', 'Start_Year': 'Year'},
            barmode='stack'
        )
        
        fig.update_layout(height=600)
        return fig
    
    def region_chart_4_total_gdp_by_year(self):
        """
        Region Chart 4: Total GDP of each region per year (2018-2023)
        Shows individual regional GDP values across all years
        """
        yearly_regional_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        
        fig = px.bar(
            yearly_regional_gdp,
            x='Start_Year',
            y='Value',
            color='Region',
            title='Total GDP by Region per Year (2018-2023)',
            labels={'Value': 'GDP Value (Billions)', 'Start_Year': 'Year'},
            barmode='group',
            facet_col='Region',
            facet_col_wrap=3
        )
        
        fig.update_layout(height=800)
        return fig
    
    def region_chart_5_gdp_trends_line(self):
        """
        Region Chart 5: Region-wise GDP Trends (Line Chart)
        Shows GDP evolution trends for each region over time
        """
        yearly_regional_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        
        fig = px.line(
            yearly_regional_gdp,
            x='Start_Year',
            y='Value',
            color='Region',
            title='Regional GDP Trends Over Time',
            labels={'Value': 'GDP Value (Billions)', 'Start_Year': 'Year'},
            markers=True
        )
        
        fig.update_layout(height=600)
        return fig
    
    def region_chart_6_regional_gdp_growth_over_time(self):
        """
        Region Chart 6: Regional GDP Growth Over Time
        Shows year-over-year growth rates for each region
        """
        yearly_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        yearly_gdp = yearly_gdp.sort_values(['Region', 'Start_Year'])
        yearly_gdp['Growth_Rate'] = yearly_gdp.groupby('Region')['Value'].pct_change() * 100
        
        growth_data = yearly_gdp.dropna()
        
        fig = px.line(
            growth_data,
            x='Start_Year',
            y='Growth_Rate',
            color='Region',
            title='Regional GDP Growth Rate Over Time',
            labels={'Growth_Rate': 'Growth Rate (%)', 'Start_Year': 'Year'},
            markers=True
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_layout(height=600)
        return fig
    
    def region_chart_7_growth_rate_choropleth_map(self):
        """
        Region Chart 7: Growth Rate Map (2023 vs 2018) - Choropleth
        Shows regional growth rates on a map visualization
        """
        # Calculate growth rates between 2018 and 2023
        gdp_2018 = self.df[self.df['Start_Year'] == 2018].groupby('Region')['Value'].sum()
        gdp_2023 = self.df[self.df['Start_Year'] == 2023].groupby('Region')['Value'].sum()
        
        growth_data = pd.DataFrame({
            'Region': gdp_2018.index,
            'GDP_2018': gdp_2018.values,
            'GDP_2023': gdp_2023.reindex(gdp_2018.index).values
        })
        
        growth_data['Growth_Rate'] = ((growth_data['GDP_2023'] - growth_data['GDP_2018']) / growth_data['GDP_2018'] * 100)
        growth_data = growth_data.dropna()
        
        # Create a choropleth-style visualization using bar chart with color mapping
        fig = px.bar(
            growth_data,
            x='Region',
            y='Growth_Rate',
            color='Growth_Rate',
            title='Regional GDP Growth Rate Map (2023 vs 2018)',
            labels={'Growth_Rate': 'Growth Rate (%)', 'Region': 'Region'},
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0
        )
        
        fig.update_layout(xaxis_tickangle=-45, height=600)
        return fig
    
    def region_chart_8_province_contribution_bar(self):
        """
        Region Chart 8: Bar chart of provinces within each region
        Shows provincial GDP contributions within their respective regions
        """
        # Filter for province-level data
        province_data = self.df[self.df['Location_Type'].str.contains('Province|City', case=False, na=False)]
        latest_year = province_data['Start_Year'].max()
        
        province_latest = province_data[province_data['Start_Year'] == latest_year]
        province_contribution = province_latest.groupby(['Region', 'Location_Name'])['Value'].sum().reset_index()
        
        fig = px.bar(
            province_contribution,
            x='Location_Name',
            y='Value',
            color='Region',
            title=f'Provincial GDP Contribution by Region ({latest_year})',
            labels={'Value': 'GDP Value (Billions)', 'Location_Name': 'Province/City'},
            facet_col='Region',
            facet_col_wrap=2
        )
        
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(height=1000)
        return fig
    
    # ==================== BY INDUSTRY TAB - 7 CHARTS ====================
    
    def industry_chart_1_top_10_regions_by_industry(self):
        """
        Industry Chart 1: Top 10 Regions by GDP in different industries
        Shows the leading regions for each major industry sector
        """
        latest_year = self.df['Start_Year'].max()
        industry_data = self.df[self.df['Start_Year'] == latest_year]
        
        # Get top 10 regions for each industry
        top_regions = industry_data.groupby('Industry').apply(
            lambda x: x.nlargest(10, 'Value')
        ).reset_index(drop=True)
        
        fig = px.bar(
            top_regions,
            x='Value',
            y='Region',
            color='Industry',
            title='Top 10 Regions by Industry GDP',
            labels={'Value': 'GDP Value (Billions)', 'Region': 'Region'},
            facet_col='Industry',
            facet_col_wrap=2,
            orientation='h'
        )
        
        fig.update_layout(height=1200)
        return fig
    
    def industry_chart_2_lowest_10_regions_by_industry(self):
        """
        Industry Chart 2: Lowest 10 Regions in different industries
        Shows regions with the smallest GDP contribution in each industry
        """
        latest_year = self.df['Start_Year'].max()
        industry_data = self.df[self.df['Start_Year'] == latest_year]
        
        # Get bottom 10 regions for each industry
        bottom_regions = industry_data.groupby('Industry').apply(
            lambda x: x.nsmallest(10, 'Value')
        ).reset_index(drop=True)
        
        fig = px.bar(
            bottom_regions,
            x='Value',
            y='Region',
            color='Industry',
            title='Lowest 10 Regions by Industry GDP',
            labels={'Value': 'GDP Value (Billions)', 'Region': 'Region'},
            facet_col='Industry',
            facet_col_wrap=2,
            orientation='h'
        )
        
        fig.update_layout(height=1200)
        return fig
    
    def industry_chart_3_national_gdp_composition(self):
        """
        Industry Chart 3: National GDP Composition by Industry
        Shows the overall industry breakdown of national GDP
        """
        latest_year = self.df['Start_Year'].max()
        industry_composition = self.df[self.df['Start_Year'] == latest_year].groupby('Industry')['Value'].sum().reset_index()
        
        fig = px.pie(
            industry_composition,
            values='Value',
            names='Industry',
            title=f'National GDP Composition by Industry ({latest_year})',
            hole=0.4
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=600)
        return fig
    
    def industry_chart_4_industry_breakdown_stacked_bar(self):
        """
        Industry Chart 4: Stacked bar chart for industry breakdown 2018-2023
        Shows how industry composition changed over time
        """
        yearly_industry_gdp = self.df.groupby(['Industry', 'Start_Year'])['Value'].sum().reset_index()
        
        fig = px.bar(
            yearly_industry_gdp,
            x='Start_Year',
            y='Value',
            color='Industry',
            title='Industry GDP Breakdown Over Time (2018-2023)',
            labels={'Value': 'GDP Value (Billions)', 'Start_Year': 'Year'},
            barmode='stack'
        )
        
        fig.update_layout(height=600)
        return fig
    
    def industry_chart_5_industry_breakdown_donut(self):
        """
        Industry Chart 5: Donut chart for industry breakdown 2018-2023
        Alternative visualization of industry composition over time
        """
        # Create subplots for each year
        years = sorted(self.df['Start_Year'].unique())
        
        fig = make_subplots(
            rows=2, cols=3,
            specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}],
                   [{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]],
            subplot_titles=[f'Year {year}' for year in years]
        )
        
        colors = px.colors.qualitative.Set3
        
        for i, year in enumerate(years):
            row = i // 3 + 1
            col = i % 3 + 1
            
            year_data = self.df[self.df['Start_Year'] == year].groupby('Industry')['Value'].sum()
            
            fig.add_trace(
                go.Pie(
                    labels=year_data.index,
                    values=year_data.values,
                    hole=0.4,
                    marker_colors=colors[:len(year_data)]
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title_text="Industry GDP Composition by Year (Donut Charts)",
            height=800
        )
        
        return fig
    
    def industry_chart_6_gdp_trend_by_industry_line(self):
        """
        Industry Chart 6: GDP Trend by Industry (Line Chart)
        Shows how each industry's GDP evolved over the years
        """
        yearly_industry_gdp = self.df.groupby(['Industry', 'Start_Year'])['Value'].sum().reset_index()
        
        fig = px.line(
            yearly_industry_gdp,
            x='Start_Year',
            y='Value',
            color='Industry',
            title='GDP Trends by Industry Over Time',
            labels={'Value': 'GDP Value (Billions)', 'Start_Year': 'Year'},
            markers=True
        )
        
        fig.update_layout(height=600)
        return fig
    
    def industry_chart_7_regions_vs_industries_heatmap(self):
        """
        Industry Chart 7: Regions vs Industries Heatmap
        Shows GDP values across regions and industries with heatmap intensity
        """
        latest_year = self.df['Start_Year'].max()
        heatmap_data = self.df[self.df['Start_Year'] == latest_year].pivot_table(
            values='Value', 
            index='Region', 
            columns='Industry', 
            aggfunc='sum'
        ).fillna(0)
        
        fig = px.imshow(
            heatmap_data,
            title=f'GDP Heatmap: Regions vs Industries ({latest_year})',
            labels=dict(x="Industry", y="Region", color="GDP Value (Billions)"),
            aspect="auto",
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=800)
        return fig
    
    # ==================== GROWTH TAB - 5 CHARTS ====================
    
    def growth_chart_1_two_year_growth_comparison_table(self):
        """
        Growth Chart 1: 2 Year Growth Comparison Table (2018-2019, 2019-2020, etc.)
        Shows year-over-year growth rates in a table format
        """
        # Calculate year-over-year growth rates
        yearly_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        yearly_gdp = yearly_gdp.sort_values(['Region', 'Start_Year'])
        yearly_gdp['Growth_Rate'] = yearly_gdp.groupby('Region')['Value'].pct_change() * 100
        
        # Create year pairs for comparison
        yearly_gdp['Year_Pair'] = yearly_gdp['Start_Year'].astype(str) + '-' + (yearly_gdp['Start_Year'] + 1).astype(str)
        
        # Remove first year (no growth rate available)
        growth_data = yearly_gdp.dropna()
        
        # Create pivot table for heatmap
        growth_pivot = growth_data.pivot(index='Region', columns='Year_Pair', values='Growth_Rate')
        
        fig = px.imshow(
            growth_pivot,
            title='Year-over-Year Growth Rates by Region (%)',
            labels=dict(x="Year Comparison", y="Region", color="Growth Rate (%)"),
            aspect="auto",
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0
        )
        
        fig.update_layout(height=600)
        return fig
    
    def growth_chart_2_growth_rate_over_time_line(self):
        """
        Growth Chart 2: Growth Rate Over Time by Region (Line Chart with % values)
        Shows growth rate trends for each region over time
        """
        yearly_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        yearly_gdp = yearly_gdp.sort_values(['Region', 'Start_Year'])
        yearly_gdp['Growth_Rate'] = yearly_gdp.groupby('Region')['Value'].pct_change() * 100
        
        growth_data = yearly_gdp.dropna()
        
        fig = px.line(
            growth_data,
            x='Start_Year',
            y='Growth_Rate',
            color='Region',
            title='Growth Rate Trends by Region (%)',
            labels={'Growth_Rate': 'Growth Rate (%)', 'Start_Year': 'Year'},
            markers=True
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Zero Growth")
        fig.update_layout(height=600)
        return fig
    
    def growth_chart_3_fastest_growing_vs_shrinking_regions(self):
        """
        Growth Chart 3: Fastest-Growing vs Shrinking Regions (Bar Chart Comparison)
        Compares average growth rates across regions
        """
        # Calculate average growth rate for each region
        yearly_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        yearly_gdp = yearly_gdp.sort_values(['Region', 'Start_Year'])
        yearly_gdp['Growth_Rate'] = yearly_gdp.groupby('Region')['Value'].pct_change() * 100
        
        avg_growth = yearly_gdp.groupby('Region')['Growth_Rate'].mean().reset_index()
        avg_growth = avg_growth.sort_values('Growth_Rate', ascending=True)
        
        # Color code positive vs negative growth
        colors = ['red' if x < 0 else 'green' for x in avg_growth['Growth_Rate']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=avg_growth['Growth_Rate'],
                y=avg_growth['Region'],
                orientation='h',
                marker_color=colors,
                text=[f"{x:.1f}%" for x in avg_growth['Growth_Rate']],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title='Average Growth Rate by Region: Fastest Growing vs Shrinking',
            xaxis_title='Average Growth Rate (%)',
            yaxis_title='Region',
            height=600
        )
        
        fig.add_vline(x=0, line_dash="dash", line_color="black")
        return fig
    
    def growth_chart_4_industry_growth_leaders(self):
        """
        Growth Chart 4: Industry Growth Leaders - Which industries grew fastest per region
        Shows the fastest-growing industry in each region
        """
        # Calculate growth rates by industry and region
        industry_yearly = self.df.groupby(['Region', 'Industry', 'Start_Year'])['Value'].sum().reset_index()
        industry_yearly = industry_yearly.sort_values(['Region', 'Industry', 'Start_Year'])
        industry_yearly['Growth_Rate'] = industry_yearly.groupby(['Region', 'Industry'])['Value'].pct_change() * 100
        
        # Get average growth rate by region and industry
        avg_industry_growth = industry_yearly.groupby(['Region', 'Industry'])['Growth_Rate'].mean().reset_index()
        
        # Get top growing industry per region
        top_industries = avg_industry_growth.loc[avg_industry_growth.groupby('Region')['Growth_Rate'].idxmax()]
        
        fig = px.bar(
            top_industries,
            x='Region',
            y='Growth_Rate',
            color='Industry',
            title='Fastest Growing Industry by Region',
            labels={'Growth_Rate': 'Average Growth Rate (%)', 'Region': 'Region'},
            text='Growth_Rate'
        )
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=600)
        return fig
    
    def growth_chart_5_growth_volatility_analysis(self):
        """
        Growth Chart 5: Growth Volatility Analysis
        Shows the consistency/volatility of growth rates across regions
        """
        # Calculate growth rate standard deviation for each region
        yearly_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        yearly_gdp = yearly_gdp.sort_values(['Region', 'Start_Year'])
        yearly_gdp['Growth_Rate'] = yearly_gdp.groupby('Region')['Value'].pct_change() * 100
        
        growth_stats = yearly_gdp.groupby('Region')['Growth_Rate'].agg(['mean', 'std']).reset_index()
        growth_stats.columns = ['Region', 'Avg_Growth', 'Growth_Volatility']
        growth_stats = growth_stats.dropna()
        
        fig = px.scatter(
            growth_stats,
            x='Avg_Growth',
            y='Growth_Volatility',
            size='Growth_Volatility',
            color='Avg_Growth',
            hover_name='Region',
            title='Growth Rate vs Volatility by Region',
            labels={
                'Avg_Growth': 'Average Growth Rate (%)',
                'Growth_Volatility': 'Growth Volatility (Standard Deviation)',
                'Region': 'Region'
            },
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(height=600)
        return fig
    
    # ==================== PERCENT SHARE TAB - 3 CHARTS ====================
    
    def share_chart_1_province_gdp_share_within_region(self):
        """
        Share Chart 1: Province GDP Share Within Region (2018-2023)
        Shows how provinces contribute to their regional GDP over time
        """
        # Filter for province-level data
        province_data = self.df[self.df['Location_Type'].str.contains('Province|City', case=False, na=False)]
        
        # Calculate regional totals
        regional_totals = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        regional_totals.rename(columns={'Value': 'Regional_Total'}, inplace=True)
        
        # Merge with province data
        province_share = province_data.merge(regional_totals, on=['Region', 'Start_Year'])
        province_share['Share_Percent'] = (province_share['Value'] / province_share['Regional_Total']) * 100
        
        fig = px.bar(
            province_share,
            x='Start_Year',
            y='Share_Percent',
            color='Location_Name',
            facet_col='Region',
            facet_col_wrap=2,
            title='Province GDP Share Within Region (2018-2023)',
            labels={'Share_Percent': 'Share (%)', 'Start_Year': 'Year'},
            barmode='stack'
        )
        
        fig.update_layout(height=800)
        return fig
    
    def share_chart_2_change_in_percent_share_over_time(self):
        """
        Share Chart 2: Change in Percent Share Over Time
        Shows how provincial shares evolved within their regions
        """
        # Calculate shares as in previous function
        province_data = self.df[self.df['Location_Type'].str.contains('Province|City', case=False, na=False)]
        regional_totals = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        regional_totals.rename(columns={'Value': 'Regional_Total'}, inplace=True)
        
        province_share = province_data.merge(regional_totals, on=['Region', 'Start_Year'])
        province_share['Share_Percent'] = (province_share['Value'] / province_share['Regional_Total']) * 100
        
        fig = px.line(
            province_share,
            x='Start_Year',
            y='Share_Percent',
            color='Location_Name',
            facet_col='Region',
            facet_col_wrap=2,
            title='Change in Province Share Over Time',
            labels={'Share_Percent': 'Share (%)', 'Start_Year': 'Year'},
            markers=True
        )
        
        fig.update_layout(height=800)
        return fig
    
    def share_chart_3_province_vs_regional_growth_gap(self):
        """
        Share Chart 3: Province vs Regional Growth Gap
        Compares provincial growth rates with their regional averages
        """
        # Calculate provincial growth rates
        province_data = self.df[self.df['Location_Type'].str.contains('Province|City', case=False, na=False)]
        province_yearly = province_data.groupby(['Region', 'Location_Name', 'Start_Year'])['Value'].sum().reset_index()
        province_yearly = province_yearly.sort_values(['Region', 'Location_Name', 'Start_Year'])
        province_yearly['Province_Growth'] = province_yearly.groupby(['Region', 'Location_Name'])['Value'].pct_change() * 100
        
        # Calculate regional growth rates
        regional_yearly = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        regional_yearly = regional_yearly.sort_values(['Region', 'Start_Year'])
        regional_yearly['Regional_Growth'] = regional_yearly.groupby('Region')['Value'].pct_change() * 100
        
        # Merge data
        growth_comparison = province_yearly.merge(
            regional_yearly[['Region', 'Start_Year', 'Regional_Growth']], 
            on=['Region', 'Start_Year']
        )
        
        growth_comparison['Growth_Gap'] = growth_comparison['Province_Growth'] - growth_comparison['Regional_Growth']
        growth_comparison = growth_comparison.dropna()
        
        fig = px.scatter(
            growth_comparison,
            x='Regional_Growth',
            y='Province_Growth',
            color='Region',
            size=abs(growth_comparison['Growth_Gap']),
            hover_data=['Location_Name', 'Start_Year', 'Growth_Gap'],
            title='Province vs Regional Growth Comparison',
            labels={
                'Regional_Growth': 'Regional Growth Rate (%)', 
                'Province_Growth': 'Provincial Growth Rate (%)'
            }
        )
        
        # Add diagonal line for equal growth
        fig.add_shape(
            type="line",
            x0=-10, y0=-10, x1=20, y1=20,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        fig.update_layout(height=600)
        return fig
    
    # ==================== MAIN EXECUTION FUNCTION ====================
    
    def generate_all_charts(self):
        """
        Generate all charts and save them as HTML files
        Creates a comprehensive dashboard with all visualizations
        """
        charts = {
            # By Region Tab - 8 Charts
            'region_1_top_thriving_industries': self.region_chart_1_top_thriving_industries(),
            'region_2_gdp_contribution_pie': self.region_chart_2_gdp_contribution_pie(),
            'region_3_gdp_contribution_stacked': self.region_chart_3_gdp_contribution_stacked_bar(),
            'region_4_total_gdp_by_year': self.region_chart_4_total_gdp_by_year(),
            'region_5_gdp_trends_line': self.region_chart_5_gdp_trends_line(),
            'region_6_gdp_growth_over_time': self.region_chart_6_regional_gdp_growth_over_time(),
            'region_7_growth_rate_choropleth': self.region_chart_7_growth_rate_choropleth_map(),
            'region_8_province_contribution_bar': self.region_chart_8_province_contribution_bar(),
            
            # By Industry Tab - 7 Charts
            'industry_1_top_10_regions': self.industry_chart_1_top_10_regions_by_industry(),
            'industry_2_lowest_10_regions': self.industry_chart_2_lowest_10_regions_by_industry(),
            'industry_3_national_composition': self.industry_chart_3_national_gdp_composition(),
            'industry_4_breakdown_stacked_bar': self.industry_chart_4_industry_breakdown_stacked_bar(),
            'industry_5_breakdown_donut': self.industry_chart_5_industry_breakdown_donut(),
            'industry_6_trend_line': self.industry_chart_6_gdp_trend_by_industry_line(),
            'industry_7_regions_vs_industries_heatmap': self.industry_chart_7_regions_vs_industries_heatmap(),
            
            # Growth Tab - 5 Charts
            'growth_1_two_year_comparison': self.growth_chart_1_two_year_growth_comparison_table(),
            'growth_2_growth_rate_over_time': self.growth_chart_2_growth_rate_over_time_line(),
            'growth_3_fastest_vs_shrinking': self.growth_chart_3_fastest_growing_vs_shrinking_regions(),
            'growth_4_industry_growth_leaders': self.growth_chart_4_industry_growth_leaders(),
            'growth_5_growth_volatility': self.growth_chart_5_growth_volatility_analysis(),
            
            # Percent Share Tab - 3 Charts
            'share_1_province_share_timeline': self.share_chart_1_province_gdp_share_within_region(),
            'share_2_share_change_over_time': self.share_chart_2_change_in_percent_share_over_time(),
            'share_3_growth_gap_analysis': self.share_chart_3_province_vs_regional_growth_gap()
        }
        
        # Save each chart as HTML
        for chart_name, fig in charts.items():
            filename = f"{chart_name}.html"
            fig.write_html(filename)
            print(f"Saved: {filename}")
        
        # Create a combined dashboard HTML file
        self.create_combined_dashboard(charts)
        
        return charts
    
    def create_combined_dashboard(self, charts):
        """
        Create a single HTML file with all charts organized by tabs
        """
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GDP Analysis Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
                .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; }
                .tab button:hover { background-color: #ddd; }
                .tab button.active { background-color: #ccc; }
                .tabcontent { display: none; padding: 12px; border: 1px solid #ccc; border-top: none; }
                .chart-container { margin: 20px 0; }
                .tab-summary { background-color: #f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>GDP Analysis Dashboard</h1>
            
            <div class="tab">
                <button class="tablinks active" onclick="openTab(event, 'RegionTab')">By Region (8 Charts)</button>
                <button class="tablinks" onclick="openTab(event, 'IndustryTab')">By Industry (7 Charts)</button>
                <button class="tablinks" onclick="openTab(event, 'GrowthTab')">Growth Analysis (5 Charts)</button>
                <button class="tablinks" onclick="openTab(event, 'ShareTab')">Percent Share (3 Charts)</button>
            </div>
        """
        
        # Add tab contents with chart placeholders
        tab_contents = {
            'RegionTab': {
                'charts': [
                    'region_1_top_thriving_industries', 'region_2_gdp_contribution_pie', 
                    'region_3_gdp_contribution_stacked', 'region_4_total_gdp_by_year',
                    'region_5_gdp_trends_line', 'region_6_gdp_growth_over_time',
                    'region_7_growth_rate_choropleth', 'region_8_province_contribution_bar'
                ],
                'description': 'Regional analysis showing GDP distribution, trends, and provincial contributions across different regions.'
            },
            'IndustryTab': {
                'charts': [
                    'industry_1_top_10_regions', 'industry_2_lowest_10_regions',
                    'industry_3_national_composition', 'industry_4_breakdown_stacked_bar',
                    'industry_5_breakdown_donut', 'industry_6_trend_line',
                    'industry_7_regions_vs_industries_heatmap'
                ],
                'description': 'Industry-focused analysis showing sectoral performance, regional leaders, and composition changes over time.'
            },
            'GrowthTab': {
                'charts': [
                    'growth_1_two_year_comparison', 'growth_2_growth_rate_over_time',
                    'growth_3_fastest_vs_shrinking', 'growth_4_industry_growth_leaders',
                    'growth_5_growth_volatility'
                ],
                'description': 'Growth rate analysis focusing on year-over-year changes, regional performance, and industry leaders.'
            },
            'ShareTab': {
                'charts': [
                    'share_1_province_share_timeline', 'share_2_share_change_over_time',
                    'share_3_growth_gap_analysis'
                ],
                'description': 'Provincial share analysis showing how provinces contribute to regional GDP and growth patterns.'
            }
        }
        
        for tab_id, tab_info in tab_contents.items():
            html_content += f'<div id="{tab_id}" class="tabcontent"'
            if tab_id == 'RegionTab':
                html_content += ' style="display:block"'
            html_content += '>\n'
            
            # Add tab description
            html_content += f'<div class="tab-summary"><p>{tab_info["description"]}</p></div>\n'
            
            for chart_name in tab_info['charts']:
                if chart_name in charts:
                    chart_html = charts[chart_name].to_html(include_plotlyjs=False, div_id=f"div_{chart_name}")
                    html_content += f'<div class="chart-container">{chart_html}</div>\n'
            
            html_content += '</div>\n'
        
        # Add JavaScript for tabs and Plotly
        html_content += """
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script>
                function openTab(evt, tabName) {
                    var i, tabcontent, tablinks;
                    tabcontent = document.getElementsByClassName("tabcontent");
                    for (i = 0; i < tabcontent.length; i++) {
                        tabcontent[i].style.display = "none";
                    }
                    tablinks = document.getElementsByClassName("tablinks");
                    for (i = 0; i < tablinks.length; i++) {
                        tablinks[i].className = tablinks[i].className.replace(" active", "");
                    }
                    document.getElementById(tabName).style.display = "block";
                    evt.currentTarget.className += " active";
                }
            </script>
        </body>
        </html>
        """
        
        with open('gdp_dashboard.html', 'w') as f:
            f.write(html_content)
        
        print("Combined dashboard saved as: gdp_dashboard.html")

# ==================== EXECUTION ====================

if __name__ == "__main__":
    # Initialize the dashboard
    dashboard = GDPAnalysisDashboard('cleaned_data.xlsx')
    
    # Generate all charts
    print("Generating GDP Analysis Dashboard...")
    charts = dashboard.generate_all_charts()
    
    print(f"\nDashboard generation complete!")
    print(f"Generated {len(charts)} charts:")
    print("- By Region Tab: 8 charts")
    print("- By Industry Tab: 7 charts") 
    print("- Growth Analysis Tab: 5 charts")
    print("- Percent Share Tab: 3 charts")
    print("\nAll charts are HTML-compatible and ready for web deployment.")
