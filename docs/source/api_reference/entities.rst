.. py:currentmodule:: lizzy.entities

lizzy.entities
==============


.. autoclass:: lizzy.entities.Node

    .. rubric:: Attributes

    .. autoattribute:: Node.idx
    .. autoattribute:: Node.coords
    .. autoattribute:: Node.triangles
    .. autoattribute:: Node.triangle_ids
    .. autoattribute:: Node.lines
    .. autoattribute:: Node.line_ids
    .. autoattribute:: Node.nodes
    .. autoattribute:: Node.node_ids

.. autoclass:: lizzy.entities.Line

    .. rubric:: Attributes

    .. autoattribute:: Line.idx
    .. autoattribute:: Line.nodes
    .. autoattribute:: Line.midpoint

.. autoclass:: lizzy.entities.Triangle

    .. rubric:: Attributes

    .. autoattribute:: Triangle.idx
    .. autoattribute:: Triangle.material_tag
    .. autoattribute:: Triangle.A
    .. autoattribute:: Triangle.h
    .. autoattribute:: Triangle.k
    .. autoattribute:: Triangle.porosity
    .. autoattribute:: Triangle.nodes
    .. autoattribute:: Triangle.node_ids
    .. autoattribute:: Triangle.lines
    .. autoattribute:: Triangle.line_ids
    .. autoattribute:: Triangle.centroid
    .. autoattribute:: Triangle.n

.. autoclass:: lizzy.entities.CV

    .. rubric:: Attributes

    .. autoattribute:: CV.node
    .. autoattribute:: CV.idx
    .. autoattribute:: CV.area
    .. autoattribute:: CV.vol
