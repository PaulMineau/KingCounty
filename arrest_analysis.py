import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import column, row, gridplot
from sklearn.ensemble import IsolationForest
from datetime import date

df = pd.read_csv('D:\\data\\Adult_Jail_Booking_April_1__2018_to_March_31__2019_as_of_April_6__2019.tsv', sep='\t', header=0)

bd = 'Booking Date'
bdt = 'Booking Date Time'
rdt = 'Release Date Time'
rdtnull = 'Release Date Time Null'
htd = 'Hold Time Days'
ht = 'Hold Time'
format = '%m/%d/%Y %H:%M:%S %p'
df[bdt] = pd.to_datetime(df[bdt], format=format)
df[rdt] = pd.to_datetime(df[rdt], format=format)
df[ht] = df[rdt] - df[bdt]
df[htd] = df[ht].dt.days
df[rdtnull] = df[rdt].isnull()
df_original = df
print("num release date null is ")
print(df[rdt].isnull().sum())
#print("hold time times")
#print(df[htd])
df[bd] = df[bdt].dt.date #strftime('%Y-%m-%d')
grouped = df.groupby([bd, 'Court'])
aggs = df.groupby([bd]).agg(['count'])
aggsCharge = df.groupby(['Charge']).size()
aggsCharge2 = df.groupby(['Charge']).size().reset_index(name='counts')

df = df.fillna(0)
df.sort_index(inplace=True)

# Hold times King County - Anomalies
source = ColumnDataSource(df)
holdTimesKingCountyAnomaliesChart = figure(x_axis_type="datetime", title="Arrest Hold Times King County", plot_width=800, plot_height=350)
holdTimesKingCountyAnomaliesChart.line(bdt, htd, source=source, legend="Hold Times")
holdTimesKingCountyAnomaliesChart.legend.location = "top_left"
holdTimesKingCountyAnomaliesChart.legend.click_policy="hide"

'''
iforest = IsolationForest(n_estimators=300, contamination=0.10)
holdTimeDaysOnly = df[[htd]]

iforest = iforest.fit(holdTimeDaysOnly)

pred_isoF = iforest.predict(holdTimeDaysOnly)
#print(pred_isoF)

isoF_outliers = df[iforest.predict(holdTimeDaysOnly) == -1]
#print(isoF_outliers)

holdTimesKingCountyAnomaliesChart.square(isoF_outliers[bdt], isoF_outliers[htd], size=3, color='red', alpha=0.5)
'''

def genChargeCountsCharts(top10Crimes, title):
  this_series = top10Crimes['counts'][::-1]
  f = figure(width=800, height=600, y_range=top10Crimes['Charge'][::-1], title=title)

  f.background_fill_color = "#EAEAF2"

  f.grid.grid_line_alpha = 1.0
  f.grid.grid_line_color = "white"

  f.xaxis.axis_label = 'Arrests'
  f.xaxis.axis_label_text_font_size = '14pt'
  f.xaxis.major_label_text_font_size = '14pt'
  # p.x_range = Range1d(0,50)
  # p.xaxis[0].ticker=FixedTicker(ticks=[i for i in xrange(0,5,1)])

  f.yaxis.major_label_text_font_size = '14pt'
  f.yaxis.axis_label = 'Charge'

  f.yaxis.axis_label_text_font_size = '14pt'

  j = 0.5
  for v in this_series:
    f.rect(x=v / 2, y=j, width=abs(v), height=0.4, color=(76, 114, 176),
           width_units="data", height_units="data")
    j += 1
  return f

def genHoldTimes(title, df):
  source2 = ColumnDataSource(df)

  f = figure(x_axis_type="datetime", title=title, plot_width=800, plot_height=350)
  f.line(bdt, htd, source=source2, legend="Hold Times")
  f.legend.location = "top_left"
  f.legend.click_policy="hide"
  return f

def genArrestsByDay(title, df):
  source2 = ColumnDataSource(df)

  f = figure(x_axis_type="datetime", title=title, plot_width=800, plot_height=350)
  f.line(bd, 'counts', source=source2, legend="Arrests By Day")
  f.legend.location = "top_left"
  f.legend.click_policy="hide"
  return f

#Top 10 Crimes King County
top10Crimes = aggsCharge2.sort_values(by='counts', ascending=False).head(10)
top10CrimesChart = genChargeCountsCharts(top10Crimes, "Top 10 Crimes King County")

#Hold Times KC - Released Only
df_released = df_original.dropna(subset=[rdt], how='all')
releasedHoldTimesKCChart = genHoldTimes("Hold Times King County - Released Only", df_released)

