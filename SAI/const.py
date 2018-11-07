""""
All constants and prompts are stored in this file

Created on Jun 15, 2016
@author: Tomas Murillo-Morales, Jaromir Plhak
"""

# AnnotationEffect
SVG_NS = "http://www.w3.org/2000/svg"
SODI_NS = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
ANNOTATION_NAME = "annotation"  # Setting
MAX_TEXT_LENGTH = 10  # Setting
SVG_NAMED_ELEMENTS = [ANNOTATION_NAME, "circle", "ellipse", "line", "path",
                      "polygon", "rect", "text"]

# RdfReader
OWL_NS = "http://www.w3.org/2002/07/owl"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns"
HAS_SVG_PROPERTY = "hasSVGElement"
HAS_X_COORD_PR = "hasXCoordinate"
HAS_Y_COORD_PR = "hasYCoordinate"
COOR_PROPERTY = "LocationPoint"
X_COOR_PROPERTY = "locationPointX"
Y_COOR_PROPERTY = "locationPointY"

# Gui
JSON_FILENAME = "viso.json"  # Setting
RDF_ROOT_NAME = "Graphic_Thing"  # Setting
INSTANCES_NAME = "Instances"  # Setting
MAX_INSTANCES_IN_DIR = 4  # Setting
BASIC_WIDTH = 225  # Setting
ENLARGERD_WIDTH = 300  # Setting
DEFAULT_NS = \
    "http://www.semanticweb.org/ak116252/ontologies/2015/2/upper-visualization"
# DEFAULT_NS = "http://lsd.fi.muni.cz/gate/ontologies/go.rdf"
RDF_NS_ATTRIBUTE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
OWL_PREFIX = "http://www.w3.org/2002/07/owl#"
COMMON_PREFIXES = set(["http://www.w3.org/2002/07/owl",
                       "http://www.w3.org/2000/01/rdf-schema",
                       "http://protege.stanford.edu/plugins/owl/protege",
                       "http://www.w3.org/2006/12/owl2-xml",
                       "http://www.owl-ontologies.com/assert.owl",
                       "http://ontosphere3d.sourceforge.net/LogicViews.owl",
                       "http://www.w3.org/2001/XMLSchema",
                       "http://www.w3.org/1999/02/22-rdf-syntax-ns"])

TREE_TAG_PROPERTIES_HEADER = "headerRow"
TREE_TAG_INSTANCES_HEADER = "instancesGroupHeader"
TREE_TAG_ENTITY = "entityRow"
TREE_TAG_PROPERTY = "propertyRow"
TREE_TAG_OBJECT_PROPERTY = "objectProperty"
TREE_TAG_DATATYPE_PROPERTY = "datatypeProperty"
TREE_TAG_INSTANCE = "instanceRow"
TREE_TAG_HIGHLIGHT = "highlightRow"
TREE_TAGS = [TREE_TAG_PROPERTIES_HEADER, TREE_TAG_INSTANCES_HEADER,
             TREE_TAG_ENTITY, TREE_TAG_PROPERTY, TREE_TAG_OBJECT_PROPERTY,
             TREE_TAG_DATATYPE_PROPERTY, TREE_TAG_INSTANCE, TREE_TAG_HIGHLIGHT]

OBJECT_PROP = "object_property"
DATATYPE_PROP = "datatype_property"

SUBJECT_INDEX = 0
PROPERTY_INDEX = 1
OBJECT_INDEX = 2

# Prompts in english

# Add
ADD = "Add"
ADD_NO_OBJECT = "No object has been selected! Please choose one or more" \
                " object that have to be annotated."
ADD_NO_ENTITY = "Entity or annotation has not been selected. Please choose" \
                " at least one entity or annotation from the tree view."
ADD_SEPARATE_ERROR = "Elements can be added separately only for entities."
ADD_ENTITY_AND_ANNOT = "Both entity and annotation has been selected." \
                            "Please choose either entities or annotation" \
                            " from the tree view."
ADD_NO_SVG = "No SVG element has been added to your annotation."

# Annotation name
ANN_NAME = "Annotation Name"
ANN_NAME_ENTER = "Name for this instance of %s:"
ANN_NAME_DUPLICATED = "Duplicated annotation name. Please add a unique name."

# Replace
REPLACE = "Replace"
REPLACE_NO_SVG = "Cannot replace: No SVG element has been chosen."
REPLACE_NO_ANNOT = "Cannot replace: No annotation has been chosen."
REPLACE_ENT_ANOT_MIX = "Cannot replace: At least one entity instead of" \
                       " annotation has been chosen."
REPLACE_MORE_ANN = "More than one annotation selected. All their SVG" \
                     " elements will be replaced."
