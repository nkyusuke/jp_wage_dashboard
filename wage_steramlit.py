import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk 
import plotly.express as px

st.title("日本の賃金データダッシュボード")

df_jp_ind=pd.read_csv("./csv_data/雇用_医療福祉_一人当たり賃金_全国_全産業.csv",encoding="shift_jis")
df_jp_category=pd.read_csv("./csv_data/雇用_医療福祉_一人当たり賃金_全国_大分類.csv",encoding="shift_jis")
df_pref_ind=pd.read_csv("./csv_data/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv",encoding="shift_jis")

st.header("■2019年:一人当たり平均賃金のヒートマップ")
jp_lat_lon=pd.read_csv("./pref_lat_lon.csv")
jp_lat_lon=jp_lat_lon.rename(columns={"pref_name":"都道府県名"})
df_pref_map=df_pref_ind[(df_pref_ind["年齢"]=="年齢計")&(df_pref_ind["集計年"]==2019)]
df_pref_map=pd.merge(df_pref_map,jp_lat_lon,on="都道府県名") 
#onは無くても自動的に共通する項目をキーとするが、分かりやすさのために明示することを推奨
df_pref_map["一人当たり賃金（相対値）"]=((df_pref_map["一人当たり賃金（万円）"]-df_pref_map["一人当たり賃金（万円）"].min())/(df_pref_map["一人当たり賃金（万円）"].max()-df_pref_map["一人当たり賃金（万円）"].min())) 
#正規化処理をしている
#丸括弧は全角で入力しないとpydeckのlayer設定でエラーが発生してしまう
view=pdk.ViewState(
    longitude=139.691648, #東京を中心とする
    latitude=35.689185,
    zoom=4,
    pitch=40.5
) 
layer=pdk.Layer(
    "HeatmapLayer",
    data=df_pref_map,
    opacity=0.4, #不透明度
    get_position=["lon","lat"],
    threshold=0.3, #閾値
    get_weight="一人当たり賃金（相対値）" #複数の列がある場合にどの列をヒートマップにするか
)
layer_map=pdk.Deck(
    layers=layer,
    initial_view_state=view
)
st.pydeck_chart(layer_map)
show_df=st.checkbox("Show DataFrame")
if show_df==True:
    st.write(df_pref_map)


st.header("■集計年別の一人当たり賃金（万円）の推移")
df_ts_mean=df_jp_ind[df_jp_ind["年齢"]=="年齢計"]
df_ts_mean=df_ts_mean.rename(columns={"一人当たり賃金（万円）":"全国_一人当たり賃金（万円）"})
df_pref_mean=df_pref_ind[df_pref_ind["年齢"]=="年齢計"]
pref_list=df_pref_mean["都道府県名"].unique()
option_pref=st.selectbox(
    "都道府県",
    (pref_list) #丸括弧で記載する
)
df_pref_mean=df_pref_mean[df_pref_mean["都道府県名"]==option_pref] #選択された都道府県のデータフレームに上書きされる
df_mean_line=pd.merge(df_ts_mean,df_pref_mean,on="集計年")
df_mean_line=df_mean_line[["集計年","全国_一人当たり賃金（万円）","一人当たり賃金（万円）"]] #列を絞る,list方を[]に入れる
df_mean_line=df_mean_line.set_index("集計年") #集計年をインデックスにする
st.line_chart(df_mean_line) #折れ線グラフで全国平均と都道府県平均を表示する


st.header("■年齢階級別の全国一人あたり平均賃金（万円）")
df_mean_bubble=df_jp_ind[df_jp_ind["年齢"]!="年齢計"] #年齢階級別なので年齢計は入らない
fig=px.scatter(df_mean_bubble, #散布図はバブルチャートを使う際はscatterを使う
               x="一人当たり賃金（万円）",
               y="年間賞与その他特別給与額（万円）",
               range_x=[150,700],
               range_y=[0,150],
               size="所定内給与額（万円）",
               size_max=38, #定めてなくても自動的に調整される
               color="年齢", #どの項目に色をつけるか
               animation_frame="集計年", #集計年毎の推移が確認できる
               animation_group="年齢"
               )
st.plotly_chart(fig)


st.header("■産業別の賃金推移")
year_list=df_jp_category["集計年"].unique()
option_year=st.selectbox(
    "集計年",
    (year_list) 
)
wage_list=["一人当たり賃金（万円）","所定内給与額（万円）","年間賞与その他特別給与額（万円）"]
option_wage=st.selectbox(
    "賃金の種類",
    (wage_list) 
)
df_mean_categ=df_jp_category[(df_jp_category["集計年"]==option_year)]
max_x=df_mean_categ[option_wage].max() + 50 #賃金の種類ごとに最大値が異なるため調整。上側に50のマージンを設ける。
fig=px.bar(df_mean_categ, #棒グラフを表示する時はbarを使う
               x=option_wage, #選択された賃金の種類
               y="産業大分類名",
               color="産業大分類名",
               animation_frame="年齢",
               range_x=[0,max_x],
               orientation="h", #横棒はh
               width=800, #指定しないとデフォルトの値が入る
               height=500,
               )
st.plotly_chart(fig)


st.text("出典：RESUS（地域経済分析システム）")
st.text("本結果はRESAS（地域経済分析システム）を加工して作成")




