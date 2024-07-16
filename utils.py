import matplotlib.pyplot as plt
import numpy as np
from discord import Embed, File
import os 
import dotenv
import torch

dotenv.load_dotenv()
CREDIT: str = os.getenv("CREDIT")

def handle_roll_command(user_input: str):
    """
    Handle the roll command.

    Parameters
    ----------
    user_input : str
        The user input.

    Returns
    -------
    str
        The response to the user input.
    """
    operators = ["+", "-", "*", "/"]
    try:
        #get all dice rolls
        dice_rolls = user_input.split()[1:]

        results = []
        for roll in dice_rolls:
            if "d" in roll:
                num_dice, num_sides, modifier = parse_roll(roll)
                results.append(roll_dice(num_dice, num_sides, modifier))
            elif any(op in roll for op in operators):
                results.append(roll)
            else:
                try:
                    results.append(int(roll))
                except:
                    raise Exception(f"Invalid roll: {roll}")
        
        #sum the results of the rolls
        outcome = 0
        next_operator = "+"
        for i in range(len(results)):
            if type(results[i]) == list:
                outcome += sum(results[i])
            elif type(results[i]) == int or type(results[i]) == float:
                if next_operator == "+":
                    outcome += results[i]
                elif next_operator == "-":
                    outcome -= results[i]
                elif next_operator == "*":
                    outcome *= results[i]
                elif next_operator == "/":
                    outcome /= results[i]
            elif results[i] in operators:
                next_operator = results[i]
            else:
                raise Exception(f"Invalid roll: {results[i]}")
            
        # print(results)
        #format the response showing the results of the rolls
        return f"{user_input[2:]} -> {format_result_array(results)} = {outcome}"
    except Exception as e:
        return f"Error: {e}"


def handle_roll_stats_command(user_input: str):
    """
    Handle the roll stats command.

    Parameters
    ----------
    user_input : str
        The user input.

    Returns
    -------
    str
        The response to the user input.
    """
    operators = ["+", "-", "*", "/"]
    accuracy = {
        1:100,
        2:1000,
        3:10000,
        4:50000,
        5:100000
    }
    try:
        #get all dice rolls
        num_tests = 1000
        #get all dice rolls
        dice_rolls = user_input.split()[1:]
        if dice_rolls[0].startswith("-a"):
            num_tests = accuracy[int(dice_rolls[0][2:])]
            dice_rolls = dice_rolls[1:]
        results = []
        for roll in dice_rolls:
            if "d" in roll:
                num_dice, num_sides, modifier = parse_roll(roll)
                results.append([roll_dice_stats(num_dice, num_sides, modifier, num_tests)])
            elif any(op in roll for op in operators):
                results.append(roll)
            else:
                try:
                    results.append(int(roll))
                except:
                    raise Exception(f"Invalid roll: {roll}")
        
        #sum the results of the rolls
        outcome = torch.zeros(num_tests)
        next_operator = "+"
        for i in range(len(results)):
            if results[i] in operators:
                next_operator = results[i]
                continue

            if next_operator == "+":
                torch.add(outcome, results[i] if type(results[i]) == int else sum(results[i]), out=outcome)
            elif next_operator == "-": 
                torch.sub(outcome, results[i] if type(results[i]) == int else sum(results[i]), out=outcome)
            elif next_operator == "*":
                torch.mul(outcome, results[i] if type(results[i]) == int else sum(results[i]), out=outcome)
            elif next_operator == "/":
                torch.div(outcome, results[i] if type(results[i]) == int else sum(results[i]), out=outcome)
            else:
                raise Exception(f"Invalid roll: {results[i]}")
            
        # create plot of the results
        fig, ax = plt.subplots()
        ax.hist(outcome, bins=20, density=True)
        ax.set_title('Sum of Dice Rolls Distribution')
        ax.set_xlabel('Sum')
        ax.set_ylabel('Probability Density')
        mean = outcome.mean().item()
        variance = outcome.var().item()
        roll = f'{num_tests} Simulations of: ' + "".join(dice_rolls)
        embed = format_embed_message_of_plot(fig=fig, title=roll, x_label="Sum", y_label="Probability Density", description="Distribution of the sum of dice rolls", mean=mean, variance=variance)
        return ["EmbedAndFile", embed[0], embed[1]]
    except Exception as e:
        return ["Embed", format_embed_error_message(e)]


