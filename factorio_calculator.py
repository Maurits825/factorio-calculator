import json

#TODO better way for this, save as json of something?
DEFAULT_ASSEMBLY_CRAFT_SPEED = 1.25
DEFAULT_ASSEMBLY_SPEED_MOD = 340
DEFAULT_ASSEMBLY_PROD_MOD = 40

DEFAULT_CRAFT_FLUID_CRAFT_SPEED = 1.25
DEFAULT_CRAFT_FLUID_SPEED_MOD = 140
DEFAULT_CRAFT_FLUID_PROD_MOD = 40

DEFAULT_CHEM_CRAFT_SPEED = 1
DEFAULT_CHEM_SPEED_MOD = 355
DEFAULT_CHEM_PROD_MOD = 30

DEFAULT_OIL_CRAFT_SPEED = 1
DEFAULT_OIL_SPEED_MOD = 355
DEFAULT_OIL_PROD_MOD = 30

DEFAULT_SMELT_CRAFT_SPEED = 2
DEFAULT_SMELT_SPEED_MOD = 370
DEFAULT_SMELT_PROD_MOD = 20

DEFAULT_DRILL_CRAFT_SPEED = 0.5
DEFAULT_DRILL_SPEED_MOD = 350
DEFAULT_DRILL_PROD_MOD = 70

DEFAULT_PUMPJACK_CRAFT_SPEED = 1
DEFAULT_PUMPJACK_SPEED_MOD = 150
DEFAULT_PUMPJACK_PROD_MOD = 70


class AssemblySetup:
    def __init__(self, craft_speed, speed_mod, prod_mod, name):
        self.craft_speed = craft_speed
        self.speed_mod = speed_mod
        self.prod_mod = prod_mod

        self.name = name


class ItemInfo:
    def __init__(self, item, base_time, inputs, outputs, assembly_setup):
        self.item = item
        self.base_time = base_time

        self.inputs = inputs
        self.input_list = []
        self.outputs = outputs

        self.assembly_setup = assembly_setup

        self.output_pas = dict()
        self.output_yield_ps = dict()
        self.assemblies_required = 0

        self.input_pas = dict()
        self.input_yield_ps = dict()


