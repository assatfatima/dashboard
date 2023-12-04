import streamlit as st
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
import folium

import altair as alt


from streamlit_folium import folium_static

import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from ipyleaflet import Map, SplitMapControl, TileLayer

from rasterio.transform import from_origin
from rasterio.enums import Resampling
import rasterio
import imageio
from folium import plugins
from folium.plugins import Geocoder
import json
import requests
from io import BytesIO
from jenkspy import jenks_breaks

import leafmap.foliumap as leafmap
import altair as alt
import rasterio as rio
import streamlit as st
from pyproj import Transformer
import folium
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
from rasterio.windows import Window
import tempfile
from PIL import Image, ImageDraw
import imageio
import requests
import io
import os


# 1. as sidebar menu
with st.sidebar:
    selected = option_menu(None, ["Home","Map","Classified Map","SplitMap","Slider","COG Exploring","Timelaps and Timeseries","Requetes ","Contact"], 
                       icons=['house','map', "list-task", 'gear','clock','cloud-upload','clock','search','envelope'],                 
                       menu_icon="cast", default_index=0,
                       styles={"container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "brown"},
    })
    if selected == "Map":
        map_option = st.radio("", ["1000 salaries around Morocco", "Search salary by coordinates"])

     # Créer une carte Folium centrée sur le Maroc
m = folium.Map(location=[31.7917, -7.0926], zoom_start=6)
     # Ajouter les communes au fond de carte

Geocoder().add_to(m)
url_to_geoparquet = "https://rihi22.github.io/geoparquet/dataset_geoparquet_maroc.geoparquet"

    # Download the Parquet file
response = requests.get(url_to_geoparquet)
parquet_content = BytesIO(response.content)

    # Read the Parquet file with Geopandas
gdf = gpd.read_parquet(parquet_content)


folium.TileLayer('openstreetmap').add_to(m)
folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', name='Esri.WorldImagery' ,attr="Esri.WorldImagery").add_to(m)
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', name='OpenTopoMap' , attr="OpenTopoMap").add_to(m)

# add layers control over the map
folium.LayerControl().add_to(m)
     # Générer des points aléatoires au Maroc


     # Extraire les coordonnées de latitude et de longitude de la colonne Geometry
gdf['Latitude'] = gdf['Geometry'].apply(lambda point: point.y)
gdf['Longitude'] = gdf['Geometry'].apply(lambda point: point.x)

def select_point_from_gdf(gdf):
    st.header("Select Position of a salary from GeoDataFrame")

    # Create a dropdown menu to choose from existing latitude and longitude values
    selected_coordinates = st.selectbox("Choose Coordinates:", gdf[['Latitude', 'Longitude']].apply(tuple, axis=1))

    # Convert the selected coordinates back to separate latitude and longitude
    selected_latitude, selected_longitude = selected_coordinates

    # Filter the GeoDataFrame based on the selected latitude and longitude
    selected_point = gdf[(gdf['Latitude'] == selected_latitude) & (gdf['Longitude'] == selected_longitude)]

    # Display information about the selected point
    if not selected_point.empty:
        selected_point = selected_point.iloc[0]  # Take the first row if there are multiple matches

        # Create a new Folium map centered around the selected point
        folium_map_selected = folium.Map(location=[selected_latitude, selected_longitude], zoom_start=3)

        
        # Add marker for the selected point
        marker=folium.Marker(location=[selected_latitude, selected_longitude]).add_to(folium_map_selected)
        for index, row in gdf.iterrows(): 

               data = {
                 'Jour': list(range(1, 7)),
                 'Niveau_Reussite': row[[f'Niveau_Reussite-{i}' for i in range(1, 7)]].values,
                 'Niveau_engagement': row[[f'Niveau_engagement-{i}' for i in range(1, 7)]].values,
                 'Niveau_difficulté': row[[f'Niveau_difficulté-{i}' for i in range(1, 7)]].values}
               df_chart = pd.DataFrame(data).melt('Jour')
               chart = alt.Chart(df_chart).mark_line().encode(
                 x='Jour',
                 y='value:Q',
                 color='variable:N',).properties(width=300, height=150)
               popup = folium.Popup(max_width=350).add_child(folium.VegaLite(chart, width=350, height=150))
               marker.add_child(popup)
               

        # Add Folium layers
        folium.TileLayer('openstreetmap').add_to(folium_map_selected)
        folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                         name='Esri.WorldImagery', attr="Esri.WorldImagery").add_to(folium_map_selected)
        folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', name='OpenTopoMap',
                         attr="OpenTopoMap").add_to(folium_map_selected)

        # Add layers control over the map
        folium.LayerControl().add_to(folium_map_selected)

        

        # Display the map
        folium.GeoJson(maroc).add_to(folium_map_selected)
        Geocoder().add_to(folium_map_selected)
 
        folium_static(folium_map_selected)
    else:
        st.sidebar.warning("No point found at the specified coordinates.")

