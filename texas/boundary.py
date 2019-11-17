import os
from compas_fofin.datastructures import Cablenet
from compas_rhino.artists import MeshArtist
from compas_rhino.artists import FrameArtist
from compas_rhino.artists import PointArtist
from compas_rhino.utilities import clear_layer
from compas.datastructures import Mesh

from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.geometry import Frame
from compas.geometry import Transformation
from compas.geometry import transform_points
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import bounding_box_xy
from compas.geometry import offset_polygon
from compas.geometry import intersection_line_plane
from compas.geometry import angles_vectors


from compas.rpc import Proxy
numerical = Proxy('compas.numerical')
pca_numpy = numerical.pca_numpy



HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'data', 'cablenet.json')

cablenet = Cablenet.from_json(FILE_I)

# # ==============================================================================
# # Set an offset parameter to define the distance between the edge of the
# # structure and the location of the boundary frame.
# # Set a padding parameter to add some extra material around the bounding box of
# # the intersection points.
# # Set beam thickness.
# # ==============================================================================

OFFSET = 0.200
PADDING = 0.020
THICKNESS = 0.04

# # ==============================================================================
# # Find the vertices on each boundary, which are all vertices where the
# # attribute `'constraint'` is set to 'NORTH' or `'SOUTH'`. 
# # ==============================================================================


NAMES = ['SOUTH', 'NORTH']


BOUNDARIES = []

# # ==============================================================================
# # Generate beams for each boundary
# # ==============================================================================

for name in NAMES:

    l = list(cablenet.vertices_where({'constraint': str(name)}))
    boundary = list(cablenet.vertices_on_boundary(ordered=True))
    l[:] = [key for key in boundary if key in l]


# # ==============================================================================
# # Construct the local axes of the boundary. Align the xaxis with the
# # main span of the boundary and the y axis with the world z axis. Use local x
# # and y to compute local z.
# # ==============================================================================

    a = cablenet.vertex_coordinates(l[0])
    b = cablenet.vertex_coordinates(l[-1])  

    xaxis = subtract_vectors(b, a)
    yaxis = [0, 0, 1.0]
    zaxis = cross_vectors(xaxis, yaxis)  

    xaxis = cross_vectors(yaxis, zaxis)

# # # ==============================================================================
# # # Construct the frame of the  boundary using first point on the list of vertices
# # # ==============================================================================

    frame_0 = Frame(a, xaxis, yaxis)


# # # ==============================================================================
# # # Construct an intersection plane from the frame of the boundary. Use the origin
# # # of the frame as the plane point and the z axis of the frame as the plane normal.
# # # Move the plane along the normal by the defined offset.
# # # ==============================================================================

    normal = frame_0.zaxis
    point_front = add_vectors(frame_0.point, scale_vector(frame_0.zaxis, OFFSET))
    plane_front = point_front, normal

    point_back = add_vectors(frame_0.point, scale_vector(frame_0.zaxis, OFFSET+THICKNESS))
    plane_back = point_back, normal

    # artist = FrameArtist(frame_0, layer= name + '::Frame', scale=0.3)
    # artist.clear_layer()
    # artist.draw()
    
# # # ==============================================================================
# # # Compute the intersections of the residual force vectors at the boundary
# # # vertices with the previously defined intersection plane.
# # # ==============================================================================

    intersections_front = []
    intersections_back = []
    pca_points = []


    for key in l:
        a = cablenet.vertex_coordinates(key)
        r = cablenet.residual(key)
        b = add_vectors(a, r)
        x_front = intersection_line_plane((a, b), plane_front)
        x_back = intersection_line_plane((a, b), plane_back)
        move_point_to_front = add_vectors(x_back, scale_vector(frame_0.zaxis, -THICKNESS))

        intersections_front.append(x_front)
        intersections_back.append(x_back)
        pca_points.append(x_front)
        pca_points.append(move_point_to_front )


    PointArtist.draw_collection(intersections_back, layer=name + "::Intersections_back", clear=True)
    PointArtist.draw_collection(pca_points, layer=name + "::Intersections_front", clear=True)

# # ==============================================================================
# # Generate a beam every 3 vertices of the boundary. Compute a local frame for the 
# # selected vertices using a PCA of the vertex locations.
# # ==============================================================================


    step = 6
    start = 0
    end = step
    clear_layer(name + "::Beams", include_children=True, include_hidden=True)

    while end <= len(pca_points):
        points = pca_points[start:end]

        start = end
        end += (step)

        origin, axes, values = pca_numpy(points)
        frame = Frame(origin, axes[0], axes[1])

# # ==============================================================================
# # Transform the local coordinates to world coordinates to make it an axis-aligned
# # problem.
# # ==============================================================================

        X = Transformation.from_frame_to_frame(frame, Frame.worldXY())
        points = transform_points(points, X)        

# # ==============================================================================
# # Compute the axis aligned bounding box in world coordinates, ignoring the Z
# # components of the points. Add some padding to the bounding box to avoid having
# # vertices on the boundaries of the box. Convert the box back to the local
# # coordinate system.
# # ============================================================================== 

        front = bounding_box_xy(points)
        front = offset_polygon(front, -PADDING)
        front = transform_points(front, X.inverse())

# # ==============================================================================
# # Check if boundary normal and local normal have the same direction, if not reverse
# # list of vertices. Create a 3D box by moving the vertices of the found 2D bounding
# # box along the z-axis of the boundary coordinate system.
# # ============================================================================== 

        back =[]
        angle = angles_vectors(frame.zaxis, frame_0.zaxis, deg=False)

        if angle[0] !=  0:
            front.reverse()    


        for v in front:
            vertex = add_vectors(v, scale_vector(frame_0.zaxis, THICKNESS))
            back.append(vertex)

# # ==============================================================================
# # Convert the box to a mesh for visualisation.
# # ==============================================================================       

        bbox = front + back
        faces = [[0, 3, 2, 1], [4, 5, 6, 7], [3, 0, 4, 7], [2, 3, 7, 6], [1, 2, 6, 5], [0, 1, 5, 4]]    
        beam = Mesh.from_vertices_and_faces(bbox, faces)

        artist = MeshArtist(beam, layer=name + "::Beams")
        artist.draw_mesh()


# # ==============================================================================
# # Visualise cablenet
# # ==============================================================================

artist = MeshArtist(cablenet, layer="Cablenet::Mesh")
artist.clear_layer()
artist.draw_mesh()

