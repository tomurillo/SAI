#!/usr/bin/env python
from lxml import etree
import sys
import inkex
from RDFReader import RDFReader
from AnnotationEffect import AnnotationEffect

if __name__ == "__main__":
    a = AnnotationEffect()
    a.affect()
    #root = Tk()
    #gui = PickerGUI(root)
    #gui.prepare(root)
    #root.mainloop()
    #root.update_idletasks()
    #root.update()