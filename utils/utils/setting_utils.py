from django.conf import settings
def readable_size_rules():
    rules = sorted(settings.F1L3_FILE_EXPIRATION_SETTINGS.items(), key=lambda k: k[0])
    for index, rule in enumerate(rules):
        limit = f'{rule[1]} hours' if rule[1] != -1 else 'forever'
        rules[index] = (rule[0] / settings.MB, limit)
    return rules