# Example usage
# Assuming 'gdf' is your GeoDataFrame

if selected=="Home":
      st.title("GeoAnalytic Dashbord")
      st.subheader("Study of 1000 salaries around morocco")
      col1, col2 = st.columns([7, 5])
      with col1:
            st.write("This application has been developed with the primary objective of studying and analyzing various statistics related to employees in Morocco. It provides an interactive platform that allows users to gain detailed insights into the difficulty levels of tasks performed by each employee. Furthermore, the application offers a comprehensive view of each employee's level of engagement in carrying out their professional responsibilities. Emphasizing data transparency, it also enables the measurement of individual success levels for each employee. With these features, users can obtain valuable insights to assess individual performances, understand workplace dynamics, and make informed decisions for continuous improvement within the Moroccan professional environment.")
            

      with col2:
            image = "https://rihi22.github.io/images/salarie.jfif"
            st.image(image, use_column_width=True)
            image="https://rihi22.github.io/images/intro.png"
            st.image(image, use_column_width=True, width=400)


            
            
            
            
if selected=="Map":
     #st.map(gdf, latitude='Latitude', longitude='Longitude')
     if map_option=="1000 salaries around Morocco":
          for index, row in gdf.iterrows(): 
               marker = folium.CircleMarker(location=[row['Latitude'], row['Longitude']],radius=1, color='red', fill=True, fill_color='red',)
               data = {
                 'Jour': list(range(1, 7)),
                 'Niveau_Reussite': row[[f'Niveau_Reussite-{i}' for i in range(1, 7)]].values,
                 'Niveau_engagement': row[[f'Niveau_engagement-{i}' for i in range(1, 7)]].values,
                 'Niveau_difficulté': row[[f'Niveau_difficulté-{i}' for i in range(1, 7)]].values}
               df_chart = pd.DataFrame(data).melt('Jour')
               chart = alt.Chart(df_chart).mark_line().encode(
                 x='Jour',
                 y='value:Q',
                 color='variable:N',).properties(width=300, height=150)
               popup = folium.Popup(max_width=350).add_child(folium.VegaLite(chart, width=350, height=150))
               marker.add_child(popup)
               marker.add_to(m)
             
          folium_static(m)
     if map_option=="Search salary by coordinates":
           select_point_from_gdf(gdf)
     
     # Afficher le tableau de données
     #st.write(gdf)

if selected=="Contact":
      st.write(
        "This project was developed as part of the Web Mapping course in the 3rd year of Topographic Engineering and Geomatics Science. The course is taught by Professor M. Hajji Hicham, and this platform was created by the following students."
    )
      col1,col2=st.columns(2)
      with col1:
            image="https://rihi22.github.io/images/rihi.png"
            st.image(image, caption='Rihi Meryame', use_column_width=True, width=400)

      with col2:
            image="https://rihi22.github.io/images/assat.png"
            st.image(image, caption='ASSAT FATIMA', use_column_width=True, width=400)
