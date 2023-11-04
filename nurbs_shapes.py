import maya.cmds as cmds
import shape_helpers

PYRAMID = [[-2.015927314758301, 0.0, -2.015927314758301], [0.0, 4.321531772613525, 0.0], [2.015927314758301, 0.0, -2.015927314758301], [0.0, 4.321531772613525, 0.0], [-2.015927314758301, 0.0, 2.015927314758301], [0.0, 4.321531772613525, 0.0], [2.015927314758301, 0.0, 2.015927314758301], [0.0, 4.321531772613525, 0.0], [2.0159272919161877, 0.0, -2.015927291916187], [2.0159272919161877, 0.0, -0.671975763972062], [2.0159272919161877, 0.0, 0.6719757639720614], [2.0159272919161877, 0.0, 2.0159272919161855], [-2.0159272919161855, 0.0, -2.015927291916187], [-0.6719757639720614, 0.0, -2.015927291916187], [0.6719757639720628, 0.0, -2.015927291916187], [2.015927291916187, 0.0, -2.015927291916187], [-2.0159272919161855, 0.0, 2.015927291916187], [-2.0159272919161855, 0.0, 0.671975763972062], [-2.0159272919161855, 0.0, -0.6719757639720614], [-2.0159272919161855, 0.0, -2.0159272919161855], [2.0159272919161877, 0.0, 2.015927291916187], [0.6719757639720627, 0.0, 2.015927291916187], [-0.6719757639720612, 0.0, 2.015927291916187], [-2.0159272919161837, 0.0, 2.015927291916187]]

def circle(name="circle_template", position=[0,0,0]):
    shape = cmds.circle(name=name, center=[0,0,0], normal=[0,1,0], sweep=360, radius=.6, degree=3, constructionHistory=True)[0]
    cmds.move(*position, shape)
    return shape

def pyramid(name="pyramid_template", position=[0,0,0]):
    shape = __from_points(name, PYRAMID)
    cmds.move(*position, shape)
    return shape

def square(name="cube_template", position=[0,0,0]):
    square = cmds.nurbsSquare(name=name, center=[0,0,0], normal=[0,1,0], sideLength1=1, sideLength2=1)[0]

    square_nurbs = cmds.listRelatives(square, children=True)
    shape_helpers.parent_shapes(square_nurbs, square)
    cmds.move(*position, square)

    return square

def __from_points(name, points):
    shape = cmds.curve(name=name, degree=1, point=points, worldSpace=True)
    return shape

def __print_points():
    
    selection = cmds.ls(selection=True)[0]
    points = []
    for cv in cmds.ls(f"{selection}.cv[:]", flatten=True):
        points.append(cmds.xform(cv, query=True, worldSpace=True, translation=True))
    
    print(points)
        

if __name__ == "__main__":
    __print_points()