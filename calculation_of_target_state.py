import math

def get_radius_center(vehicle_speed, yaw_rate):
    if yaw_rate == 0.0:
        radius = 100000
    else:
        radius = (180 * vehicle_speed)/(yaw_rate * math.pi)
    return radius

def state_of_target_instantaneous(obj_distlong, obj_distlat, obj_VrelLong, obj_VrelLat, car_YawRateDegS, car_SpeedMs):
    car_StraightRadiusValue = 10000 # m

    car_RadiusCenterX = get_radius_center(car_SpeedMs, car_YawRateDegS)

    turnX = obj_distlat - car_RadiusCenterX
    obj_TurnRadius = math.sqrt(math.pow(obj_distlong, 2) + math.pow(turnX, 2))
    obj_RangeCos = turnX / obj_TurnRadius
    obj_RangeSin = obj_distlong / obj_TurnRadius
    radLaneSpeed = obj_VrelLong

    if car_RadiusCenterX < car_StraightRadiusValue:
        # curve motion - speed recalculation via YawRate
        radLaneSpeed = ((2 * math.pi * obj_TurnRadius) / 360) * car_YawRateDegS
        obj_VabsLong = obj_VrelLong - radLaneSpeed * obj_RangeCos
    else:
        # straight motion - speed recalculation via self speed value
        obj_VabsLong = car_SpeedMs + obj_VrelLong

    obj_VabsLat = obj_VrelLat + radLaneSpeed * obj_RangeSin

    obj_VabsVector = math.sqrt(math.pow(obj_VabsLong, 2) + math.pow(obj_VabsLat, 2))
    # Abs Tan is the absolute angle and to get it right Y must be lateral offset.
    # @VabsTan is the angle - pi to pi where 0 is the direct way.
    obj_VabsTan = math.atan2(obj_VabsLat, obj_VabsLong)

    return obj_VabsVector, obj_VabsTan


def state_of_target(vehicle_velocity_global_y, vehicle_velocity_global_x, target_vx_raw, target_vy_raw, phi):
    target_velocity_global_y = vehicle_velocity_global_y + target_vx_raw * math.cos(phi) + target_vy_raw * math.sin(phi)
    target_velocity_global_x = vehicle_velocity_global_x - target_vx_raw * math.sin(phi) + target_vy_raw * math.cos(phi)

    return target_velocity_global_y, target_velocity_global_x
