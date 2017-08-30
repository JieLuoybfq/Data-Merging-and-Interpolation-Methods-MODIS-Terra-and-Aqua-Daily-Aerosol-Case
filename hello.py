import os

os.system("gdal_contour -a elev MOD04L2.A2015333.0254.006.2015333030251.tif output.shp -i 10.0")

topojson -o output.shp input.json