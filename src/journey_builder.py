from collections import defaultdict


def build_journeys(df_all):
    """
    Reconstruit les parcours clients à partir du DataFrame consolidé.
    Chaque parcours est une liste d'états (expositions et Conversion/No_Conversion).
    Retourne un dict : {customer_id: [ [etats_parcours1], [etats_parcours2], ... ], ...}
    """
    journeys = defaultdict(list)

    for customer_id, group in df_all.groupby('customer_id'):
        group_sorted = group.sort_values('timestamp')
        current_path = ['Start']
        for _, row in group_sorted.iterrows():
            state = row['state']
            if state == 'Conversion':
                current_path.append('Conversion')
                journeys[customer_id].append(current_path)
                current_path = ['Start']
            else:
                current_path.append(state)
        if len(current_path) > 1 and current_path[-1] != 'Conversion':
            current_path.append('No_Conversion')
            journeys[customer_id].append(current_path)

    return journeys