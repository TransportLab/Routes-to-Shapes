"""
Model exported as python.
Name : Shapes
Group : Bahman
With QGIS : 31400
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsExpression
import processing


class Shapes(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        # Select the routes shapefine. This layer should have ['route_id','agency_id','route_short_name','route_long_name','route_desc','route_type']
        self.addParameter(QgsProcessingParameterFeatureSource('routes', 'route(s)', types=[QgsProcessing.TypeVectorLine,QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        # Unique identifier for routes. Could be the name of the routes. The algoorithm will add '_shape' to generate shape-ids.
        self.addParameter(QgsProcessingParameterField('routeid', 'route_id', type=QgsProcessingParameterField.Any, parentLayerParameterName='routes', allowMultiple=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterFeatureSink('Shapes', 'shapes', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(8, model_feedback)
        results = {}
        outputs = {}

        # routes+shape-id
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'shape_id',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 2,
            'FORMULA': parameters['routeid'] + '+ \'_shape\'',
            'INPUT': parameters['routes'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Routesshapeid'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract vertices
        alg_params = {
            'INPUT': outputs['Routesshapeid']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractVertices'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Field calculator1
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'shape_pt_lat',
            'FIELD_PRECISION': 6,
            'FIELD_TYPE': 0,
            'FORMULA': '$y',
            'INPUT': outputs['ExtractVertices']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator1'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Field calculator2
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'shape_pt_lon',
            'FIELD_PRECISION': 6,
            'FIELD_TYPE': 0,
            'FORMULA': '$x',
            'INPUT': outputs['FieldCalculator1']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator2'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Field calculator3
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'shape_pt_sequence',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 1,
            'FORMULA': ' \"vertex_index\"  + 1',
            'INPUT': outputs['FieldCalculator2']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator3'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Field calculator4
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'shape_dist_traveled',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,
            'FORMULA': '\"distance\" * 111000',
            'INPUT': outputs['FieldCalculator3']['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator4'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Drop field(s)
        alg_params = {
            'COLUMN': ['route_id','agency_id','route_short_name','route_long_name','route_desc','route_type','vertex_index','vertex_part','vertex_part_index','distance','angle'],
            'INPUT': outputs['FieldCalculator4']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFields'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Drop field-route-id
        alg_params = {
            'COLUMN': parameters['routeid'],
            'INPUT': outputs['DropFields']['OUTPUT'],
            'OUTPUT': parameters['Shapes']
        }
        outputs['DropFieldrouteid'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Shapes'] = outputs['DropFieldrouteid']['OUTPUT']
        return results

    def name(self):
        return 'Shapes'

    def displayName(self):
        return 'Shapes'

    def group(self):
        return 'Bahman'

    def groupId(self):
        return 'Bahman'

    def createInstance(self):
        return Shapes()

    def shortHelpString(self):
        return """<html><body><h2>Algorithm description</h2>
<p>This algorithm takes route(s) shapefile (with same column in GTFS file) and return the shapes file associated with it. You can save it as csv file or shapefile. </p>
<h2>Input parameters</h2>
<h3>route_id</h3>
<p>Select the route_id or any other filed that shape-id can be create upon.</p>
<h3>shapes</h3>
<p>This is the output of the algorithm. By default it returns the vertices of routes in a point shapefile. You can save it as .csv file into a specified directory. </p>
<h3>route(s)</h3>
<p>Select the route shapefile. This GTFS layer should have at least ['route_id','agency_id','route_short_name','route_long_name','route_desc','route_type']</p>
<h2>Outputs</h2>
<h3>shapes</h3>
<p>This is the output of the algorithm. By default it returns the vertices of routes in a point shapefile. You can save it as .csv file into a specified directory. </p>
<br></body></html>"""