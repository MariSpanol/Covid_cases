import pandas as pd
import streamlit as st
import numpy as np
from IPython.core.display import display, HTML
from ast import literal_eval
from urllib.request import urlopen
import json
import plotly.graph_objects as go
import plotly
from plotly.offline import iplot, init_notebook_mode
import plotly.offline as off
import plotly.express as px




st.set_page_config(page_icon="🧊",
    layout="wide")


vac_caract = pd.read_csv('vacine_table_uf.csv')
vac_caract = vac_caract[['uf', 'Estado']]

df = pd.read_csv('time_series.csv')
df = df[df.indicador != 'sum']
df.indicador = df.indicador.astype(int)
df = df.groupby(['UF', 'vacina_descricao_dose'])['indicador'].sum().reset_index()

df = df.merge(vac_caract,
how = 'inner',
right_on = 'uf',
left_on =  'UF')

df = df.pivot(values = 'indicador', index = ['UF', 'Estado'], columns = 'vacina_descricao_dose').reset_index()
df = df.fillna(0)

df = df.iloc[:,0:4]
df.columns = [ 'UF', 'Estado',  'primeira_dose', 'segunda_dose']
df['total_dose'] = df['primeira_dose'] + df['segunda_dose']
df = df[['UF',	'Estado', 'total_dose',	'primeira_dose',	'segunda_dose']]

populacao = pd.read_csv('populacao_UF.csv')
populacao.Estado = populacao.Estado.str.strip()
df = df.merge(populacao,
how = 'inner',
on = 'Estado' )
df['pct_populacao_vacinado_all'] = df['total_dose']/df['Populacao'] *100
df['pct_populacao_vacinado_pdose'] = df['primeira_dose']/df['Populacao'] *100
df['pct_populacao_vacinado_sdose'] = df['segunda_dose']/df['Populacao'] *100

df = df[['UF', 'Estado', 'total_dose',	'primeira_dose',	'segunda_dose',
         'pct_populacao_vacinado_all',	'pct_populacao_vacinado_pdose',	'pct_populacao_vacinado_sdose']]

with urlopen("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson") as response:
 Brazil = json.load(response) # Javascrip object notation

tx_ids=[Brazil['features'][k]['properties']['name'] for k in range(len(Brazil['features']))]
sources=[{"type": "FeatureCollection", 'features': [feat]} for feat in Brazil['features']]

df = df.set_index('Estado') #ESTADO
df = df.reindex(tx_ids)

rate_list = ['num_all_dose', 'num_prim_dose', 'num_seg_dose', 'pct_pop_all', 'pct_pdose', 'pct_sdose'] #vacina
mins_list = ['zmin1','zmin2', 'zmin3', 'zmin4', 'zmin5', 'zmin6']
maxs_list = ['zmax1','zmax2', 'zmin3', 'zmax4', 'zmax5', 'zmax6']


dct = {}
for i in rate_list:
    dct['%s' % i] = None

dct_min = {}
for i in mins_list:
    dct_min['%s' % i] = None

dct_max = {}
for i in maxs_list:
    dct_max['%s' % i] = None

parties = ['total_dose', 'primeira_dose', 'segunda_dose','pct_populacao_vacinado_all',
           'pct_populacao_vacinado_pdose',	'pct_populacao_vacinado_sdose']
for n in range(0,len(rate_list)):
    dct[rate_list[n]] = [df.loc[Estado, parties[n]] for Estado in tx_ids]
    dct_min[mins_list[n]] = min(dct[rate_list[n]])
    dct_max[maxs_list[n]] = max(dct[rate_list[n]])


def get_color_for_val(val, vmin, vmax, pl_colorscale):
    if vmin >= vmax:
        raise ValueError('vmin should be < vmax')

    plotly_scale, plotly_colors = list(map(float, np.array(pl_colorscale)[:,0])), np.array(pl_colorscale)[:,1]
    colors_01=np.array(list(map(literal_eval,[color[3:] for color in plotly_colors] )))/255.

    v= (val - vmin) / float((vmax - vmin))

    idx = 0

    while(v > plotly_scale[idx+1]):
        idx+=1
    left_scale_val = plotly_scale[idx]
    right_scale_val = plotly_scale[idx+ 1]
    vv = (v - left_scale_val) / (right_scale_val - left_scale_val)

    val_color01 = colors_01[idx]+vv*(colors_01[idx + 1]-colors_01[idx])
    val_color_0255 = list(map(np.uint8, 255*val_color01+0.5))
    return 'rgb'+str(tuple(val_color_0255))


