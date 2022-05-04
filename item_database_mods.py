from slpp import slpp as lua
import json

DEFAULT_RESULT_COUNT = 1
DEFAULT_ENERGY_REQUIRED = 0.5
DEFAULT_CATEGORY = 'crafting'


def main():
    with open("crafting_data.json") as f:
        crafting_data = json.load(f)

    format_recipes(crafting_data)


def format_ingredient_list(ingredient_list):
    formatted_list = []
    for ingredient in ingredient_list:
        if type(ingredient) is dict:
            formatted_list.append(ingredient)
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
        if item == "sand":
            a = 4

        recipes[item]['category'] = data['recipe'][item].get('category', DEFAULT_CATEGORY)

        current_recipe = data['recipe'][item]

        recipes[item]['ingredients'] = format_ingredient_list(current_recipe['ingredients'])

        recipes[item]['result'] = current_recipe['products']
        for index, result in enumerate(recipes[item]['result']):
            if 'amount_min' in result:
                diff = float(result['amount_max']) - float(result['amount_min'])
                amount = int(float(result['amount_min']) + (diff / 2.0))
                recipes[item]['result'][index]['amount'] = amount

        recipes[item]['craft_time'] = current_recipe.get('energy', DEFAULT_ENERGY_REQUIRED)

    file_name = r"recipes_mods.json"
    with open(file_name, "w", newline="\n") as f:
        json.dump(recipes, f, indent=4)


if __name__ == '__main__':
    main()