def parse_roll(roll: str):
    """
    Parse a roll command.

    Parameters
    ----------
    roll : str
        The roll command.

    Returns
    -------
    tuple
        The number of dice, the number of sides on each die, and the modifier.
    """
    num_dice = 1
    num_sides = 0
    modifier = ""

    # Split the roll command into its components
    roll_components = roll.split("d")

    # Get the number of dice
    if roll_components[0]:
        num_dice = int(roll_components[0])

    # Get the number of sides on each die and the modifier
    if roll_components[1]:
        if "kh" in roll_components[1]:
            num_sides, modifier = roll_components[1].split("kh")
            modifier = "kh" + modifier
        elif "rr" in roll_components[1]:
            num_sides, modifier = roll_components[1].split("rr")
            modifier = "rr" + modifier
        elif "mi" in roll_components[1]:
            num_sides, modifier = roll_components[1].split("mi")
            modifier = "mi" + modifier
        elif "ma" in roll_components[1]:
            num_sides, modifier = roll_components[1].split("ma")
            modifier = "ma" + modifier
        else:
            num_sides = int(roll_components[1])

    return int(num_dice), int(num_sides), modifier

def roll_dice(num_dice: int, num_sides: int, modifier: str = "") -> torch.Tensor:
    """
    Roll dice.

    Parameters
    ----------
    num_dice : int
        The number of dice to roll.
    num_sides : int
        The number of sides on each die.
    modifier : str
        The modifier to apply to the roll.

    Returns
    -------
    torch.Tensor
        The results of the dice rolls.
    """
    # Roll the dice
    results = torch.randint(1, num_sides + 1, (num_dice,))
    # Apply the modifier
    if modifier:
        if "kh" in modifier:
            if len(modifier) > 2:
                num_highest = int(modifier[2:])
            else:
                num_highest = 1
            _, indices = torch.topk(results, num_highest)
            results = results[indices]
        elif "rr" in modifier:
            if len(modifier) > 2:
                num_rerolls = int(modifier[2:])
            else:
                num_rerolls = 1
            for _ in range(num_rerolls):
                reroll_indices = torch.where(results == 1)[0]
                results[reroll_indices] = torch.randint(1, num_sides + 1, reroll_indices.shape)
        elif "mi" in modifier:
            if len(modifier) > 2:
                min_value = int(modifier[2:])
            else:
                min_value = 1
            results = torch.max(results, torch.tensor(min_value))
        elif "ma" in modifier:
            if len(modifier) > 2:
                max_value = int(modifier[2:])
            else:
                max_value = num_sides
            results = torch.min(results, torch.tensor(max_value))

    return results.tolist()

def roll_dice_stats(num_dice: int, num_sides: int, modifier: str = "", num_tests: int = 1000) -> list[int]:
    """
    Roll dice multiple times and return the results.

    Parameters
    ----------
    num_dice : int
        The number of dice to roll.
    num_sides : int
        The number of sides on each die.
    modifier : str
        The modifier to apply to the roll.
    num_tests : int
        The number of times to roll the dice.

    Returns
    -------
    list[int]
        The results of the dice rolls.
    """
    # Roll the dice multiple times
    results = torch.randint(1, num_sides + 1, (num_tests, num_dice))
    # Apply the modifier
    if modifier:
        if "kh" in modifier:
            if len(modifier) > 2:
                num_highest = int(modifier[2:])
            else:
                num_highest = 1
            _, indices = torch.topk(results, num_highest, dim=1)
            results = results.gather(1, indices)
        elif "rr" in modifier:
            if len(modifier) > 2:
                num_rerolls = int(modifier[2:])
            else:
                num_rerolls = 1
            for _ in range(num_rerolls):
                reroll_indices = torch.where(results == 1)
                results[reroll_indices] = torch.randint(1, num_sides + 1, reroll_indices[0].shape)
        elif "mi" in modifier:
            if len(modifier) > 2:
                min_value = int(modifier[2:])
            else:
                min_value = 1
            results = torch.where(results < min_value, torch.tensor(min_value), results)
        elif "ma" in modifier:
            if len(modifier) > 2:
                max_value = int(modifier[2:])
            else:
                max_value = num_sides
            results = torch.where(results > max_value, torch.tensor(max_value), results)
        
    results = results.sum(dim=1)

    return results