if selected == "Classified Map":
    

    def jenks_classifier(data, column, k=5):
        values = data[column].values
        breaks = jenks_breaks(values, k)
        return breaks



    # Sidebar for selecting the option (Attribute/Property)
    option = st.sidebar.radio("Choisir une option", ("","Dynamic Properties", "unchanging Properties"))

    if option == "Dynamic Properties":
        # List of attributes for selection
        attributs = ['Niveau_Reussite-', 'Niveau_engagement-', 'Niveau_difficulté-']
        selected_attribute = st.selectbox("Sélectionner un attribut", attributs)

        # List of days for selection
        jours = [6, 5, 4, 3, 2, 1, 0]
        selected_day = st.selectbox("Sélectionner un jour", jours)

        # Filter data based on selected attribute and day
        selected_column_day = f'{selected_attribute}{selected_day}'
        filtered_data = gdf[(gdf[selected_column_day] >= 0)]

        # Reproject the geometries to a projected CRS (Web Mercator, EPSG:3857)
        #gdf = gdf.to_crs(epsg=3857)

        # Create a Leaflet map centered on the average coordinates of the geometries
        m = leafmap.Map(location=[31.7917,-7.0926], latlon_control=True, minimap_control=True, zoom_start=5.5)
        

        # Define the scale for proportional symbols
        scale = filtered_data[selected_column_day].max()
        echelle=filtered_data[selected_column_day].min()

        # Obtain classes using Jenks classification
        breaks = jenks_classifier(filtered_data, selected_column_day, k=5)

        

        # Create a dynamic legend HTML
        legend_html = f'''
            <div style="position: fixed; bottom: 50px; left: 50px; background-color: transparent; border: 2px solid grey; z-index: 9999; font-size: 14px;">
                <p><span style="background-color: blue; solid grey; border-radius: 50%; display: inline-block; height: 5px; width: 5px;"></span> 0-{breaks[1]:.2f}</p>
                <p><span style="background-color: blue; solid grey; border-radius: 50%; display: inline-block; height: 10px; width: 10px;"></span> {breaks[1]:.2f}-{breaks[2]:.2f}</p>
                <p><span style="background-color: blue; solid grey; border-radius: 50%; display: inline-block; height: 15px; width: 15px;"></span> {breaks[2]:.2f}-{breaks[3]:.2f}</p>
                <p><span style="background-color: blue; solid grey; border-radius: 50%; display: inline-block; height: 20px; width: 20px;"></span> {breaks[3]:.2f}-{breaks[4]:.2f}</p>
                <p><span style="background-color: blue; solid grey; border-radius: 50%; display: inline-block; height: 25px; width: 25px;"></span> {breaks[4]:.2f}-{scale:.2f}</p>
            </div>
        '''

        # Add the dynamic legend to the map
        m.add_html(html=legend_html)

        # Add data to the map as proportional symbols
        for idx, row in filtered_data.iterrows():
            popup = f"{selected_column_day}: {row[selected_column_day]}"
            folium.CircleMarker(
                location=[row['Geometry'].y, row['Geometry'].x],
                radius=(row[selected_column_day] / scale) * 10,
                popup=popup,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.6,
            ).add_to(m)

        # Display the map in Streamlit
        folium_static(m)

        
    if option == "unchanging Properties":
        # List of properties for selection
        proprietes = ['Formation', 'Experience']
        selected_property = st.selectbox("Sélectionner une propriété", proprietes)

        # Classify values using the Jenks method
        breaks = jenks_classifier(gdf, selected_property, k=5)

        # Create a Leaflet map centered on the average coordinates of the geometries
        m = leafmap.Map(location=[31.7917,-7.0926], latlon_control=True, minimap_control=True, zoom_start=6)
        

        # Define colors for classes
        colors =['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#a63603']
        cmap = LinearColormap(['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#a63603'], vmin=0, vmax=100).to_step(5)
        cmap.add_to(m)

        # Add data to the map with colors for classes
        for idx, row in gdf.iterrows():
            popup = f"{selected_property}: {row[selected_property]}"
            value = row[selected_property]
            class_idx = sum(value > i for i in breaks)
            color = colors[class_idx] if class_idx < len(colors) else '#a63603'
            folium.CircleMarker(
                location=[row['Geometry'].y, row['Geometry'].x],
                radius=5,
                popup=popup,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
            ).add_to(m)
        folium_static(m)
