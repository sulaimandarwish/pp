import math
from collections import Counter
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopAbs import TopAbs_SOLID, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.Bnd import Bnd_OBB
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder

def v3(v): return [v.X(), v.Y(), v.Z()]
def parallel(a,b): return abs(sum(x*y for x,y in zip(a,b))) > math.cos(math.radians(3))

def analyse_step(path):
    reader=STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone: raise ValueError("STEP file could not be read.")
    reader.TransferRoots()
    shape=reader.OneShape()
    solids=[]
    ex=TopExp_Explorer(shape,TopAbs_SOLID)
    while ex.More(): solids.append(ex.Current()); ex.Next()
    if not solids: raise ValueError("No solid bodies found. Export a watertight solid STEP.")
    if len(solids)>1: raise ValueError(f"This file contains {len(solids)} solids. Upload one manufacturable part at a time.")
    solid=solids[0]
    if not BRepCheck_Analyzer(solid).IsValid(): raise ValueError("The STEP solid is invalid or needs repair.")
    vp,ap=GProp_GProps(),GProp_GProps()
    BRepGProp.VolumeProperties_s(solid,vp); BRepGProp.SurfaceProperties_s(solid,ap)
    volume=abs(vp.Mass()); area=abs(ap.Mass())
    box=Bnd_OBB(); BRepBndLib.AddOBB_s(solid,box,False,True,False)
    dims=[2*box.XHSize(),2*box.YHSize(),2*box.ZHSize()]
    axes=[v3(box.XDirection()),v3(box.YDirection()),v3(box.ZDirection())]
    faces=Counter(); cyl=[]; directions=[]; oblique=False
    ex=TopExp_Explorer(solid,TopAbs_FACE)
    while ex.More():
        face=TopoDS.Face_s(ex.Current()); surf=BRepAdaptor_Surface(face); kind=surf.GetType()
        if kind==GeomAbs_Plane: faces["planar"]+=1
        elif kind==GeomAbs_Cylinder:
            faces["cylindrical"]+=1; c=surf.Cylinder(); axis=v3(c.Axis().Direction()); cyl.append(c)
            if not any(parallel(axis,d) for d in directions): directions.append(axis)
            if not any(parallel(axis,a) for a in axes): oblique=True
        else: faces["complex"]+=1
        ex.Next()
    turning=bool(cyl) and not faces["complex"]
    reasons=[]
    if turning: route="TURNING CANDIDATE"
    elif faces["complex"]: route="COMPLEX MILLING / MANUAL REVIEW"
    elif oblique: route="INDEXED / ANGLED MILLING"
    else: route="3-AXIS MILLING CANDIDATE"
    if turning: reasons.append("Rotational geometry detected; a turning-specific cycle model is not enabled.")
    if faces["complex"]: reasons.append("Complex surfaces need CAM/tool-access review.")
    if oblique: reasons.append("Oblique cylindrical axes may need indexed workholding or extra setups.")
    setups=max(1,1+len(directions)//2)
    return {"units":"mm","dimensions_mm":dims,"volume_mm3":volume,"surface_area_mm2":area,
            "face_counts":dict(faces),"solid_count":1,"cylinder_axis_groups":len(directions),
            "route":route,"assumed_setups":setups,"estimate_allowed":not reasons,
            "review_reasons":reasons,
            "limitations":["STEP geometry does not prove tolerances, threads, tool accessibility, fixturing or stock availability.",
                           "No CAM toolpath or collision simulation is performed.",
                           "Complex and rotational parts are deliberately flagged rather than falsely priced."]}
