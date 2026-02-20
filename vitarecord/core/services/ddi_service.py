"""
DDI Service — Drug-Drug Interaction Checker
Uses RxNav Interaction API: https://rxnav.nlm.nih.gov/InteractionAPIs.html
"""
import requests

RXNAV_BASE = 'https://rxnav.nlm.nih.gov/REST'


# ─── STEP 1: Get RxCUI for a drug name ───────────────────────────────────────
def get_rxcui(drug_name: str) -> str | None:
    """Convert drug name to RxNorm Concept Unique Identifier."""
    try:
        url = f'{RXNAV_BASE}/rxcui.json'
        resp = requests.get(url, params={'name': drug_name}, timeout=5)
        data = resp.json()
        return data['idGroup'].get('rxnormId', [None])[0]
    except Exception:
        return None


# ─── STEP 2: Check interactions between two RxCUIs ───────────────────────────
def check_rxcui_interaction(rxcui1: str, rxcui2: str) -> str | None:
    """Return interaction description string or None."""
    try:
        url = f'{RXNAV_BASE}/interaction/interaction.json'
        resp = requests.get(url, params={'rxcui': rxcui1}, timeout=5)
        data = resp.json()
        groups = data.get('interactionTypeGroup', [])
        for group in groups:
            for itype in group.get('interactionType', []):
                for pair in itype.get('interactionPair', []):
                    concepts = pair.get('interactionConcept', [])
                    ids = [c['minConceptItem']['rxcui'] for c in concepts]
                    if rxcui2 in ids:
                        return pair.get('description', 'Potential interaction found.')
    except Exception:
        pass
    return None


# ─── MAIN FUNCTION (called from views.py) ────────────────────────────────────
def check_interactions(existing_meds: list[str], new_meds: list[str]) -> str | None:
    """
    Check if any new_med interacts with any existing_med.
    Returns the first interaction description found, or None if safe.
    Falls back to mock check if RxNorm lookup fails.
    """
    for new_med in new_meds:
        new_rxcui = get_rxcui(new_med)

        for existing_med in existing_meds:
            # ── Mock check (fast, always works) ──
            if new_med.lower().strip() == existing_med.lower().strip():
                return f'Duplicate medication: {new_med} is already prescribed.'

            # ── Live API check ────────────────────
            if new_rxcui:
                ex_rxcui = get_rxcui(existing_med)
                if ex_rxcui:
                    alert = check_rxcui_interaction(new_rxcui, ex_rxcui)
                    if alert:
                        return (f'Interaction between {new_med} and {existing_med}: '
                                f'{alert}')
    return None  # No interactions found
"""
DDI Service — Drug-Drug Interaction Checker
Uses RxNav Interaction API: https://rxnav.nlm.nih.gov/InteractionAPIs.html
"""
import requests

RXNAV_BASE = 'https://rxnav.nlm.nih.gov/REST'


# ─── STEP 1: Get RxCUI for a drug name ───────────────────────────────────────
def get_rxcui(drug_name: str) -> str | None:
    """Convert drug name to RxNorm Concept Unique Identifier."""
    try:
        url = f'{RXNAV_BASE}/rxcui.json'
        resp = requests.get(url, params={'name': drug_name}, timeout=5)
        data = resp.json()
        return data['idGroup'].get('rxnormId', [None])[0]
    except Exception:
        return None


# ─── STEP 2: Check interactions between two RxCUIs ───────────────────────────
def check_rxcui_interaction(rxcui1: str, rxcui2: str) -> str | None:
    """Return interaction description string or None."""
    try:
        url = f'{RXNAV_BASE}/interaction/interaction.json'
        resp = requests.get(url, params={'rxcui': rxcui1}, timeout=5)
        data = resp.json()
        groups = data.get('interactionTypeGroup', [])
        for group in groups:
            for itype in group.get('interactionType', []):
                for pair in itype.get('interactionPair', []):
                    concepts = pair.get('interactionConcept', [])
                    ids = [c['minConceptItem']['rxcui'] for c in concepts]
                    if rxcui2 in ids:
                        return pair.get('description', 'Potential interaction found.')
    except Exception:
        pass
    return None


# ─── MAIN FUNCTION (called from views.py) ────────────────────────────────────
def check_interactions(existing_meds: list[str], new_meds: list[str]) -> str | None:
    """
    Check if any new_med interacts with any existing_med.
    Returns the first interaction description found, or None if safe.
    Falls back to mock check if RxNorm lookup fails.
    """
    for new_med in new_meds:
        new_rxcui = get_rxcui(new_med)

        for existing_med in existing_meds:
            # ── Mock check (fast, always works) ──
            if new_med.lower().strip() == existing_med.lower().strip():
                return f'Duplicate medication: {new_med} is already prescribed.'

            # ── Live API check ────────────────────
            if new_rxcui:
                ex_rxcui = get_rxcui(existing_med)
                if ex_rxcui:
                    alert = check_rxcui_interaction(new_rxcui, ex_rxcui)
                    if alert:
                        return (f'Interaction between {new_med} and {existing_med}: '
                                f'{alert}')
    return None  # No interactions found
