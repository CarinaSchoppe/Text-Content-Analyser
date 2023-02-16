def filter(string, words_to_contain: tuple, filtered_items, header, ignore=True, intense=False, block=True, absatz=None):
    # filter wird angewendet gehe alle elemente durch
    amount_tuple, words = words_to_contain[0], words_to_contain[1]
    # soll der filter angewendet werden
    if ignore:
        if block:
            block_dict = dict()
            block_dict[string] = dict()
            if header in filtered_items:
                filtered_items[header][string] = dict()
            else:
                filtered_items[header] = block_dict
        else:
            for word in words:
                if word in string:  # wort im satz
                    if word in filtered_items[header][absatz]:
                        if string.lstrip() not in filtered_items[header][absatz][word]:
                            filtered_items[header][absatz][word].append(string.lstrip())
                    else:
                        filtered_items[header][absatz][word] = [string.lstrip()]
        return True


    amount = 0
    # wie oft der begriff vorgekommen ist
    if block:
        for word in words:
            if word in string:
                amount += 1

        # der satz oder absatz ist gültig
        if amount >= amount_tuple:
            # der string ist important
            # subsätze bzw. mehrere einträge pro artikel werden nicht gestattet
            block_dict = dict()
            block_dict[string] = dict()
            if intense:
                filtered_items[header] = block_dict
            # integriere mehrere einträge pro artikel
            else:
                if header in filtered_items:
                    filtered_items[header][string] = dict()

                else:
                    # liste block zu einem titel
                    # zu einem block eine liste von sätzen
                    filtered_items[header] = block_dict

                    # zu jedem titel bekommen wir ein dict mit einem block zu jedem block eine liste von sätzen
            return True
        else:
            return False
    else:
        for word in words:
            if word in string:  # wort im satz
                if word in filtered_items[header][absatz]:
                    if string.lstrip() not in filtered_items[header][absatz][word]:
                        filtered_items[header][absatz][word].append(string.lstrip())
                else:
                    filtered_items[header][absatz][word] = [string.lstrip()]


# diese methode filtert ob das mehrere subeinträge unterer einem punkt nicht erlaubt sind oder komprimiert werden
# sollen
# nimm nur den ersten eintrag in einem bereich wo die kombination der möglichkeiten bereits vorgekommen ist
def cleanup(data):
    for key, dict_list in data.items():  # title & [dicts]
        subjects = list()
        for result in dict_list:  # results = dict -> {'subject': 'startup', 'relation': 'has raised', 'object': '€ 10 million'}
            is_in = False
            for subject, information in result.items():  # subject, startup
                for item in subjects:  # dict (new) in list(dicts) new
                    if information in item.values():
                        is_in = True
                        break
                if is_in:
                    break
            if not is_in:
                subjects.append(result)
        data[key] = subjects
    return data


# umwandeln des ca verfahrens in eine stanford struktur
def sentence_creator(items: dict, senten: bool = True, stanford_only: bool = False) -> dict:
    # input ("code", "title") -> items: text
    # output "title" -> text
    result_dict = dict()
    for key, item in items.items():
        for text, contents in item.items():
            if senten and not stanford_only:
                for cat, sentences in contents.items():
                    for sentence in sentences:
                        if key in result_dict:
                            if sentence not in result_dict[key]:
                                result_dict[key] += sentence + " "
                        else:
                            result_dict[key] = sentence + " "
            else:
                if key in result_dict:
                    result_dict[key] += text + " "
                else:
                    result_dict[key] = text + " "
    return result_dict
