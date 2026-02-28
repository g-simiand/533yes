"""Métriques et fonctions de calcul pour l'évaluation HTR/OCR."""

import re


def clean_text_for_wer(text):
    """
    Nettoie le texte pour le calcul du WER en supprimant les marqueurs [XXX],
    les balises markdown au début et à la fin, et tout texte de réflexion avant la transcription.
    Gère plusieurs cas de formatage markdown.
    """
    # Supprimer les marqueurs [XXX]
    text = re.sub(r'\[XXX\]', '', text)
    
    # Cas 1: Bloc markdown complet avec ```markdown ... ```
    if re.search(r'```markdown.*?```', text, re.DOTALL):
        match = re.search(r'```markdown(.*?)```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    
    # Cas 2: Bloc markdown sans spécifier "markdown" - ```...```
    elif re.search(r'```.*?```', text, re.DOTALL):
        match = re.search(r'```(.*?)```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    
    # Cas 3: Texte qui commence par ```markdown mais sans fermeture
    elif text.strip().startswith('```markdown'):
        text = re.sub(r'^```markdown\s*', '', text).strip()
    
    # Cas 4: Texte qui commence par ``` mais sans fermeture
    elif text.strip().startswith('```'):
        text = re.sub(r'^```\s*', '', text).strip()
    
    # Cas 5: Texte qui se termine par ``` mais sans ouverture
    elif text.strip().endswith('```'):
        text = re.sub(r'\s*```$', '', text).strip()
    
    # Cas 6: Si le mot "markdown" apparaît seul au début
    elif text.strip().startswith('markdown'):
        text = re.sub(r'^markdown\s*', '', text).strip()
    
    # Cas 7: Si le modèle a réfléchi avant de donner sa réponse
    # Chercher des indicateurs de fin de réflexion
    reflection_markers = [
        r'Voici la transcription\s*:', 
        r'Transcription\s*:', 
        r'Voici le texte\s*:',
        r'Le texte transcrit\s*:',
        r'Ma transcription\s*:',
        r'Voici ma transcription\s*:',
        r'Texte transcrit\s*:',
        r'Contenu du document\s*:'
    ]
    
    for marker in reflection_markers:
        match = re.search(marker, text)
        if match:
            # Ne garder que ce qui suit le marqueur
            text = text[match.end():].strip()
            break
    
    # Normaliser les espaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def calculate_wer(reference: str, hypothesis: str) -> float:
    """
    Calculate Word Error Rate (WER) between reference and hypothesis texts.
    
    Args:
        reference: The reference text (ground truth)
        hypothesis: The hypothesis text (prediction)
        
    Returns:
        float: WER score (0.0 = perfect match, 1.0 = all words wrong)
    """
    # Nettoyer les textes avant le calcul
    reference = clean_text_for_wer(reference)
    hypothesis = clean_text_for_wer(hypothesis)
    
    # Diviser en mots
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    # Si la référence est vide, retourner 1.0 si l'hypothèse n'est pas vide, sinon 0.0
    if len(ref_words) == 0:
        return 1.0 if len(hyp_words) > 0 else 0.0
    
    # Create a matrix to store the edit distances
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    
    # Initialize matrix edges
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j
    
    # Fill the matrix using Levenshtein distance algorithm
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion = d[i][j-1] + 1
                deletion = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    
    # The bottom-right cell contains the edit distance
    edit_distance = d[len(ref_words)][len(hyp_words)]
    return edit_distance / len(ref_words)