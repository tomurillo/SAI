"""
Created on Apr 27, 2016
@author: Tomas Murillo-Morales, Jaromir Plhak
"""

import Tkinter
from ttk import Treeview
import tkFileDialog
from RDFReader import RDFReader
from SVGParser import SVGParser
import inkex
import os
import tkMessageBox
import tkSimpleDialog
import json
from lxml import etree
import const as c


class PickerGUI():
    """ This class maintains the TK Inter user interface and contains all the
        data from ontology. Data can be loaded from (and store to) .rdf using
        RDFReader class or from JSON (that is much faster). """

    def __init__(self, master, annotationEffect):
        self.fileName = ""
        self.namespace = None
        self.aEffect = annotationEffect
        self.root = master
        self.root.bind('<Escape>', self.close)
        self.leftFrame = Tkinter.Frame(master)
        self.middleFrame = Tkinter.Frame(master)
        self.rightFrame = Tkinter.Frame(master)
        self.leftFrame.pack(side=Tkinter.LEFT, padx=10, pady=10)
        self.middleFrame.pack(side=Tkinter.LEFT)
        self.rightFrame.pack(side=Tkinter.LEFT)
        self.bottomLeftFrame = Tkinter.Frame(self.leftFrame)
        self.bottomMiddleFrame = Tkinter.Frame(self.middleFrame)
        self.bottomRightFrame = Tkinter.Frame(self.rightFrame)
        self.menuBar = Tkinter.Menu(master)
        self.fileMenu = Tkinter.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Load Ontology", accelerator="Ctrl+L",
                                  command=self.loadOntology)
        self.fileMenu.add_command(label="Save to Ontology",
                                  accelerator="Ctrl+S",
                                  command=self.saveOntology)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenuUndo = Tkinter.Menu(self.menuBar, tearoff=0)
        self.fileMenuUndo.add_command(label="Undo", accelerator="Ctrl+Z",
                                      command=self.undoOperation)
        self.root.bind_all("<Control-l>", self.loadOntology)
        self.root.bind_all("<Control-s>", self.saveOntology)
        self.root.bind_all("<Control-z>", self.undoOperation)
        self.menuBar.add_cascade(label="Edit", menu=self.fileMenuUndo)
        # Treeview to choose Ontology Entities to annotate new elements
        self.treeEntityPicker = Treeview(self.leftFrame)
        self.treeEntityPicker.heading("#0", text="Entity/Subject")
        self.treeEntityPicker.column("#0", width=c.BASIC_WIDTH,
                                     stretch=Tkinter.NO)
        # Treeview to choose Object Properties
        self.treePropertyPicker = Treeview(self.middleFrame)
        self.treePropertyPicker.heading("#0", text="Properties")
        self.treePropertyPicker.column("#0", width=c.ENLARGERD_WIDTH,
                                       stretch=Tkinter.NO)
        # Treeview to choose range individuals of property
        self.treeRangePicker = Treeview(self.rightFrame)
        self.treeRangePicker.heading("#0", text="Object")
        self.treeRangePicker.column("#0", width=c.BASIC_WIDTH,
                                     stretch=Tkinter.NO)
        self.buttonAdd = Tkinter.Button(self.bottomLeftFrame)
        self.buttonAdd["text"] = "Add"
        self.buttonAddProperty = Tkinter.Button(self.bottomRightFrame)
        self.buttonAddProperty["text"] = "Add Prop."
        self.buttonEditProperty = Tkinter.Button(self.bottomRightFrame)
        self.buttonEditProperty["text"] = "Edit Prop."
        self.buttonRemoveProperty = Tkinter.Button(self.bottomRightFrame)
        self.buttonRemoveProperty["text"] = "Delete Prop."
        self.buttonSeparateAdd = Tkinter.Button(self.bottomLeftFrame)
        self.buttonSeparateAdd["text"] = "Add Separately"
        self.buttonReplace = Tkinter.Button(self.bottomLeftFrame)
        self.buttonReplace["text"] = "Replace"
        self.buttonRemove = Tkinter.Button(self.bottomLeftFrame)
        self.buttonRemove["text"] = "Remove"
        self.buttonClear = Tkinter.Button(self.bottomMiddleFrame)
        self.buttonClear["text"] = "Clear Views"
        # define options for opening or saving a file
        self.file_opt = options = {}
        options["defaultextension"] = ".rdf"
        options["filetypes"] = [("RDF files", ".rdf")]
        options["parent"] = master
        options["title"] = "Load a RDF Ontology"
        self.resetVariables()

    def prepare(self, master):
        self.treeEntityPicker.pack(pady=15)
        self.treePropertyPicker.pack(pady=15)
        self.treePropertyPicker.bind("<ButtonRelease-1>", self.propertySelect)
        # Handle double click on Property Tree
        self.treePropertyPicker.bind("<Double-1>", self.propertyClick)
        self.treeRangePicker.pack(pady=15)
        self.bottomLeftFrame.pack(fill=Tkinter.X)
        self.bottomMiddleFrame.pack(fill=Tkinter.X)
        self.bottomRightFrame.pack(fill=Tkinter.X, padx=25)
        self.buttonAdd.pack(side=Tkinter.LEFT)
        self.buttonSeparateAdd.pack(side=Tkinter.LEFT)
        self.buttonReplace.pack(side=Tkinter.LEFT)
        self.buttonAddProperty.pack(side=Tkinter.LEFT)
        self.buttonEditProperty.pack(side=Tkinter.LEFT)
        self.buttonRemoveProperty.pack(side=Tkinter.LEFT)
        self.buttonRemove.pack(side=Tkinter.LEFT)
        self.buttonClear.pack(side=Tkinter.BOTTOM)
        self.buttonAdd.bind("<ButtonRelease-1>", self.buttonAddClick)
        self.buttonAdd.bind("<Return>", self.buttonAddClick)
        self.buttonSeparateAdd.bind("<ButtonRelease-1>",
                                    self.buttonSeparateAddClick)
        self.buttonSeparateAdd.bind("<Return>", self.buttonSeparateAddClick)
        self.buttonAddProperty.bind("<ButtonRelease-1>",
                                    self.buttonAddPropertyClick)
        self.buttonAddProperty.bind("<Return>", self.buttonAddPropertyClick)
        self.buttonEditProperty.bind("<ButtonRelease-1>",
                                     self.buttonEditPropertyClick)
        self.buttonEditProperty.bind("<Return>", self.buttonEditPropertyClick)
        self.buttonRemoveProperty.bind("<ButtonRelease-1>",
                                       self.buttonRemovePropertyClick)
        self.buttonRemoveProperty.bind("<Return>",
                                       self.buttonRemovePropertyClick)
        self.buttonReplace.bind("<ButtonRelease-1>", self.buttonReplaceClick)
        self.buttonReplace.bind("<Return>", self.buttonReplaceClick)
        self.buttonRemove.bind("<ButtonRelease-1>", self.buttonRemoveClick)
        self.buttonRemove.bind("<Return>", self.buttonRemoveClick)
        self.buttonClear.bind("<ButtonRelease-1>", self.buttonClearClick)
        self.buttonClear.bind("<Return>", self.buttonClearClick)
        master.config(menu=self.menuBar)
        self.loadSerializedOntology(self.treeEntityPicker)

    def resetVariables(self):
        # Keys: classHierarchy, instances; Values: temporary data
        # (to be serialized and saved)
        self.tempData = {}
        # Key: Class Name; Value: List of IDs of instances of that class
        self.instancesbyClass = {}
        # Key: Property Name; Values: Entities that belong to its range
        self.rangesByProperty = {}
        # Key: Property Name; Values: Entities that belong to its domain
        self.domainsByProperty = {}
        self.ontologyTree = None
        self.lastId = -1
        self.defaultName = ""
        self.defaultTypeValue = ""
        self.defaultTypeValue = ""
        self.undoStack = []
        self.selectedEntities = None
        self.selectedRange = None
        self.selectedProperties = None
        # Keys: properties; Values: occurrences of the property
        # i.e. (s,p,o) triples
        self.objectProperties = {}
        # (s,p,o) triples with object properties to be added to the ontology
        self.objectPropertiesToAdd = []
        self.objectPropertiesToRemove = []
        # Key: TreeView element ID. #Value: (s,p,o) triple.
        self.propertiesByTreeID = {}
        self.dataTypeProperties = {}
        self.dataTypePropertiesToAdd = []
        self.dataTypePropertiesToRemove = []

    def buttonAddClick(self, event):
        """ Button handler for adding entities. """
        self.prepareSelectedEntities()
        close = self.aEffect.addAnnotation(separateAdd=False)
        if close:
            self.closeGUI(isInstanceListChanged=True)

    def buttonSeparateAddClick(self, event):
        """ Button handler for adding entities separately. """
        self.prepareSelectedEntities()
        close = self.aEffect.addAnnotation(separateAdd=True)
        if close:
            self.closeGUI(isInstanceListChanged=True)

    def buttonAddPropertyClick(self, event):
        """ Button handler for adding properties. """
        selectedProperty, tags, rowID = self.prepareSelectedProperty(limitObjects=False)
        if self.validateProperty(selectedProperty, tags):
            serialize = self.aEffect.addProperty(selectedProperty, tags)
            if serialize:
                self.serialize()
                self.refreshPropertyTree(self.treePropertyPicker)

    def buttonEditPropertyClick(self, event):
        """ Button handler for editing properties. Removes the previous
            (s,p,o) triple and adds a new one. """
        selectedProperty, tags, rowID = self.prepareSelectedProperty()
        if self.validateProperty(selectedProperty, tags):
            serialize = self.aEffect.editProperty(selectedProperty, tags, rowID)
            if serialize:
                self.serialize()
                self.refreshPropertyTree(self.treePropertyPicker)

    def buttonRemovePropertyClick(self, event):
        """ Button handler for removing properties. """
        selectedProperties, tags, rowIDs = \
            self.getSelectedProperty(multiselect=True)

        for p in selectedProperties:
            if not self.validateProperty(p, ""):
                return
        for p, tagList in tags.iteritems():
            if not self.validateProperty("", tagList):
                return 
        ser = self.aEffect.removeProperty(selectedProperties, tags, rowIDs)
        if ser:
            self.serialize()
            self.refreshPropertyTree(self.treePropertyPicker)
            
    def validateProperty(self, property, tags):
        """" Validate that the selected property can be chosen
        :param property: The property name
        :param tags: A list of tags of a selected tree row, containing
        the property name in the case of an instance
        :return: boolean Whether the property is valid
        """
        valid = True
        invalidProperties = [c.HAS_SVG_PROPERTY, 
                             c.HAS_X_COORD_PR, 
                             c.HAS_Y_COORD_PR]
        if property in invalidProperties:
            valid = False
            tkMessageBox.showwarning(c.PROP, c.PROP_INVALID_PROP % property)
        elif tags:
            for tag in tags:
                if tag in invalidProperties:
                    tkMessageBox.showwarning(c.PROP, c.PROP_INVALID_PROP % tag)
                    valid = False
                    break
        return valid

    def prepareSelectedProperty(self, limitObjects=True):
        """ Returns the selected property and ensures that instances of its
            domain (for its range, use validateSelectedRange) have been
            selected.
        :param limitObjects: True if only one object can be selected
        :return: selected property
        """

        selectedProperty, tags, rowID = self.getSelectedProperty()
        if selectedProperty:
            validEntity = self.prepareSelectedEntities(allowOnlyInstances=True)
            if validEntity:
                if len(self.selectedEntities) > 0:
                    if limitObjects and len(self.selectedEntities) > 1:
                        tkMessageBox.showwarning(c.PROP, c.PROP_MORE_SUBJ)
                    else:
                        # TODO: validate that subject and object are instances
                        # and are within the domain and range of the property
                        return selectedProperty, tags, rowID
                else:
                    tkMessageBox.showwarning(c.PROP, c.PROP_NO_SUBJ)
        return None, None, None

    def getSelectedProperty(self, multiselect=False):
        """ Fetches the selected Property from the middle TreeView and handles
            incorrect selections. Returns a triple with the property name
            (as in the Treeview), its tags and the row ID on the TreeView.
        :param multiselect: Is set to 'True' if selection of multiple
            properties is allowed, 'False' otherwise.
        """

        selectedProperty = None
        tags = None
        rowID = None
        selectedProperties = self.treePropertyPicker.selection()
        if len(selectedProperties) == 0:
            tkMessageBox.showwarning(c.PROP, c.PROP_NO_PROP)
        elif multiselect:
            rowIDs = {}
            properties = []
            tags = {}
            for rowID in selectedProperties:
                p = self.treePropertyPicker.item(rowID, "text")
                properties.append(p)
                tags[p] = self.treePropertyPicker.item(rowID, "tags")
                rowIDs[p] = rowID
            return properties, tags, rowIDs
        elif len(selectedProperties) > 1:
            tkMessageBox.showwarning(c.PROP, c.PROP_MORE_PROP)
        else:
            rowID = selectedProperties[0]
            selectedProperty = self.treePropertyPicker.item(rowID, "text")
            tags = self.treePropertyPicker.item(rowID, "tags")
        return selectedProperty, tags, rowID

    def buttonReplaceClick(self, event):
        """ Button handler for replace svg elements in annotation. """
        self.prepareSelectedEntities()
        close = self.aEffect.replaceAnnotation()
        if close:
            self.closeGUI(isInstanceListChanged=True)

    def buttonRemoveClick(self, event):
        """ Button handler for moving svg elements from annotation. """
        self.prepareSelectedEntities()
        close = self.aEffect.removeAnnotation(None, fromUndo=False)
        if close:
            self.closeGUI(isInstanceListChanged=True)

    def undoOperation(self, *args):
        """ Button handler for undo operation. """
        self.prepareSelectedEntities()
        close = self.aEffect.undoAnnotation()
        if close:
            self.closeGUI(isInstanceListChanged=True)

    def buttonClearClick(self, event):
        """ Button handler for clearing tree view and set
            it into default state. """
        self.treeEntityPicker.delete(*self.treeEntityPicker.get_children())
        self.populatePropertyTree(self.treeEntityPicker, [])
        self.treeRangePicker.delete(*self.treeRangePicker.get_children())

    def propertyClick(self, event):
        """ Load the individuals that belong to the range of the selected
            Property on the right-hand TreeView, and to its domain on the
            left-hand TreeView.
        """

        selectedProperty, tags, rowID = self.getSelectedProperty()
        if selectedProperty and c.TREE_TAG_PROPERTIES_HEADER not in tags:
            self.treeRangePicker.delete(*self.treeRangePicker.get_children())
            self.treeEntityPicker.delete(*self.treeEntityPicker.get_children())
            if c.TREE_TAG_INSTANCE in tags:
                # Auto-expand branches of domain and range of selected property
                propertyTriple = self.propertiesByTreeID[rowID]
                self.selectedEntities = [propertyTriple[c.SUBJECT_INDEX]]
                if c.TREE_TAG_OBJECT_PROPERTY in tags:
                    # Auto select range only for object properties
                    self.selectedRange = [propertyTriple[c.OBJECT_INDEX]]
                else:
                    self.selectedRange = []
                # Fetch property name from tags
                for tag in tags:
                    if tag not in c.TREE_TAGS:
                        selectedProperty = tag
                        break

            if selectedProperty in self.rangesByProperty:
                rangeEntities = self.rangesByProperty[selectedProperty]
            else:
                rangeEntities = None
            if selectedProperty in self.domainsByProperty:
                domainEntities = self.domainsByProperty[selectedProperty]
            else:
                domainEntities = None

            self.populatePropertyTree(self.treeEntityPicker, domainEntities,
                                      selectPrevious="subject")
            if c.TREE_TAG_DATATYPE_PROPERTY in tags:
                self.treeRangePicker.delete(*self.treeRangePicker.get_children())
            else:
                self.populatePropertyTree(self.treeRangePicker, rangeEntities,
                                          selectPrevious="object")

    def propertySelect(self, event):
        """ Take note of selected properties. """
        selectedPropertyIDs = self.treePropertyPicker.selection()
        self.selectedProperties = [self.treePropertyPicker.item(rowID, "text")
                                   for rowID in selectedPropertyIDs]

    def populatePropertyTree(self, treeViewInstance, entityList,
                             selectPrevious="none"):
        """ Populate an Entity & Individuals TreeView according to the range
            or domain of a property (passed as a list of entities).
            For each entity of the list, its children (entities or individuals)
            are added to the TreeView.
        :param treeViewInstance: View of the tree.
        :param entityList: List of entities.
        :param selectPrevious: This should be "object", "subject" or "none".
        """

        subtrees = []
        if entityList:
            for entity in entityList:
                subtree = self.getSubTreeFromEntity(entity, self.ontologyTree)
                if subtree:
                    subtrees.append(subtree)
        if subtrees:
            for tree in subtrees:
                self.stack = ['']
                self.subTreeFromFileRecursive(tree, treeViewInstance,
                                              selectPrevious)
        else:
            self.stack = ['']
            self.subTreeFromFileRecursive(self.ontologyTree, treeViewInstance,
                                          selectPrevious)

    def getSubTreeFromEntity(self, entity, entityTree):
        """ Returns a subTree with the given entity as the root.
        :param entity: Searched entity for a root of a tree.
        :param entityTree: Tree structure that should be searched.
        :return: subtree with the entity as a root.
        """

        nodeQueue = entityTree[:]
        while nodeQueue:
            element = nodeQueue.pop(0)
            if isinstance(element[0], basestring):
                if element[0] == entity:
                    return element
            iternodes = iter(element)
            next(iternodes)
            for n in iternodes:
                nodeQueue.append(n)
        return []

    def prepareSelectedEntities(self, allowOnlyInstances=False):
        """ Initializes the selectedEntities and selectedRange properties
            (Entities and/or Instances)  according to the user's selection on
            the treeView.
        :param allowOnlyInstances: 'True' if only instances should be added.
        return: 'True' if preparation process finishes correctly,
            'False' otherwise.
        """

        selectedSubjectIDs = self.treeEntityPicker.selection()
        selectedEntities = []
        correct = True
        for s in selectedSubjectIDs:
            text = self.treeEntityPicker.item(s, "text")
            tags = self.treeEntityPicker.item(s, "tags")
            # Select all children of "Instances" group
            if c.TREE_TAG_INSTANCES_HEADER in tags:
                for child in self.treeEntityPicker.get_children(s):
                    text = self.treeEntityPicker.item(child, "text")
                    selectedEntities.append(text)
            else:
                if allowOnlyInstances and c.TREE_TAG_ENTITY in tags:
                    tkMessageBox.showwarning(c.SELECT, c.SELECT_INST)
                    correct = False
                elif text not in selectedEntities:
                    selectedEntities.append(text)
        self.selectedEntities = selectedEntities
        selectedObjectIDs = self.treeRangePicker.selection()
        selectedRange = []
        for o in selectedObjectIDs:
            text = self.treeRangePicker.item(o, "text")
            tags = self.treeRangePicker.item(o, "tags")
            # Select all children of "Instances" group
            if c.TREE_TAG_INSTANCES_HEADER in tags:
                for child in self.treeRangePicker.get_children(o):
                    text = self.treeRangePicker.item(child, "text")
                    selectedRange.append(text)
            else:
                if allowOnlyInstances and c.TREE_TAG_ENTITY in tags:
                    tkMessageBox.showwarning(c.SELECT, c.SELECT_INST)
                    correct = False
                elif text not in selectedRange:
                    selectedRange.append(text)
        self.selectedRange = selectedRange
        return correct

    def saveOntology(self, *args):
        """ This method saves the ontology. It takes data from JSON and
            stores it in the rdf file.
        """

        if not self.instancesbyClass:
            tkMessageBox.showwarning(c.SAVE, c.SAVE_NOT_LOADED)
            return

        if tkMessageBox.askyesno(c.SAVE, c.SAVE_TO_ORIGINAL):
            fileName = self.fileName
        else:
            fileName = tkFileDialog.askopenfilename(**self.file_opt)

        if fileName:
            self.readerOperation(fileName, self.namespace, serialize=False,
                                 save=True)

            filePath = os.path.join(os.path.expanduser("~"), c.JSON_FILENAME)
            if os.path.exists(filePath):
                os.remove(filePath)
            self.closeGUI(isInstanceListChanged=False)
        else:
            tkMessageBox.showwarning(c.SAVE, c.SAVE_NOT_CHOSEN)

    def loadOntology(self, *args):
        """ Ask user to choose rdf file. Then load the ontology onto GUI
            and serialize it to a temp file.
        """

        if self.ontologyTree and tkMessageBox.askyesno(c.LOAD, c.LOAD_SAVING):
            self.saveOntology()
            tkMessageBox.showwarning(c.LOAD, c.LOAD_CHOOSING)

        self.resetVariables()
        filePath = os.path.join(os.path.expanduser("~"), c.JSON_FILENAME)
        if os.path.exists(filePath):
            os.remove(filePath)

        namespace = None
        fileName = tkFileDialog.askopenfilename(**self.file_opt)

        if fileName:
            self.fileName = fileName
            candidateSet = self.getCandidateSetOfPrefixes(fileName)
            namespace = self.resolveNamespace(candidateSet)
            if not namespace:
                # User cancels the process or enter empty namespace
                return
            self.namespace = namespace

            self.readerOperation(fileName, namespace, serialize=True,
                                 save=False)

            # Detect if the ontology is not loaded properly
            if self.ontologyTree == [c.RDF_ROOT_NAME]:
                tkMessageBox.showwarning(c.LOAD, c.LOAD_NO_TREE)

    def readerOperation(self, fileName, namespace, serialize=True, save=False):
        """ Function created instance of a reader class and loads the data
            into appropriate variables or saves them into rdf file.
        :param fileName: Original fileName of .rdf file.
        :param namespace: Namespace of the original .rdf file.
        :param serialize: If it is 'True' than loaded data are saved into JSON
        :param save: If it is 'True' than data from JSON
            are stored into .rdf file
        """

        try:
            reader = RDFReader(fileName, namespace)
            if save:
                self.addDefaultProperties(reader)
            self.treeEntityPicker.delete(*self.treeEntityPicker.get_children())
            self.treePropertyPicker.delete(*self.treePropertyPicker.get_children())
            self.treeRangePicker.delete(*self.treeRangePicker.get_children())
            self.ontologyTree = reader.generateSubTree(c.RDF_ROOT_NAME,
                                                       self.treeEntityPicker)
            self.instancesbyClass = reader.instancesbyClass
            self.initializeTriples(reader, "object")
            self.initializeTriples(reader, "datatype")
            self.domainsByProperty = reader.domainsByProperty
            self.rangesByProperty = reader.rangesByProperty
            self.treeConfiguration(self.treeEntityPicker)
            self.treeConfiguration(self.treeRangePicker)
            self.initializePropertyTree(self.treePropertyPicker)
            self.lastId = reader.getLastId()
            if serialize:
                self.serialize()
            if save:
                self.savingOperations(reader)
        except IOError as e:
            tkMessageBox.showwarning(c.FILE, c.FILE_ERROR % e.strerror)
            self.closeGUI()

    def initializeTriples(self, reader, type):
        """ Initialize instances of properties. Allowed types:
            object, datatype.
        :param reader: Reader instance with data.
        :param type: Type of the data.
        """

        if type == "object":
            properties = reader.objectProperties
        else:
            # type == "datatype":
            properties = reader.dataTypeProperties

        for property in properties:
            triples = reader.getPropertyInstances(property)
            if type == "object":
                self.objectProperties[property] = []
            else:
                self.dataTypeProperties[property] = []
            for s, p, o in triples:
                subject = s.split('#')[1]
                obj = o.split('#')
                # Some objects (e.g. SVG paths) have no NS
                obj = obj[1 if len(obj) > 1 else 0]
                if type == "object":
                    # Cast to lists so they can be serialized
                    self.objectProperties[property].append([subject, property,
                                                            obj])
                else:
                    self.dataTypeProperties[property].append([subject,
                                                              property, obj])

    def savingOperations(self, reader):
        """ Method performs the operations for correct saving of data into
            .rdf file.
        :param reader: Instance of the reader class.
        """

        self.loadSerializedInstances()
        # Check all 'remove' operations performed; maybe elements need
        # to be removed from the ontology

        self.loadSerializedInstances()
        for operation in self.undoStack:
            for atomicAction in operation:
                if atomicAction["type"] == "remove":
                    instance = atomicAction["instanceId"]
                    entity = atomicAction["entityName"]
                    if entity not in self.instancesbyClass or instance not in \
                            self.instancesbyClass[entity]:
                        # Whole annotation removed; check if exists in ontology
                        # and if so, delete it
                        if reader.hasInstance(entity, instance):
                            reader.removeInstance(instance)
                    else:
                        svgElements = atomicAction["SVGElements"]
                        for svgElement in svgElements:
                            if reader.hasSVGElement(instance, svgElement):
                                reader.removeSVGElementProperty(instance,
                                                                svgElement)

        for entity, annotations in self.instancesbyClass.iteritems():
            if reader.hasEntity(entity):  # Ensure entity belongs to ontology
                for annotation, svgElements in annotations.iteritems():
                    if not reader.hasInstance(entity, annotation):
                        reader.addInstance(entity, annotation)

                    svg = SVGParser(self.aEffect.document.getroot())
                    cPnt = svg.countCentralPointForListOfElements(svgElements)
                    if cPnt is not None:
                        reader.addCoordinatesXY(annotation, cPnt[0], cPnt[1])

                    for svgElement in svgElements:
                        reader.addSVGElementProperty(annotation, svgElement)

        for triple in self.objectPropertiesToRemove:
            reader.removeObjectProperty(triple[c.SUBJECT_INDEX],
                                        triple[c.PROPERTY_INDEX],
                                        triple[c.OBJECT_INDEX])
        for triple in self.objectPropertiesToAdd:
            reader.addObjectProperty(triple[c.SUBJECT_INDEX],
                                     triple[c.PROPERTY_INDEX],
                                     triple[c.OBJECT_INDEX])

        for triple in self.dataTypePropertiesToRemove:
            reader.removeDatatypeProperty(triple[c.SUBJECT_INDEX],
                                          triple[c.PROPERTY_INDEX],
                                          triple[c.OBJECT_INDEX])
        for triple in self.dataTypePropertiesToAdd:
            reader.addDatatypeProperty(triple[c.SUBJECT_INDEX],
                                       triple[c.PROPERTY_INDEX],
                                       triple[c.OBJECT_INDEX])

        reader.saveOntology()

    def getCandidateSetOfPrefixes(self, fileName):
        """ This method tries to find the correct prefix of ontology directly
            from .rdf file.
        :param fileName: Name of the file to be searched.
        :return: Candidate set of prefixes that are used in ontology without
            common ones.
        """

        tree = etree.parse(fileName)
        root = tree.getroot()
        setOfPrefixes = set()

        for name in root.nsmap:
            setOfPrefixes.add(self.removeLastHTag(root.nsmap[name]))

        # namespace generated by the Protege
        inkex.NSS['owl'] = c.OWL_PREFIX
        ontNS = root.xpath(".//owl:Ontology", namespaces=inkex.NSS)
        if ontNS is not None and len(ontNS) > 0 and ontNS[0] is not None:
            if c.RDF_NS_ATTRIBUTE in ontNS[0].attrib:
                cand = self.removeLastHTag(ontNS[0].attrib[c.RDF_NS_ATTRIBUTE])
                setOfPrefixes.add(cand)

        return setOfPrefixes - c.COMMON_PREFIXES

    def resolveNamespace(self, candidateNSSet):
        """ Method allows to resolve the selection of namespaces. It solves
            the cases when nothing is is found, one is found or multiple
            namespaces exists.
        :param candidateNSSet: Candidate set of namespaces.
        :return: Final name of the namespace.
        """

        if len(candidateNSSet) == 0:
            fName = tkSimpleDialog.askstring(c.NSNAME, c.NSNAME_NO_NS)
            if fName is not None and not fName:
                tkMessageBox.showwarning(c.NSNAME, c.NSNAME_NOT_ADDED)
                fName = c.DEFAULT_NS
        elif len(candidateNSSet) == 1:
            el = next(iter(candidateNSSet))
            if tkMessageBox.askokcancel(c.NSNAME, c.NSNAME_DETECTED % el):
                fName = el
            else:
                fName = tkSimpleDialog.askstring(c.NSNAME, c.NSNAME_ENTER)
                if fName is not None and not fName:
                    tkMessageBox.showwarning(c.NSNAME, c.NSNAME_NOT_ADDED)
                    fName = c.DEFAULT_NS
        else:
            description = "\n".join(candidateNSSet)
            el = next(iter(candidateNSSet))

            fName = tkSimpleDialog.askstring(c.NSNAME,
                                             c.NSNAME_MULTIPLE % description,
                                             initialvalue=el)
        return fName

    def removeLastHTag(self, str):
        """ Removes the last hashtag form the string.
        :param str: String to be changed.
        :return: String without the last hashtag.
        """

        if str.endswith("#"):
            return str[:-1]
        return str

    def treeConfiguration(self, treeInstance):
        """ Method configures the tree and set colors for different type of
            entities and instances in the tree.
        :param treeInstance: instance of the tree.
        """

        treeInstance.tag_configure(c.TREE_TAG_ENTITY, background="white")
        treeInstance.tag_configure(c.TREE_TAG_INSTANCE, background="grey")
        treeInstance.tag_configure(c.TREE_TAG_HIGHLIGHT, background="yellow")

    def subTreeFromFileRecursive(self, treeList, treeViewInstance,
                                 selectPrevious="none"):
        """ Method creates tree from the treeList.
        :param treeList: List with data from whom the tree is generated.
        :param treeViewInstance:
        :param selectPrevious: This should be "object", "subject" or "none".
        """

        if selectPrevious != "none":
            selected = self.previousSelectedEntities(selectPrevious)
        for i in iter(treeList):
            if isinstance(i, basestring):
                parentID = self.stack[-1]
                # Insert element into GUI ViewTree
                childID = treeViewInstance.insert(parentID, 'end', text=i,
                                                  tags=(c.TREE_TAG_ENTITY,))
                if selectPrevious != "none" and i in selected:
                    self.expandBranches(treeViewInstance, childID)
                # Insert instances of current Entity
                if i in self.instancesbyClass:
                    self.insertInstancesInTree(self.instancesbyClass[i],
                                               treeViewInstance, childID,
                                               selectPrevious)
                self.stack.append(childID)
            else:
                self.subTreeFromFileRecursive(i, treeViewInstance,
                                              selectPrevious)
        if self.stack:
            self.stack.pop()

    def expandBranches(self, treeViewInstance, rowID):
        """ Expand all branches from the root to the given one.
        :param treeViewInstance: View of the tree.
        :param rowID: Id of the searched row.
        """

        treeViewInstance.item(rowID, open=True)
        tempStack = self.stack[:]  # Slice clone
        while tempStack:
            treeViewInstance.item(tempStack.pop(), open=True)
        self.setFocus(treeViewInstance, rowID)

    def insertInstancesInTree(self, instanceList, treeViewInstance, parentID,
                              selectPrevious="none"):
        """ Insert instances from instanceList into treeView.
        :param instanceList: List of instances.
        :param treeViewInstance: View of the tree.
        :param parentID: Id of the parent in the tree view.
        :param selectPrevious: This should be "object", "subject" or "none".
        """

        localParentID = parentID
        # Only in case that there is a lot of instances
        if len(instanceList) > c.MAX_INSTANCES_IN_DIR:
            localParentID = \
                treeViewInstance.insert(parentID, 'end', text=c.INSTANCES_NAME,
                                        tags=(c.TREE_TAG_INSTANCE,
                                              c.TREE_TAG_INSTANCES_HEADER, ))

        for instance in sorted(instanceList.keys()):
            if set(self.aEffect.selected).intersection(instanceList[instance]):
                tag = c.TREE_TAG_HIGHLIGHT
            else:
                tag = c.TREE_TAG_INSTANCE

            rowID = treeViewInstance.insert(localParentID, 'end',
                                            text=instance, tags=(tag,))
            # Expand all branches to instance if it was previously selected
            if selectPrevious != 'none' and instance in \
                    self.previousSelectedEntities(selectPrevious):
                self.expandBranches(treeViewInstance, localParentID)
                # If instances are grouped, expand "Instances" header
                if parentID != localParentID:
                    treeViewInstance.item(parentID, open=True)
                self.setFocus(treeViewInstance, rowID)

    def initializePropertyTree(self, treeViewInstance):
        """ Method initializes tree of properties.
        :param treeViewInstance: View of the tree.
        """
        if self.objectProperties:
            oID = treeViewInstance.insert('', 'end', text='Object Properties',
                                          tags=(c.TREE_TAG_PROPERTIES_HEADER,))
        if self.dataTypeProperties:
            dID = treeViewInstance.insert('', 'end', text='Datatype Properties',
                                          tags=(c.TREE_TAG_PROPERTIES_HEADER,))
        self.addPropertiesToTreeView(treeViewInstance, self.objectProperties,
                                     oID, type=c.TREE_TAG_OBJECT_PROPERTY)
        self.addPropertiesToTreeView(treeViewInstance, self.dataTypeProperties,
                                     dID, type=c.TREE_TAG_DATATYPE_PROPERTY)

    def addPropertiesToTreeView(self, treeViewInstance, props, headerID, type):
        """ Insert properties from the instanceList into treeView.
        :param treeViewInstance: View of the tree.
        :param props: Properties to be added.
        :param headerID: Id of the header for adding properties.
        :param type: Type of the property.
        """
        selected = self.previousSelectedProperties()
        for property in props:
            textAdd = property
            parID = treeViewInstance.insert(headerID, 'end', text=textAdd,
                                            tags=(c.TREE_TAG_PROPERTY, type))
            triples = props[property]
            if selected and textAdd in selected:
                self.expandPropertyBranches(treeViewInstance, [headerID],
                                            parID)
            for triple in triples:
                textAdd = "%s -> %s" % (triple[c.SUBJECT_INDEX],
                                        triple[c.OBJECT_INDEX])
                childID = treeViewInstance.insert(parID, 'end', text=textAdd,
                                                  tags=(c.TREE_TAG_INSTANCE,
                                                        type, property))
                self.propertiesByTreeID[childID] = [triple[c.SUBJECT_INDEX],
                                                    property,
                                                    triple[c.OBJECT_INDEX]]
                if selected and textAdd in selected:
                    self.expandPropertyBranches(treeViewInstance,
                                                [headerID, parID], childID)

    def expandPropertyBranches(self, treeViewInstance, ancestorIDs, childID):
        """ Method for expanding branches in the property tree view.
        :param treeViewInstance: View of the tree.
        :param ancestorIDs: ID of the ancestor.
        :param childID: ID of the child.
        """

        for id in ancestorIDs:
            treeViewInstance.item(id, open=True)
        treeViewInstance.item(childID, open=True)
        self.setFocus(treeViewInstance, childID)

    def setFocus(self, treeViewInstance, rowID):
        """ Method for expanding setting focus on specific in the property
            row in the tree view.
        :param treeViewInstance: View of the tree.
        :param rowID: ID of the row that should be focused.
        """

        treeViewInstance.focus(rowID)
        treeViewInstance.selection_set(rowID)
        treeViewInstance.focus_set()

    def refreshPropertyTree(self, treeViewInstance):
        """ Reload all properties and feed the given TreeView with them.
        :param treeViewInstance: View of the tree.
        """

        treeViewInstance.delete(*treeViewInstance.get_children())
        if self.objectProperties or self.dataTypeProperties:
            self.initializePropertyTree(treeViewInstance)
        else:
            tkMessageBox.showwarning(c.PROP, c.PROP_NOTHING_FOUND)

    def loadSerializedOntology(self, treeViewInstance):
        """ Tries to load a serialized ontology and other relevant data
            from a json file.
        :param treeViewInstance: View of the tree.
        """

        filePath = os.path.join(os.path.expanduser("~"), "viso.json")
        if os.path.exists(filePath):
            with open(filePath, 'r') as f:
                try:
                    self.tempData = json.load(f)
                    self.ontologyTree = self.tempData["classHierarchy"]
                    self.stack = ['']
                    self.instancesbyClass = self.tempData["instances"]
                    self.defaultName = self.tempData["defaultName"]
                    self.defaultTypeValue = self.tempData["defaultValue"]
                    self.defaultTypeValue = self.tempData["defaultValue"]
                    self.fileName = self.tempData["fileName"]
                    self.namespace = self.tempData["namespace"]
                    self.lastId = self.tempData["lastId"]
                    self.undoStack = self.tempData["undoStack"]
                    self.subTreeFromFileRecursive(self.ontologyTree,
                                                  treeViewInstance,
                                                  selectPrevious="subject")
                    self.treeConfiguration(self.treeEntityPicker)
                    self.treeConfiguration(self.treeRangePicker)
                    self.objectProperties = self.tempData["objectProperties"]
                    self.dataTypeProperties = \
                        self.tempData["dataTypeProperties"]
                    self.domainsByProperty = self.tempData["domains"]
                    self.rangesByProperty = self.tempData["ranges"]
                    self.objectPropertiesToAdd = \
                        self.tempData["propertyTriples"]
                    self.objectPropertiesToRemove = \
                        self.tempData["propertyTriplesToRemove"]
                    self.dataTypePropertiesToAdd = \
                        self.tempData["dataTypePropertyTriples"]
                    self.dataTypePropertiesToRemove = \
                        self.tempData["dataTypePropertyTriplesToRemove"]
                    self.initializePropertyTree(self.treePropertyPicker)
                except ValueError:
                    self.ontologyTree = None
                finally:
                    self.stack = None
                    f.close()

    def loadSerializedInstances(self):
        """ Load the current instance information (intancesByClass,
            domains, ranges) from the JSON file.
        """

        filePath = os.path.join(os.path.expanduser("~"), "viso.json")
        if os.path.exists(filePath):
            with open(filePath, 'r') as f:
                try:
                    self.tempData = json.load(f)
                    self.instancesbyClass = self.tempData["instances"]
                    self.domainsByProperty = self.tempData["domains"]
                    self.rangesByProperty = self.tempData["ranges"]
                    self.objectProperties = self.tempData["objectProperties"]
                    self.dataTypeProperties = \
                        self.tempData["dataTypeProperties"]
                    self.objectPropertiesToAdd = \
                        self.tempData["propertyTriples"]
                    self.dataTypePropertiesToAdd = \
                        self.tempData["dataTypePropertyTriples"]
                    self.dataTypePropertiesToRemove = \
                        self.tempData["dataTypePropertyTriplesToRemove"]
                    self.objectPropertiesToRemove = \
                        self.tempData["propertyTriplesToRemove"]
                    self.namespace = self.tempData["namespace"]
                except ValueError as e:
                    tkMessageBox.showwarning(c.FILE,
                                             c.FILE_SER_ERROR % e.strerror)
                finally:
                    f.close()

    def previousSelectedEntities(self, type="subject"):
        """ Returns the selected Entities/Instances previously selected
            by the user on the last time the GUI was closed.
        :param type: This should be "object", "subject" or "none".
        """

        if type == "subject":
            if self.selectedEntities:
                selected = self.selectedEntities
            elif "selectedEntities" in self.tempData:
                selected = self.tempData["selectedEntities"]
            else:
                selected = []
        elif type == "object":
            if self.selectedRange:
                selected = self.selectedRange
            elif "selectedRanges" in self.tempData:
                selected = self.tempData["selectedRanges"]
            else:
                selected = []
        else:
            selected = []
        return selected

    def previousSelectedProperties(self):
        """ Returns the last properties selected by the user. """
        if self.selectedProperties:
            selected = self.selectedProperties
        elif "selectedProperties" in self.tempData:
            selected = self.tempData["selectedProperties"]
        else:
            selected = []
        return selected

    def instanceExists(self, instance):
        """ Checks if instance exist.
        :param instance: Instance to be checked.
        :return: 'True' if instance already exist, 'False' otherwise.
        """

        for entity in self.instancesbyClass:
            if instance in self.instancesbyClass[entity]:
                return True
        return False

    def addDefaultProperties(self, reader):
        """ Check if the ontology has the required properties.
            If not, add them and inform the user.
        :param reader: Instance of the RDFReader class that allows to store
            properties into .rdf file.
        """

        default_properties = [c.HAS_SVG_PROPERTY, c.COOR_PROPERTY,
                              c.X_COOR_PROPERTY, c.Y_COOR_PROPERTY]
        added = []
        for property in default_properties:
            if not reader.hasProperty(property, "datatype"):
                added.append(property)
                reader.addProperty(property, "datatype")
        if added:
            tkMessageBox.showwarning(c.PROP,
                                     c.PROP_DATA_NOT_FOUND % ', '.join(added))
            reader.saveOntology()

    def close(self, event):
        self.closeGUI(isInstanceListChanged=True)

    def closeGUI(self, isInstanceListChanged):
        """ Closes the gui.
        :param isInstanceListChanged: True if something was changed and
            serialization should be done.
        """

        if isInstanceListChanged:
            self.serialize()

        self.root.destroy()

    def serialize(self):
        """ Serialize Ontology into JSON file in the user's home folder. """
        serializedInfo = {}
        if self.ontologyTree:
            serializedInfo["classHierarchy"] = self.ontologyTree
        else:
            tkMessageBox.showwarning(c.FILE, c.FILE_JSON_ERROR)
        serializedInfo["fileName"] = self.fileName
        serializedInfo["namespace"] = self.namespace
        serializedInfo["instances"] = self.instancesbyClass
        serializedInfo["objectProperties"] = self.objectProperties
        serializedInfo["dataTypeProperties"] = self.dataTypeProperties
        serializedInfo["ranges"] = self.rangesByProperty
        serializedInfo["domains"] = self.domainsByProperty
        serializedInfo["lastId"] = self.lastId
        serializedInfo["undoStack"] = self.undoStack
        serializedInfo["selectedEntities"] = [] if not self.selectedEntities \
            else self.selectedEntities
        serializedInfo["selectedRanges"] = [] if not self.selectedRange \
            else self.selectedRange
        serializedInfo["selectedProperties"] = [] if not self.selectedProperties \
            else self.selectedProperties
        serializedInfo["propertyTriples"] = self.objectPropertiesToAdd
        serializedInfo["propertyTriplesToRemove"] = \
            self.objectPropertiesToRemove
        serializedInfo["dataTypePropertyTriples"] = \
            self.dataTypePropertiesToAdd
        serializedInfo["dataTypePropertyTriplesToRemove"] = \
            self.dataTypePropertiesToRemove
        serializedInfo["defaultName"] = self.defaultName
        serializedInfo["defaultValue"] = self.defaultTypeValue
        serializedInfo["defaultValue"] = self.defaultTypeValue
        serialized = json.dumps(serializedInfo)
        filePath = os.path.join(os.path.expanduser("~"), c.JSON_FILENAME)
        try:
            f = open(filePath, 'w+')
            f.write(serialized)
        except IOError as e:
            tkMessageBox.showwarning(c.FILE, c.FILE_JSON_FOLDER)
            raise e
        finally:
            f.close()
