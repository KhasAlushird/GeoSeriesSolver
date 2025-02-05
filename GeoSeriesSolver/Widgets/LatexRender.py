
import sys
from PyQt6.QtWebEngineWidgets import QWebEngineView
from sympy import latex,simplify
from PyQt6.QtCore import Qt
import os
import re

# current_dir = os.path.dirname(os.path.abspath(__file__))
# resources_dir = os.path.join(current_dir, '..', 'Resources')
# if resources_dir not in sys.path:
#     sys.path.append(resources_dir)
# from Helpers import latex_render
from GeoSeriesSolver.Resources.Helpers import latex_render


class LatexRender(QWebEngineView):

    def __init__(self):
        super().__init__()

    def render(self,text:str):
        '''
        text 为latex 表达式(str)
        '''
        
        try:
            final_content = latex_render(text)
            self.setHtml(final_content)
        except Exception as e:
            self.setHtml(f"<p>Error: {e}</p>")

    def error_render(self,text:str):
        self.setHtml(f"<p>Error: {text}</p>")





            



    