alldose =  [[0.0, 'rgb(255, 255, 204)'],
                [0.35, 'rgb(161, 218, 180)'],
                [0.5, 'rgb(65, 182, 196)'],
                [0.6, 'rgb(44, 127, 184)'],
                [0.7, 'rgb(8, 104, 172)'],
                [1.0, 'rgb(37, 52, 148)']]

pdose= [[0.0, 'rgb(255, 255, 204)'],
                [0.35, 'rgb(161, 218, 180)'],
                [0.5, 'rgb(65, 182, 196)'],
                [0.6, 'rgb(44, 127, 184)'],
                [0.7, 'rgb(8, 104, 172)'],
                [1.0, 'rgb(37, 52, 148)']]

sdose=[[0.0, 'rgb(255, 255, 204)'],
                [0.35, 'rgb(161, 218, 180)'],
                [0.5, 'rgb(65, 182, 196)'],
                [0.6, 'rgb(44, 127, 184)'],
                [0.7, 'rgb(8, 104, 172)'],
                [1.0, 'rgb(37, 52, 148)']]

pctdose=[[0.0, 'rgb(255, 255, 204)'],
                [0.35, 'rgb(161, 218, 180)'],
                [0.5, 'rgb(65, 182, 196)'],
                [0.6, 'rgb(44, 127, 184)'],
                [0.7, 'rgb(8, 104, 172)'],
                [1.0, 'rgb(37, 52, 148)']]

pctpdose= [[0.0, 'rgb(255, 255, 204)'],
                [0.35, 'rgb(161, 218, 180)'],
                [0.5, 'rgb(65, 182, 196)'],
                [0.6, 'rgb(44, 127, 184)'],
                [0.7, 'rgb(8, 104, 172)'],
                [1.0, 'rgb(37, 52, 148)']]

pctsdose= [[0.0, 'rgb(255, 255, 204)'],
                [0.35, 'rgb(161, 218, 180)'],
                [0.5, 'rgb(65, 182, 196)'],
                [0.6, 'rgb(44, 127, 184)'],
                [0.7, 'rgb(8, 104, 172)'],
                [1.0, 'rgb(37, 52, 148)']]



facecolor_list = ['facecoloralldose','facecolorpdose', 'facecolorsdose', 'facecolorpctdose',
                  'facecolorpctpdose', 'facecolorpctsdose']
scale_list = [alldose, pdose,sdose, pctdose, pctpdose, pctsdose]


dct_facecolor = {}
for i in facecolor_list:
    dct_facecolor['%s' % i] = None

for n in range(0,len(facecolor_list)):
    dct_facecolor[facecolor_list[n]] = [get_color_for_val(r, dct_min[mins_list[n]], dct_max[maxs_list[n]], scale_list[n]) for r in dct[rate_list[n]]]


counties = tx_ids

text_all = [c+'<br>Estado de '+ w + ' com o total de ' + '{:0.0f}'.format(r)+' vacinados por COVID-19' for c, r, w in zip(df.UF, dct[rate_list[0]], counties)]

text_p=[c+'<br>Estado de '+ w + ' com o total de ' + '{:0.0f}'.format(r)+' vacinados na primeira dose por COVID-19' for c, r, w in zip(df.UF, dct[rate_list[1]], counties)]

text_s=[c+'<br>Estado de '+ w + ' com o total de ' + '{:0.0f}'.format(r)+' vacinados na segunda dose por COVID-19' for c, r, w in zip(df.UF, dct[rate_list[2]], counties)]

text_pct = [c+'<br>Estado de '+ w + ' com o total de "' + '{:0.2f}'.format(r)+'%" da população vacinados por COVID-19' for c, r, w in zip(df.UF, dct[rate_list[3]], counties)]

text_pctp=[c+'<br>Estado de '+ w + ' com o total de "' + '{:0.2f}'.format(r)+'%"" da população vacinados na primeira dose por COVID-19' for c, r, w in zip(df.UF, dct[rate_list[4]], counties)]

text_pcts=[c+'<br>Estado de '+ w + ' com o total de "' + '{:0.2f}'.format(r)+'%" da população vacinados na segunda dose por COVID-19' for c, r, w in zip(df.UF, dct[rate_list[5]], counties)]