if selected=="Requetes ":
     type_requete = st.radio("Choisissez le type de requete :", ["","requete spatiale", "requete attributaire"])
     if type_requete=="requete spatiale":
          requete = st.radio("what do you want to do :", ["","select salaries based on a polygon", "select salaries based on a region"])
          if requete=="select salaries based on a polygon":
               uploaded_file = st.file_uploader("Uploader un fichier Shapefile", type=["shp"])
               if uploaded_file is not None:
                    #temp_file_path = " https://rihi22.github.io/fichier/fichier1.shp"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".shp") as temp_file:
                      temp_file.write(uploaded_file.read())
                      temp_file_path = temp_file.name
                    os.environ["SHAPE_RESTORE_SHX"] = "YES"

                    # Read the file from the temporary location
                    uploaded_gdf = gpd.read_file(temp_file_path)
    

                       # Bouton pour choisir si les points doivent être à l'intérieur ou à l'extérieur de la zone définie
                    spatial_filter_choice = st.radio("Choisissez le filtre spatial :", ["","À l'intérieur", "À l'extérieur"])

                     # Appliquer le filtrage spatial
                    if spatial_filter_choice == "À l'intérieur":
                         filtered_data_spatial = gdf[gdf.geometry.within(uploaded_gdf.unary_union)]
                    else:
                         filtered_data_spatial = gdf[~gdf.geometry.within(uploaded_gdf.unary_union)]

                    # Mettre à jour la carte avec les points filtrés spatialement
                    st.map(filtered_data_spatial, latitude='Latitude', longitude='Longitude')
          if requete=="select salaries based on a region":
               shapefile_path = "https://rihi22.github.io/geoparquet/maroc_region.geojson"
               maroc = gpd.read_file(shapefile_path)
               gdf.crs=maroc.crs
               gdf['Date'] = gdf['Date'].astype(str)
               unique_regions = maroc['RegionFr'].unique()
               selected_region = st.selectbox("Choose Region:", unique_regions)
               selected_region_geometry = maroc[maroc['RegionFr'] == selected_region].unary_union
               gdf_selected_region = gdf[gdf.geometry.within(selected_region_geometry)]
               st.map(gdf_selected_region, latitude='Latitude', longitude='Longitude')
     if type_requete=="requete attributaire":
          gdf['latitude'] = gdf['Geometry'].y
          gdf['longitude'] = gdf['Geometry'].x

          with st.expander("Filtre"):
               operators = ['==', '!=', '>', '<', '>=', '<=']
               num_conditions = st.number_input("Nombre de conditions", min_value=1, value=1)
               conditions = []
               filter_columns = [col for col in gdf.columns if col not in ['Geometry', 'Propriete1']]
               for i in range(num_conditions):
                    column = st.selectbox(f"Sélectionner l'attribut {i + 1}", filter_columns, key=f"select_{i}")
                    operator = st.selectbox(f"Opérateur logique pour {column}", operators, key=f"operator_{i}")
                    value_input = st.text_input(f"Condition pour {column}", key=f"input_{i}")
                    dtype = gdf[column].dtype
                    if value_input:
                         try:
                              value = dtype.type(value_input)
                         except ValueError:
                              st.warning(f"Impossible de convertir la valeur '{value_input}' en type {dtype}")
                              continue
                    else:
                         st.warning("La valeur d'entrée ne peut pas être vide.")
                         continue

                    conditions.append((column, operator, value))
               filtered_gdf = gdf.copy()
               for condition in conditions:
                    column, operator, value = condition
                    filtered_gdf = filtered_gdf[eval(f"filtered_gdf['{column}'] {operator} {repr(value)}")]
               st.map(filtered_gdf[['latitude', 'longitude']])

