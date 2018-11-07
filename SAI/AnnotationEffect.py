"""
AnnotationEffect class processes the SVG elements and annotation(s) selected
by the user. It allows to add, remove and replace annotations and also offers
undo function.

Created on Apr 27, 2016
@author: Tomas Murillo-Morales, Jaromir Plhak
"""

import inkex
from gui import PickerGUI
from Tkinter import Tk
import tkMessageBox
import tkSimpleDialog
import re
import const as c


class AnnotationEffect(inkex.Effect):
    """
    AnnotationEffect class processes the SVG elements and annotation(s)
        selected by the user. It allows to add, remove, replace and undo
        annotations. It works with the data in the temporary JSON file.
    """

    def __init__(self):
        inkex.Effect.__init__(self)
        self.gui = None

    def numSelectedItems(self):
        """ Method returns the number of selected elements
        :return: Number of selected elements
        """

        return len(self.selected)

    def effect(self):
        """ Method prepares the TkInter GUI """
        root = Tk()
        self.gui = PickerGUI(root, self)
        self.gui.prepare(root)
        root.mainloop()

    def addAnnotation(self, separateAdd):
        """ This method allows to create annotation in the JSON file
        :param separateAdd: It is 'True', if the separate annotation should be
            created for every SVG element.
        :return: 'True', if GUI should be closes, 'False' otherwise.
        """

        if self.numSelectedItems() < 1:
            tkMessageBox.showwarning(c.ADD, c.ADD_NO_OBJECT)
            return True

        if len(self.gui.selectedEntities) < 1:
            tkMessageBox.showwarning(c.ADD, c.ADD_NO_ENTITY)
            return False

        tmpAnnot = self.getTempAnnotations()
        if len(tmpAnnot) == len(self.gui.selectedEntities):
            # This is the case when only annotations were selected
            if not separateAdd:
                self.addElementsIntoAnnotation(tmpAnnot, None, fromUndo=False)
                return True
            else:
                tkMessageBox.showwarning(c.ADD, c.ADD_SEPARATE_ERROR)
                return False
        elif len(tmpAnnot) == 0:
            # This is the case when only entities were selected
            rValue = self.addSeparateAnnotationForEntities() if separateAdd \
                else self.addAnnotationForEntities()
            return rValue
        else:
            tkMessageBox.showwarning(c.ADD, c.ADD_ENTITY_AND_ANNOT)
            return False

        return True

    def getTempAnnotations(self):
        """ Takes all selected annotations and returns them as a list.
        :return: List of all annotations.
        """
        temp = []
        for entity, instances in self.gui.instancesbyClass.iteritems():
            for instance in instances:
                if instance in self.gui.selectedEntities:
                    temp.append((entity, instance))
        return temp

    def addElementsIntoAnnotation(self, tempAnnot, undoDataDict, fromUndo):
        """ Add new SVG elements into chosen annotation. If elements are
            already in annotation than nothing happens. Changes are stored in
            undoStack to be available for undo function. If fromUndo is True
            than this function only reverts changes given in undoDataDict
            and does not save changes into undoStack.
        :param tempAnnot: Prepared list of annotations.
        :param undoDataDict: Dictionary with the data that should be undone.
        :param fromUndo: Is 'True' if this function is call as an undo
            function. 'False' otherwise.
        :return: 'True', if GUI should be closes, 'False' otherwise.
        """

        added = False
        undoList = []
        selected = undoDataDict["SVGElements"] if fromUndo else self.selected

        for (entity, instance) in tempAnnot:
            undoElems = []
            if instance not in self.gui.instancesbyClass[entity]:
                self.gui.instancesbyClass[entity][instance] = []

            for element in selected:
                if element not in self.gui.instancesbyClass[entity][instance]:
                    self.gui.instancesbyClass[entity][instance].append(element)
                    triple = [instance, c.HAS_SVG_PROPERTY, element]
                    self.addPropertyTriple(triple, c.DATATYPE_PROP, undoList)
                    undoElems.append(element)
                    added = True
            undoList.append({"type": "add", "instanceId": instance,
                             "entityName": entity, "SVGElements": undoElems})

        if not added and not fromUndo:
            tkMessageBox.showwarning(c.ADD, c.ADD_NO_SVG)

        if not fromUndo:
            self.gui.undoStack.append(undoList)
        return True

    def addAnnotationForEntities(self):
        """ Create annotations for given entities. Changes are stored in
            undoStack to be available for undo function.
        :return: 'True', if GUI should be closes, 'False' otherwise.
        """

        outputList = []
        undoList = []  # undo function
        for element in self.selected:
            outputList.append(element)

        for tagName in self.gui.selectedEntities:
            finalName = ""
            while finalName == "":
                finalName = \
                    tkSimpleDialog.askstring(c.ANN_NAME,
                                             c.ANN_NAME_ENTER % tagName,
                                             initialvalue=self.gui.defaultName)
                # User clicks cancel
                if not finalName:
                    return False
                if tagName in self.gui.instancesbyClass and\
                        self.gui.instanceExists(finalName):
                    finalName = ""
                    tkMessageBox.showwarning(c.ANN_NAME,
                                             c.ANN_NAME_DUPLICATED)

            if tagName not in self.gui.instancesbyClass:
                self.gui.instancesbyClass[tagName] = {}

            self.gui.lastId += 1
            self.gui.defaultName = finalName
            self.gui.instancesbyClass[tagName][finalName] = {}
            self.gui.instancesbyClass[tagName][finalName] = outputList
            undoList.append({"type": "add", "instanceId": finalName,
                             "entityName": tagName, "SVGElements": outputList})
            for element in outputList:
                triple = [finalName, c.HAS_SVG_PROPERTY, element]
                self.addPropertyTriple(triple, c.DATATYPE_PROP)

        self.gui.undoStack.append(undoList)
        return True

    def addSeparateAnnotationForEntities(self):
        """ Create separate annotations for given entities.
            One SVG element means one annotation.
        :return: 'True', if GUI should be closed, 'False' otherwise.
        """

        undoList = []  # undo function
        for tagName in self.gui.selectedEntities:
            for element in self.selected:
                if tagName not in self.gui.instancesbyClass:
                    self.gui.instancesbyClass[tagName] = {}

                self.gui.lastId += 1
                annotationName = self.getAnnotationName(element)
                finalName = annotationName + str(self.gui.lastId)
                if self.gui.lastId not in self.gui.instancesbyClass[tagName]:
                    self.gui.instancesbyClass[tagName][finalName] = {}

                self.gui.instancesbyClass[tagName][finalName] = [element]
                undoList.append({"type": "add", "instanceId": finalName,
                                 "entityName": tagName,
                                 "SVGElements": [element]})
                triple = [finalName, c.HAS_SVG_PROPERTY, element]
                self.addPropertyTriple(triple, c.DATATYPE_PROP, undoList)
        self.gui.undoStack.append(undoList)
        return True

    def getAnnotationName(self, tagId):
        """ Automatically generates the name for annotation. It is based
            on SVG element tag and its id.
        :param tagId: id of the SVG element that should be named.
        :return: Name of the element.
        """

        groupElementList = self.document.xpath("//*[@id = '" + tagId + "']",
                                               namespaces=inkex.NSS)
        if groupElementList[0] is not None:
            tag = self.removeSVGPrefix(groupElementList[0].tag)
            if tag in c.SVG_NAMED_ELEMENTS:
                if tag == "text":
                    return self.resolveText(groupElementList[0])
                if tag == "path":
                    return self.resolvePath(groupElementList[0].attrib)
                else:
                    return tag

        return c.ANNOTATION_NAME

    def removeSVGPrefix(self, tagName):
        """ Parses the text and removes SVG prefix.
        :return: Text without SVG prefix.
        """

        if c.SVG_NS in tagName:
            return tagName[len(c.SVG_NS) + 2:]
        return tagName

    def resolveText(self, element):
        """ Resolves the text elements. It named the element according the
            text in text element that is shortened to given length.
        :param element: Text SVG element to be named.
        :return: name of the text SVG element.
        """

        output = "text"
        add = ""

        # Inkscape specific text
        subelemList = element.xpath(".//svg:tspan", namespaces=inkex.NSS)
        if subelemList and subelemList[0] is not None:
            add = subelemList[0].text
        # Text directly in element
        elif element.text is not None and len(element.text) > 0:
            add = element.text

        add = re.sub(r'\W+', '_', add)[:c.MAX_TEXT_LENGTH]
        if len(add) > 0:
            output = output + "_" + add + "_"
        return output

    def resolvePath(self, attributes):
        """ Resolves the elements created in Inkscape
            (hardcoded for version 0.91). It is needed because Inscape saves
            the polygone, circles and other shapes as paths.

        :param attributes: Dictionary of attibutes for given SVG elements.
        :return: The name of the path element.
        """

        if "r" in attributes or "{" + c.SODI_NS + "}r" in attributes:
            return "circle"

        if "cx" in attributes or "{" + c.SODI_NS + "}cx" in attributes:
            return "ellipse"
        if "d" in attributes and "m " in attributes["d"]:
            if " z" in attributes["d"]:
                return "polygon"
            if attributes["d"].count(" ") < 5:
                return "line"
        if "{" + c.SODI_NS + "}type" in attributes and \
                attributes["{" + c.SODI_NS + "}type"] == "star":
            return "polygon"

        return "path"

    def replaceAnnotation(self):
        """ This function resolves the replacement of SVG elements in the
            annotation. Changes are stored in undoStack to be available for
            undo function.
        :return: 'True', if GUI should be closes, 'False' otherwise.
        """

        if self.numSelectedItems() < 1:
            tkMessageBox.showwarning(c.REPLACE, c.REPLACE_NO_SVG)
            return True

        if len(self.gui.selectedEntities) < 1:
            tkMessageBox.showwarning(c.REPLACE, c.REPLACE_NO_ANNOT)
            return False

        tempInstance = self.getTempAnnotations()
        if len(tempInstance) < len(self.gui.selectedEntities):
            tkMessageBox.showwarning(c.REPLACE, c.REPLACE_ENT_ANOT_MIX)
            return False

        # Test if selected svg elements are the same as the original one
        selSVGElements = []
        same = 0
        changed = 0
        sameList = []
        for element in self.selected:
            selSVGElements.append(element)

        for (entity, instance) in tempInstance:
            origSVGElements = self.gui.instancesbyClass[entity][instance]
            if origSVGElements == selSVGElements:
                same += 1
                sameList.append(instance)
            else:
                changed += 1

        if same > 0:
            if changed == 0:
                tkMessageBox.showwarning(c.REPLACE, c.REPLACE_ALL_SAME)
                return False
            tkMessageBox.showwarning(c.REPLACE,
                                     c.REPLACE_SOME_SAME % ", ".join(sameList))

        cont = False
        if changed > 1:
            cont = tkMessageBox.askokcancel(c.REPLACE, c.REPLACE_MORE_ANN)
        else:
            cont = True

        undoList = []  # Undo function
        if cont:
            for (entity, instance) in tempInstance:
                tmpSVGElem = self.gui.instancesbyClass[entity][instance]
                if tmpSVGElem != selSVGElements:
                    undoList.append({"type": "remove", "instanceId": instance,
                                     "entityName": entity,
                                     "SVGElements": tmpSVGElem})
                    self.gui.instancesbyClass[entity][instance] = []
                    for elem in tmpSVGElem:
                        triple = [instance, c.HAS_SVG_PROPERTY, elem]
                        self.removePropertyTriple(triple, c.DATATYPE_PROP,
                                                  False, undoList)
                    undoElements = []
                    for element in self.selected:
                        self.gui.instancesbyClass[entity][instance].append(element)
                        undoElements.append(element)
                        triple = [instance, c.HAS_SVG_PROPERTY, element]
                        self.addPropertyTriple(triple, c.DATATYPE_PROP, undoList)
                    undoList.append({"type": "add", "instanceId": instance,
                                     "entityName": entity,
                                     "SVGElements": undoElements})

            self.gui.undoStack.append(undoList)
            return True

    def removeAnnotation(self, undoDataDict, fromUndo):
        """ Remove SVG elements from chosen annotation or the whole annotation.
            If elements are not in annotation than nothing will happen.
            Changes are stored in undoStack to be available for undo function.
            If fromUndo is True than this function only reverts changes given
            in undoDataDict and does not save changes into undoStack.
        :param undoDataDict: Dictionary with the data that should be undone
        :param fromUndo: Is 'True' if this function is call as an undo
            function. 'False' otherwise.
        :return: 'True', if GUI should be closes, 'False' otherwise.
        """

        if len(self.gui.selectedEntities) < 1 and not fromUndo:
            tkMessageBox.showwarning(c.REMOVE, c.REMOVE_NO_ANNOT)
            return False

        tempInst = [(undoDataDict["entityName"], undoDataDict["instanceId"])]\
            if fromUndo else self.getTempAnnotations()
        if len(tempInst) < len(self.gui.selectedEntities) and not fromUndo:
            tkMessageBox.showwarning(c.REMOVE, c.REMOVE_ENTITY_SEL)
            return False

        if self.numSelectedItems() == 0 and not fromUndo:
            if tkMessageBox.askokcancel(c.REMOVE, c.REMOVE_NO_ELEM):
                undoList = []  # undo function
                for (entity, instance) in tempInst:
                    tmpSVGElem = self.gui.instancesbyClass[entity][instance]
                    undoList.append({"type": "remove", "instanceId": instance,
                                     "entityName": entity,
                                     "SVGElements": tmpSVGElem})
                    for element in tmpSVGElem:
                        triple = [instance, c.HAS_SVG_PROPERTY, element]
                        self.removePropertyTriple(triple, c.DATATYPE_PROP,
                                                  False, undoList)
                    del self.gui.instancesbyClass[entity][instance]
                    self.removePropertiesOfAnnotation(instance, undoList)
                    # Append parent Entity of instance in order to
                    # automatically expand the tree to it later on
                    self.gui.selectedEntities.append(entity)

                if not fromUndo:
                    self.gui.undoStack.append(undoList)
            else:
                return False

            return True

        # Last case when we have ale least one selected element and at least
        # one annotation selected
        self.removeElements(tempInst, undoDataDict, fromUndo)
        return True

    def removePropertiesOfAnnotation(self, instance, undoList):
        """ Removes all the properties that an instance (annotation) is
            involved in. This needs to be done after deleting an instance.
        :param instance: Instance whose properties should be removed.
        """
        # TODO: improve efficiency
        for property in self.gui.objectProperties:
            triples = self.gui.objectProperties[property]
            for triple in triples:
                if instance in triple:
                    self.gui.removePropertyTriple(triple, 'object_property', 
                                                  False, undoList)
        for property in self.gui.dataTypeProperties:
            triples = self.gui.dataTypeProperties[property]
            for triple in triples:
                if instance in triple:
                    self.gui.removePropertyTriple(triple, 'datatype_property', 
                                                  False, undoList)

    def removeElements(self, tempInstance, undoDataDict, fromUndo):
        """ Subsidiary function to remove annotation.
        :param tempInstance: Prepared list of instances.
        :param undoDataDict: Dictionary with the data that should be undone.
        :param fromUndo: Is 'True' if this function is call as an undo
            function. 'False' otherwise.
        :return: 'True', if GUI should be closes, 'False' otherwise.
        """

        removed = False
        empty = False
        selected = undoDataDict["SVGElements"] if fromUndo else self.selected
        emptyList = []

        undoList = []  # undo function
        for (entity, instance) in tempInstance:
            tempList = self.gui.instancesbyClass[entity][instance]
            self.gui.instancesbyClass[entity][instance] = []

            removedElements = []
            for tempListElement in tempList:
                if tempListElement not in selected:
                    self.gui.instancesbyClass[entity][instance]\
                        .append(tempListElement)
                else:
                    removedElements.append(tempListElement)
                    # Add entity to selected in order to automatically
                    # expand the tree to it later on
                    self.gui.selectedEntities.append(entity)
                    removed = True

            for element in removedElements:
                triple = [instance, c.HAS_SVG_PROPERTY, element]
                self.removePropertyTriple(triple, c.DATATYPE_PROP, 
                                          False, undoList)

            undoList.append({"type": "remove", "instanceId": instance,
                             "entityName": entity,
                             "SVGElements": removedElements})

            if len(self.gui.instancesbyClass[entity][instance]) == 0:
                # Solve the case that every element was removed
                del self.gui.instancesbyClass[entity][instance]
                empty = True
                emptyList.append(instance)

        if empty and not fromUndo:
            tkMessageBox.showwarning(c.REMOVE,
                                     c.REMOVE_EMPTY % ", ".join(emptyList))
            removed = True
        elif not removed and not fromUndo:
            tkMessageBox.showwarning(c.REMOVE, c.REMOVE_NO_REMOVE)

        if not fromUndo and removed:
            self.gui.undoStack.append(undoList)
        return

    def undoAnnotation(self):
        """ Resolves the undo operation. It takes one entry from the undoStack
            and do the opposite operation.
        :return: 'True', if GUI should be closes, 'False' otherwise.
        """

        if not self.gui.undoStack:
            tkMessageBox.showwarning(c.UNDO, c.UNDO_NO_OPERATION)
            return False

        undoOperationList = self.gui.undoStack.pop()
        removeOperationList = []
        updElm = set()
        isTriple = False
        tripleAdd = 0
        tripleRemove = 0

        for operation in undoOperationList:

            if operation["type"] == "add_property":
                # Removes the property from property triples
                # (there should be only one added property)
                isTriple = True
                tripleAdd += 1
                triple = operation["triple"]
                ptype = operation["tripleType"]
                self.removePropertyTriple(triple, ptype)
            elif operation["type"] == "remove_property":
                isTriple = True
                tripleRemove += 1
                triple = operation["triple"]
                ptype = operation["tripleType"]
                self.addPropertyTriple(triple, ptype)
            else:
                updElm.add(operation["instanceId"])
                if operation["type"] == "add":
                    self.removeAnnotation(operation, fromUndo=True)
                if operation["type"] == "remove":
                    removeOperationList.append(operation)

        for operation in removeOperationList:
            self.addElementsIntoAnnotation([(operation["entityName"],
                                             operation["instanceId"])],
                                           operation, fromUndo=True)

        self.gui.serialize()

        if isTriple:
            changedTriples = abs(tripleAdd - tripleRemove)
            if changedTriples == 0:
                tkMessageBox.showwarning(c.UNDO, c.UNDO_TRIPLES)
            elif changedTriples == 1:
                tkMessageBox.showwarning(c.UNDO, c.UNDO_ONE_TRIPLE)
            else:
                tkMessageBox.showwarning(c.UNDO, c.UNDO_VAR_TRIPLES %
                                         str(changedTriples))
            self.gui.refreshPropertyTree(self.gui.treePropertyPicker)

        # Clear the original tree and reload it
        self.gui.treeEntityPicker.\
            delete(*self.gui.treeEntityPicker.get_children())
        self.gui.treePropertyPicker.\
            delete(*self.gui.treePropertyPicker.get_children())
        self.gui.loadSerializedOntology(self.gui.treeEntityPicker)

        if not isTriple:
            tkMessageBox.showwarning(c.UNDO,
                                     c.UNDO_VAR_ANNOT % str(len(updElm)))

        return False

    def addProperty(self, selectedProperty, tags):
        """ Adds the property ie. the triple object - property - subject.
        :param selectedProperty: Property that was selected.
        :param tags:
        :return: 'True' if at least one property has been added,
            'False' otherwise.
        """

        if selectedProperty and tags:
            if c.TREE_TAG_PROPERTY in tags:
                isPropertyAdded = False
                countExisting = 0
                countNew = 0
                undoList = []  # undo function
                subjects = self.gui.selectedEntities
                # TODO: validate that subject and object are instances and
                # are within the domain and range of the property
                if c.TREE_TAG_OBJECT_PROPERTY in tags and \
                        self.validateSelectedRange():
                    for subject in subjects:
                        for obj in self.gui.selectedRange:
                            newTriple = [subject, selectedProperty, obj]
                            if not self.propertyTripleExists(newTriple,
                                                             c.OBJECT_PROP):
                                self.addPropertyTriple(newTriple, c.OBJECT_PROP, 
                                                       undoList)
                                countNew += 1
                                isPropertyAdded = True
                            else:
                                countExisting += 1
                elif c.TREE_TAG_DATATYPE_PROPERTY in tags:
                    for subject in subjects:
                        value = self.dataTypeInputPrompt(subject, selectedProperty)
                        if value is not None:
                            newTriple = [subject, selectedProperty, value]
                            if not self.propertyTripleExists(newTriple,
                                                             c.DATATYPE_PROP):
                                self.addPropertyTriple(newTriple,
                                                       c.DATATYPE_PROP, undoList)
                                countNew += 1
                                isPropertyAdded = True
                            else:
                                countExisting += 1
                        else:
                            return False
                if isPropertyAdded:
                    if countExisting > 0:
                        show = (str(countExisting), str(countNew))
                        tkMessageBox.showwarning(c.PROP,
                                                 c.PROP_EXIST_ADD % show)

                    self.gui.undoStack.append(undoList)
                    return True
                else:
                    tkMessageBox.showwarning(c.PROP, c.PROP_ALL_EXIST)
            elif c.TREE_TAG_PROPERTIES_HEADER in tags:
                tkMessageBox.showwarning(c.PROP, c.PROP_HEADER)
                return False
            elif c.TREE_TAG_INSTANCE in tags:
                tkMessageBox.showwarning(c.PROP, c.PROP_INSTANCE)
                return False
            else:
                tkMessageBox.showwarning(c.PROP, c.PROP_WRONG_CHOICE)
                return False
        return False

    def removeProperty(self, selectedProperties, tags, rowIDs):
        """ Removes the property ie. the triple object - property - subject.
        :param selectedProperties: Properties that were selected.
        :param tags:
        :return: 'True' if at least one property has been removed,
            'False' otherwise.
        """
        changed = False
        if selectedProperties and tags and rowIDs:
            undoList = []
            for selProperty in selectedProperties:
                if c.TREE_TAG_INSTANCE in tags[selProperty]:
                    oldTriple = \
                        self.gui.propertiesByTreeID[rowIDs[selProperty]]
                    changed = True
                    if c.TREE_TAG_OBJECT_PROPERTY in tags[selProperty]:
                        self.removePropertyTriple(oldTriple, c.OBJECT_PROP, 
                                                  False, undoList)
                    elif c.TREE_TAG_DATATYPE_PROPERTY in tags[selProperty]:
                        self.removePropertyTriple(oldTriple, c.DATATYPE_PROP, 
                                                  False, undoList)
                else:
                    sp = selProperty
                    tkMessageBox.showwarning(c.PROP, c.PROP_INST_REMOVE % sp)
                    return False
            if changed:
                self.gui.undoStack.append(undoList)
                return True
        return False

    def validateSelectedRange(self):
        """ Validates the range of an object property after it has been
            selected. N.B. prepareSelectedEntities needs to be called
            beforehand.
        :return: 'True' is range is valid, 'False' otherwise.
        """
        valid = True
        if len(self.gui.selectedRange) == 0:
            valid = False
            tkMessageBox.showwarning(c.PROP, c.PROP_NO_RANGE)
        return valid

    def propertyTripleExists(self, triple, type):
        """ Returns whether a property triple already exists.
        :param triple: Tested triple.
        :param type: Type of triple (object or datatype property).
        :return: 'True' if property triple exists, 'False' otherwise.
        """

        exists = False
        if len(triple) == 3:
            p = triple[c.PROPERTY_INDEX]
            if type == c.OBJECT_PROP:
                if triple in self.gui.objectProperties[p]:
                    exists = True
            elif type == c.DATATYPE_PROP:
                if triple in self.gui.dataTypeProperties[p]:
                    exists = True
        return exists

    def addPropertyTriple(self, triple, type, undoList=None):
        """ Adds a property triple to the system. N.B. It does not check
            for existence.
        :param triple: Triple to be added.
        :param type: Type of triple (object or datatype property).
        :param undoList: the partial list of undo operations
        """

        p = triple[c.PROPERTY_INDEX]
        self.gui.selectedProperties = ["%s -> %s" % (triple[c.SUBJECT_INDEX],
                                                     triple[c.OBJECT_INDEX])]
        if type == c.OBJECT_PROP:
            self.gui.objectPropertiesToAdd.append(triple)
            if p not in self.gui.objectProperties:
                self.gui.objectProperties[p] = []
            self.gui.objectProperties[p].append(triple)
        elif type == c.DATATYPE_PROP:
            self.gui.dataTypePropertiesToAdd.append(triple)
            if p not in self.gui.dataTypeProperties:
                self.gui.dataTypeProperties[p] = []
            self.gui.dataTypeProperties[p].append(triple)
        if undoList is not None:
            undoList.append({"type": "add_property",
                            "triple": triple,
                            "tripleType": type})

    def removePropertyTriple(self, triple, type, fromEdit=False, 
                             undoList = None):
        """ Removes a property triple from the system.
        :param triple: Triple to be removed.
        :param type: Type of triple (object or datatype property).
        :param fromEdit: whether this method is being called as part of an
        edit operation
        :param undoList: the partial list of undo operations
        """

        property = triple[c.PROPERTY_INDEX]
        # When coming from prop. edit, the selected property should be
        # the edited property, already done in addPropertyTriple
        if not fromEdit:
            self.gui.selectedProperties = [property]
        if type == c.OBJECT_PROP:
            if triple in self.gui.objectPropertiesToAdd:
                self.gui.objectPropertiesToAdd.remove(triple)
            if triple in self.gui.objectProperties[property]:
                self.gui.objectProperties[property].remove(triple)
                self.gui.objectPropertiesToRemove.append(triple)
        elif type == c.DATATYPE_PROP:
            if triple in self.gui.dataTypePropertiesToAdd:
                self.gui.dataTypePropertiesToAdd.remove(triple)
            if triple in self.gui.dataTypeProperties[property]:
                self.gui.dataTypeProperties[property].remove(triple)
                self.gui.objectPropertiesToRemove.append(triple)
        if undoList is not None:
            undoList.append({"type": "remove_property",
                            "triple": triple,
                            "tripleType": type})

    def editProperty(self, selectedProperty, tags, rowID):
        """ Edit the property ie. the triple object - property - subject.
        :param selectedProperty: Property that was selected.
        :param tags:
        :return: 'True' if at least one property has been added,
            'False' otherwise.
        """

        if selectedProperty and tags and rowID:
            if c.TREE_TAG_INSTANCE in tags:
                undoList = []
                newTriples = 0
                oldTriple = self.gui.propertiesByTreeID[rowID]
                selectedProperty = oldTriple[c.PROPERTY_INDEX]
                if c.TREE_TAG_OBJECT_PROPERTY in tags:
                    ptype = c.OBJECT_PROP
                    for o in self.gui.selectedRange:
                        newTriple = \
                            [self.gui.selectedEntities[0], selectedProperty, o]
                        if not self.propertyTripleExists(newTriple, ptype):
                            newTriples += 1
                            self.addPropertyTriple(newTriple, ptype, undoList)
                        else:
                            tkMessageBox.showwarning(c.PROP,
                                                     c.PROP_EXIST % newTriple)
                elif c.TREE_TAG_DATATYPE_PROPERTY in tags:
                    ptype = c.DATATYPE_PROP
                    self.gui.defaultTypeValue = oldTriple[c.OBJECT_INDEX]
                    v = self.dataTypeInputPrompt(self.gui.selectedEntities[0],
                                                 selectedProperty)
                    if v:
                        newTriple = \
                            [self.gui.selectedEntities[0], selectedProperty, v]
                        if not self.propertyTripleExists(newTriple, ptype):
                            newTriples += 1
                            self.addPropertyTriple(newTriple, ptype, undoList)
                        else:
                            tkMessageBox.showwarning(c.PROP,
                                                     c.PROP_EXIST % newTriple)
                    else:
                        return
                if newTriples > 0:
                    self.removePropertyTriple(oldTriple, ptype, 
                                              True, undoList)
                    self.gui.undoStack.append(undoList)
                    return True
            elif c.TREE_TAG_PROPERTIES_HEADER in tags:
                tkMessageBox.showwarning(c.PROP, c.PROP_HEADER_EDIT)
                return False
            else:
                tkMessageBox.showwarning(c.PROP, c.PROP_INST_EDIT)
                return False
        return False

    def dataTypeInputPrompt(self, subject, property):
        """ Prompt the user to add a value (object) for a given datatype
         property (subject - property - value). Returns the user's input.
         :param subject: Subject of the property.
         :param property: Property name.
         :return: User's input.
         """

        dataType = self.gui.rangesByProperty[property]
        if not dataType:
            dataType = "value"
        else:
            dataType = dataType[0]
        prompt = "%s %s (input a %s):" % (subject, property, dataType)
        return tkSimpleDialog.askstring(c.PROP, prompt,
                                        initialvalue=self.gui.defaultTypeValue)
