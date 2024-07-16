# Dice Bot Documentation

## Introduction

This bot is designed to calculate dice statistics through simulating dice rolls.

**Notes:**

- You can set the prefix to whatever you like, but in this document, we will use `$`.
- You can DM yourself private results with another prefix you can specify. In this document, we will use `?`. For example, `!?r d20` would send the result to your DM. Note: the bot host can still see these in the log files.
- Spaces are important for parsing, so follow the examples carefully. Currently, there is no support for parentheses, so calculations are done strictly left to right (NOT following BEDMAS).

## Rolling

### Command Format

```
$r <num_dice>d<num_sides> <operation> <modifier>
```

- `<num_dice>`: The number of dice to roll (default is 1).
- `<num_sides>`: The number of sides on each die.
- `<operation>`: The mathematical operation to apply (one of `+`, `-`, `*`, `/`).
- `<modifier>`: The number to apply the operation with.

### Example

```
$r 4d6 + 5
```

### Description

A user can roll dice similarly to how they would in other apps using the `r` (roll) flag. The default value for `<num_dice>` is 1, and the default operation will be adding 0 to the roll. Supported operations include `+`, `-`, `*`, and `/`. Users can chain expressions.

## Statistics

A user can simulate their roll to determine statistics of the outcome and apply additional modifiers like rerolling 1s and taking the highest result. This is done through the `rs` (roll statistics) flag. The formatting of the command is identical to rolling dice except there are additional optional fields to adjust the simulation. The command will return a plot of the simulation, the mean, and the standard deviation.

### Command Format

```
$rs <accuracy> <num_dice>d<num_sides><dice_mod> <operation> <modifier>
```

- `<accuracy>`: The number of iterations to run for the simulation (1 to 5).
- `<num_dice>`: The number of dice to roll.
- `<num_sides>`: The number of sides on each die.
- `<dice_mod>`: The dice modifier (if any).
- `<operation>`: The mathematical operation to apply (one of `+`, `-`, `*`, `/`).
- `<modifier>`: The number to apply the operation with.

### Examples

```
$rs -a2 4d6 + 5
$rs -a5 2d20kh1 - 5
$rs 10d20rr1
```

### Accuracy

By default, the simulation will run 1,000 iterations, but this can be changed with the `-a` (accuracy) flag. The accuracy flag is in the range [1, 5].

- `1` indicates 100 iterations.
- `2` indicates 1,000 iterations.
- `3` indicates 10,000 iterations.
- `4` indicates 50,000 iterations.
- `5` indicates 100,000 iterations.

**Note:** Higher accuracies will take longer for the bot to respond. Please allow a few minutes when accuracies are above 2.

## Dice Modifiers

There are five types of dice modifiers currently supported:

1. `dX`: No dice modifier. The simulation will assume this dice is normal with no advantage or rerolls.
2. `dXkh`: "Keep highest". If multiple dice are specified, it will roll all of them and only take the highest result. For example, `$r 2d20kh` is the same as `$r d20 adv`.
   - Note: `adv` and `dis` are not implemented yet.
3. `dXrr`: Allows you to simulate rerolling 1s, similar to the "Halfling Luck" feature in D&D 5e.
4. `dXmi`: Replaces rolls below the minimum so that they are equal to the minimum. For example, you could emulate the "Elemental Adept" feature from D&D 5e with `8d6mi2` to turn all 1s into 2s.
5. `dXma`: Replaces rolls below the minimum so that they are equal to the minimum.

### Examples of Dice Modifiers

- `4d6kh3`: Roll 4d6 and keep the highest 3 rolls.
- `2d20rr1`: Roll 2d20 and reroll any 1s.
- `8d6mi2`: Roll 8d6 and replace any roll below 2 with 2.

## Additional Notes and Tips

- Ensure that spaces are used correctly in commands as they are essential for parsing.
- Currently, there is no support for parentheses, so calculations are done strictly from left to right.
- For high accuracy simulations, please be patient as they can take some time to complete.

## Error Handling

- If a command is not recognized or is formatted incorrectly, the bot will provide an error message indicating the issue.
- Ensure that all components of the command are included and correctly formatted.
