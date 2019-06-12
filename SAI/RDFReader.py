"""
Created on Apr 27, 2016
@author: Tomas Murillo-Morales, Jaromir Plhak
"""

import rdflib
from rdflib.term import URIRef
from rdflib import RDF
import const as c


class RDFReader(object):
    """ This class enables us the operation with .rdf ontology. The basic
        basic functionality is - load data from ontology, save data to
        ontology, create a tree view of the data using SPARQL. """

    def __init__(self, path, namespace):
        self.filePath = path
        self.namespace = namespace
        self.namespacePrefix = "<%s#>" % self.namespace
        self.graph = rdflib.Graph()
        self.graph.load(path)
        self.ontologyTree = []
        # Index: Property Name; Values: Entities that belong to its range
        self.rangesByProperty = {}
        # Index: Property Name; Values: Entities that belong to its domain
        self.domainsByProperty = {}
        self.instancesbyClass = {}
        # Initialize instancesbyClass. e.g.
        # {"Graphic_Object", {"annotation123", [path123, rect567]}}
        instanceList = self.getInstanceList()
        for entity, instances in instanceList.iteritems():
            if entity not in self.instancesbyClass:
                self.instancesbyClass[entity] = {}
            for instance in instances:
                self.instancesbyClass[entity][instance] = \
                    self.getSVGElementsOfInstance(instance)
        self.objectProperties = self.getObjectPropertyList()
        self.dataTypeProperties = self.getDatatypePropertyList()
        self.initializeDomainsAndRanges()

    def initializeDomainsAndRanges(self):
        """ Initialize domainsByProperty and rangesByProperty dictionaries. """
        for property in self.objectProperties:
            self.domainsByProperty[property] = self.domainOfProperty(property)
            self.rangesByProperty[property] = self.rangeOfProperty(property)
        for property in self.dataTypeProperties:
            self.rangesByProperty[property] = self.rangeOfProperty(property)

    def hasEntity(self, entityName):
        """ Returns whether the given Entity exists in the ontology.
        :param entityName: Name of the tested entity.
        :return: 'True' if the entity with entityName exists in the ontology,
            'False' otherwise.
        """

        entityURI = URIRef("%s#%s" % (self.namespace, entityName))
        owlClassURI = URIRef("%s#Class" % c.OWL_NS)
        return (entityURI, RDF.type, owlClassURI) in self.graph

    def hasProperty(self, propertyName, type):
        """ Check whether a property exists in the ontology.
            Allowed types: object, datatype.
        :param propertyName: Name of the property to be tested
        :param type: Type of the property to be tested
        :return: 'True' if the property with propertyName exists
            in the ontology, 'False' otherwise
        """

        objectURI = URIRef("%s#%s" % (self.namespace, propertyName))
        dataPropertyURI = URIRef("%s#type" % c.RDF_NS)
        if type == "object":
            subjectURI = URIRef("%s#ObjectProperty" % c.OWL_NS)
        else:
            subjectURI = URIRef("%s#DatatypeProperty" % c.OWL_NS)
        return (objectURI, dataPropertyURI, subjectURI) in self.graph

    def addProperty(self, propertyName, type):
        """ Adds a new property to the ontology (NOT a property instance).
            Allowed types: object, datatype.
        :param propertyName: Name of the property to be added
        :param type: Type of the property to be added
        """

        if not self.hasProperty(propertyName, type):
            objectURI = URIRef("%s#%s" % (self.namespace, propertyName))
            dataPropertyURI = URIRef("%s#type" % c.RDF_NS)
            if type == "object":
                subjectURI = URIRef("%s#ObjectProperty" % c.OWL_NS)
            else:
                subjectURI = URIRef("%s#DatatypeProperty" % c.OWL_NS)
            self.graph.add((objectURI, dataPropertyURI, subjectURI))

    def hasInstance(self, entityName, instanceName):
        """ Returns whether the given individual (annotation) for an entity
            exists in the ontology.
        :param entityName: Name of the entity for tested instance.
        :param instanceName: Name of the tested instance.
        :return: 'True' if entity with the entityName has instance with
            the instanceName.
        """

        entityURI = URIRef("%s#%s" % (self.namespace, entityName))
        instanceURI = URIRef("%s#%s" % (self.namespace, instanceName))
        namedIndividualURI = URIRef("%s#%s" % (c.OWL_NS, "NamedIndividual"))
        return ((instanceURI, RDF.type, entityURI) in self.graph) and \
               ((instanceURI, RDF.type, namedIndividualURI) in self.graph)

    def hasSVGElement(self, instanceName, dataPropertyValue):
        """ Returns whether a given instance has a given
            SVG element (Data Property Value)
        :param instanceName: Name if the instance to be tested
        :param dataPropertyValue: Value of the data property
        :return: 'True' if given instance with instanceName has a given
            SVG element
        """

        return self.hasDatatypeProperty(instanceName, c.HAS_SVG_PROPERTY,
                                        dataPropertyValue)

    def hasDatatypeProperty(self, instanceName, datapropertyName,
                            dataPropertyValue):
        """ Returns whether a given instance has a given value for a given
            Datatype Property.
        :param instanceName:
        :param datapropertyName:
        :param dataPropertyValue:
        :return:
        """

        instanceURI = URIRef("%s#%s" % (self.namespace, instanceName))
        dataPropertyURI = URIRef("%s#%s" % (self.namespace, datapropertyName))
        dataPropertyValURI = rdflib.term.Literal(dataPropertyValue)
        return (instanceURI, dataPropertyURI, dataPropertyValURI) in self.graph

    def hasCoordinates(self, instanceName, dataPropertyValue):
        """ Returns whether a given instance has a given SVG element
            (Data Property Value).
        :param instanceName:
        :param dataPropertyValue:
        :return:
        """

        instanceURI = URIRef("%s#%s" % (self.namespace, instanceName))
        dataPropertyURI = URIRef("%s#%s" % (self.namespace, c.HAS_X_COORD_PR))
        dataPrValueURI = rdflib.term.Literal(dataPropertyValue)
        return (instanceURI, dataPropertyURI, dataPrValueURI) in self.graph

    def addInstance(self, entityName, instanceName):
        """ Adds an instance of a given name to a given entity of the ontology
        :param entityName:
        :param instanceName:
        """

        entityURI = URIRef("%s#%s" % (self.namespace, entityName))
        instanceURI = URIRef("%s#%s" % (self.namespace, instanceName))
        namedIndividualURI = URIRef("%s#%s" % (c.OWL_NS, "NamedIndividual"))
        self.graph.add((instanceURI, RDF.type, entityURI))
        self.graph.add((instanceURI, RDF.type, namedIndividualURI))

    def removeInstance(self, instanceName):
        """ Removes an instance with a given name and entity from the ontology.
            Also removes all of its properties.
        :param instanceName:
        """

        instanceURI = URIRef("%s#%s" % (self.namespace, instanceName))
        self.graph.remove((instanceURI, None, None))

    def addSVGElementProperty(self, instanceName, dataPropertyValue):
        """ Adds a hasSVGElement data property value to the given
            instance (annotation).
        :param instanceName:
        :param dataPropertyValue:
        """

        self.addDatatypeProperty(instanceName, c.HAS_SVG_PROPERTY, 
                                 dataPropertyValue)

    def addDatatypeProperty(self, instanceName, dataPrName, dataPrValue):
        """ Adds a datatype property triple
        :param instanceName:
        :param dataPrName:
        :param dataPrValue:
        """

        if not self.hasDatatypeProperty(instanceName, dataPrName, dataPrValue):
            instanceURI = URIRef("%s#%s" % (self.namespace, instanceName))
            dataPropertyURI = URIRef("%s#%s" % (self.namespace, dataPrName))
            dataPrValueURI = rdflib.term.Literal(dataPrValue)
            self.graph.add((instanceURI, dataPropertyURI, dataPrValueURI))

    def removeSVGElementProperty(self, instanceName, dataPropertyValue):
        """ Removes a hasSVGElement data property value from the
            given instance (annotation).
        :param instanceName:
        :param dataPropertyValue:
        """

        if self.hasSVGElement(instanceName, dataPropertyValue):
            self.removeDatatypeProperty(instanceName, c.HAS_SVG_PROPERTY,
                                        dataPropertyValue)

    def removeDatatypeProperty(self, instanceName, dataPrName, dataPrValue):
        """ Removes a datatype property value from the given
            instance (annotation).
        :param instanceName:
        :param dataPrName:
        :param dataPrValue:
        """
        """"""
        if self.hasDatatypeProperty(instanceName, dataPrName, dataPrValue):
            instanceURI = URIRef("%s#%s" % (self.namespace, instanceName))
            dataPrURI = URIRef("%s#%s" % (self.namespace, dataPrName))
            dataPrValueURI = rdflib.term.Literal(dataPrValue)
            self.graph.remove((instanceURI, dataPrURI, dataPrValueURI))

    def addCoordinatesXY(self, instanceName, dataPropertyValueX,
                         dataPropertyValueY):
        """ Adds hasX and hasYCoordinates data property value to the given
            instance (annotation).
        :param instanceName:
        :param dataPropertyValueX:
        :param dataPropertyValueY:
        :return:
        """

        instanceURI = URIRef("%s#%s" % (self.namespace, instanceName))
        dataPropertyURI = URIRef("%s#%s" % (self.namespace, c.HAS_X_COORD_PR))
        dataPropertyValueXURI = rdflib.term.Literal(dataPropertyValueX)
        self.graph.remove((instanceURI, dataPropertyURI, None))
        self.graph.add((instanceURI, dataPropertyURI, dataPropertyValueXURI))

        dataPropertyURI = URIRef("%s#%s" % (self.namespace, c.HAS_Y_COORD_PR))
        dataPropertyValueYURI = rdflib.term.Literal(dataPropertyValueY)
        self.graph.remove((instanceURI, dataPropertyURI, None))
        self.graph.add((instanceURI, dataPropertyURI, dataPropertyValueYURI))

    def addObjectProperty(self, subj, property, obj):
        """ Adds an instance of an object property to the ontology.
        :param subj:
        :param property:
        :param obj:
        """

        subjectURI = URIRef("%s#%s" % (self.namespace, subj))
        propertyURI = URIRef("%s#%s" % (self.namespace, property))
        objectURI = URIRef("%s#%s" % (self.namespace, obj))
        if not (subjectURI, propertyURI, objectURI) in self.graph:
            self.graph.add((subjectURI, propertyURI, objectURI))


    def addLengthAndWidth(self, instanceName, length, width):
        """
        Adds has_length and has_width properties to the given instance (annotation)
        :param instanceName: string; name of instance in the ontology
        :param length: float; value of the has_length property for the instance
        :param width: float; value of the has_width property for the instance
        :return:
        """
        instanceURI = URIRef("%s#%s" % (self.namespace, instanceName))
        dataPropertyURI = URIRef("%s#%s" % (self.namespace, c.HAS_LENGTH_PR))
        dataPropertyValueURI = rdflib.term.Literal(length)
        self.graph.remove((instanceURI, dataPropertyURI, None))
        self.graph.add((instanceURI, dataPropertyURI, dataPropertyValueURI))
        dataPropertyURI = URIRef("%s#%s" % (self.namespace, c.HAS_WIDTH_PR))
        dataPropertyValueURI = rdflib.term.Literal(width)
        self.graph.remove((instanceURI, dataPropertyURI, None))
        self.graph.add((instanceURI, dataPropertyURI, dataPropertyValueURI))

    def removeObjectProperty(self, subj, property, obj):
        """ Removes an instance of an object property to the ontology.
        :param subj:
        :param property:
        :param obj:
        """

        subjectURI = URIRef("%s#%s" % (self.namespace, subj))
        propertyURI = URIRef("%s#%s" % (self.namespace, property))
        objectURI = URIRef("%s#%s" % (self.namespace, obj))
        if (subjectURI, propertyURI, objectURI) in self.graph:
            self.graph.remove((subjectURI, propertyURI, objectURI))

    def getLastId(self):
        """ Search for the last Id of  instances for making them unique.
        :return: The highest id that has specific name from SVG_NAMED_ELEMENTS
        """

        lastId = 0
        for key, value in self.getInstanceList().iteritems():
            for instance in value:
                for svgName in c.SVG_NAMED_ELEMENTS:
                    if svgName in instance:
                        annotationRest = instance[len(svgName):]
                        if annotationRest.isdigit() and \
                           int(annotationRest) > lastId:
                            lastId = int(annotationRest)
        return lastId

    def getInstanceList(self):
        """ Returns a dict, indexed by Entity name, with the instances of said
            entity in the ontology.
        :return: dict that is indexed by Entity name, with the instances of
            said entity in the ontology.
        """

        instancesOfClass = {}
        query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX owl: <http://www.w3.org/2002/07/owl#>
                   SELECT ?cl ?ind
                   WHERE {
                       ?ind rdf:type ?cl .
                       ?ind rdf:type owl:NamedIndividual
                   }
                   """
        query_res = self.graph.query(query)
        for row in query_res:
            entityName = row.cl.split('#')[1]
            if entityName != 'NamedIndividual' and entityName != 'Class':
                individualName = row.ind.split('#')[1]
                if (entityName not in instancesOfClass):
                    instancesOfClass[entityName] = []
                instancesOfClass[entityName].append(individualName)
        return instancesOfClass

    def getPropertyInstances(self, propertyName):
        """ Returns all occurrences of a given Property
        :param propertyName: Name of the tested property
        :return: All occurrences of a given Property
        """

        propertyURI = URIRef("%s#%s" % (self.namespace, propertyName))
        return self.graph.triples((None, propertyURI, None))

    def getObjectPropertyList(self):
        """ Returns a list of all object properties in the ontology.
        :return: List of all object properties in the ontology.
        """

        query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX owl: <http://www.w3.org/2002/07/owl#>
                   SELECT DISTINCT ?id
                   WHERE {
                       ?id rdf:type owl:ObjectProperty
                   }
                   """
        query_res = self.graph.query(query)
        retlist = [row.id.split("#")[1] for row in query_res]
        retlist.sort()
        return retlist

    def getDatatypePropertyList(self):
        """ Returns a list of all Datatype properties in the ontology.
        :return: List of all Datatype properties in the ontology
        """

        query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX owl: <http://www.w3.org/2002/07/owl#>
                   SELECT DISTINCT ?id
                   WHERE {
                       ?id rdf:type owl:DatatypeProperty
                   }
                   """
        query_res = self.graph.query(query)
        retlist = [row.id.split("#")[1] for row in query_res]
        retlist.sort()
        return retlist

    def domainOfProperty(self, property):
        """ Returns the entity(ies) of the domain of the given property.
        :param property: Property to be tested
        :return: Entity(ies) of the domain of the given property.
        """

        query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                   PREFIX vis: %s
                   SELECT DISTINCT ?dom
                   WHERE {
                       vis:%s rdfs:domain ?dom
                   }
                   """ % (self.namespacePrefix, property)
        query_res = self.graph.query(query)
        return [row.dom.split("#")[1] for row in query_res]

    def rangeOfProperty(self, property):
        """ Returns the entity(ies) of the range of the given property.
        :param property: Property to be tested.
        :return: Entity(ies) of the range of the given property.
        """

        query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                   PREFIX vis: %s
                   SELECT DISTINCT ?range
                   WHERE {
                       vis:%s rdfs:range ?range
                   }
                   """ % (self.namespacePrefix, property)
        query_res = self.graph.query(query)
        return [row.range.split("#")[1] for row in query_res]

    def termsBelongingToNameSpace(self, nameSpace, *types):
        """ Returns a list of terms belonging to the given namespace.
            Allowed types: {Class, ObjectProperty, DatatypeProperty}.
        :param nameSpace:
        :param types:
        :return:
        """

        valueString = "{"
        for type in types:
            valueString += (" (owl:%s)" % type)
        valueString += " }"
        query = """PREFIX owl: <http://www.w3.org/2002/07/owl#>
                   SELECT DISTINCT ?a
                   WHERE {
                       VALUES (?c) %s
                       ?a a ?c
                       FILTER strstarts(str(?a), %s")
                   }
                   """ % (valueString, nameSpace)
        query_res = self.graph.query(query)
        retlist = [row.id.split("#")[1] for row in query_res]
        return retlist

    def getSVGElementsOfInstance(self, instanceID):
        """ Returns an array with the IDs of the SVG Elements that an Entity
            Instance has (according to its hasSVGElement Data Properties).
        :param instanceID:
        :return:
        """

        query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX owl: <http://www.w3.org/2002/07/owl#>
                   PREFIX vis: %s
                   SELECT ?id
                   WHERE {
                       vis:%s rdf:type owl:NamedIndividual .
                       vis:%s vis:hasSVGElement ?id
                   }
                   """ % (self.namespacePrefix, instanceID, instanceID)
        query_res = self.graph.query(query)
        return [row.id.toPython() for row in query_res]

    def classOfIndividual(self, individualName):
        """ Return the Entity an individual belongs to; an empty string
            if none found.
        :param individualName:
        :return:
        """

        query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX owl: <http://www.w3.org/2002/07/owl#>
                   PREFIX vis: %s
                   SELECT ?cl
                   WHERE { vis:%s rdf:type ?cl
                       FILTER EXISTS { vis:%s rdf:type owl:NamedIndividual }
                   }
                   """ % (self.namespacePrefix, individualName, individualName)
        query_res = self.graph.query(query)
        retlist = [row.cl.split("#")[1] for row in query_res]
        if retlist:
            classNameList = [r for r in retlist if 'NamedIndividual' not in r]
            className = classNameList[0]
        else:
            className = ''
        return className

    def getSubclasses(self, parentClass):
        """ Returns all subclasses for the parent class.
        :param parentClass: Parent class to be tested.
        :return: All subclasses for the parent class.
        """

        query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                   PREFIX vis: %s
                   SELECT ?cl
                   WHERE { ?cl rdfs:subClassOf vis:%s }
                   """ % (self.namespacePrefix, parentClass)
        query_res = self.graph.query(query)
        retlist = [row.cl.split("#")[1] for row in query_res]
        return retlist

    def getParentclasses(self, childClass):
        """ Return parent class for the given child class.
        :param childClass: Child class to be tested.
        :return: Parent class for the given child class.
        """

        query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                   PREFIX vis: %s
                   SELECT ?cl
                   WHERE { vis:%s rdfs:subClassOf ?cl }
                   """ % (self.namespacePrefix, childClass)
        query_res = self.graph.query(query)
        retlist = [row.cl.split("#")[1] for row in query_res]
        return retlist

    def generateSubTree(self, rootEntity, treeViewInstance):
        """ Generates subtree
        :param rootEntity:
        :param treeViewInstance:
        """
        tree = self.subTreeRecursive(rootEntity, treeViewInstance)
        return tree

    def subTreeRecursive(self, rootEntity, treeViewInstance, parentID=''):
        """ Get all entities from the ontology and feed the treeView with them.
        :param rootEntity:
        :param treeViewInstance:
        :param parentID:
        :return:
        """

        # Insert element into GUI ViewTree
        childID = treeViewInstance.insert(parentID, 'end', text=rootEntity,
                                          tags=('entityRow', ))
        # Insert instances of current Entitiy
        if (rootEntity in self.instancesbyClass):
            self.insertInstancesInTree(self.instancesbyClass[rootEntity],
                                       treeViewInstance, childID)
        subtree = [rootEntity]
        rootChildren = self.getSubclasses(rootEntity)
        if rootChildren:
            for child in rootChildren:
                subtree.append(self.subTreeRecursive(child, treeViewInstance,
                                                     childID))
        return subtree

    def insertInstancesInTree(self, instanceList, treeViewInstance, parentID):
        """ Insert instances in the tree structure
        :param instanceList:
        :param treeViewInstance:
        :param parentID:
        :return:
        """
        for instance in instanceList:
            # InstanceList is a dict, whose keys are annotation IDs
            treeViewInstance.insert(parentID, 'end', text=instance,
                                    tags=('instanceRow', ))

    def saveOntology(self):
        """Save current graph into a RDF file"""
        self.graph.serialize(self.filePath)

    """
    # Unused methods

    def getDomainAndRangeInstances(self, property, domainOrRange="domain"):
        # Returns the instances/individuals/annotations of the domain or
        # range of the given property

        individuals = []
        if type == "domain":
            propertyClasses = self.domainOfProperty(property)
        else:
            propertyClasses = self.rangeOfProperty(property)
        if propertyClasses:
            for entity in propertyClasses:
                ent_individuals = self.instancesbyClass[entity].keys()
                if ent_individuals:
                    individuals.append(ent_individuals)
        return individuals
        
        def entitiesList(self):
            #Create list of entities
            #:return: List of entities in the following structure:
            Output example
            (
                rdflib.term.URIRef(u'http://www.semanticweb.org/ak116252/
                    ontologies/2015/2/upper-visualization#Visual_Attribute'),
                rdflib.term.URIRef(u'http://www.w3.org/1999/02/
                    22-rdf-syntax-ns#type'),
                rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#Class')
            )
            
    
            typePredicate = URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
            classObject = URIRef(u'http://www.w3.org/2002/07/owl#Class')
            upperVisClasses = self.graph.subjects(typePredicate, classObject)
    
            return upperVisClasses
    """
