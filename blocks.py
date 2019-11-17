import os
from compas_fofin.datastructures import Cablenet
from compas_rhino.artists import MeshArtist
from compas.datastructures import Mesh
from compas.datastructures import mesh_flip_cycles
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import offset_polygon
from compas.geometry import intersection_line_plane
from compas.utilities import pairwise

# ==============================================================================
# Set the path to the input file.
# The input file was generated with `FOFIN_to`, which serialises the cablenet
# data structure to JSON.
# ==============================================================================

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'cablenet.json')

# ==============================================================================
# Make a cablenet.
# ==============================================================================

cablenet = Cablenet.from_json(FILE_I)

# ==============================================================================
# Flip the cycles of the mesh because the cycles are currently such that the
# normals point to the interior of the structure.
# Note that you could also just flip the cycles once and update the JSON file.
# ==============================================================================

mesh_...(cablenet)

# ==============================================================================
# Set the value of the thickness of the foam blocks in [m].
# Set the value of the offset distance for the edges of the faces to create space
# for the ribs.
# ==============================================================================

THICKNESS = 0.060
OFFSET = 0.020

# ==============================================================================
# Generate the formwork blocks.
# ==============================================================================

blocks = []

for fkey in cablenet.faces():
    
    vertices = cablenet.face_vertices(fkey)
    points = ...

    # the edges of the bottom face polygon have to be offset to create space
    # for the ribs.

    bottom = ...

    # the vertices of the top face are the intersection points of the face normal
    # placed at each (offset) bottom vertex and a plane perpendicular to the 
    # face normal placed at a distance THICKNESS along the face normal from the
    # face centroid.

    # define the plane
    origin = ...
    normal = ...
    plane = add_vectors(origin, ...), normal

    top = []
    for a in bottom:
        b = ...
        ... = intersection_line_plane(...)
        top.append(...)

    top[:] = ...

    vertices = ... + ...
    faces = [[0, 3, 2, 1], ..., [3, 0, 4, 7], [2, 3, 7, 6], [1, 2, 6, 5], [0, 1, 5, 4]]

    block = Mesh.from_...(...)

    blocks.append(block)

# ==============================================================================
# Visualize the block with a mesh artist in the specified layer. Use
# `draw_faces` (with `join_faces=True`) instead of `draw_mesh` to get a flat
# shaded result. Also draw the vertex labels tovisualize the cycle directions.
# ==============================================================================

artist = MeshArtist(None, layer="...")
artist.clear_layer()

for mesh in blocks:
    ...
