# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import logging

import cobra

logger = logging.getLogger(__name__)


def _is_positive(n):
    """Robustly test if n is positive, yielding True on Exceptions"""
    try:
        if n >= 0:
            return True
        else:
            return False
    except Exception:
        return True


class Frozendict(dict):
    def __init__(self, iterable, **kwargs):
        super(Frozendict, self).__init__(iterable, **kwargs)

    def popitem(self):
        raise AttributeError("'Frozendict' object has no attribute 'popitem")

    def pop(self, k, d=None):
        raise AttributeError("'Frozendict' object has no attribute 'pop")

    def __setitem__(self, key, value):
        raise AttributeError(
            "'Frozendict' object has no attribute '__setitem__")

    def setdefault(self, k, d=None):
        raise AttributeError(
            "'Frozendict' object has no attribute 'setdefault")

    def __delitem__(self, key):
        raise AttributeError(
            "'Frozendict' object has no attribute '__delitem__")

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def update(self, E=None, **F):
        raise AttributeError("'Frozendict' object has no attribute 'update")


class AutoVivification(dict):
    """Implementation of perl's autovivification feature. Checkout
    http://stackoverflow.com/a/652284/280182 """

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


def add_exchange(model, metabolite, demand=True, prefix='DM_', bound=1000.0):
    """Add an exchange reaction for a metabolite (demand=TRUE: metabolite
    --> Ø or demand=False: 0 --> metabolite )

    Parameters
    ----------
    model : cobra.core.Model
        The model to add the exchange reaction to.
    metabolite : cameo.core.Metabolite
    demand : bool, optional
        True for sink type exchange, False for uptake type exchange
    prefix : str, optional
        A prefix that will be added to the metabolite ID to be used as the
        demand reaction's ID (defaults to 'DM_').
    bound : float, optional
        Upper bound for sink reaction / lower bound for uptake (multiplied
        by -1)

    Returns
    -------
    Reaction
        The created exchange reaction.
    """
    reaction_id = str(prefix + metabolite.id)
    m_name = metabolite.name
    name = "Exchange %s" % m_name if prefix != "DM_" else "Demand %s" % m_name
    if reaction_id in model.reactions:
        raise ValueError("The metabolite already has a demand reaction.")

    reaction = cobra.core.Reaction(id=reaction_id, name=name)
    reaction.add_metabolites({metabolite: -1})
    reaction.bounds = (0, bound) if demand else (-bound, 0)
    model.add_reactions([reaction])
    return reaction