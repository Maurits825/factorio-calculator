from slpp import slpp as lua
import json

DEFAULT_RESULT_COUNT = 1
DEFAULT_ENERGY_REQUIRED = 0.5
DEFAULT_CATEGORY = 'crafting'


def main():
    with open('raw.txt', 'r') as file:
        raw_data = file.read()

    data = lua.decode(raw_data)
    format_recipes(data)


def format_ingredient_list(ingredient_list):
    formatted_list = []
    for ingredient in ingredient_list:
        if type(ingredient) is dict:
            continue
        else:
            ingredient_dict = dict()
            ingredient_dict['amount'] = ingredient[1]
            ingredient_dict['name'] = ingredient[0]
            ingredient_dict['type'] = 'item'
            formatted_list.append(ingredient_dict)

    return formatted_list


# TODO make this return/create a class not a dict?
# TODO make a recipe class here? with ingredients/inputs, result/outputs, craft/base_time, category
# leave other things the same, so ingredients will be dict, so on? actually wont change the ['name/amount'] in calc func
def format_recipes(data):
    recipes = dict()
    for item in data['recipe']:
        recipes[item] = dict()

        recipes[item]['category'] = data['recipe'][item].get('category', DEFAULT_CATEGORY)

        if 'normal' in data['recipe'][item]:
            current_recipe = data['recipe'][item]['normal']
        else:
            current_recipe = data['recipe'][item]

        recipes[item]['ingredients'] = format_ingredient_list(current_recipe['ingredients'])

        if 'result' in current_recipe:
            result_count = current_recipe.get('result_count', DEFAULT_RESULT_COUNT)
            result = dict()
            result['amount'] = result_count
            result['name'] = current_recipe['result']
            result['type'] = 'unknown'
            recipes[item]['result'] = [result]
        else:
            recipes[item]['result'] = current_recipe['results']

        recipes[item]['craft_time'] = current_recipe.get('energy_required', DEFAULT_ENERGY_REQUIRED)

    file_name = r"recipes.json"
    with open(file_name, "w", newline="\n") as f:
        json.dump(recipes, f, indent=4)


if __name__ == '__main__':
    main()