class FactorioCalculator:
    def __init__(self):
        self.recipes = None

    def load_recipes(self, json_file):
        """
        Loads the json recipe file to a dictionary
        :param json_file: json file name
        :return: dictionary of the json file
        """
        with open(json_file) as f:
            self.recipes = json.load(f)

    # TODO check if factorio gives total speed, or you have to - the prod speed loss, i think its total
    def get_craft_time(self, base_time, craft_speed, speed_mod):
        """
        Return the time in second to craft a resource
        :param base_time: base time in seconds to craft the resource
        :param craft_speed: craft speed of the assembly/refinery/plant etc...
        :param speed_mod: total speed % of the speed modules
        :return: time in seconds to craft a resource
        """
        return base_time / (craft_speed + (craft_speed * speed_mod/100))

    def get_output_pas(self, assembly_setup: AssemblySetup, base_time, output_count):
        """
        Returns the resources crafted per assembly-seconds (pas)
        :param assembly_setup: AssemblySetup class
        :param base_time: base time in seconds to craft the resource
        :param output_count: output yield of crafting the resource
        :return: number of resources crafted pas, ie per assembly per second
        """
        craft_time = self.get_craft_time(base_time, assembly_setup.craft_speed, assembly_setup.speed_mod)
        return (output_count + (output_count * assembly_setup.prod_mod / 100)) / craft_time

    def get_input_pas(self, craft_time, input_count):
        """
        Returns the input resources need per assembly-seconds (pas)
        :param craft_time: craft time in seconds
        :param input_count: input yield needed to craft the resource
        :return: number resources need pas
        """
        return input_count / craft_time

    def get_assembly_requirements(self, wanted_yield, pas):
        """
        Returns the number of assemblies needed to provide the wanted yield
        :param wanted_yield: Wanted yield of the resource per second
        :param pas: per assembly-seconds of the resource
        :return: number of assemblies needed
        """
        return wanted_yield / pas

    def get_input_per_sec_requirements(self, assembly_num, pas):
        """
        Return the number of resources needed per seconds to provide the num of assemblies
        :param assembly_num: number of assembly used
        :param pas: pas of the input
        :return: resource per seconds
        """
        return pas * assembly_num

    def get_item_info(self, item, recipe, assembly_setup, wanted_yield):
        item_info = ItemInfo(item, recipe['craft_time'], recipe['ingredients'], recipe['result'],
                             assembly_setup)

        item_info.output_yield_ps = wanted_yield

        for output in item_info.outputs:
            item_name = output['name']
            item_info.output_pas[item_name] = self.get_output_pas(assembly_setup, item_info.base_time,
                                                                  output['amount'])
            item_info.assemblies_required = self.get_assembly_requirements(wanted_yield[item],
                                                                           item_info.output_pas[item_name])
            # TODO make print summary a func
            print("To make " + str(round(wanted_yield[item], 2)) + " " + item_name + " per sec, " +
                  "you need " + str(round(item_info.assemblies_required, 2)) + " " + assembly_setup.name)

        for input_item in item_info.inputs:
            # TODO craft time is calced twice, this is OUTPUT craft time!
            item_name = input_item['name']
            craft_time = self.get_craft_time(item_info.base_time, assembly_setup.craft_speed,
                                             assembly_setup.speed_mod)
            item_info.input_pas[item_name] = self.get_input_pas(craft_time, input_item['amount'])
            item_info.input_yield_ps[item_name] = self.get_input_per_sec_requirements(
                item_info.assemblies_required,
                item_info.input_pas[item_name])
            item_info.input_list.append(item_name)

        return item_info

    def calculate(self, item, wanted_yield):
        items = [item]
        wanted_yield_dict = {item: wanted_yield}
        info_list = []

        self.calculate_input_tree(items, wanted_yield_dict, info_list, 0)
        self.print_tree_summary(info_list)

    def calculate_input_tree(self, items, wanted_yield, item_info_list, depth_index):
        """

        :param items:
        :param wanted_yield:
        :param item_info_list:
        :param depth_index:
        :return:
        """
        for item in items:
            try:
                recipe = self.recipes[item]
            except KeyError:
                # TODO check if item is actually a resource, could be a typo
                recipe = dict()
                # TODO better way?
                if item == "crude-oil":
                    recipe['category'] = "fluid-resource"
                else:
                    recipe['category'] = "resource"
                recipe['ingredients'] = []

                result = dict()
                result['amount'] = 1
                result['name'] = item
                result['type'] = 'unknown'
                recipe['result'] = [result]

                recipe['craft_time'] = 1 #TODO its 2 for uranium

            category = recipe['category']

            # TODO how to handle yield for multiple outputs? -- oil processing and stuff -
            # TODO handle some fluids also, look at naming, the naming might not be the actual output like in crafting

            if category == "crafting" or category == "advanced-crafting" or category == "basic-crafting":
                assembly_setup = AssemblySetup(DEFAULT_ASSEMBLY_CRAFT_SPEED, DEFAULT_ASSEMBLY_SPEED_MOD,
                                               DEFAULT_ASSEMBLY_PROD_MOD, "assembling-machine-3")
            elif category == "crafting-with-fluid":
                assembly_setup = AssemblySetup(DEFAULT_CRAFT_FLUID_CRAFT_SPEED, DEFAULT_CRAFT_FLUID_SPEED_MOD,
                                               DEFAULT_CRAFT_FLUID_PROD_MOD, "assembling-machine-3")
            elif category == "smelting":
                assembly_setup = AssemblySetup(DEFAULT_SMELT_CRAFT_SPEED, DEFAULT_SMELT_SPEED_MOD,
                                               DEFAULT_SMELT_PROD_MOD, "electric-furnace")
            elif category == "resource":
                assembly_setup = AssemblySetup(DEFAULT_DRILL_CRAFT_SPEED, DEFAULT_DRILL_SPEED_MOD,
                                               DEFAULT_DRILL_PROD_MOD, "electric-mining-drill")
            elif category == "fluid-resource":
                assembly_setup = AssemblySetup(DEFAULT_PUMPJACK_CRAFT_SPEED, DEFAULT_PUMPJACK_SPEED_MOD,
                                               DEFAULT_PUMPJACK_PROD_MOD, "pumpjack")
            elif category == "chemistry":
                assembly_setup = AssemblySetup(DEFAULT_CHEM_CRAFT_SPEED, DEFAULT_CHEM_SPEED_MOD,
                                               DEFAULT_CHEM_PROD_MOD, "chemical-plant")
            elif category == "oil-processing":
                assembly_setup = AssemblySetup(DEFAULT_OIL_CRAFT_SPEED, DEFAULT_OIL_SPEED_MOD,
                                               DEFAULT_OIL_PROD_MOD, "oil-refinery")
            else:
                print("category: " + category + ", item: " + item)
                assembly_setup = None

            if assembly_setup:
                item_info = self.get_item_info(item, recipe, assembly_setup, wanted_yield)
            else:
                item_info = None

            if item_info:  # TODO recursion stop condition, might change later
                # TODO add recursion depth index? need to know what raw resource is used for what item?
                # TODO maybe for each ingredient have another list/tree, make our own tree class
                try:
                    item_info_list[depth_index].append(item_info)
                except IndexError:
                    item_info_list.append([item_info])

                depth_index = depth_index + 1
                self.calculate_input_tree(item_info.input_list, item_info.input_yield_ps, item_info_list, depth_index)
                depth_index = depth_index - 1


                #TODO make a total summary, a dict with the key the items, if key exists then add on the required assemblies
                # TODO also with ability to remove/filter some items? like green circuits

    def print_tree_summary(self, item_info_list):
        print("\nTree Summary:\n---")
        main_item = True
        for inputs in item_info_list:
            for item_info in inputs:
                print("To make " + str(round(item_info.output_yield_ps[item_info.item], 2)) + " " + item_info.item + " per sec, " +
                      "you need " + str(round(item_info.assemblies_required, 2)) + " " + item_info.assembly_setup.name)

                if main_item:
                    print("Output pas:")
                    for item, pas in item_info.output_pas.items():
                        print(item + ": " + str(round(pas, 3)))

                    print("Input pas:")
                    for item, pas in item_info.input_pas.items():
                        print(item + ": " + str(round(pas, 3)))
                    main_item = False


            print("---")


def main():
    factorio_calc = FactorioCalculator()
    factorio_calc.load_recipes('recipes.json')
    factorio_calc.calculate('rail', 10)


if __name__ == '__main__':
    main()
