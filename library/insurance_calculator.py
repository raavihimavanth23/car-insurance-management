from datetime import datetime
def calculate_max_assurance(car, policy, car_damages):
    current_year = datetime.now().year
    car_age = current_year - car.car_year

    # Depreciation factor: Assuming 5% depreciation per year
    depreciation_factor = 1 - (0.05 * car_age)
    max_assurance = policy.max_assurance * depreciation_factor

    # Adjust for earlier car damages.
    damage = 0
    for d in car_damages:
        if d.severity is 'Low':
            damage += 0.02
        elif d.severity is 'Moderate':
            damage += 0.03
        else: 
            damage += 0.04

    max_assurance *= (1-damage)

    # Ensure max assurance is within policy limits
    max_assurance = max(policy.min_assurance, min(max_assurance, policy.max_assurance))
    print('calculated max_assurance: ', max_assurance, 'policy_max_assurance', policy.max_assurance)
    return max_assurance

