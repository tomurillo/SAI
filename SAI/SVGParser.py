""""
Created on May 23, 2016
@author: Tomas Murillo-Morales, Jaromir Plhak
"""

from svg.path import parse_path
import inkex
import sys
import const

class SVGParser:
    """
    This class counts the x and y coordinates for list of SVG elements for
    the given etree root node.
    """

    def __init__(self, svgRoot):
        self.svgRoot = svgRoot
        self.dict = {}  # Element coordinate dictionary
        self.att_dict = {}  # Other element attributes

    def findCenters(self):
        """ This is the main method for detecting centers of SVG elements.
            It selects the specific svg elements and calls the appropriate
            function for them.
        """

        self.addRectCenter(self.svgRoot.xpath("//svg:rect",
                                              namespaces=inkex.NSS))
        self.addEllipseCenter(self.svgRoot.xpath("//svg:ellipse",
                                                 namespaces=inkex.NSS))
        self.addPathCenter(self.svgRoot.xpath("//svg:path",
                                              namespaces=inkex.NSS))
        self.addTextCenter(self.svgRoot.xpath("//svg:text",
                                              namespaces=inkex.NSS))

    def addRectCenter(self, elList):
        """ Searches the central point and other attributes of all rect SVG elements. Coordinates
            are added to the dictionary using elements id as the key.
        :param elList: List of rect elements to whom the coordinates are counted
        """

        for rect in elList:
            if rect is not None and "id" in rect.attrib and "x" in rect.attrib\
                    and "y" in rect.attrib and "height" in rect.attrib \
                    and "width" in rect.attrib:
                
                x_orig = float(rect.attrib["x"])
                y_orig = float(rect.attrib["y"])
                cx_orig = (x_orig + (x_orig + float(rect.attrib["width"]))) / 2
                cy_orig = (y_orig + (y_orig + float(rect.attrib["height"]))) / 2
                if "transform" in rect.attrib:
                    transVector = self.__transformStringToVector(
                                                     rect.attrib["transform"])
                    (x, y) = self.__calculateTransformedCoordinates(
                                                            cx_orig, 
                                                            cy_orig, 
                                                            transVector)
                else:
                    x = cx_orig
                    y = cy_orig    
                self.dict[rect.attrib["id"]] = (str(x), str(y))
                self.att_dict[rect.attrib["id"]] = {}
                self.att_dict[rect.attrib["id"]]['height'] = str(rect.attrib["height"])
                self.att_dict[rect.attrib["id"]]['width'] = str(rect.attrib["width"])

    def addEllipseCenter(self, elList):
        """ Searches the central point of all ellipse SVG elements. Coordinates
            are added to the dictionary using elements id as the key.
        :param elList List of ellipse elements to whom the coordinates
            are counted
        """
        for ell in elList:
            if (ell is not None and "id" in ell.attrib and "cx" in ell.attrib
                    and "cy" in ell.attrib):
                
                x_orig = ell.attrib["cx"]
                y_orig = ell.attrib["cy"]
                
                if "transform" in ell.attrib:
                    transVector = self.__transformStringToVector(
                                                     ell.attrib["transform"])
                    (x, y) = self.__calculateTransformedCoordinates(
                                                            x_orig, 
                                                            y_orig, 
                                                            transVector)
                else:
                    x = x_orig
                    y = y_orig
                                
                self.dict[ell.attrib["id"]] = (x, y)

    def addPathCenter(self, elList):
        """ Searches the central point of all path SVG elements. Coordinates
            are added to the dictionary using elements id as the key.
        :param elList: List of path elements whose coordinates are
            counted
        """
        for path in elList:
            if (path is not None and "id" in path.attrib
                    and "{" + const.SODI_NS + "}cx" in path.attrib
                    and "{" + const.SODI_NS + "}cy" in path.attrib):
                
                x_orig = path.attrib["{" + const.SODI_NS + "}cx"]
                y_orig = path.attrib["{" + const.SODI_NS + "}cy"]
                
                if "transform" in path.attrib:
                    transVector = self.__transformStringToVector(
                                                     path.attrib["transform"])
                    (x, y) = self.__calculateTransformedCoordinates(
                                                            x_orig, 
                                                            y_orig, 
                                                            transVector)
                else:
                    x = x_orig
                    y = y_orig
                    
                self.dict[path.attrib["id"]] = (x, y)
            elif (path is not None and "id" in path.attrib
                    and "d" in path.attrib):
                
                svgpath = parse_path(path.attrib["d"])

                maxX = -sys.float_info.max
                minX = sys.float_info.max
                maxY = -sys.float_info.max
                minY = sys.float_info.max
                for pt in svgpath:
                    parsedX = float(str(pt.point(0))[1:str(pt.point(0)).
                                    index("+")])
                    parsedY = float(str(pt.point(0))[str(pt.point(0)).
                                    index("+") + 1: -2])
                    if parsedX > maxX:
                        maxX = parsedX
                    if parsedX < minX:
                        minX = parsedX
                    if parsedY > maxY:
                        maxY = parsedY
                    if parsedY < minY:
                        minY = parsedY

                self.dict[path.attrib["id"]] = \
                    (str((minX + maxX) / 2), str((minY + maxY) / 2))

    def addTextCenter(self, elList):
        """ Searches the central point of all text SVG elements. Coordinates
            are added to the dictionary using elements id as the key.
            Note: Currently, the function only takes the top-left corner
            of the text as its center.
        :param elList: List of text elements to whom the coordinates are
            counted
        """

        for text in elList:
            if (text is not None and "id" in text.attrib and "x" in text.attrib
                    and "y" in text.attrib):
                
                if "transform" in text.attrib:
                    transVector = self.__transformStringToVector(
                                                     text.attrib["transform"])
                    (x, y) = self.__calculateTransformedCoordinates(
                                                            text.attrib["x"], 
                                                            text.attrib["y"], 
                                                            transVector)
                else:
                    x = text.attrib["x"]
                    y = text.attrib["y"]
                    
                self.dict[text.attrib["id"]] = (x, y)
                
                # TODO: Find the exact center of the text
                # Variables for computing central point
                # lList = text.xpath("./svg:tspan",
                #                   namespaces=inkex.NSS)
                # lines = len(lList) if lList else 0
                # styleText = str(text.attrib["style"])
                # startF = styleText.index("font-size:")
                # endF = styleText.index(";", startF)
                # font = float(styleText[startF +
                #                   len("font-size:"): endF - len("px")])
                # letters = 0
                # for tspan in lList:
                #    if len(tspan.text) > letters:
                #        letters = len(tspan.text)

    def countCentralPointForListOfElements(self, elList):
        """ This method count the central point for elements in ElList.
            It takes the maximal and minimal coordinate and makes the average
            of them. Elements without coordinates are not taken
            into consideration.
        :param elList: List of elements for which the coordinates are counted
        :return: A pair (x-coordinate, y-coordinate) if they can be determined,
            'None" otherwise
        """

        self.findCenters()

        maxX = -sys.float_info.max
        minX = sys.float_info.max
        maxY = -sys.float_info.max
        minY = sys.float_info.max
        for element in elList:
            if element in self.dict:
                if float(self.dict[element][0]) > maxX:
                    maxX = float(self.dict[element][0])
                if float(self.dict[element][0]) < minX:
                    minX = float(self.dict[element][0])
                if float(self.dict[element][1]) > maxY:
                    maxY = float(self.dict[element][1])
                if float(self.dict[element][1]) < minY:
                    minY = float(self.dict[element][1])

        if maxX == -sys.float_info.max:
            return None
        else:
            roundX = round((minX + maxX) / 2, 3)
            roundY = round((minY + maxY) / 2, 3)
            return (str(roundX), str(roundY))

    def computeDimForListOfElements(self, eList):
        """
        Computes the total length and width of rectangles or annotations made up of rectangles
        :param eList: List of elements
        :return: (height, width); dimensions for the annotation made up of the given elements
        """
        c_max_y, c_max_x = -sys.float_info.max, -sys.float_info.max
        c_min_y, c_min_x = sys.float_info.max, sys.float_info.max
        min_len, min_width, max_len, max_width = (0.0,)*4
        n_found = 0
        for element in eList:
            if element in self.att_dict:
                if float(self.dict[element][0]) < c_min_x and 'width' in self.att_dict[element]:
                    c_min_x = float(self.dict[element][0])
                    min_width = self.att_dict[element]['width']
                    n_found += 1
                if float(self.dict[element][1]) < c_min_y and 'height' in self.att_dict[element]:
                    c_min_y = float(self.dict[element][1])
                    min_len = self.att_dict[element]['height']
                    n_found += 1
                if float(self.dict[element][0]) > c_max_x and 'width' in self.att_dict[element]:
                    c_max_x = float(self.dict[element][0])
                    max_width = self.att_dict[element]['width']
                    n_found += 1
                if float(self.dict[element][1]) > c_max_y and 'height' in self.att_dict[element]:
                    max_len = self.att_dict[element]['height']
                    n_found += 1
                    c_max_y = float(self.dict[element][1])
        h, w = None, None
        if n_found >= 4:
            h = (float(max_len) / 2.0) + (float(min_len) / 2.0) + abs(c_max_y - c_min_y)
            w = (float(max_width) / 2.0) + (float(min_width) / 2.0) + abs(c_max_x - c_min_x)
        return str(h), str(w)

    def __calculateTransformedCoordinates(self, origX, origY, transform):
        """Calculate the final coordinates of an element given its original
        coordinates and a transform matrix.
        See https://www.w3.org/TR/SVG/coords.html#TransformMatrixDefined
        :param origX: X coordinate before transformation
        :param origY: Y coordinate before transformation
        :param transform: [a,b,c,d,e,f] transform matrix
        :return: A (x, y) pair containing the final coordinates of 
        the element
        """
        a = transform[0]
        b = transform[1]
        c = transform[2]
        d = transform[3]
        e = transform[4]
        f = transform[5]
        """
        Transformation Matrix:
                      [ a c e ]
        transMatrix = [ b d f ]
                      [ 0 0 1 ]
        """
        transMatrix = [[a, c, e], [b, d, f], [0.0, 0.0, 1.0]]
        """
        [ Xfinal ]                  [ Xoriginal ]
        [ Yfinal ] = transMatrix *  [ Yoriginal ]
        [   1    ]                  [     1     ] 
        """
        coorVector = self.__matmult(transMatrix, [[float(origX)], 
                                                  [float(origY)],
                                                  [1.0]])
        return (coorVector[0][0], coorVector[1][0])
    
    def __transformStringToVector(self, transformAttribute):
        """Converts the textual value of a transform attribute to an array
        of parameters for a transform matrix
        :param transformAttribute: the value of an SVG transform attribute
                e.g. 'matrix(1,2,3,4,0,0)' or 'translate(50,50)'
        :return: A vector (list) of transform parameters [a b c d e f]
                e.g. [1,2,3,4,0,0] or [1,0,0,1,50,50] (a translate vector
                gets converted to a transform)
        """
        transform = []
        if transformAttribute and transformAttribute.endswith(')'):
            if transformAttribute.startswith('matrix('):
                transform = transformAttribute[7:-1].split(',')
            elif transformAttribute.startswith('translate('):
                translate = transformAttribute[10:-1].split(',')
                transform = [1, 0, 0, 1].extend(translate)
        return [float(n) for n in transform]
    
    def __matmult(self, a,b):
        """
        Multiply two matrices. From stackoverflow.com/questions/10508021
        """
        zip_b = zip(*b)
        return [[sum(ele_a*ele_b for ele_a, ele_b in zip(row_a, col_b)) 
                 for col_b in zip_b] for row_a in a]
