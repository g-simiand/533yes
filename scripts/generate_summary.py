#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour générer le tableau récapitulatif des performances des modèles.
"""

import sys
from pathlib import Path
# Add the parent directory to sys.path to import modules
sys.path.append(str(Path(__file__).parent.parent))
from reporting import generate_results_md_table

if __name__ == "__main__":
    generate_results_md_table()
    print("Tableau récapitulatif généré avec succès.") 