if selected=="SplitMap":
     def main():
          
          
          st.title("Split-panel Map")
          jours_attributs = {
        "1": ["difficulte1", "reussite1", "engagement1"],
        "2": ["difficulte2", "reussite2", "engagement2"],
        "3": ["difficulte3", "reussite3", "engagement3"],
        "4": ["difficulte4", "reussite4", "engagement4"],
        "5": ["difficulte5", "reussite5", "engagement5"],
        "6": ["difficulte6", "reussite6", "engagement6"],
        # Ajoutez les jours restants ici de la même manière
    }

    # Sélecteurs pour les jours gauche et droit
          left_jour_key = st.selectbox("Sélectionner le jour à gauche", list(jours_attributs.keys()))
          jours_disponibles = list(jours_attributs.keys())
          jours_disponibles.remove(left_jour_key)
          right_jour_key = st.selectbox("Sélectionner le jour à droite", jours_disponibles)
          attributs_jour = ["difficulte","reussite","engagement"]
          attribut_selectionne = st.selectbox("Sélectionner l'attribut à comparer", attributs_jour)
          left_image_url = f"https://rihi22.github.io/rasterf/{attribut_selectionne}{left_jour_key}.tif"
          right_image_url = f"https://rihi22.github.io/rasterf/{attribut_selectionne}{right_jour_key}.tif"
          m = leafmap.Map()
          m.split_map(left_image_url, right_image_url)
          m.to_streamlit(height=700)

     if __name__ == "__main__":
          main()
if selected=="Slider":
     dst_crs = 'EPSG:4326'
     selected_day = st.sidebar.slider('Select Day:', 1, 6, 1)
     selected_attribute = st.sidebar.selectbox('Select Attribute:', ['difficulte', 'engagement', 'reussite'])
     image_path = f"https://rihi22.github.io/rasterf/{selected_attribute}{selected_day}.tif"
     with rio.open(image_path) as src:
          img = src.read()
          src_crs = src.crs.to_string().upper()
          min_lon, min_lat, max_lon, max_lat = src.bounds

     bounds_orig = [[min_lat, min_lon], [max_lat, max_lon]]

     bounds_fin = []
     for item in bounds_orig:
          lat = item[0]
          lon = item[1]

          proj = Transformer.from_crs(src_crs, dst_crs, always_xy=True)

          lon_n, lat_n = proj.transform(lon, lat)

          bounds_fin.append([lat_n, lon_n])


     centre_lon = bounds_fin[0][1] + (bounds_fin[1][1] - bounds_fin[0][1]) / 2
     centre_lat = bounds_fin[0][0] + (bounds_fin[1][0] - bounds_fin[0][0]) / 2
     m = folium.Map(location=[centre_lat, centre_lon], zoom_start=6)
     m.add_child(folium.raster_layers.ImageOverlay(img.transpose(1, 2, 0), opacity=.7,
                                              bounds=bounds_fin))
     vmin = 0
     if selected_attribute == 'difficulte':
          vmax = 50
          legend_colors = ['#ffffb2', '#fd8d3c', '#810f7c', '#54278f']
    
     elif selected_attribute == 'engagement':
          vmax = 20
          legend_colors = ['#ffffd4', '#78c679', '#31a354', '#045a8d']
    
     elif selected_attribute == 'reussite':
          vmax = 100
          legend_colors = ['#253494', '#00FF00', '#FFFF00', '#FF0000']

     cmap = LinearColormap(legend_colors, vmin=vmin, vmax=vmax).to_step(10, method='log')


     cmap.add_to(m)
     folium_static(m)