def format_result_array(results: list[int]) -> str:
    """
    Format an array of results.

    Parameters
    ----------
    results : list[int]
        The results to format.

    Returns
    -------
    str
        The formatted results.
    """
    return f"[{', '.join(map(str, results))}]"

def format_embed_message_of_plot(fig: plt, title: str, x_label: str, y_label: str, description: str, mean: float = None, variance: float = None) -> Embed:
    """
    Format an embed message with a plot.

    Parameters
    ----------
    plt : plt
        The plot to include in the embed message.
    title : str
        The title of the plot.
    x_label : str
        The x-axis label of the plot.
    y_label : str
        The y-axis label of the plot.
    description : str
        The description of the plot.

    Returns
    -------
    Embed
        The formatted embed message with the plot.
    File
        The file containing the plot.
    """
    # Save the plot as a temporary file
    dir_path = os.path.dirname(os.path.realpath(__file__)) + "/temp/"
    temp_file_name = "temp" + str(np.random.randint(0, 1000)) + ".png"
    plt.savefig(dir_path + temp_file_name)

    file = File(dir_path + temp_file_name, filename=temp_file_name)
    plt.close()

    embed = Embed()
    embed.title = title
    embed.description = description
    embed.set_image(url="attachment://" + temp_file_name)
    if mean is not None and variance is not None:
        embed.add_field(name="Mean", value=mean)
        embed.add_field(name="Variance", value=variance)
        embed.add_field(name="Standard Deviation", value=variance ** 0.5)
    embed.set_footer(text=f"Powered by {CREDIT}")
    return embed, file

def format_embed_error_message(error: Exception) -> Embed:
    """
    Format an embed message with an error message.

    Parameters
    ----------
    error : Exception
        The error that occurred.

    Returns
    -------
    Embed
        The formatted embed message with the error message.
    """
    embed = Embed()
    embed.title = "Error"
    embed.description = f"An error occurred: {error}"
    embed.set_footer(text=f"Powered by {CREDIT}")
    return embed

def expected_value_of_choosing_highest_dice(num_dice, num_sides):
    """
    Calculate the expected value when choosing the highest dice in a set of dice rolls.
    https://www.youtube.com/watch?v=X_DdGRjtwAo

    Parameters
    ----------
    num_dice : int
        The number of dice to roll each time.
    num_sides : int
        The number of sides on each die.

    Returns
    -------
    float
        The expected value of choosing the highest dice rolled.
    """

    return num_sides * num_dice / (num_dice + 1)  + 1/2

def expected_value_of_choosing_lowest_dice(num_dice, num_sides):
    """
    Calculate the expected value when choosing the lowest dice in a set of dice rolls.
    https://www.youtube.com/watch?v=X_DdGRjtwAo (pinned comment)

    Parameters
    ----------
    num_dice : int
        The number of dice to roll each time.
    num_sides : int
        The number of sides on each die.

    Returns
    -------
    float
        The expected value of choosing the lowest dice rolled.
    """

    return num_sides / (num_dice + 1)  + 1/2

def main():
    print("This is the main function of the dice_utils module")
    


if __name__ == "__main__":
    main()