#DUI Hold Times KC
df_dui = df_released.loc[df_released['Charge']=='DUI']
duiHoldTimesKCChart = genHoldTimes("DUI Hold Times King County - Released Only", df_dui)

#Arrests by day King County
aggs = df_released.groupby([bd]).size().reset_index(name='counts')
arrestsByDayKCChart = genArrestsByDay("Arrests By Day King County", aggs)

#Redmond Courthouse Hold times
df_redmond = df_released.loc[df_released['Court']=='KCDC East Division Redmond Courthouse']
holdTimesRedmondChart = genHoldTimes("Redmond Courthouse Hold Times", df_redmond)

#TOP 10 CRIMES Redmond
aggsCharge2Redmond = df_redmond.groupby(['Charge']).size().reset_index(name='counts')
top10CrimesRedmond = aggsCharge2Redmond.sort_values(by='counts', ascending=False).head(10)
topTenCrimesRedmondChart = genChargeCountsCharts(top10CrimesRedmond, "Top 10 Crimes Redmond")

#TOP 10 CRIMES Seattle
df_seattle = df_released.loc[df_released['Court']=='Seattle Municipal Court']
aggsChargeSeattle = df_seattle.groupby(['Charge']).size().reset_index(name='counts')
top10CrimesSeattle = aggsChargeSeattle.sort_values(by='counts', ascending=False).head(10)
topTenCrimesSeattleChart = genChargeCountsCharts(top10CrimesSeattle, "Top 10 Crimes Seattle")

#KCDC West Division Seattle Courthouse
df_west_seattle = df_released.loc[df_released['Court']=='KCDC West Division Seattle Courthouse']
aggsChargeWestSeattle = df_west_seattle.groupby(['Charge']).size().reset_index(name='counts')
top10CrimesWestSeattle = aggsChargeWestSeattle.sort_values(by='counts', ascending=False).head(10)
topTenCrimesWestSeattleChart = genChargeCountsCharts(top10CrimesWestSeattle, "Top 10 Crimes West Seattle")

#K C Superior Court
df_kc_superior = df_released.loc[df_released['Court']=='K C Superior Court']
aggsChargeKCSuperior = df_kc_superior.groupby(['Charge']).size().reset_index(name='counts')
top10CrimesKCSuperior = aggsChargeKCSuperior.sort_values(by='counts', ascending=False).head(10)
topTenCrimesKCSuperiorChart = genChargeCountsCharts(top10CrimesKCSuperior, "Top 10 Crimes KC Superior Court")

#Arrests by day Redmond
arrests_by_day_redmond = df_redmond.groupby([bd]).size().reset_index(name='counts')
arrestsByDayRedmondChart = genArrestsByDay("Arrests By Day Redmond", arrests_by_day_redmond)

#Arrests by day KC Superior
arrests_by_day_kc_superior = df_kc_superior.groupby([bd]).size().reset_index(name='counts')
arrestsByDayKCSuperiorChart = genArrestsByDay("Arrests By Day King County Superior", arrests_by_day_kc_superior)

#Arrests by day Seattle
arrests_by_day_seattle = df_seattle.groupby([bd]).size().reset_index(name='counts')
arrestsByDaySeattleChart = genArrestsByDay("Arrests By Day Seattle", arrests_by_day_seattle)

arrests_by_day_seattle[bd] = pd.to_datetime(arrests_by_day_seattle[bd])
print(arrests_by_day_seattle.groupby(arrests_by_day_seattle[bd].dt.strftime('%B'))['counts'].sum()) #.sort_values())

#Output Html
output_file("arrest_analysis.html")
grid = gridplot([[holdTimesKingCountyAnomaliesChart, top10CrimesChart], [releasedHoldTimesKCChart, duiHoldTimesKCChart], [arrestsByDayKCChart, holdTimesRedmondChart],
                 [topTenCrimesRedmondChart, topTenCrimesSeattleChart], [topTenCrimesWestSeattleChart, topTenCrimesKCSuperiorChart], [arrestsByDayRedmondChart, arrestsByDayKCSuperiorChart],
                 [arrestsByDaySeattleChart, None]])
show(grid)


#Arrests by Month (Does not work
aggs['Booking Date'] = pd.to_datetime(aggs['Booking Date'], errors='coerce')
#print(aggs)
GB=aggs.groupby([(aggs['Booking Date'].dt.year),(aggs['Booking Date'].dt.month)]).sum()

#print(GB)
source5 = ColumnDataSource(GB)

p6 = figure(x_axis_type="datetime", title="Arrests By Month", plot_width=800, plot_height=350)
p6.line('Booking Date', 'counts', source=source5, legend="Number arrests")
p6.legend.location = "top_left"
p6.legend.click_policy="hide"