if selected=="COG Exploring":
     def get_tile_coordinates(cog_path, x_coord, y_coord):
          with rio.open(cog_path) as src:
               if 0 <= x_coord < src.width and 0 <= y_coord < src.height:
                    tile_x = x_coord // src.profile['blockxsize'] * src.profile['blockxsize']
                    tile_y = y_coord // src.profile['blockysize'] * src.profile['blockysize']
                    return tile_x, tile_y
               else:
                    return None

     def create_tile(cog_path, tile_coords, tile_size):
          with rio.open(cog_path) as src:
               window = Window(tile_coords[0], tile_coords[1], tile_size, tile_size)
               tile = src.read(window=window, out_shape=(src.count, tile_size, tile_size))
               output_path = "selected_tile.tif"
               profile = src.profile
               profile.update(width=tile_size, height=tile_size, transform=src.window_transform(window))
          with rio.open(output_path, 'w', **profile) as dst:
            dst.write(tile)
            return output_path

     jours = ["1", "2", "3", "4", "5", "6"]
     attributs = ["difficulte", "engagement", "reussite"]  # Ajoutez vos attributs ici
     jour_selectionne = st.selectbox("Sélectionnez le jour", jours)
     attribut_selectionne = st.selectbox("Sélectionnez l'attribut", attributs)
     cog_path = f"https://rihi22.github.io/COG/{attribut_selectionne}{jour_selectionne}.tif"
     st.title("Affichage de la Tuile COG sur une Carte")
     m = folium.Map(location=[31.7917,-7.0926], zoom_start=5)
     with rio.open(cog_path) as src:
          coordonnees_tuiles = [(window.col_off, window.row_off) for ij, window in src.block_windows()]
          tuile_selectionnee = st.selectbox("Sélectionnez les coordonnées de la tuile", coordonnees_tuiles)

     x_coord, y_coord = tuile_selectionnee
     st.subheader("Coordonnées de la Tuile Sélectionnée:")
     st.write(f"Coordonnée X: {x_coord}, Coordonnée Y: {y_coord}")
     if tuile_selectionnee:
          st.subheader("Coordonnées de la Tuile Sélectionnée:")
          tile_size = 256  # Adjust the tile size as needed
          selected_tile_path = create_tile(cog_path, tuile_selectionnee, tile_size)

          with rio.open(selected_tile_path) as selected_tile:
               img = selected_tile.read()
               bounds = selected_tile.bounds
          bounds_fin = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
          m.add_child(folium.raster_layers.ImageOverlay(img.transpose(1, 2, 0), opacity=.7, bounds=bounds_fin))
          folium_static(m)
     else:
          st.warning("Les coordonnées spécifiées sont en dehors de la plage valide.")
