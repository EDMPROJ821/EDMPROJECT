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
        
    # ==================== BY REGION TAB CHARTS ====================
    
    def top_thriving_industries_by_region(self):
        """
        Chart 1: Top Thriving Industries in Each Region
        Creates a grouped bar chart showing top industries per region
        """
        # Get latest year data for each region-industry combination
        latest_data = self.df.loc[self.df.groupby(['Region', 'Industry'])['Start_Year'].idxmax()]
        
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
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=600,
            showlegend=True
        )
        
        return fig
    
    def gdp_contribution_per_region(self):
        """
        Chart 2: GDP Contribution per Region (Pie Chart)
        Shows regional contribution to total national GDP
        """
        # Sum GDP by region for latest available year
        latest_year = self.df['Start_Year'].max()
        regional_gdp = self.df[self.df['Start_Year'] == latest_year].groupby('Region')['Value'].sum().reset_index()
        
        fig = px.pie(
            regional_gdp,
            values='Value',
            names='Region',
            title=f'Regional GDP Contribution ({latest_year})',
            hole=0.3  # Creates a donut chart
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=600)
        
        return fig
    
    def total_gdp_by_region_yearly(self):
        """
        Chart 3: Total GDP of each region per year (2018-2023)
        Stacked bar chart showing regional GDP over time
        """
        # Group by region and year, sum GDP values
        yearly_regional_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        
        fig = px.bar(
            yearly_regional_gdp,
            x='Start_Year',
            y='Value',
            color='Region',
            title='Total GDP by Region (2018-2023)',
            labels={'Value': 'GDP Value (Billions)', 'Start_Year': 'Year'},
            barmode='stack'
        )
        
        fig.update_layout(height=600)
        
        return fig
    
    def regional_gdp_trends(self):
        """
        Chart 4: Region-wise GDP Trends (Line Chart)
        Shows GDP growth trends for each region over time
        """
        # Group by region and year, sum GDP values
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
    
    def growth_rate_calculation(self):
        """
        Chart 5: Growth Rate Map (2023 vs 2018)
        Calculates and visualizes growth rates between 2018 and 2023
        """
        # Get 2018 and 2023 data
        gdp_2018 = self.df[self.df['Start_Year'] == 2018].groupby('Region')['Value'].sum()
        gdp_2023 = self.df[self.df['Start_Year'] == 2023].groupby('Region')['Value'].sum()
        
        # Calculate growth rate
        growth_data = pd.DataFrame({
            'Region': gdp_2018.index,
            'GDP_2018': gdp_2018.values,
            'GDP_2023': gdp_2023.reindex(gdp_2018.index).values
        })
        
        growth_data['Growth_Rate'] = ((growth_data['GDP_2023'] - growth_data['GDP_2018']) / growth_data['GDP_2018'] * 100)
        growth_data = growth_data.dropna()
        
        fig = px.bar(
            growth_data,
            x='Region',
            y='Growth_Rate',
            title='Regional GDP Growth Rate (2023 vs 2018)',
            labels={'Growth_Rate': 'Growth Rate (%)', 'Region': 'Region'},
            color='Growth_Rate',
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=600
        )
        
        return fig
    
    def province_contribution_to_regional_gdp(self):
        """
        Chart 6: Province Contribution to Regional GDP - WITH REGION DROPDOWN
        Bar chart showing provinces within each region
        """
        # Filter for province-level data
        province_data = self.df[self.df['Location_Type'].str.contains('Province|City', case=False, na=False)]
        latest_year = province_data['Start_Year'].max()
        
        province_latest = province_data[province_data['Start_Year'] == latest_year]
        province_contribution = province_latest.groupby(['Region', 'Location_Name'])['Value'].sum().reset_index()
        
        # Get unique regions
        regions = province_contribution['Region'].unique()
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each region (initially show first region)
        for i, region in enumerate(regions):
            region_data = province_contribution[province_contribution['Region'] == region]
            fig.add_trace(
                go.Bar(
                    x=region_data['Location_Name'],
                    y=region_data['Value'],
                    name=region,
                    visible=True if i == 0 else False
                )
            )
        
        # Create dropdown buttons
        buttons = []
        for i, region in enumerate(regions):
            visibility = [False] * len(regions)
            visibility[i] = True
            buttons.append(
                dict(
                    label=region,
                    method="update",
                    args=[{"visible": visibility},
                          {"title": f"Province Contribution to {region} GDP ({latest_year})"}]
                )
            )
        
        fig.update_layout(
            title=f"Province Contribution to {regions[0]} GDP ({latest_year})",
            xaxis_title="Province/City",
            yaxis_title="GDP Value (Billions)",
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                )
            ],
            height=600
        )
        
        return fig
    
    # ==================== BY INDUSTRY TAB CHARTS ====================
    
    def top_regions_by_industry(self):
        """
        Chart 7: Top 10 Regions by GDP in different industries - WITH INDUSTRY DROPDOWN
        Shows leading regions for each major industry
        """
        latest_year = self.df['Start_Year'].max()
        industry_data = self.df[self.df['Start_Year'] == latest_year]
        
        # Get unique industries
        industries = industry_data['Industry'].unique()
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each industry
        for i, industry in enumerate(industries):
            industry_top = industry_data[industry_data['Industry'] == industry].nlargest(10, 'Value')
            fig.add_trace(
                go.Bar(
                    x=industry_top['Value'],
                    y=industry_top['Region'],
                    orientation='h',
                    name=industry,
                    visible=True if i == 0 else False
                )
            )
        
        # Create dropdown buttons
        buttons = []
        for i, industry in enumerate(industries):
            visibility = [False] * len(industries)
            visibility[i] = True
            buttons.append(
                dict(
                    label=industry,
                    method="update",
                    args=[{"visible": visibility},
                          {"title": f"Top 10 Regions by {industry} GDP"}]
                )
            )
        
        fig.update_layout(
            title=f"Top 10 Regions by {industries[0]} GDP",
            xaxis_title="GDP Value (Billions)",
            yaxis_title="Region",
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                )
            ],
            height=600
        )
        
        return fig
    
    def lowest_regions_by_industry(self):
        """
        Chart 8: Lowest 10 Regions in different industries - WITH INDUSTRY DROPDOWN
        Shows regions with lowest GDP in each industry
        """
        latest_year = self.df['Start_Year'].max()
        industry_data = self.df[self.df['Start_Year'] == latest_year]
        
        # Get unique industries
        industries = industry_data['Industry'].unique()
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each industry
        for i, industry in enumerate(industries):
            industry_bottom = industry_data[industry_data['Industry'] == industry].nsmallest(10, 'Value')
            fig.add_trace(
                go.Bar(
                    x=industry_bottom['Value'],
                    y=industry_bottom['Region'],
                    orientation='h',
                    name=industry,
                    visible=True if i == 0 else False
                )
            )
        
        # Create dropdown buttons
        buttons = []
        for i, industry in enumerate(industries):
            visibility = [False] * len(industries)
            visibility[i] = True
            buttons.append(
                dict(
                    label=industry,
                    method="update",
                    args=[{"visible": visibility},
                          {"title": f"Lowest 10 Regions by {industry} GDP"}]
                )
            )
        
        fig.update_layout(
            title=f"Lowest 10 Regions by {industries[0]} GDP",
            xaxis_title="GDP Value (Billions)",
            yaxis_title="Region",
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                )
            ],
            height=600
        )
        
        return fig
    
    def national_gdp_composition_by_industry(self):
        """
        Chart 9: National GDP Composition by Industry - WITH YEAR DROPDOWN
        Stacked bar chart showing industry breakdown over time
        """
        yearly_industry_gdp = self.df.groupby(['Industry', 'Start_Year'])['Value'].sum().reset_index()
        
        # Get unique years
        years = sorted(yearly_industry_gdp['Start_Year'].unique())
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each year
        for i, year in enumerate(years):
            year_data = yearly_industry_gdp[yearly_industry_gdp['Start_Year'] == year]
            fig.add_trace(
                go.Bar(
                    x=year_data['Industry'],
                    y=year_data['Value'],
                    name=str(year),
                    visible=True if i == 0 else False
                )
            )
        
        # Create dropdown buttons
        buttons = []
        for i, year in enumerate(years):
            visibility = [False] * len(years)
            visibility[i] = True
            buttons.append(
                dict(
                    label=str(year),
                    method="update",
                    args=[{"visible": visibility},
                          {"title": f"National GDP Composition by Industry ({year})"}]
                )
            )
        
        fig.update_layout(
            title=f"National GDP Composition by Industry ({years[0]})",
            xaxis_title="Industry",
            yaxis_title="GDP Value (Billions)",
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                )
            ],
            height=600
        )
        
        return fig
    
    def gdp_trend_by_industry(self):
        """
        Chart 10: GDP Trend by Industry (Line Chart)
        Shows how each industry's GDP evolved over time
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
    
    def gdp_heatmap_regions_vs_industries(self):
        """
        Chart 11: Regions vs Industries GDP Heatmap
        Heatmap showing GDP values across regions and industries
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
            labels=dict(x="Industry", y="Region", color="GDP Value"),
            aspect="auto",
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=800)
        
        return fig
    
    # ==================== GROWTH TAB CHARTS ====================
    
    def two_year_growth_comparison(self):
        """
        Chart 12: 2-Year Growth Comparison Table
        Shows growth rates for consecutive years
        """
        # Calculate year-over-year growth rates
        yearly_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        yearly_gdp = yearly_gdp.sort_values(['Region', 'Start_Year'])
        
        # Calculate growth rates
        yearly_gdp['Growth_Rate'] = yearly_gdp.groupby('Region')['Value'].pct_change() * 100
        
        # Create pivot table for better visualization
        growth_pivot = yearly_gdp.pivot(index='Region', columns='Start_Year', values='Growth_Rate')
        
        fig = px.imshow(
            growth_pivot,
            title='Year-over-Year Growth Rates by Region (%)',
            labels=dict(x="Year", y="Region", color="Growth Rate (%)"),
            aspect="auto",
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0
        )
        
        fig.update_layout(height=600)
        
        return fig
    
    def growth_rate_over_time_by_region(self):
        """
        Chart 13: Growth Rate Over Time by Region (Line Chart)
        Shows growth rate trends for each region
        """
        yearly_gdp = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        yearly_gdp = yearly_gdp.sort_values(['Region', 'Start_Year'])
        yearly_gdp['Growth_Rate'] = yearly_gdp.groupby('Region')['Value'].pct_change() * 100
        
        # Remove first year (no growth rate available)
        growth_data = yearly_gdp.dropna()
        
        fig = px.line(
            growth_data,
            x='Start_Year',
            y='Growth_Rate',
            color='Region',
            title='Growth Rate Trends by Region',
            labels={'Growth_Rate': 'Growth Rate (%)', 'Start_Year': 'Year'},
            markers=True
        )
        
        fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Zero Growth")
        fig.update_layout(height=600)
        
        return fig
    
    def fastest_growing_vs_shrinking_regions(self):
        """
        Chart 14: Fastest-Growing vs Shrinking Regions
        Bar chart comparison of regional performance
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
                marker_color=colors
            )
        ])
        
        fig.update_layout(
            title='Average Growth Rate by Region (Fastest Growing vs Shrinking)',
            xaxis_title='Average Growth Rate (%)',
            yaxis_title='Region',
            height=600
        )
        
        fig.add_vline(x=0, line_dash="dash", line_color="black")
        
        return fig
    
    def industry_growth_leaders(self):
        """
        Chart 15: Industry Growth Leaders
        Shows which industries grew fastest in each region
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
            labels={'Growth_Rate': 'Average Growth Rate (%)', 'Region': 'Region'}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=600
        )
        
        return fig
    
    # ==================== PERCENT SHARE TAB CHARTS ====================
    
    def province_gdp_share_within_region(self):
        """
        Chart 16: Province GDP Share Within Region - WITH REGION DROPDOWN
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
        
        # Get unique regions
        regions = province_share['Region'].unique()
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each region
        for i, region in enumerate(regions):
            region_data = province_share[province_share['Region'] == region]
            provinces = region_data['Location_Name'].unique()
            
            for j, province in enumerate(provinces):
                province_data_filtered = region_data[region_data['Location_Name'] == province]
                fig.add_trace(
                    go.Bar(
                        x=province_data_filtered['Start_Year'],
                        y=province_data_filtered['Share_Percent'],
                        name=province,
                        visible=True if i == 0 else False
                    )
                )
        
        # Create dropdown buttons
        buttons = []
        trace_count = 0
        for i, region in enumerate(regions):
            region_data = province_share[province_share['Region'] == region]
            provinces_in_region = len(region_data['Location_Name'].unique())
            
            visibility = [False] * len(fig.data)
            for j in range(trace_count, trace_count + provinces_in_region):
                visibility[j] = True
            
            buttons.append(
                dict(
                    label=region,
                    method="update",
                    args=[{"visible": visibility},
                          {"title": f"Province GDP Share Within {region} (2018-2023)"}]
                )
            )
            
            trace_count += provinces_in_region
        
        fig.update_layout(
            title=f"Province GDP Share Within {regions[0]} (2018-2023)",
            xaxis_title="Year",
            yaxis_title="Share (%)",
            barmode='stack',
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                )
            ],
            height=600
        )
        
        return fig
    
    def change_in_percent_share_over_time(self):
        """
        Chart 17: Change in Percent Share Over Time - WITH REGION DROPDOWN
        Shows how provincial shares changed over the years
        """
        # Calculate shares as in previous function
        province_data = self.df[self.df['Location_Type'].str.contains('Province|City', case=False, na=False)]
        regional_totals = self.df.groupby(['Region', 'Start_Year'])['Value'].sum().reset_index()
        regional_totals.rename(columns={'Value': 'Regional_Total'}, inplace=True)
        
        province_share = province_data.merge(regional_totals, on=['Region', 'Start_Year'])
        province_share['Share_Percent'] = (province_share['Value'] / province_share['Regional_Total']) * 100
        
        # Get unique regions
        regions = province_share['Region'].unique()
        
        # Create figure
        fig = go.Figure()
        
        # Add traces for each region
        trace_count = 0
        for i, region in enumerate(regions):
            region_data = province_share[province_share['Region'] == region]
            provinces = region_data['Location_Name'].unique()
            
            for j, province in enumerate(provinces):
                province_data_filtered = region_data[region_data['Location_Name'] == province]
                fig.add_trace(
                    go.Scatter(
                        x=province_data_filtered['Start_Year'],
                        y=province_data_filtered['Share_Percent'],
                        mode='lines+markers',
                        name=province,
                        visible=True if i == 0 else False
                    )
                )
        
        # Create dropdown buttons
        buttons = []
        trace_count = 0
        for i, region in enumerate(regions):
            region_data = province_share[province_share['Region'] == region]
            provinces_in_region = len(region_data['Location_Name'].unique())
            
            visibility = [False] * len(fig.data)
            for j in range(trace_count, trace_count + provinces_in_region):
                visibility[j] = True
            
            buttons.append(
                dict(
                    label=region,
                    method="update",
                    args=[{"visible": visibility},
                          {"title": f"Change in Province Share Over Time - {region}"}]
                )
            )
            
            trace_count += provinces_in_region
        
        fig.update_layout(
            title=f"Change in Province Share Over Time - {regions[0]}",
            xaxis_title="Year",
            yaxis_title="Share (%)",
            updatemenus=[
                dict(
                    buttons=buttons,
                    direction="down",
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                )
            ],
            height=600
        )
        
        return fig
    
    def province_vs_regional_growth_gap(self):
        """
        Chart 18: Province vs Regional Growth Gap
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
            size='Growth_Gap',
            hover_data=['Location_Name', 'Start_Year'],
            title='Province vs Regional Growth Comparison',
            labels={'Regional_Growth': 'Regional Growth Rate (%)', 'Province_Growth': 'Provincial Growth Rate (%)'}
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
            # By Region Tab
            'region_top_industries': self.top_thriving_industries_by_region(),
            'region_gdp_contribution': self.gdp_contribution_per_region(),
            'region_yearly_gdp': self.total_gdp_by_region_yearly(),
            'region_gdp_trends': self.regional_gdp_trends(),
            'region_growth_rate': self.growth_rate_calculation(),
            'province_contribution': self.province_contribution_to_regional_gdp(),
            
            # By Industry Tab
            'industry_top_regions': self.top_regions_by_industry(),
            'industry_lowest_regions': self.lowest_regions_by_industry(),
            'national_industry_composition': self.national_gdp_composition_by_industry(),
            'industry_trends': self.gdp_trend_by_industry(),
            'regions_industries_heatmap': self.gdp_heatmap_regions_vs_industries(),
            
            # Growth Tab
            'two_year_growth': self.two_year_growth_comparison(),
            'growth_trends': self.growth_rate_over_time_by_region(),
            'fastest_growing_regions': self.fastest_growing_vs_shrinking_regions(),
            'industry_growth_leaders': self.industry_growth_leaders(),
            
            # Percent Share Tab
            'province_share_timeline': self.province_gdp_share_within_region(),
            'share_change_over_time': self.change_in_percent_share_over_time(),
            'growth_gap_analysis': self.province_vs_regional_growth_gap()
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
            </style>
        </head>
        <body>
            <h1>GDP Analysis Dashboard - Enhanced with Interactive Dropdowns</h1>
            
            <div class="tab">
                <button class="tablinks active" onclick="openTab(event, 'RegionTab')">By Region</button>
                <button class="tablinks" onclick="openTab(event, 'IndustryTab')">By Industry</button>
                <button class="tablinks" onclick="openTab(event, 'GrowthTab')">Growth Analysis</button>
                <button class="tablinks" onclick="openTab(event, 'ShareTab')">Percent Share</button>
            </div>
        """
        
        # Add tab contents with chart placeholders
        tab_contents = {
            'RegionTab': ['region_top_industries', 'region_gdp_contribution', 'region_yearly_gdp', 'region_gdp_trends', 'region_growth_rate', 'province_contribution'],
            'IndustryTab': ['industry_top_regions', 'industry_lowest_regions', 'national_industry_composition', 'industry_trends', 'regions_industries_heatmap'],
            'GrowthTab': ['two_year_growth', 'growth_trends', 'fastest_growing_regions', 'industry_growth_leaders'],
            'ShareTab': ['province_share_timeline', 'share_change_over_time', 'growth_gap_analysis']
        }
        
        for tab_id, chart_list in tab_contents.items():
            html_content += f'<div id="{tab_id}" class="tabcontent"'
            if tab_id == 'RegionTab':
                html_content += ' style="display:block"'
            html_content += '>\n'
            
            for chart_name in chart_list:
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
        
        with open('gdp_dashboard_enhanced.html', 'w') as f:
            f.write(html_content)
        
        print("Enhanced dashboard with dropdowns saved as: gdp_dashboard_enhanced.html")

if __name__ == "__main__":
    # Initialize the dashboard
    dashboard = GDPAnalysisDashboard('cleaned_data.xlsx')
    
    # Generate all charts
    print("Generating Enhanced GDP Analysis Dashboard with Interactive Dropdowns...")
    charts = dashboard.generate_all_charts()
    
    print(f"\nDashboard generation complete!")
    print(f"Generated {len(charts)} charts across 4 main categories:")
    print("- By Region: 6 charts")
    print("- By Industry: 5 charts") 
    print("- Growth Analysis: 4 charts")
    print("- Percent Share: 3 charts")
    print("\nEnhanced Features Added:")
    print("✓ Top 10 highest regions by industry GDP - Industry dropdown")
    print("✓ Top 10 lowest regions by industry GDP - Industry dropdown") 
    print("✓ National GDP composition - Year dropdown")
    print("✓ Provincial GDP contribution - Region dropdown")
    print("✓ Province GDP share - Region dropdown")
    print("✓ Share change over time - Region dropdown")
    print("\nAll charts are HTML-compatible and ready for web deployment.")