REPLACE_ALL_SAME = "No annotation has be replaced because they already" \
                   " have exactly the same SVG elements."
REPLACE_SOME_SAME = "Annotations \"%s\" have not been be replaced because" \
                    " they already have exactly the same SVG elements"

# Remove
REMOVE = "Remove"
REMOVE_NO_ANNOT = "Annotation has not been selected. Please choose at least" \
                  " one annotation from the tree view."
REMOVE_ENTITY_SEL = "SVG elements can be removed only from annotations."
REMOVE_NO_ELEM = "No SVG element was selected. Selected annotation(s) will " \
                 " be removed completely."
REMOVE_EMPTY = "All elements were removed from the selected annotation. The" \
               " annotation(s) \"%s\" was (were) removed as well."
REMOVE_NO_REMOVE = "No SVG element has been removed from your annotation."

# Undo
UNDO = "Undo"
UNDO_NO_OPERATION = "No undo operation can be done."
UNDO_TRIPLES = "Triple edition has been undone."
UNDO_ONE_TRIPLE = "1 triple has been updated by undo function."
UNDO_VAR_TRIPLES = "%s triples have been updated by undo function."
UNDO_VAR_ANNOT = "%s annotation(s) had been updated by undo function."

# Property
PROP = "Property"
PROP_EXIST_ADD = "%s triple(s) already exist, %s new added."
PROP_ALL_EXIST = "All triples already exist. Please choose another one."
PROP_HEADER = "You chose a header in the Properties View." \
              " Please choose a Property to add."
PROP_INSTANCE = "You chose a Property Instance. Please choose a" \
               " Property to add."
PROP_WRONG_CHOICE = "Wrong property choice. Please choose a Property to add."
PROP_NO_RANGE = "No Object (range) chosen. Please choose one annotation" \
                 " from the right-hand tree"
PROP_INST_REMOVE = "You chose a Property (%s)." \
                       " Only property instances can be removed."
PROP_HEADER_EDIT = "You chose a Header. Please choose a" \
                   " Property Instance to edit."
PROP_INST_EDIT = "You chose a Property. Please choose a" \
                 " Property Instance to edit."
PROP_EXIST = "Triple %s already exists."
PROP_MORE_SUBJ = "More than one Subject chosen. Please choose only" \
                 " one annotation from the left-hand tree"
PROP_NO_SUBJ = "No Subject chosen. Please choose one annotation" \
               " from the left-hand tree"
PROP_NO_PROP = "No property has been selected!."
PROP_MORE_PROP = "More than one property has been selected." \
                 " Please choose only one."
PROP_NOTHING_FOUND = "No properties found. Please reload the ontology."
PROP_DATA_NOT_FOUND =  "The following Datatype Properties were not found in" \
                       " the ontology and were added automatically: %s"
PROP_INVALID_PROP = "The property you chose (%s) cannot be edited! " \
                        "Please use the Entity TreeView to modify instance " \
                        "information."

# Selection
SELECT = "Selection"
SELECT_INST = "You selected one or more Entities. " \
              "Only instances (Annotations) can be chosen."

# Save
SAVE = "Save Ontology"
SAVE_NOT_LOADED = "Ontology has not been loaded yet."
SAVE_TO_ORIGINAL = "Do you want to save ontology to the original .rdf file?"
SAVE_NOT_CHOSEN = "File was not chosen."

# Load
LOAD = "Load Ontology"
LOAD_SAVING = "Would you like to save your changes before" \
              " loading a new ontology?"
LOAD_CHOOSING = "Please choose a new ontology to be loaded."
LOAD_NO_TREE = "Only root element was loaded. There should be a problem with" \
               " the namespace or the ontology structure. Please reload" \
               " the ontology."

# File
FILE = "File"
FILE_ERROR = "Cannot create serialized ontology file: %s"
FILE_SER_ERROR = "Error while loading serialized file: %s"
FILE_JSON_ERROR = "Cannot serialize ontology tree in Json tree."
FILE_JSON_FOLDER = "Can't write temp file to user home folder"

# NAMESPACE
NSNAME = "Namespace Name"
NSNAME_NO_NS = "No ontology namespace had been detected." \
               " Please enter the namespace for your ontology."
NSNAME_DETECTED = "We detected this namespace: %s"
NSNAME_ENTER = "Please enter ontology namespace."
NSNAME_NOT_ADDED = "No namespace has been added. The default one will be used."
NSNAME_MULTIPLE = "Multiple ontology namespaces have been detected." \
                  "Please enter the namespace for your ontology.\n\nThe" \
                  " following ontologies were detected:\n %s"