if selected=="Timelaps and Timeseries":
     time = st.radio("Choisissez entre :", ["","Timelaps", "Timeseries"])
     if time=="Timelaps":
          def get_gif_path(property_name):
               property_gifs = {
        'timelapse_difficulte': 'https://rihi22.github.io/gif/difficulte.gif',
        'timelapse_engagement': 'https://rihi22.github.io/gif/engagement.gif',
        'timelapse_reussite': 'https://rihi22.github.io/gif/reussite.gif'
    }
               return property_gifs.get(property_name, None)

          m = folium.Map(location=[31.7917, -7.0926], zoom_start=6)  # Coordonnées au centre du Maroc et niveau de zoom
          selected_property = st.selectbox("Choisissez une propriété", ['timelapse_difficulte', 'timelapse_engagement', 'timelapse_reussite'])
          gif_path = get_gif_path(selected_property)
          if gif_path:
               st.image(gif_path, caption=f"{selected_property} gif", use_column_width=True)
          else:
               st.warning("Aucun GIF disponible pour la propriété sélectionnée.")
     if time=="Timeseries":
          output_folder = "timelapses"
          os.makedirs(output_folder, exist_ok=True)

          st.markdown("<h2 style='font-size:32px; text-align:center;'>TIMELAPSE </h2>", unsafe_allow_html=True)

          attributs = ['difficulte', 'engagement', 'reussite']
          selected_attribute = st.selectbox("Sélectionner un attribut", attributs)

          def create_timelapse(attribute, DAY_names, duration, gif_size=(256, 240)):
               images = []
               for i in range(1, 7):
                    url = f"https://rihi22.github.io/rasterf/{attribute}{i}.tif"
                    response = requests.get(url)
                    image_data = Image.open(io.BytesIO(response.content))

                    # Convertir l'image en tableau NumPy
                    image_array = np.array(image_data)

                    # Créer un objet de dessin
                    draw = ImageDraw.Draw(image_data)

                    # Annoter chaque image avec les noms des jours
                    draw.text((10, 10), f'{attribute} jour {i}', fill='white', font=None)

                    # Ajouter l'image annotée à la liste
                    images.append(np.array(image_data))

          # Générer le GIF à partir des images annotées
               gif_filename = f'timelapse_{attribute}.gif'
               with imageio.get_writer(gif_filename, mode='I', duration=duration, loop=0, size=gif_size) as writer:
                    for image in images:
                         writer.append_data(image)
               return gif_filename

               # Liste des noms de jours
          DAY_names = [f'jour{jour}' for jour in range(1, 7)]
          duration = 350
          maroc_coordinates = {
          "latitude": [27.6664, 35.9225],  # Latitude du bas et du haut
          "longitude": [-17.0205, -1.1256]  # Longitude de la gauche et de la droite
          }
               # Utiliser la première image pour définir les limites
          first_image_url = f"https://rihi22.github.io/rasterf/{attributs[0]}1.tif"
          first_image_data = Image.open(io.BytesIO(requests.get(first_image_url).content))
          gif_size = (256, 240)
          bounds = [
               [maroc_coordinates["latitude"][0], maroc_coordinates["longitude"][0]],
               [maroc_coordinates["latitude"][1], maroc_coordinates["longitude"][1]]
               ]


               # Créer les timelapses pour chaque attribut
          gif_filenames = {}
          for attribute in attributs:
                    gif_filenames[attribute] = create_timelapse(attribute, DAY_names, duration)

               # Reste du code pour afficher la carte avec Folium
          m = folium.Map(location=[28.7917, -9.6026], zoom_start=5)

          selected_gif_filename = gif_filenames[selected_attribute]

          bounds_morocco = [
               [36, -17],  # Coin supérieur droit (nord-ouest)
               [20.8, -1]   # Coin inférieur gauche (sud-est)
               ]
          gif_layer = folium.raster_layers.ImageOverlay(
               selected_gif_filename,
               bounds=bounds_morocco,
               opacity=0.7,
               name=f'GIF Layer - {selected_attribute}'
               ).add_to(m)

          vmin = 0
          if selected_attribute == 'difficulte':
                         vmax = 50
                         legend_colors = ['#ffffb2', '#fd8d3c', '#810f7c', '#54278f']
               
          elif selected_attribute == 'engagement':
                         vmax = 20
                         legend_colors = ['#ffffd4', '#78c679', '#31a354', '#045a8d']
               
          elif selected_attribute == 'reussite':
                         vmax = 100
                         legend_colors = ['#253494', '#00FF00', '#FFFF00', '#FF0000']

          cmap = LinearColormap(legend_colors, vmin=vmin, vmax=vmax).to_step(10, method='log')
          cmap.add_to(m)
          folium.LayerControl().add_to(m)
          folium_static(m)
               # Vous pouvez utiliser st.success pour informer l'utilisateur que les GIF ont été créés
          st.success("Les GIF ont été créés avec succès!")
