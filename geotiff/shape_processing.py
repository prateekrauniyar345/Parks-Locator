import os
import geopandas as gpd
import json
import fiona
import tempfile

class Shapefile:
    def __init__(self, drawn_json):
        self.stats = []

        if not drawn_json:
            self.error = "No user defined features"
        
        # read the shapefile
        cwd = os.getcwd()
        parent_dir = os.path.dirname(cwd)

        shapefile_path = os.path.join(parent_dir, 'test_map/static/data/USA_Parks.shp')
        boundary_file_path = os.path.join(parent_dir, 'test_map/static/data/usa_boundary.geojson')

        # List of columns to extract
        desired_columns = ['FID', 'NAME', 'SQMI', 'FEATTYPE', 'Shape__Are', 'Shape__Len']
       
        #check the boundary
        try:
            result = self.check_boundary(drawn_json, boundary_file_path ) 
        except Exception as e:
            print(f"The error drawn shape and boundary : {e}")
       
        #read the user drawn polygons
        '''
        difference between EPSG:4326  and EPSG:3857
        Google Earth is in a Geographic coordinate system with the wgs84 datum. (EPSG: 4326)
        Google Maps is in a projected coordinate system that is based on the wgs84 datum. (EPSG 3857)
        The data in Open Street Map database is stored in a gcs with units decimal degrees & datum of wgs84. (EPSG: 4326)
        The Open Street Map tiles and the WMS webservice, are in the projected coordinate system that is based on the wgs84 datum. (EPSG 3857)
        So if you are making a web map, which uses the tiles from Google Maps or tiles from the Open Street Map webservice,
        they will be in Sperical Mercator (EPSG 3857 or srid: 900913) and hence your map has to have the same projection.
        '''

        ply=None
        try:
            ply = gpd.GeoDataFrame.from_features(drawn_json, crs="EPSG:4326")
            ply.to_crs(epsg=3857)
        except Exception as e:
            print(f"Error reading the drawn json:  {e}")

        # read the main shapefile
        park_data = gpd.read_file(shapefile_path)

        with tempfile.NamedTemporaryFile() as tf:
            crsName = tf.name
        ply.to_file(crsName)

        with fiona.open(crsName, "r") as shapefile:
            shapes = [feature["geometry"] for feature in shapefile]
            print(f"\nnumber of polygons drawns are: {len(shapes)}\n") 

            for index, shape in enumerate(shapes):
                clipped_shapefile = park_data.clip(gpd.GeoDataFrame(geometry=[shape], crs=park_data.crs))
                # Extract desired columns
                extracted_data = clipped_shapefile[desired_columns]
                # Convert to dictionary format
                shape_dict = extracted_data.to_dict(orient='records')
                # Append to stats list
                self.stats.append(shape_dict)

    def display_data(self):
        return {
            'stats' : self.stats
        }
    
    def check_boundary(self, drawn_json, boundary_file_path):
        """
        Check if the polygons in drawn_json are within the boundary defined in the boundary_file_path.

        Parameters:
        drawn_json (dict): The GeoJSON data representing drawn polygons.
        boundary_file_path (str): The file path to the boundary GeoJSON or shapefile.

        Returns:
        bool: True if any of the drawn polygons are within the boundary, False otherwise.
        """
        # Create GeoDataFrame from drawn JSON
        drawn = gpd.GeoDataFrame.from_features(drawn_json, crs="EPSG:4326")
        
        # Read the boundary file
        boundary_gdf = gpd.read_file(boundary_file_path)
        
        # Ensure the drawn polygons and boundary are in the same CRS
        if drawn.crs != boundary_gdf.crs:
            drawn = drawn.to_crs(boundary_gdf.crs)
        
        # Check if drawn polygons are within the boundary
        result = drawn.geometry.within(boundary_gdf.geometry.unary_union)
        
        # Return True if any of the drawn polygons are within the boundary
        return result.any()
