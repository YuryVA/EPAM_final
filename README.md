# EPAM_final
Realty estate prices heatmap

Used data from realtymag.com

Usage:
 - run get_data_from_web.py 
   - creates city_app_offers.xlsx with offers data
 - run data_preproc.py - prepare data to be vizualized
   - creates city_app_grid_gpd.gpkg and grid_city_bound.gpkg
 - run predictions.py - make predictions to missing polygons 
   - creates city_new_predict.gpkg
 - run offer_heatmap.py
   - creates city_app.html
 - run hist.py
   - creates city.png
 
Example output: https://github.com/YuryVA/EPAM_final/tree/main/EPAM_final/Output
