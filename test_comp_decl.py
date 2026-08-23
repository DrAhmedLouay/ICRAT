
import os
import streamlit.components.v1 as components

comp_dir = '/Users/ahmedlouay/.gemini/antigravity/scratch/iraq_construction_risk_tool/iraq_map_component'
os.makedirs(comp_dir, exist_ok=True)
my_comp = components.declare_component('iraq_map_component', path=comp_dir)
print('Declared successfully in module:', my_comp)
