from core import RoadPath
mainRoad = RoadPath()
mainRoad.roadName = "Main Road"
mainRoad.direction = "south_to_north"
mainRoad.addPoint(773,1963)
mainRoad.addPoint(853,1636)
mainRoad.addPoint(844,1316)
mainRoad.addPoint(860,1165)
mainRoad.addPoint(1093,846)
mainRoad.addPoint(1211,334)
mainRoad.addPoint(1221,146)
mainRoad.addPoint(1223,0)

leftRoadA = RoadPath()
leftRoadA.roadName = "Left Road A"
leftRoadA.direction = "west_to_east"
leftRoadA.addPoint(463,293)
leftRoadA.addPoint(620,220)
leftRoadA.addPoint(1230,140)

leftRoadAr = RoadPath()
leftRoadAr.roadName = "Left Road A R"
leftRoadAr.direction = "east_to_west"
leftRoadAr.addPoint(1230,120)
leftRoadAr.addPoint(620,200)
leftRoadAr.addPoint(463,273)

leftRoadB = RoadPath()
leftRoadB.roadName = "Left Road B"
leftRoadB.direction = "horizontal"
leftRoadB.addPoint(790,1130)
leftRoadB.addPoint(861,1160)


leftRoadC = RoadPath()
leftRoadC.roadName = "Left Road C"
leftRoadC.direction = "horizontal"
leftRoadC.addPoint(683,1280)
leftRoadC.addPoint(773,1336)
leftRoadC.addPoint(843,1316)

leftRoadD = RoadPath()
leftRoadD.roadName = "Left Road D"
leftRoadD.direction = "horizontal"
leftRoadD.addPoint(736,1826)
leftRoadD.addPoint(800,1850)