text_list = [text_all, text_p,text_s, text_pct, text_pctp, text_pcts]

data = []

mapbox_access_token = ''

lons=[]
lats=[]

for k in range(len(Brazil['features'])):
    county_coords=np.array(Brazil['features'][k]['geometry']['coordinates'][0][0])
    m, M =county_coords[:,0].min(), county_coords[:,0].max()
    lons.append(0.5*(m+M))
    m, M =county_coords[:,1].min(), county_coords[:,1].max()
    lats.append(0.5*(m+M))



data = [dict(type='scattermapbox',
             lat=lats,
             lon=lons,
             mode='markers',
             marker=dict(size=1, color='white'),
             showlegend=False,
             text=text_list[0],
             hoverinfo='text'
            )]

for a in range(1,len(text_list)):
    data.append(dict(type='scattermapbox',
                 lat=lats,
                 lon=lons,
                 mode='markers',
                 text=text_list[a],
                 showlegend=False,
                 marker=dict(size=1, color='white'),
                 hoverinfo='text'
                ))


layers_list = ['layers1','layers2', 'layers3', 'layers4','layers5', 'layers6']

dct_layers = {}
for i in layers_list:
    dct_layers['%s' % i] = None

for l in range(0,len(layers_list)):
    dct_layers[layers_list[l]]=[dict(sourcetype = 'geojson',
             source =sources[k],
             #below="water",
             type = 'fill',
             color = dct_facecolor[facecolor_list[l]][k],
             opacity=1.0
            ) for k in range(len(sources))]


lay_list = [dct_layers[layers_list[0]],dct_layers[layers_list[1]],
            dct_layers[layers_list[2]], dct_layers[layers_list[3]], dct_layers[layers_list[4]], dct_layers[layers_list[5]]]

updatemenus = list([dict(buttons=list()),
                    dict(direction='down',
                         showactive=True)])

party_list = ['TOTAL','PRIMEIRA DOSE','SEGUNDA DOSE', '% POPULAÇÃO (TOTAL)','% POPULAÇÃO (PRIMEIRA DOSE)','% POPULAÇÃO (SEGUNDA DOSE)' ]
vis_list = [[True,False, False, False, False, False],[False,True, False, False, False, False], [False, False, True, False, False, False],
[False, False, False, True, False, False], [False, False, False, False, True, False], [False, False, False, False, False, True]]

layout = dict(hovermode='closest',
             font=dict(family='Arial Black'),
              autosize=False,
              width=1000,
              height=900,
              mapbox=dict(accesstoken=mapbox_access_token,
                          layers=dct_layers[layers_list[0]],
                          bearing=0,
                          center=dict(
                          lat=-15.47,
                          lon=-47.56),
                          pitch=0,
                          zoom = 3
                    )
              )


for s in range(0,len(party_list)):
    updatemenus[0]['buttons'].append(dict(args=[{'visible': vis_list[s]},
                                               {'mapbox.layers': lay_list[s]}],
                                          label=party_list[s],
                                          method='update'))

layout['updatemenus'] = updatemenus

fig = dict(data=data, layout=layout)
st.plotly_chart(fig)

st.sidebar.title("Heatmap de vacinação COVID-19 (BR)")
st.sidebar.write("Período de Dezembro/2020 à Abril/2021")
st.sidebar.write("Dados extraídos através do scrapping nos dados do OpenDataSUS que eu ensino [aqui](https://github.com/MariSpanol/Covid_cases/blob/main/scrapping_vacine.ipynb)")
st.sidebar.markdown("###### *As informações de população para calculo de percentual da população vacinada foram extraídos através do scrapping nos dados da Wikipédia deste notebook [aqui](https://github.com/MariSpanol/Covid_cases/blob/main/scrapping_population.ipynb)")
st.sidebar.markdown('###### *foram considerados apenas dados com primeira e segunda doses não nulos')
st.sidebar.markdown('')
st.sidebar.markdown('**Mariana Spanol**')
st.sidebar.markdown('Faculdade de Saúde Pública - USP')
st.sidebar.markdown('')
st.sidebar.markdown('')
st.sidebar.markdown('Meus contatos:')
st.sidebar.markdown('mailto:marianaspanol@usp.br')
st.sidebar.markdown('https://github.com/MariSpanol')

st.markdown("""
         <style>
         body {
             background: #ff0099}
             </style>
             """, unsafe_allow_html=True)




